"""Pinned acquisition inputs: one invocation, no invented multivalue expansion."""
from copy import deepcopy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_expanded_source_proof import ExpandedSource
from validate_native_json_schemas import build_validators
from v04_conversion_diagnostics import classify_failure, VARIABLE

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / 'tests/fixtures/v04-current-source-proofs/ind-def_shellcommand_windows_test.xml'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
I = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}'
ID = 'oval:navy.navwar.niwcatlantic.scc:tst:4'


class AcquisitionInputProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ET.parse(FILE).getroot()
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())

    def test_original_named_single_value_inputs_still_compile_and_prove(self):
        report = check_conversion(self.visitor(self.root), ID, self.validator)
        self.assertEqual(report['source_proof'], 'PROVED', report)
        self.assertTrue(report['compiled_operands_verified'])
        assessment = assessment_for(self.visitor(self.root), ID)
        self.assertEqual(len(assessment['variables']), 2)

    def constant(self, values, check):
        root = deepcopy(self.root)
        variable = root.find(O + 'variables')[1]
        variable.tag = O + 'constant_variable'; variable[:] = []
        for value in values:
            ET.SubElement(variable, O + 'value').text = value
        obj = root.find(O + 'objects')[3]
        obj.find(I + 'command').set('var_check', check)
        return root

    def test_one_constant_input_is_not_an_array_or_an_implicit_or(self):
        for check in ('all', 'at least one', 'only one'):
            root = self.constant(['netstat'], check)
            report = check_conversion(self.visitor(root), ID, self.validator)
            self.assertEqual(report['source_proof'], 'PROVED', report)
            self.assertTrue(report['compiled_operands_verified'])
            a = assessment_for(self.visitor(root), ID)
            self.assertEqual(a['tests'][a['evaluate']['test']]['object']['command'], 'netstat')

    def test_multivalue_and_complement_inputs_do_not_invent_invocations(self):
        for values, check in ((['netstat', 'whoami'], 'at least one'), (['netstat'], 'none satisfy')):
            root = self.constant(values, check)
            with self.assertRaisesRegex(ValueError, 'approved expansion rule') as error:
                assessment_for(self.visitor(root), ID)
            self.assertEqual(classify_failure(str(error.exception))['category'], VARIABLE)
            with self.assertRaisesRegex(ValueError, 'unproved.*acquisition parameter'):
                ExpandedSource(root).test(ID)

    def test_dynamic_nondefault_quantifier_cannot_be_erased(self):
        root = deepcopy(self.root)
        variable = root.find(O + 'variables')[1]
        variable[:] = []
        ET.SubElement(variable, O + 'object_component',
                      object_ref='oval:navy.navwar.niwcatlantic.scc:obj:1', item_field='stdout_line')
        root.find(O + 'objects')[3].find(I + 'command').set('var_check', 'at least one')
        with self.assertRaisesRegex(ValueError, 'var_check outside bounded proof'):
            assessment_for(self.visitor(root), ID)
        with self.assertRaisesRegex(ValueError, 'unproved runtime acquisition parameter expansion'):
            ExpandedSource(root).test(ID)


if __name__ == '__main__':
    unittest.main()
