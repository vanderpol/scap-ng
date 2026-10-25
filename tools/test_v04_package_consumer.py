"""Adversarial package-consumer checks independent of compiler verification (#251)."""
import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from jsonschema import ValidationError
from test_v04_public_cli_smoke import schema_valid_docs, authoring_archives
from v04_native_bundle_compiler import build_bundle
from verify_v04_package_consumer import verify, canonical, authoring


def fixture():
    docs = schema_valid_docs()
    docs['authoring/demo/applicability.json'] = {
        'applicability': {'id': 'demo-applicability', 'conditions': {}}}
    return docs


class IndependentConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = fixture()
        self.path = self.root / 'sample.scapng'
        self.path.write_bytes(build_bundle(self.docs)[0])

    def mutate(self, change):
        with zipfile.ZipFile(self.path) as z:
            members = {n: z.read(n) for n in z.namelist()}
        manifest = json.loads(members['META-INF/manifest.json'])
        change(members, manifest)
        members['META-INF/manifest.json'] = canonical(manifest)
        target = self.root / 'mutated.scapng'
        with zipfile.ZipFile(target, 'w') as z:
            for name, raw in members.items():
                z.writestr(name, raw)
        return target

    @staticmethod
    def replace(members, row, value):
        data = canonical(value)
        members[row['path']] = data
        row.update(size=len(data), sha256=sha256(data).hexdigest())

    @staticmethod
    def refresh_graph(members, manifest):
        records = []
        for ident, info in manifest['objects'].items():
            doc = json.loads(members[info['path']])
            kind = next(iter(doc))
            records.append({'kind': kind, 'id': ident, 'sha256': sha256(canonical(doc)).hexdigest()})
        records.sort(key=lambda r: (r['kind'], r['id']))
        manifest['build_provenance']['source_graph_sha256'] = sha256(canonical(records)).hexdigest()

    def test_positive_independent_process_external_json_yaml_and_no_compiler_import(self):
        js, ya = authoring_archives(self.docs, self.root)
        script = Path(__file__).with_name('verify_v04_package_consumer.py')
        result = subprocess.run([sys.executable, str(script), str(self.path),
            '--source-json', str(js), '--source-yaml', str(ya)],
            check=True, capture_output=True, text=True)
        report = json.loads(result.stdout)
        self.assertEqual((report['documents'], report['programs'], report['tests']), (4, 1, 1))
        self.assertTrue(report['external_source_compared'])
        self.assertFalse(report['publisher_trust_verified'])
        tree = ast.parse(script.read_text())
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        self.assertFalse(any(n and ('compiler' in n or n.startswith('v04_')) for n in imports))

    def test_crc_damage_rejected(self):
        with zipfile.ZipFile(self.path) as z:
            members = {n: z.read(n) for n in z.namelist()}
        with zipfile.ZipFile(self.path, 'w', compression=zipfile.ZIP_STORED) as z:
            for name, data in members.items():
                z.writestr(name, data)
        raw = bytearray(self.path.read_bytes())
        with zipfile.ZipFile(self.path) as z:
            info = z.getinfo('benchmark.json')
            start = info.header_offset
        name = int.from_bytes(raw[start + 26:start + 28], 'little')
        extra = int.from_bytes(raw[start + 28:start + 30], 'little')
        raw[start + 30 + name + extra] ^= 1
        self.path.write_bytes(raw)
        with self.assertRaises((ValueError, zipfile.BadZipFile)):
            verify(self.path)

    def test_stale_member_hash_and_unlisted_unsafe_members_rejected(self):
        for name in ('extra.json', '../outside.json'):
            target = self.mutate(lambda m, _: m.update({name: b'{}'}))
            with self.assertRaises(ValueError):
                verify(target)
        target = self.mutate(lambda m, _: m.update({'benchmark.json': b'{}'}))
        with self.assertRaisesRegex(ValueError, 'hash/size'):
            verify(target)

    def test_rehashed_compiled_test_and_result_operand_forgery_rejected(self):
        for result in (False, True):
            def change(members, manifest):
                row, = manifest['build_provenance']['compiled_programs'].values()
                program = json.loads(members[row['path']])
                if result:
                    program['result_instructions'][0]['id'] = 'missing-test'
                else:
                    program['test_instructions'][0]['operands']['require']['items_found'] = 'none'
                self.replace(members, row, program)
            with self.assertRaisesRegex(ValueError, 'operand|result program'):
                verify(self.mutate(change))

    def test_unresolved_rule_and_object_refs_rejected_even_after_hash_refresh(self):
        for kind in ('rule', 'assessment', 'applicability', 'requires'):
            def change(members, manifest):
                node_kind = 'assessment' if kind == 'assessment' else 'rule'
                info = next(r for r in manifest['objects'].values() if r['type'] == node_kind)
                doc = json.loads(members[info['path']])
                if kind == 'rule':
                    doc[kind]['assessment_choices']['automated']['assessment'] = 'missing-assessment'
                elif kind == 'applicability':
                    doc['rule']['applicability'] = ['missing-condition']
                elif kind == 'requires':
                    doc['rule']['requires'] = ['missing-rule']
                else:
                    next(iter(doc[kind]['tests'].values()))['object'] = 'missing-object'
                self.replace(members, info, doc)
                self.refresh_graph(members, manifest)
            with self.assertRaisesRegex(ValueError, 'unresolved|Object'):
                verify(self.mutate(change))

    def test_missing_catalog_in_existing_smoke_wrapper_is_not_accepted(self):
        self.path.write_bytes(build_bundle(schema_valid_docs())[0])
        with self.assertRaisesRegex(ValueError, 'applicability catalog'):
            verify(self.path)

    def test_unsupported_package_and_assessment_versions_rejected(self):
        target = self.mutate(lambda _, m: m.update(format_version='0.3.0'))
        with self.assertRaisesRegex(ValueError, 'unsupported package version'):
            verify(target)
        def change(members, manifest):
            info = next(r for r in manifest['objects'].values() if r['type'] == 'assessment')
            doc = json.loads(members[info['path']])
            doc['assessment']['specification']['version'] = '9.0.0'
            self.replace(members, info, doc)
        with self.assertRaises((ValueError, ValidationError)):
            verify(self.mutate(change))

    def test_consistent_altered_package_requires_external_source_to_detect_change(self):
        changed = deepcopy(self.docs)
        a = changed['authoring/demo/assessments/a1.json']['assessment']
        next(iter(a['tests'].values()))['require']['fields']['mode']['equals'] = '0777'
        self.path.write_bytes(build_bundle(changed)[0])
        self.assertFalse(verify(self.path)['publisher_trust_verified'])
        js, _ = authoring_archives(self.docs, self.root)
        with self.assertRaisesRegex(ValueError, 'external authoring'):
            verify(self.path, source=authoring(js))


if __name__ == '__main__':
    unittest.main()
