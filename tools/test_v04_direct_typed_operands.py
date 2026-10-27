"""Explicit typed arrays/references retain original matching and all 39 rights Rules."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_direct_authoring_examples import walk
from v04_direct_converter import convert
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import SourceModel
from v04_native_bundle_compiler import build_bundle, verify_bundle
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]


class TypedOperandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pin = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
        cls.source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / pin['fixture'], pin['zip_sha256'])
        cls.rules = [r['source_rule'] for r in SourceInventory(cls.source).rules()
                     if 'windows.userright' in r['needed_capabilities']]
        cls.docs, cls.trace = convert(cls.source, cls.rules)

    def test_all_39_original_rights_rules_prove_validate_and_compile(self):
        self.assertEqual(len(self.rules), 39)
        self.assertEqual(len(verify_original(self.source.root, self.docs, self.trace)), 39)
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for document in self.docs.values():
            kind, = document
            self.assertFalse(list(document_errors(validators[kind + '.schema.json'], document)))
        raw, _ = build_bundle(self.docs)
        self.assertEqual(len(verify_compiled(self.docs, raw)), 39)
        verify_bundle(raw)  # Compiled schema, operands, graph and integrity.

    def test_arrays_and_predicate_references_have_explicit_types_and_independent_quantifiers(self):
        count = 0
        for document in self.docs.values():
            if 'assessment' not in document:
                continue
            for node in walk(document['assessment']):
                if 'value_match' not in node:
                    continue
                self.assertIn('datatype', node)
                self.assertIn(node['datatype'], ('string', 'integer', 'boolean'))
                if isinstance(node.get('equals'), list):
                    self.assertEqual(node['datatype'], 'string')
                count += 1
        self.assertEqual(count, 1)
        # A type annotation must not erase/change Variable matching or its
        # independent State population quantifier. The original reader rejects
        # this change even though it still satisfies the authoring schema.
        wrong = deepcopy(self.docs)
        changed = False
        for document in wrong.values():
            if 'assessment' not in document:
                continue
            for node in walk(document['assessment']):
                if 'value_match' in node:
                    node['value_match'] = 'none' if node['value_match'] != 'none' else 'every'
                    changed = True
                    break
            if changed:
                break
        self.assertTrue(changed)
        with self.assertRaises(AssertionError):
            verify_original(self.source.root, wrong, self.trace)


if __name__ == '__main__':
    unittest.main()
