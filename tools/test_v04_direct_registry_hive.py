"""Original closed-domain Registry selector proof; no scanner evaluation."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_converter import convert, load_mappings
from v04_direct_inventory import SourceInventory
from v04_expanded_source_proof import original_registry_hive_contract
from v04_object_contract import object_sites
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
O = '{' + OVAL + '}'
W = '{' + OVAL + '#windows}'


class RegistryHiveDirectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        inventory = SourceInventory(cls.source)
        cls.rules = []
        for rule in cls.source.rules.values():
            try:
                component, definition, _ = cls.source.automated_check(rule)
            except UnsupportedSource:
                continue
            closure, problems = inventory.closure(component, definition)
            assert not problems
            objects = [cls.source.node(component, n['id'], 'object') for n in closure if n['kind'] == 'object']
            if any(n.tag == W + 'registry_object' and n.find(W + 'hive') is not None
                   and n.find(W + 'hive').get('operation') == 'case insensitive equals' for n in objects):
                cls.rules.append(rule.get('id'))
        cls.documents, cls.trace = convert(cls.source, cls.rules)

    def test_original_object_item_domains_and_native_crosswalk_prove_all_49_relations(self):
        proof = original_registry_hive_contract()
        self.assertEqual(proof['literal_pairs_proved'], 49)
        a, b = proof['domains'].values()
        self.assertEqual(a, b)
        mapping = next(m for m in load_mappings() if m['capability'] == 'windows.registry')
        aliases = mapping['migration_crosswalk'][mapping['native']['selector_value_crosswalk']['hive']]
        enum = mapping['native']['selector_value_enums']['hive']
        self.assertEqual(set(a) - {''}, set(aliases) - {''})
        self.assertEqual({aliases[v] for v in a if v}, set(enum))
        self.assertNotIn(aliases[''], enum)  # Original Variable/error marker has no native hive value.
        for expected in a:
            for observed in b:
                self.assertEqual(expected == observed, expected.casefold() == observed.casefold())

    def test_every_new_original_rule_preserves_operands_source_tokens_and_dependency_proof(self):
        self.assertEqual(len(self.rules), 19)
        proofs = verify_original(self.source.root, self.documents, self.trace)
        self.assertEqual(len(proofs), 19)
        self.assertEqual(len(verify_compiled(self.documents, build_bundle(self.documents)[0])), 19)
        for binding, proof in zip(self.trace['rules'], proofs):
            self.assertEqual(proof['outcome'], 'PROVED')
            self.assertTrue(proof['selector_equivalences'])
            self.assertTrue(binding['selector_equivalences'])
            for equivalent in binding['selector_equivalences']:
                self.assertEqual(equivalent['source_selector']['attributes']['operation'], 'case insensitive equals')
                self.assertEqual(equivalent['native_comparator'], 'equals')
                self.assertIn(equivalent['source_object'], binding['dependencies'])

    def test_all_six_literal_hives_in_controlled_original_copies_prove_and_compile(self):
        # Controlled primitive coverage is separate from the 19 unmodified Rules.
        for hive in original_registry_hive_contract()['domains']['EntityObjectRegistryHiveType']:
            if not hive:
                continue
            source = deepcopy(self.source)
            component, definition, _ = source.automated_check(source.rules[PINS['rules'][1]])
            closure, _ = SourceInventory(source).closure(component, definition)
            node = next(source.node(component, n['id'], 'object') for n in closure if n['kind'] == 'object')
            node.find(W + 'hive').set('operation', 'case insensitive equals')
            node.find(W + 'hive').text = hive
            source.index()
            with self.subTest(hive=hive):
                docs, trace = convert(source, [PINS['rules'][1]])
                self.assertEqual(verify_original(source.root, docs, trace)[0]['outcome'], 'PROVED')
                self.assertEqual(len(verify_compiled(docs, build_bundle(docs)[0])), 1)

    def test_equal_relation_sources_keep_identical_collection_and_evaluation_contracts(self):
        source = deepcopy(self.source)
        for binding in self.trace['rules']:
            for row in binding['selector_equivalences']:
                source.node(binding['component'], row['source_object'], 'object').find(W + 'hive').set('operation', 'equals')
        source.index()
        docs, trace = convert(source, self.rules)
        # Every native selector, Variable, Item/field cardinality, reporting
        # choice and Boolean boundary is identical; no Item/status fabrication.
        self.assertEqual(docs, self.documents)
        self.assertTrue(all('selector_equivalences' not in b for b in trace['rules']))
        verify_original(source.root, docs, trace)

    def test_invalid_hives_dynamic_operands_states_and_unrelated_comparators_stay_strict(self):
        binding = self.trace['rules'][0]
        oid = binding['selector_equivalences'][0]['source_object']
        for mutation in ('empty', 'unknown', 'lowercase', 'pattern', 'dynamic', 'datatype', 'state'):
            source = deepcopy(self.source)
            hive = source.node(binding['component'], oid, 'object').find(W + 'hive')
            if mutation in ('empty', 'unknown', 'lowercase'):
                hive.text = {'empty': '', 'unknown': 'HKEY_FAKE', 'lowercase': 'hkey_local_machine'}[mutation]
            elif mutation == 'pattern':
                hive.set('operation', 'pattern match')
            elif mutation == 'dynamic':
                variable = ET.SubElement(source.components[binding['component']].find(O + 'variables'),
                    O + 'constant_variable', id='oval:org.scapng.hive:var:1', version='1', datatype='string')
                ET.SubElement(variable, O + 'value').text = 'HKEY_LOCAL_MACHINE'
                hive.set('var_ref', variable.get('id')); hive.text = None
            elif mutation == 'datatype':
                hive.set('datatype', 'int'); hive.text = '0'
            else:
                state_id = next(k for k, v in binding['dependencies'].items() if v['kind'] == 'state')
                ET.SubElement(source.node(binding['component'], state_id, 'state'), W + 'hive',
                              operation='case insensitive equals').text = 'HKEY_LOCAL_MACHINE'
            source.index()
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])
        source = deepcopy(self.source)
        source.node(binding['component'], oid, 'object').find(W + 'key').set('operation', 'case insensitive equals')
        source.index()
        docs, trace = convert(source, [binding['source_rule']])
        verify_original(source.root, docs, trace)
        assessment = next(d['assessment'] for d in docs.values() if 'assessment' in d)
        obj = next(s.node for s in object_sites(assessment) if 'key' in s.node)
        self.assertIn('case_insensitive_equals', obj['key'])
        obj['key'] = {'equals': obj['key']['case_insensitive_equals']}
        with self.assertRaises(AssertionError):
            verify_original(source.root, docs, trace)
        docs = deepcopy(self.documents)
        assessment = next(d['assessment'] for d in docs.values() if 'assessment' in d)
        next(s.node for s in object_sites(assessment) if 'hive' in s.node)['hive'] = {'equals': 'users'}
        with self.assertRaises(AssertionError):
            verify_original(self.source.root, docs, self.trace)


if __name__ == '__main__':
    unittest.main()
