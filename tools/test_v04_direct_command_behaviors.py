"""Original command collection-error controls stay distinct from matching."""
from copy import deepcopy
import itertools
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_inventory import SourceInventory
from v04_direct_converter import convert
from v04_expanded_source_proof import ExpandedSource, actual_items_evidence
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors
from v04_direct_authoring_examples import capability_examples, walk

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
I = '{' + OVAL + '#independent}'
CAP = 'independent.shellcommand'
FLAGS = ('error_if_exit_status_not_0', 'error_if_stderr_exists')


class DirectCommandBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / PINS['fixture'], PINS['zip_sha256'])
        cls.rules = [r['source_rule'] for r in SourceInventory(cls.source).rules() if any(
            n['kind'] == 'object' and cls.source.node(n['component'], n['id'], 'object').tag == I + 'shellcommand_object'
            and cls.source.node(n['component'], n['id'], 'object').find(I + 'behaviors') is not None
            for n in r['dependencies'])]
        cls.docs, cls.trace = convert(cls.source, cls.rules)

    def object(self, source):
        binding = self.trace['rules'][0]
        identifier = next(k for k, v in binding['dependencies'].items() if v['kind'] == 'object' and
                          source.node(binding['component'], k, 'object').find(I + 'behaviors') is not None)
        return binding, source.node(binding['component'], identifier, 'object')

    def test_all_ten_actual_closures_validate_compile_and_prove_error_flags(self):
        self.assertEqual(len(self.rules), 10)
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 10)
        self.assertEqual(len(verify_compiled(self.docs, build_bundle(self.docs)[0])), 10)
        validators = build_validators(ROOT / 'schema/v0.4.0')
        combinations = set()
        for doc in self.docs.values():
            if 'assessment' not in doc:
                continue
            self.assertFalse(list(document_errors(validators['assessment.schema.json'], doc)))
            self.assertTrue(any(t['object']['error_if_stderr_exists'] is True
                                for t in doc['assessment']['tests'].values()))
            for test in doc['assessment']['tests'].values():
                combinations.add(tuple(test['object'][f] for f in FLAGS))
                self.assertIsInstance(test['object']['error_if_stderr_exists'], bool)
                self.assertIs(test['object']['error_if_exit_status_not_0'], False)
                self.assertFalse(any(set(n) & set(FLAGS) for n in walk(test['require'])))
        # One real closure also includes a separate default-behavior command;
        # enabling the feature must not turn every command's flag on.
        self.assertEqual(combinations, {(False, True), (False, False)})
        samples = capability_examples(self.docs, CAP)
        self.assertIn('source-error-behavior', samples)
        self.assertEqual(len(samples), len({a['id'] for a in samples.values()}))

    def test_original_optional_defaults_and_flag_combinations_are_preserved(self):
        xs = '{http://www.w3.org/2001/XMLSchema}'
        root = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/independent-definitions-schema.xsd').getroot()
        kind = root.find(xs + 'complexType[@name="ShellCommandBehaviors"]')
        for flag in FLAGS:
            attr = kind.find(xs + 'attribute[@name="' + flag + '"]')
            self.assertEqual((attr.get('use'), attr.get('default')), ('optional', 'false'))
            self.assertIn("flag of 'error'", ''.join(attr.itertext()))
        for values in itertools.product(('0', '1'), repeat=2):
            source = deepcopy(self.source)
            binding, obj = self.object(source)
            behavior = obj.find(I + 'behaviors'); behavior.attrib.clear(); behavior.attrib.update(zip(FLAGS, values))
            command = obj.find(I + 'command').text
            docs, trace = convert(source, [binding['source_rule']])
            verify_original(source.root, docs, trace)
            verify_compiled(docs, build_bundle(docs)[0])
            native = next(t['object'] for d in docs.values() if 'assessment' in d for t in d['assessment']['tests'].values())
            self.assertEqual(tuple(native[f] for f in FLAGS), tuple(v == '1' for v in values))
            self.assertEqual(native['command'], command)

    def test_changed_or_missing_flags_cannot_replace_error_controls_with_matching(self):
        for mutation in ('disable', 'delete', 'matching'):
            docs = deepcopy(self.docs)
            test = next(t for d in docs.values() if 'assessment' in d for t in d['assessment']['tests'].values())
            if mutation == 'disable': test['object']['error_if_stderr_exists'] = False
            elif mutation == 'delete': del test['object']['error_if_stderr_exists']
            else:
                test['object']['error_if_stderr_exists'] = False
                test['require']['fields'] = {'stderr_line': {'equals': '', 'values_found': 'one_or_more', 'values_matching': 'every'}}
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                verify_original(self.source.root, docs, self.trace)
        for flag in ('error', 'incomplete', 'not_collected'):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                actual_items_evidence(flag, [], claims_complete_success=True)

    def test_invalid_duplicate_foreign_and_nonempty_behaviors_fail_closed(self):
        for mutation in ('boolean', 'unknown', 'duplicate', 'foreign', 'child'):
            source = deepcopy(self.source)
            binding, obj = self.object(source)
            behavior = obj.find(I + 'behaviors')
            if mutation == 'boolean': behavior.set('error_if_stderr_exists', 'yes')
            elif mutation == 'unknown': behavior.set('invented', 'true')
            elif mutation == 'duplicate': obj.insert(0, deepcopy(behavior))
            elif mutation == 'foreign': behavior.tag = '{urn:foreign}behaviors'
            else: ET.SubElement(behavior, I + 'invented')
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, [binding['source_rule']])
            with self.assertRaises(ValueError):
                ExpandedSource(source.components[binding['component']]).object(obj.get('id'))


if __name__ == '__main__':
    unittest.main()
