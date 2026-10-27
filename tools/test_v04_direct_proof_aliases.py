"""Original Registry and WMI identity aliases retain predicates and dependencies."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from lxml import etree

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion, closure
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_inventory import SourceInventory
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-proof-aliases'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'


def dictionaries(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from dictionaries(child)
    elif isinstance(value, list):
        for child in value:
            yield from dictionaries(child)


class DirectProofAliasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.mappings = load_mappings()

    def originals(self):
        for item in self.pin['files']:
            raw = (FIXTURE / Path(item['path']).name).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), item['sha256'])
            yield item, ET.fromstring(raw)

    def test_original_identity_aliases_compile_and_prove(self):
        for item, root in self.originals():
            count = 0
            for test in root.find(O + 'tests'):
                visitor = AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings)
                result = check_conversion(visitor, test.get('id'), self.validator)
                if result['compiled']:
                    self.assertEqual(result['source_proof'], 'PROVED', result)
                    count += 1
            self.assertEqual(count, 14 if 'registry' in item['path'] else 5)

    def test_alias_proof_does_not_ignore_values_or_cardinality(self):
        for item, root in self.originals():
            for test in root.find(O + 'tests'):
                visitor = AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings)
                result = check_conversion(visitor, test.get('id'), self.validator)
                if result['source_proof'] != 'PROVED':
                    continue
                a = assessment_for(AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings), test.get('id'))
                ident = a['evaluate']['test']
                expected = ExpandedSource(root).test(test.get('id'))
                wrong = deepcopy(a)
                requirement = wrong['tests'][ident]['require']
                requirement['items_found'] = 'one_or_more' if requirement['items_found'] == 'none' else 'none'
                self.assertNotEqual(expected, ExpandedNative(wrong).test(ident))
                for predicate in dictionaries(a['tests'][ident]['require']):
                    if isinstance(predicate.get('equals'), str):
                        wrong = deepcopy(a)
                        target = next(p for p in dictionaries(wrong['tests'][ident]['require']) if isinstance(p.get('equals'), str))
                        target['equals'] = 'changed-operand'
                        self.assertNotEqual(expected, ExpandedNative(wrong).test(ident))
                        break

    def test_every_compiled_original_closure_is_valid_and_nondeprecated(self):
        validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        proved = 0
        for item, root in self.originals():
            raw = (FIXTURE / Path(item['path']).name).read_bytes()
            report = validator.validate(etree.fromstring(raw))
            nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, item['path'])).nodes.items()}
            for test in root.find(O + 'tests'):
                result = check_conversion(AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings), test.get('id'), self.validator)
                if not result['compiled']:
                    continue
                ids, problems = closure(nodes, test.get('id'))
                self.assertFalse(problems)
                validity = closure_validity([nodes[i] for i in ids], {item['path']: report})
                self.assertEqual(validity['status'], 'VALID', validity)
                self.assertFalse(any(i['kind'] == 'deprecated' for i in validity['issues']))
                proved += 1
        self.assertEqual(proved, 24)

    def test_hierarchy_depth_and_expansion_controls_are_not_discarded(self):
        changed = 0
        for item, root in self.originals():
            for test in root.find(O + 'tests'):
                visitor = AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings)
                result = check_conversion(visitor, test.get('id'), self.validator)
                if result['source_proof'] != 'PROVED':
                    continue
                a = assessment_for(AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings), test.get('id'))
                wrong = deepcopy(a)
                for node in dictionaries(wrong):
                    if 'traversal' in node:
                        depth = node['traversal']['max_depth']
                        node['traversal']['max_depth'] = 0 if depth != 0 else 1
                        ident = a['evaluate']['test']
                        self.assertNotEqual(ExpandedSource(root).test(test.get('id')), ExpandedNative(wrong).test(ident))
                        changed += 1
                        break
        self.assertEqual(changed, 6)
        for attribute, value in (('include_group', 'false'), ('resolve_group', 'true'),
                                 ('recurse_direction', 'up'), ('max_depth', 'nonnumeric')):
            root = ET.parse(FIXTURE / 'win-def_regkeyeffectiverights53_test.xml').getroot()
            test = root.find(O + 'tests')[0]
            obj = next(o for o in root.find(O + 'objects') if o.get('id') == test[0].get('object_ref'))
            ET.SubElement(obj, obj.tag.rsplit('}', 1)[0] + '}behaviors', {attribute: value})
            with self.subTest(attribute=attribute), self.assertRaises(ValueError):
                assessment_for(AssessmentConverter(OvalDocument(root, item['path']), item['path'], self.mappings), test.get('id'))


if __name__ == '__main__':
    unittest.main()
