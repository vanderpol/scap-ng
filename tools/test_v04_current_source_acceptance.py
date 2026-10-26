"""Original-source current acceptance, independent negatives, no archive rewrite."""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET

from prove_v04_current_bluetooth_source import prove as prove_bluetooth, FIXTURE
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_scap_source import SourceModel, UnsupportedSource
from v04_source_proof_contract import validators
from v04_canonical_source_ir import normalize_documents, decode_and_verify
from audit_v04_eight_assessment_pilot import verify_program

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/fixtures/v04-current-source-proofs'
SCHEMA = ROOT / 'schema/v0.4.0'
XSD = ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3'
CASES = (
    ('shellcommand', DATA / 'ind-def_shellcommand_windows_test.xml', 1, 6),
    ('cmdlet', DATA / 'win-def_cmdlet_test.xml', 3, 3),
    ('cmdlet_variable', DATA / 'win-def_cmdlet_test.xml', 3, 3),
    ('wmi57', ROOT / 'tests/fixtures/v04-absence-only/win-def_wmi57_object_test.xml', 5, 5),
)


class CurrentSourceAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.output = Path(cls.temp.name)
        cls.proofs = {}
        for name, path, count, tests in CASES:
            module = importlib.import_module('prove_v04_oval_windows_' + name + '_source')
            cls.proofs[name] = module.prove(path, SCHEMA, XSD, cls.output / name)
        cls.bluetooth = prove_bluetooth(FIXTURE, cls.output / 'bluetooth')

    def test_all_original_assertions_schema_compile_consumer_and_source_counts(self):
        for name, _, count, tests in CASES:
            proof = self.proofs[name]
            self.assertEqual(proof['native_assessment_schema'], 'PASS')
            self.assertEqual(len(proof['current_compilation']), count)
            actual_tests = 0
            for row in proof['current_compilation']:
                self.assertTrue(row['synthetic_benchmark_wrapper'])
                self.assertEqual(row['compiler']['native_source_schema'], 'PASS')
                actual_tests += row['compiler']['tests']
            self.assertEqual(actual_tests, tests)

    def test_original_set_filters_all_operators_nesting_and_negative_controls(self):
        from test_v04_oval_set_filter_source import prove
        proof = prove(DATA / 'oval-def_set-windows.xml', XSD)
        self.assertTrue(proof['synthetic_item_semantics_equal'])
        self.assertTrue(proof['filters_evaluated_before_set_operator'])
        self.assertEqual(proof['native_set_objects_valid'], 7)
        self.assertEqual(set(proof['operators']), {'union', 'intersection', 'difference'})
        self.assertGreaterEqual(proof['maximum_nesting'], 3)

    def test_additional_original_mac_lockout_and_fixed_unknown_graphs(self):
        for family in ('macos_diskinfo', 'macos_softwareupdate', 'macos_systemsetup',
                       'windows_lockout', 'unknown'):
            module = importlib.import_module('prove_v04_oval_' + family + '_source')
            proof = module.prove(DATA / module.FILE, SCHEMA, XSD, self.output / family)
            self.assertEqual(proof['native_assessment_schema'], 'PASS')
            self.assertEqual(proof['original_root_semantic_graph'], 'PASS')
        from prove_v04_oval_macos_statefree_source import prove
        results = prove(DATA, SCHEMA, XSD, self.output / 'macos-statefree')
        self.assertEqual(len(results), 3)
        for proof in results.values():
            self.assertEqual(proof['native_assessment_schema'], 'PASS')

    def test_bluetooth_actual_applicability_direct_filter_and_synthetic_union_negative(self):
        proof = self.bluetooth
        self.assertEqual(proof['outcome'], 'PROVED')
        self.assertEqual(len(proof['original_closure']['nodes']), 4)
        self.assertFalse(proof['original_set_present'])
        self.assertFalse(proof['historical_archive_used'])
        self.assertIn('synthetic_union', proof['mutations_rejected'])
        self.assertEqual(len(proof['mutations_rejected']), 5)
        self.assertTrue(proof['context']['uses'])

    def test_bluetooth_compiled_operand_and_boolean_mutations_are_rejected(self):
        path, = (self.output / 'bluetooth/compiled').glob('*.scapng')
        with zipfile.ZipFile(path) as package:
            manifest = json.loads(package.read('META-INF/manifest.json'))
            info, = manifest['build_provenance']['compiled_programs'].values()
            program = json.loads(package.read(info['path']))
        assessment = json.loads((self.output / 'bluetooth/bluetooth.assessment.json').read_text())['assessment']
        verify_program(assessment, program)
        bad = deepcopy(program)
        bad['test_instructions'][0]['operands']['object']['command'] += ' -altered'
        with self.assertRaises(ValueError):
            verify_program(assessment, bad)
        bad = deepcopy(program)
        bad['result_expression_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            verify_program(assessment, bad)

    def test_deprecated_original_wmi_is_an_error_not_a_wmi57_upgrade(self):
        source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype/server2025-signed.zip',
            '2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0')
        found = set()
        for component, nodes in source.nodes.items():
            for node in nodes.values():
                kind = {'wmi_test': 'test', 'wmi_object': 'object'}.get(node.tag.rsplit('}', 1)[-1])
                if kind:
                    converter = AssessmentConverter(source, component, load_mappings())
                    with self.assertRaisesRegex(UnsupportedSource, 'unsupported .* capability'):
                        converter.capability(node, kind)
                    found.add(kind)
        # This original STIG uses deprecated WMI as a Variable Object, not a
        # standalone Test. Cover its real node and a separately labeled typed
        # Test mutation; do not claim the latter is an original fixture.
        self.assertEqual(found, {'object'})
        controlled_test = ET.Element('{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}wmi_test')
        with self.assertRaisesRegex(UnsupportedSource, 'unsupported test capability'):
            AssessmentConverter(source, component, load_mappings()).capability(controlled_test, 'test')

    def test_current_reverse_export_boundary_rejects_old_native_grammar(self):
        import prove_v04_oval_windows_shellcommand_source as module
        raw = (DATA / 'ind-def_shellcommand_windows_test.xml').read_bytes()
        with self.assertRaises(ValueError):
            module.native_to_oval(module._read_source_view(raw))

    def test_field_index_is_stable_after_canonical_json_and_forgery_fails(self):
        path = self.output / 'wmi57/compiled/original-windows-wmi57-10-assessment.json.zip'
        with zipfile.ZipFile(path) as package:
            docs = {name: json.loads(package.read(name)) for name in package.namelist()}
        ir = normalize_documents(docs)
        canonical = json.loads(json.dumps(ir, sort_keys=True))
        self.assertEqual(decode_and_verify(canonical), docs)
        altered = deepcopy(canonical)
        test = next(r['typed_tests'][0] for r in altered['records'] if r['typed_tests'])
        test['field_requirements'][0]['path'].append('forged')
        with self.assertRaises(ValueError):
            decode_and_verify(altered)

    def test_explicit_migration_covers_variable_object_filters_but_not_literal_records(self):
        from build_v04_canonical_six_stigs import promote, recover
        from v04_canonical_source_ir import validate_docs
        from v04_object_contract import object_sites
        source = json.loads((DATA / 'historical-sv278028.json').read_text())
        with self.assertRaisesRegex(ValueError, 'Object schema failure'):
            validate_docs({'authoring/historical.json': source}, validators())
        current, _ = promote(source, legacy_review=True)
        validate_docs({'authoring/current.json': current}, validators())
        recover(current, source, legacy_review=True)
        self.assertEqual(promote(current, legacy_review=True)[0], current)
        targets = [site.node for site in object_sites(current['assessment'])
                   if site.path[1] == 'variables' and 'set' in site.node]
        self.assertTrue(targets)
        changed = deepcopy(current)
        target = next(site.node for site in object_sites(changed['assessment'])
                      if site.path[1] == 'variables' and 'set' in site.node)
        predicate = target['set']['operands'][0]['filters'][0]['include']['result']
        self.assertEqual(predicate['values_matching'], 'every')
        predicate['matches_regex'] = 'changed-original-filter'
        with self.assertRaises(ValueError):
            recover(changed, source, legacy_review=True)
        literal = {'datatype': 'record', 'value': {'require': 'literal data',
                   'value_match': 'literal data', 'object': {'collect': {'never': 'visit'}}}}
        enriched = deepcopy(source)
        enriched['assessment']['variables']['literal-metadata-variable'] = {
            'kind': 'constant', 'datatype': 'record', 'expression': {'literal': literal}}
        migrated, _ = promote(enriched, legacy_review=True)
        self.assertEqual(migrated['assessment']['variables']['literal-metadata-variable']['expression']['literal'], literal)


if __name__ == '__main__':
    unittest.main()
