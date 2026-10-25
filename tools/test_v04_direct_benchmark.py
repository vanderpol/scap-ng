"""Whole original Benchmark acceptance, with separately labeled fault injection."""
from copy import copy, deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL, XCCDF
from v04_direct_converter import CAPABILITIES, convert, convert_benchmark
from v04_direct_inventory import SourceInventory
from audit_v04_direct_benchmark import verify_original, verify_inventory, verify_compiled, public_gates, accepted_coverage
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-prototype'
PINS = json.loads((FIXTURE / 'provenance.json').read_text())
O, X = '{' + OVAL + '}', '{' + XCCDF + '}'


class DirectBenchmarkAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(FIXTURE / PINS['fixture'], PINS['zip_sha256'])
        cls.documents, cls.trace, cls.coverage = convert_benchmark(cls.source)
        cls.bundle = build_bundle(cls.documents)[0]

    def restricted(self, identifiers):
        """Source-backed admission unit: restrict the discovery lookup, not XML semantics.

        This controlled test view is not published as a complete source inventory.
        The unmodified complete 291-Rule inventory has its own independent test.
        """
        source = copy(self.source)
        source.rules = {identifier: source.rules[identifier] for identifier in identifiers}
        return source

    def test_complete_inventory_and_denominators_match_independent_original_reader(self):
        result = verify_inventory(self.source.root, self.coverage)
        self.assertEqual((result['original_rules'], result['original_profiles'], result['checks']), (291, 11, 843))
        self.assertEqual(self.coverage['summary']['statuses'], {'blocked': 207, 'converted': 84})
        self.assertEqual(len(self.trace['omitted_rules']), 207)
        self.assertEqual(self.source.parse_count, 1)

    def test_all_emitted_references_schemas_capabilities_and_shared_titles(self):
        validators = build_validators(ROOT / 'schema/v0.4.0')
        bindings = {b['source_rule']: b for b in self.trace['rules']}
        for row in self.coverage['rules']:
            with self.subTest(rule=row['source_rule']):
                if row['status'] == 'blocked':
                    self.assertTrue(row['blockers'])
                    self.assertEqual(row['artifacts'], [])
                    self.assertEqual(row['proof_level'], 'none')
                    self.assertNotIn(row['source_rule'], bindings)
                    continue
                self.assertLessEqual(set(row['needed_capabilities']), set(CAPABILITIES))
                self.assertEqual(len(row['artifacts']), 2)
                self.assertEqual(row['proof_level'], 'authoring_validated')
                for path in row['artifacts']:
                    document = self.documents[path]
                    kind, = document
                    self.assertEqual(list(document_errors(validators[kind + '.schema.json'], document)), [])
                    for obj in document.get('assessment', {}).get('shared_objects', {}).values():
                        self.assertTrue(obj['object_title'])
        self.assertEqual(len(self.documents), 170)
        self.assertTrue(self.documents['authoring/direct-slice/benchmark.json']['benchmark']['metadata']['prototype_subset'])

    def test_every_claimed_proof_and_every_compiled_operand_including_original_pair(self):
        proofs = verify_original(self.source.root, self.documents, self.trace, require_proof=False)
        self.assertEqual(sum(p['outcome'] == 'PROVED' for p in proofs), 81)
        self.assertEqual(sum(p['outcome'] == 'UNVERIFIABLE/UNSUPPORTED' for p in proofs), 3)
        self.assertEqual(len(verify_compiled(self.documents, self.bundle)), 84)
        accepted = accepted_coverage(self.coverage, self.trace, proofs, verify_compiled(self.documents, self.bundle))
        self.assertEqual(accepted['summary']['proof_levels'], {'compiled_unproved': 3, 'none': 207, 'source_proved': 81})
        wrong = deepcopy(proofs)
        wrong[0]['outcome'] = 'MISMATCH'
        with self.assertRaises(AssertionError):
            accepted_coverage(self.coverage, self.trace, wrong, verify_compiled(self.documents, self.bundle))
        for identifier in PINS['rules']:
            position = next(i for i, row in enumerate(self.trace['rules']) if row['source_rule'] == identifier)
            self.assertEqual(proofs[position]['outcome'], 'PROVED')
            documents, _ = convert(self.source, [identifier])
            for path, document in documents.items():
                if 'assessment' in document:
                    self.assertEqual(document, self.documents[path])

    def test_zero_one_many_and_mixed_capability_admission(self):
        converted = [r for r in self.coverage['rules'] if r['status'] == 'converted']
        blocked = next(r['source_rule'] for r in self.coverage['rules'] if r['status'] == 'blocked')
        registry = [r['source_rule'] for r in converted if r['needed_capabilities'] == ['windows.registry']]
        mixed = next(r['source_rule'] for r in converted if len(r['needed_capabilities']) > 1)
        self.assertGreater(len(registry), 2)
        for identifiers, count in [([blocked], 0), ([blocked, registry[0]], 1), (registry[:3] + [mixed, blocked], 4)]:
            with self.subTest(count=count):
                documents, trace, coverage = convert_benchmark(self.restricted(identifiers))
                self.assertEqual(len(trace['rules']), count)
                self.assertEqual(sum(coverage['summary']['statuses'].values()), len(identifiers))
                self.assertEqual(sum('assessment' in d for d in documents.values()), count)
                if count == 0:
                    self.assertEqual(documents, {})

    def test_missing_and_cyclic_dependencies_are_isolated_per_rule(self):
        for mutation in ('missing', 'cycle'):
            source = deepcopy(self.restricted(PINS['rules']))
            component, _, _ = source.automated_check(source.rules[PINS['rules'][0]])
            variable = next(n for n in source.nodes[component].values() if n.tag == O + 'local_variable'
                            and n.get('id') in self.trace_binding(PINS['rules'][0])['dependencies'])
            for child in list(variable):
                variable.remove(child)
            ET.SubElement(variable, O + 'variable_component', var_ref=variable.get('id') if mutation == 'cycle' else 'missing-variable')
            documents, trace, coverage = convert_benchmark(source)
            self.assertEqual([r['source_rule'] for r in trace['rules']], [PINS['rules'][1]])
            row = next(r for r in coverage['rules'] if r['source_rule'] == PINS['rules'][0])
            self.assertTrue(any(b['category'] == 'source-invalid' for b in row['blockers']))
            self.assertEqual(sum('assessment' in d for d in documents.values()), 1)

    def trace_binding(self, identifier):
        return next(r for r in self.trace['rules'] if r['source_rule'] == identifier)

    def test_profile_and_unsupported_obligations_do_not_silently_disappear(self):
        source = deepcopy(self.restricted(PINS['rules']))
        ET.SubElement(source.benchmark.find(X + 'Profile'), X + 'refine-rule', idref=PINS['rules'][0])
        documents, _, coverage = convert_benchmark(source)
        self.assertEqual(documents, {})
        self.assertTrue(all(any(b['category'] == 'unsupported-selection' for b in r['blockers']) for r in coverage['rules']))
        # A supported capability does not make unsupported sibling obligations admissible.
        source = deepcopy(self.restricted([PINS['rules'][1]]))
        component, _, _ = source.automated_check(source.rules[PINS['rules'][1]])
        state = next(n for n in source.nodes[component].values() if n.tag.endswith('registry_state')
                     and n.get('id') in self.trace_binding(PINS['rules'][1])['dependencies'])
        state[0].set('operation', 'unapproved-operation')
        state[1].set('operation', 'another-unapproved-operation')
        documents, _, coverage = convert_benchmark(source)
        self.assertFalse(documents)
        paths = {b.get('source_path') for b in coverage['rules'][0]['blockers'] if b['source_id'] == state.get('id')}
        self.assertGreaterEqual(len(paths), 3)  # Whole node plus both independent entity obligations.

    def test_determinism_and_independent_negative_inventory_and_program_guards(self):
        documents, trace, coverage = convert_benchmark(self.source)
        self.assertEqual((documents, trace, coverage), (self.documents, self.trace, self.coverage))
        mutant = deepcopy(coverage)
        next(r for r in mutant['rules'] if r['dependencies'])['dependencies'].pop()
        with self.assertRaises(AssertionError):
            verify_inventory(self.source.root, mutant)
        mutant = deepcopy(coverage)
        mutant['rules'].pop()
        with self.assertRaises(AssertionError):
            verify_inventory(self.source.root, mutant)
        with zipfile.ZipFile(io.BytesIO(self.bundle)) as package:
            members = {n: package.read(n) for n in package.namelist()}
        manifest = json.loads(members['META-INF/manifest.json'])
        info = next(iter(manifest['build_provenance']['compiled_programs'].values()))
        program = json.loads(members[info['path']])
        program['test_instructions'][0]['operands']['require']['items_found'] = 'none'
        members[info['path']] = json.dumps(program).encode()
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as package:
            for name, raw in members.items():
                package.writestr(name, raw)
        with self.assertRaises(ValueError):
            verify_compiled(documents, output.getvalue())

    def test_full_and_inventory_public_cli_and_unmodified_public_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            for mode in ('--inventory-only', '--all-rules'):
                output = directory / mode.removeprefix('--')
                process = subprocess.run([sys.executable, str(ROOT / 'tools/v04_direct_converter.py'),
                    str(FIXTURE / PINS['fixture']), '--sha256', PINS['zip_sha256'], mode, '--output', str(output)],
                    capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stderr)
                coverage = json.loads((output / 'coverage.json').read_text())
                self.assertEqual(len(coverage['rules']), 291)
                self.assertIn('291', str(coverage['summary']['source_rules']))
                if mode == '--inventory-only':
                    self.assertFalse((output / 'authoring').exists())
                    self.assertEqual(coverage['summary']['statuses'], {'inventoried': 291})
                else:
                    self.assertEqual(coverage, self.coverage)
                    for path, document in self.documents.items():
                        self.assertEqual(json.loads((output / path).read_text()), document)
                    gates, bundle = public_gates(output, directory / 'public-gates')
                    self.assertEqual((gates['json_valid'], gates['yaml_valid']), (170, 170))
                    self.assertEqual(bundle.read_bytes(), self.bundle)


if __name__ == '__main__':
    unittest.main()
