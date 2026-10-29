"""Explicit OVAL default equality on nil UNIX filenames preserves directories (#251)."""
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import digest, xml_identity
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-nil-filename-defaults'
CASES = json.loads((FIXTURE / 'provenance.json').read_text())['cases']
U = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#unix}'
NIL = '{http://www.w3.org/2001/XMLSchema-instance}nil'


class NilFilenameDefaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        cls.source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')

    def original(self, case=CASES[0]):
        raw = (FIXTURE / case['fixture']).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), case['fixture_sha256'])
        root = ET.fromstring(raw)
        nodes = {n.get('id'): n for n in root.iter() if n.get('id')}
        self.assertEqual(set(nodes), {r['id'] for r in case['dependencies']})
        for r in case['dependencies']:
            self.assertEqual(digest(xml_identity(nodes[r['id']])), r['sha256'])
        return root

    def visitor(self, root):
        return AssessmentConverter(OvalDocument(root, 'original.xml'), 'original.xml', load_mappings())

    def entity(self, root):
        return next(n for n in root.iter(U + 'filename') if NIL in n.attrib)

    def proved(self, root, case=CASES[0]):
        before = ET.tostring(root)
        r = check_conversion(self.visitor(root), case['test'], self.validator)
        self.assertTrue(r['schema_valid'], r)
        self.assertTrue(r['compiled_operands_verified'], r)
        self.assertEqual(r['source_proof'], 'PROVED', r)
        self.assertEqual(ET.tostring(root), before)
        return assessment_for(self.visitor(root), case['test'])

    def test_original_sparc_and_x86_closures_validate_and_prove(self):
        for case in CASES:
            with self.subTest(case=case['fixture']):
                root = self.original(case)
                result = self.source_validator.validate(etree.fromstring(ET.tostring(root)))
                inventory = SourceInventory(OvalDocument(root, 'original.xml'))
                validity = closure_validity(list(inventory.nodes.values()), {'original.xml': result})
                self.assertEqual(validity['status'], 'VALID', validity)
                self.assertFalse(any(r['kind'] == 'deprecated' for r in validity['issues']))
                self.proved(root, case)

    def test_omitted_and_explicit_default_equality_produce_identical_authoring(self):
        for case in CASES:
            root = self.original(case)
            baseline = self.proved(root, case)
            self.entity(root).attrib.pop('operation')
            self.assertEqual(self.proved(root, case), baseline)
            self.entity(root).set('operation', 'equals')
            self.entity(root).set('datatype', 'string')
            self.assertEqual(self.proved(root, case), baseline)

    def test_nondefault_comparators_and_malformed_nil_fail_closed(self):
        for change in ('pattern match', 'not equal', 'case insensitive equals',
                       'false', 'integer', 'text', 'child', 'var_ref'):
            root = self.original(); entity = self.entity(root)
            if change in ('pattern match', 'not equal', 'case insensitive equals'):
                entity.set('operation', change)
            elif change == 'false': entity.set(NIL, 'false')
            elif change == 'integer': entity.set('datatype', 'int')
            elif change == 'text': entity.text = 'directory'
            elif change == 'child': ET.SubElement(entity, U + 'unexpected')
            else: entity.set('var_ref', 'oval:org.scapng.nil:var:1')
            with self.subTest(change=change), self.assertRaises(ValueError):
                assessment_for(self.visitor(root), CASES[0]['test'])
            reader = ExpandedSource(root)
            object_id = next(n.get('id') for n in root.iter(U + 'file_object') if entity in list(n))
            with self.subTest(reader=change), self.assertRaises(ValueError):
                reader.object(object_id)

    def test_explicit_nil_comparator_remains_rejected_for_other_capabilities(self):
        root = self.original()
        entity = self.entity(root)
        mapping = next(m for m in load_mappings() if m['capability'] == 'windows.registry')
        with self.assertRaises(ValueError):
            self.visitor(root).predicate(entity, mapping, selector=True)

    def test_replacing_nil_with_file_selection_cannot_retain_independent_proof(self):
        root = self.original(); a = self.proved(root)
        def mutate(node):
            if isinstance(node, dict):
                if node.get('name', 'missing') is None:
                    node['name'] = {'matches_regex': '.*'}
                    return True
                return any(mutate(v) for v in node.values())
            if isinstance(node, list): return any(mutate(v) for v in node)
            return False
        self.assertTrue(mutate(a))
        try: result = expanded_compare(ExpandedSource(root), CASES[0]['definition'], a)
        except ValueError: return
        self.assertNotEqual(result['outcome'], 'PROVED', result)


if __name__ == '__main__':
    unittest.main()
