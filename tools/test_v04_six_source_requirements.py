"""Original source validity and non-repairing inventory regression boundaries."""
from copy import deepcopy
from pathlib import Path
import unittest

from lxml import etree as E

from inventory_v04_six_source_requirements import (candidate_closures, closure_validity,
    scope_mappings, summary)
from oval_source_validation import SourceValidator
from v04_direct_inventory import SourceInventory
from v04_direct_platform_inventory import platform_inventory
from v04_direct_scap_source import SourceModel, UnsupportedSource, XLINK

ROOT = Path(__file__).resolve().parents[1]
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
PIN = '2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0'


class SixSourceRequirementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = E.parse(str(ROOT / 'tests/fixtures/v04-current-source-proofs/ind-def_shellcommand_windows_test.xml')).getroot()
        cls.validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype/server2025-signed.zip', PIN)

    def test_original_xml_validates_against_unchanged_xsd_and_schematron(self):
        checked = self.validator.validate(self.original)
        self.assertEqual(checked['status'], 'VALID', checked)
        self.assertFalse(any(i['kind'] == 'invalid' for i in checked['issues']))
        self.assertIn('oval-definitions-schema.xsd', checked['schema_sha256'])

    def test_missing_required_acquisition_is_xsd_invalid_and_node_attributed(self):
        original = deepcopy(self.original)
        obj = original.find(O + 'objects')[0]
        obj.remove(obj[0])
        checked = self.validator.validate(original)
        self.assertEqual(checked['status'], 'INVALID')
        self.assertTrue(any(i['validator'] == 'XSD' and i['source_id'] == obj.get('id') for i in checked['issues']), checked)

    def test_none_exist_with_state_is_original_schematron_error(self):
        original = deepcopy(self.original)
        test = next(n for n in original.find(O + 'tests') if any(c.tag.endswith('}state') for c in n))
        test.set('check_existence', 'none_exist')
        checked = self.validator.validate(original)
        self.assertTrue(any(i['validator'] == 'Schematron' and i['source_id'] == test.get('id')
                            and i['kind'] == 'invalid' for i in checked['issues']), checked)

    def broken_source(self, tolerant):
        source = deepcopy(self.source)
        source.inventory_broken_references = tolerant
        rule = next(r for identifier, r in source.rules.items() if 'SV-278139' in identifier)
        component, _, _ = source.automated_check(rule)
        reference = next(r for r in source.references.values() if r.get(XLINK) == '#' + component)
        reference.set(XLINK, '#controlled-unresolved-component')
        source.index()
        return source

    def test_strict_converter_parser_still_rejects_broken_original_binding(self):
        with self.assertRaisesRegex(UnsupportedSource, 'unresolved/nonlocal component href'):
            self.broken_source(False)

    def test_inventory_records_candidate_graph_without_repairing_binding(self):
        source = self.broken_source(True)
        self.assertTrue(source.catalog_errors)
        inventory = SourceInventory(source)
        row = next(r for r in inventory.rules() if any(x['references'] for x in r['checks'])
                   and any(x['category'] == 'source-invalid' for x in r['inventory_problems']))
        candidates = candidate_closures(source, inventory, row['checks'])
        self.assertTrue(candidates)
        self.assertFalse(any(c['binding_resolved'] for c in candidates))
        self.assertTrue(all(c['dependencies'] for c in candidates))
        with self.assertRaisesRegex(UnsupportedSource, 'unresolved checklist catalog href'):
            source.automated_check(source.rules[row['source_rule']])

    def test_bad_unreachable_declaration_does_not_pollute_valid_closure(self):
        node = {'component': 'component', 'id': 'used'}
        checks = {'component': {'issues': [{'source_id': 'unused', 'kind': 'invalid', 'message': 'bad source'}]}}
        self.assertEqual(closure_validity([node], checks)['status'], 'VALID')
        checks['component']['issues'].append({'source_id': None, 'kind': 'invalid', 'message': 'bad header'})
        self.assertEqual(closure_validity([node], checks)['status'], 'INVALID')

    def test_only_owner_approved_source_families_are_implementation_candidates(self):
        mappings = scope_mappings()
        self.assertTrue(mappings)
        self.assertTrue(all(m['source']['namespace'].split('#')[-1] in
                            ('independent', 'linux', 'unix', 'windows') for m in mappings))
        self.assertIn('variable.value', {m['capability'] for m in mappings})

    def test_applicability_keeps_original_boolean_tree_and_scoped_oval_dependencies(self):
        inventory = SourceInventory(self.source)
        platforms = platform_inventory(self.source, inventory)
        local = [p for p in platforms.values() if p['source_kind'] == 'CPE language platform']
        self.assertTrue(local)
        self.assertTrue(any(p['dependencies'] for p in local))
        self.assertTrue(all(p['original_tree'] for p in local))
        self.assertTrue(any(p['source_kind'] == 'CPE dictionary name' for p in platforms.values()))

    def test_missing_cpe_name_is_not_replaced_with_a_similar_item(self):
        source = deepcopy(self.source)
        platform = source.benchmark.find('{http://checklists.nist.gov/xccdf/1.2}platform')
        self.assertIsNotNone(platform)
        platform.set('idref', 'cpe:/o:controlled:missing')
        record = platform_inventory(source, SourceInventory(source))['cpe:/o:controlled:missing']
        self.assertTrue(record['problems'])
        self.assertFalse(record['dependencies'])


if __name__ == '__main__':
    unittest.main()
