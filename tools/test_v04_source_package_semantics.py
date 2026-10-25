#!/usr/bin/env python3
"""Pinned actual package/source proof terms and adversarial boundaries (#251)."""
import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from audit_v04_eight_assessment_pilot import CASES, original, verify_program
from v04_source_package_semantics import (Native, Source, Unsupported, compare,
                                         digest, local, xml_term)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/v04-source-package-pilot'


def fixture(platform='ms_windows_11', rule='SV-253254'):
    return json.loads((FIXTURES / (platform + '-' + rule + '.json')).read_text())


def checked(f):
    source = Source(ET.fromstring(f['source_xml']))
    source.closure(f['source_definition'])
    return compare(source, f['source_definition'], f['assessment'])


def consistently_rehash_program(f):
    """An internally consistent forged graph must still fail ORIGINAL proof."""
    p, a = f['compiled_program'], f['assessment']
    p['assessment_source_sha256'] = digest(a)
    for i in p['test_instructions']:
        t = a['tests'][i['test_id']]
        i['operands'], i['source_test_sha256'] = deepcopy(t), digest(t)
    verify_program(a, p)


class ExactOriginalPackageProofTests(unittest.TestCase):
    def test_all_eight_exact_graph_outcomes_and_source_fingerprints(self):
        for platform, rule, _ in CASES:
            with self.subTest(platform=platform, rule=rule):
                f = fixture(platform, rule)
                source = Source(ET.fromstring(f['source_xml']))
                closure = source.closure(f['source_definition'])
                self.assertEqual(closure['nodes'], f['provenance']['source_dependency_closure']['nodes'])
                self.assertEqual(digest({'assessment': f['assessment']}), f['provenance']['assessment_sha256'])
                self.assertEqual(digest(f['compiled_program']), f['provenance']['program_sha256'])
                verify_program(f['assessment'], f['compiled_program'])
                self.assertEqual(checked(f)['outcome'], f['expected_outcome'])

    def test_changed_literal_selector_is_mismatch(self):
        f = fixture()
        t = next(iter(f['assessment']['tests'].values()))
        t['object']['key']['equals'] += '\\Changed'
        consistently_rehash_program(f)
        result = checked(f)
        self.assertEqual(result['outcome'], 'MISMATCH')
        self.assertIn('selectors.key', result['first_divergence']['path'])

    def test_changed_test_quantifiers_are_mismatches(self):
        for axis, value in (('items_found', 'may_be_absent'), ('items_satisfying', 'one_or_more')):
            with self.subTest(axis=axis):
                f = fixture()
                next(iter(f['assessment']['tests'].values()))['require'][axis] = value
                consistently_rehash_program(f)
                self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_changed_boolean_structure_is_mismatch(self):
        f = fixture('ms_windows_11', 'SV-253260')
        f['assessment']['evaluate'] = {'or': f['assessment']['evaluate']['and']}
        self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_changed_state_operator_is_mismatch(self):
        f = fixture()
        root = ET.fromstring(f['source_xml'])
        next(n for n in root.iter() if local(n) == 'registry_test').set('state_operator', 'AND')
        f['source_xml'] = ET.tostring(root, encoding='unicode')
        self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_missing_original_dependency_is_rejected_before_comparison(self):
        f = fixture()
        root = ET.fromstring(f['source_xml'])
        section = next(n for n in root if local(n) == 'states')
        section.remove(section[0])
        with self.assertRaisesRegex(Unsupported, 'missing original reference'):
            Source(root).closure(f['source_definition'])

    def test_missing_native_variable_subgraph_cannot_prove(self):
        f = fixture('ms_windows_server_dns', 'SV-259345')
        f['assessment']['variables'].clear()
        result = checked(f)
        self.assertEqual(result['outcome'], 'UNVERIFIABLE/UNSUPPORTED')
        self.assertTrue(any('missing native reference' in x['reason'] for x in result['unsupported_obligations']))

    def test_dynamic_command_and_function_operands_are_compared(self):
        f = fixture('ms_windows_server_dns', 'SV-259345')
        variable = next(iter(f['assessment']['variables'].values()))
        variable['expression']['concat'][0]['literal']['value'] += 'CHANGED'
        self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_record_and_expected_array_mutations_are_mismatches(self):
        for mutation in ('record', 'array'):
            with self.subTest(mutation=mutation):
                f = fixture('ms_windows_server_2025', 'SV-278001')
                tests = f['assessment']['tests']
                if mutation == 'record':
                    t = next(t for t in tests.values() if t['capability'] == 'windows.wmi.query')
                    t['require']['or'][0]['fields']['result']['record']['fields']['domainrole']['equals'] = '6'
                else:
                    t = next(t for t in tests.values() if t['capability'] == 'independent.shellcommand')
                    t['require']['and'][0]['fields']['stdout_line']['matches_regex'].pop()
                self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_variable_datatype_does_not_erase_comparison_datatype(self):
        f = fixture('ms_windows_server_2025', 'SV-278001')
        root = ET.fromstring(f['source_xml'])
        n = next(n for n in root.iter() if local(n) == 'stdout_line' and n.get('var_ref'))
        n.set('datatype', 'integer')
        f['source_xml'] = ET.tostring(root, encoding='unicode')
        self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_empty_comparisons_are_not_silently_discarded(self):
        f = fixture('ms_windows_server_dns', 'SV-259345')
        root = ET.fromstring(f['source_xml'])
        n = next(n for n in root.iter() if n.get('check_existence') == 'none_exist')
        n.set('operation', 'equals')
        n.text = ''
        f['source_xml'] = ET.tostring(root, encoding='unicode')
        self.assertEqual(checked(f)['outcome'], 'UNVERIFIABLE/UNSUPPORTED')
        f = fixture('oracle_linux_9', 'SV-271844')
        self.assertEqual(checked(f)['outcome'], 'UNVERIFIABLE/UNSUPPORTED')

    def test_all_exist_is_not_broadened_or_automatically_normalized(self):
        f = fixture()
        root = ET.fromstring(f['source_xml'])
        next(n for n in root.iter() if local(n) == 'registry_test').set('check_existence', 'all_exist')
        f['source_xml'] = ET.tostring(root, encoding='unicode')
        result = checked(f)
        self.assertEqual(result['outcome'], 'UNVERIFIABLE/UNSUPPORTED')
        self.assertEqual(result['normalizations_applied'], [])

    def test_program_operand_and_result_instruction_mutations_rejected(self):
        for which in ('operand', 'boolean', 'source-hash', 'missing-test'):
            with self.subTest(which=which):
                f = fixture()
                p = f['compiled_program']
                if which == 'operand':
                    p['test_instructions'][0]['operands']['require']['items_found'] = 'none'
                elif which == 'boolean':
                    p['result_instructions'][0]['id'] = 'missing-test'
                elif which == 'source-hash':
                    p['assessment_source_sha256'] = '0' * 64
                else:
                    p['test_instructions'].clear()
                with self.assertRaises(ValueError):
                    verify_program(f['assessment'], p)

    def test_unknown_source_and_native_semantic_attributes_fail_closed(self):
        for side in ('source', 'native'):
            with self.subTest(side=side):
                f = fixture()
                if side == 'source':
                    root = ET.fromstring(f['source_xml'])
                    next(n for n in root.iter() if local(n) == 'registry_test').set('new_semantics', 'true')
                    f['source_xml'] = ET.tostring(root, encoding='unicode')
                else:
                    next(iter(f['assessment']['tests'].values()))['new_semantics'] = True
                self.assertEqual(checked(f)['outcome'], 'UNVERIFIABLE/UNSUPPORTED')

    def test_collection_error_flags_and_variable_order_are_not_erased(self):
        for which in ('error-flag', 'function-order'):
            with self.subTest(which=which):
                f = fixture('ms_windows_server_dns', 'SV-259345')
                if which == 'error-flag':
                    next(iter(f['assessment']['tests'].values()))['object']['error_if_stderr_exists'] = True
                else:
                    next(iter(f['assessment']['variables'].values()))['expression']['concat'].reverse()
                self.assertEqual(checked(f)['outcome'], 'MISMATCH')

    def test_original_reference_cycle_is_rejected(self):
        f = fixture()
        source = Source(ET.fromstring(f['source_xml']))
        root = source.nodes[f['source_definition']]
        criteria = next(n for n in root if local(n) == 'criteria')
        criteria.clear()
        ET.SubElement(criteria, '{http://oval.mitre.org/XMLSchema/oval-definitions-5}extend_definition',
                      definition_ref=f['source_definition'])
        with self.assertRaisesRegex(Unsupported, 'cyclic original dependency'):
            source.closure(f['source_definition'])

    def test_comparison_is_independent_of_converter_compiler_exporter(self):
        for name in ('v04_source_package_semantics.py', 'audit_v04_eight_assessment_pilot.py'):
            tree = ast.parse((ROOT / 'tools' / name).read_text())
            imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
            self.assertFalse(any(any(x in (m or '') for x in ('converter', 'compiler', 'export', 'upconvert'))
                                 for m in imports))

    def test_catalog_scopes_duplicate_oval_ids_to_correct_component(self):
        f = fixture()
        od = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'
        scap = 'http://scap.nist.gov/schema/scap/source/1.2'
        xc = 'http://checklists.nist.gov/xccdf/1.2'
        root = ET.Element('{' + scap + '}data-stream-collection')
        cref = ET.SubElement(root, '{' + scap + '}component-ref', id='right-ref')
        cref.set('{http://www.w3.org/1999/xlink}href', '#right-component')
        ET.SubElement(root, '{urn:oasis:names:tc:entity:xmlns:xml:catalog}uri',
                      name='source.xml', uri='#right-ref')
        for ident in ('wrong-component', 'right-component'):
            comp = ET.SubElement(root, '{' + scap + '}component', id=ident)
            comp.append(ET.fromstring(f['source_xml']))
        rule = ET.SubElement(root, '{' + xc + '}Rule', id='xccdf_demo_rule_SV-253254r1_rule')
        check = ET.SubElement(rule, '{' + xc + '}check', system=od, selector='automated')
        ET.SubElement(check, '{' + xc + '}check-content-ref', href='source.xml', name=f['source_definition'])
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'source.zip'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('original.xml', ET.tostring(root))
            pin = {'file': path.name, 'zip_sha256': sha256(path.read_bytes()).hexdigest(),
                   'revision': 'test-only', 'source_path': 'test-only'}
            _, definition, evidence = original(Path(td), 'test', 'SV-253254', {'test': pin})
            self.assertEqual(definition, f['source_definition'])
            self.assertEqual(evidence['component'], 'right-component')
            pin['zip_sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'ZIP pin mismatch'):
                original(Path(td), 'test', 'SV-253254', {'test': pin})

    def test_unused_native_declarations_cannot_receive_whole_graph_proof(self):
        f = fixture()
        f['assessment']['variables'] = {'unused-variable': {'kind': 'local', 'datatype': 'string',
                                                          'expression': {'literal': 'unproved'}}}
        with self.assertRaisesRegex(Unsupported, 'unaccounted native declarations'):
            checked(f)


if __name__ == '__main__':
    unittest.main()
