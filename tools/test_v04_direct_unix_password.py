"""Pinned UNIX password source proofs; no capability-specific lowering algorithm."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree as original_xml

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from audit_v04_eight_assessment_pilot import verify_program
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_scap_source import digest, xml_identity
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from v04_native_bundle_compiler import compile_assessment_program
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/v04-direct-unix'


def convert_case(case):
    tree = ET.fromstring(case['source_xml'])
    source = OvalDocument(tree, 'original')
    visitor = AssessmentConverter(source, 'original', load_mappings())
    expression = visitor.reference(case['definition'], 'definition')
    original = source.node('original', case['definition'], 'definition')
    assessment = {'id': 'original-unix-password-assessment', 'version': 1,
                  'assessment_title': case['title'], 'class': original.get('class'),
                  'purpose': 'assessment', 'mode': 'automated',
                  'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'},
                  'tests': visitor.tests, 'evaluate': expression}
    for section in ('variables', 'shared_objects'):
        if getattr(visitor, section):
            assessment[section] = getattr(visitor, section)
    return tree, assessment


class DirectUnixPasswordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = [json.loads(p.read_text()) for p in sorted((FIXTURES / 'cases').glob('*.json'))]
        cls.validators = build_validators(ROOT / 'schema/v0.4.0')

    def test_six_real_linux_rule_closures_source_schema_compile_and_proof(self):
        self.assertEqual(len(self.cases), 6)
        validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        for case in self.cases:
            with self.subTest(rule=case['rule']):
                source, assessment = convert_case(case)
                checked = validator.validate(original_xml.fromstring(case['source_xml'].encode()))
                self.assertEqual(checked['status'], 'VALID', checked)
                self.assertEqual(list(document_errors(self.validators['assessment.schema.json'], {'assessment': assessment})), [])
                self.assertEqual(expanded_compare(ExpandedSource(source), case['definition'], assessment)['outcome'], 'PROVED')
                program = compile_assessment_program(assessment)
                verify_program(assessment, program)
                actual = ExpandedSource(source).closure(case['definition'])
                self.assertEqual(actual, case['closure'])

    def test_all_six_pinned_original_self_assertion_tests(self):
        provenance = json.loads((FIXTURES / 'provenance.json').read_text())
        raw = (FIXTURES / Path(provenance['path']).name).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), provenance['sha256'])
        root = ET.fromstring(raw)
        model = OvalDocument(root, 'original')
        tests = root.find('{http://oval.mitre.org/XMLSchema/oval-definitions-5}tests')
        self.assertEqual(len(tests), 6)
        for test in tests:
            visitor = AssessmentConverter(model, 'original', load_mappings())
            result = check_conversion(visitor, test.get('id'), self.validators['assessment.schema.json'])
            self.assertTrue(result['compiled'], result)
            self.assertEqual(result['source_proof'], 'PROVED', result)

    def test_changed_existence_or_variable_datatype_is_not_proved(self):
        for case in self.cases:
            source, assessment = convert_case(case)
            wrong = deepcopy(assessment)
            if wrong.get('variables'):
                variable = next((v for v in wrong['variables'].values() if v['datatype'] == 'integer'), None)
                if variable is None:
                    continue
                variable['datatype'] = 'string'
            else:
                test = next(iter(wrong['tests'].values()))
                test['require']['items_found'] = 'none'
            self.assertNotEqual(expanded_compare(ExpandedSource(source), case['definition'], wrong)['outcome'], 'PROVED')

    def test_compiled_operand_mutation_fails_independent_program_check(self):
        _, assessment = convert_case(self.cases[0])
        program = compile_assessment_program(assessment)
        wrong = deepcopy(program)
        wrong['test_instructions'][0]['operands']['require']['items_found'] = 'none'
        with self.assertRaises((AssertionError, ValueError)):
            verify_program(assessment, wrong)

    def test_original_foreign_state_field_namespace_is_rejected(self):
        case = self.cases[0]
        source, _ = convert_case(case)
        state = next(n for n in source.iter() if n.tag.endswith('}password_state'))
        state[0].tag = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}' + state[0].tag.rsplit('}', 1)[-1]
        with self.assertRaises(ValueError):
            ExpandedSource(source).state(state.get('id'), 'unix.password')


if __name__ == '__main__':
    unittest.main()
