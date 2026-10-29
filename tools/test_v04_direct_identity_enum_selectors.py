"""Closed enum identity graphs: preserve names, structure and var_check."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion, closure
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_inventory import SourceInventory
from lxml import etree
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_scap_source import native_identifier
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from validate_native_json_schemas import build_validators
ROOT = Path(__file__).resolve().parents[1]
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
W = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}'
PREFIX = 'oval:navy.navwar.niwcatlantic.scc.test:'
CASES = [('v04-direct-enum-selectors', 'win-def_appcmd_test.xml', 101, 'Apppool'), ('v04-windows-acquisition-proof', 'win-def_appcmdlistconfig_test.xml', 301, 'Site')]

class IdentityEnumSelectorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def original(self, case):
        folder, file, _, _ = case
        directory = ROOT / 'tests/fixtures' / folder
        pin = json.loads((directory / 'provenance.json').read_text())
        raw = (directory / file).read_bytes()
        item = next((x for x in pin.get('files', [pin]) if Path(x['path']).name == file))
        self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
        return ET.fromstring(raw)

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())

    def proved(self, root, ident):
        source = OvalDocument(root, 'original.xml')
        nodes = {i: n for (_, i), n in SourceInventory(source).nodes.items()}
        ids, problems = closure(nodes, ident)
        self.assertFalse(problems)
        check = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3').validate(etree.fromstring(ET.tostring(root)))
        validity = closure_validity([nodes[i] for i in ids], {'original.xml': check})
        self.assertEqual(validity['status'], 'VALID', validity)
        self.assertFalse(any((i['kind'] == 'deprecated' for i in validity['issues'])))
        report = check_conversion(self.visitor(root), ident, self.validator)
        self.assertEqual(report['source_proof'], 'PROVED', report)
        self.assertTrue(report['compiled_operands_verified'])
        return assessment_for(self.visitor(root), ident)

    def test_both_pinned_originals_preserve_named_variables(self):
        for case in CASES:
            with self.subTest(file=case[1]):
                root = self.original(case)
                before = ET.tostring(root)
                identifier = PREFIX + 'tst:' + str(case[2])
                a = self.proved(root, identifier)
                source = root.find(O + 'variables').find("*[@id='" + PREFIX + 'var:' + str(case[2]) + "']")
                name = native_identifier(source, 'variable')
                obj = a['tests'][a['evaluate']['test']]['object']
                self.assertEqual(obj['identifier_type']['equals'], {'variable': name})
                self.assertIn(name, a['variables'])
                self.assertEqual(ET.tostring(root), before)

    def test_reference_unique_graph_preserves_all_four_quantifiers(self):
        case = CASES[1]
        for check in ('all', 'at least one', 'none satisfy', 'only one'):
            with self.subTest(check=check):
                root = self.original(case)
                variables = root.find(O + 'variables')
                local = variables.find("*[@id='" + PREFIX + "var:301']")
                local[:] = []
                node = ET.SubElement(local, O + 'unique')
                ET.SubElement(node, O + 'variable_component', var_ref=PREFIX + 'var:999')
                constant = ET.SubElement(variables, O + 'constant_variable', id=PREFIX + 'var:999', version='1', datatype='string', comment='Closed duplicate Site values')
                ET.SubElement(constant, O + 'value').text = 'Site'
                ET.SubElement(constant, O + 'value').text = 'Site'
                obj = root.find(O + 'objects').find("*[@id='" + PREFIX + "obj:301']")
                obj.find(W + 'identifier_type').set('var_check', check)
                self.proved(root, PREFIX + 'tst:301')

    def test_unknown_values_casts_and_computed_graphs_stay_blocked(self):
        for mutation in ('unknown', 'cast', 'concat', 'object'):
            with self.subTest(mutation=mutation):
                root = self.original(CASES[1])
                node = root.find(O + 'variables').find("*[@id='" + PREFIX + "var:301']")
                if mutation == 'unknown':
                    node[0].text = 'not-a-supported-identifier'
                elif mutation == 'cast':
                    node.set('datatype', 'int')
                    node[0].set('datatype', 'int')
                    node[0].text = '1'
                elif mutation == 'concat':
                    node[:] = []
                    expression = ET.SubElement(node, O + 'concat')
                    ET.SubElement(expression, O + 'literal_component').text = 'Site'
                else:
                    node[:] = []
                    ET.SubElement(node, O + 'object_component', object_ref=PREFIX + 'obj:1', item_field='identifier_type')
                with self.assertRaises(ValueError):
                    assessment_for(self.visitor(root), PREFIX + 'tst:301')

    def test_comparator_and_cycle_guards_remain_closed(self):
        for mutation in ('regex', 'cycle'):
            root = self.original(CASES[1])
            if mutation == 'regex':
                root.find(O + 'objects').find("*[@id='" + PREFIX + "obj:301']").find(W + 'identifier_type').set('operation', 'pattern match')
            else:
                node = root.find(O + 'variables').find("*[@id='" + PREFIX + "var:301']")
                node[:] = []
                ET.SubElement(node, O + 'variable_component', var_ref=PREFIX + 'var:301')
            with self.assertRaises(ValueError):
                assessment_for(self.visitor(root), PREFIX + 'tst:301')

    def test_changed_enum_value_or_quantifier_fails_independent_comparison(self):
        root = self.original(CASES[1])
        assessment = self.proved(root, PREFIX + 'tst:301')
        original = ExpandedSource(root).test(PREFIX + 'tst:301')
        for mutation in ('value', 'quantifier'):
            changed = deepcopy(assessment)
            selector = changed['tests'][changed['evaluate']['test']]['object']['identifier_type']
            if mutation == 'quantifier':
                selector['value_match'] = 'none'
            else:
                changed['variables'][selector['equals']['variable']]['expression']['literal']['value'] = 'Apppool'
            self.assertNotEqual(original, ExpandedNative(changed).test(changed['evaluate']['test']))
if __name__ == '__main__':
    unittest.main()
