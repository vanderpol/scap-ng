"""Approved identity migration does not change source contracts (#255/#268)."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from generate_capability_schema_v04 import generate
from v04_native_capability_names import RENAMES, archival_witness_identities, rename_native_identities
from v04_canonical_source_ir import _supported_capabilities, _validate_capability_identities
from v04_scalar_source_proof import CONTRACTS, contract
from v04_native_bundle_compiler import compile_test_instruction

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / 'schema/v0.4.0/capability-mappings/supported'
PRESERVED = ROOT / 'tests/fixtures/v04-owner-original-mappings-20261031'


class NativeCapabilityNames(unittest.TestCase):
    def test_all_eleven_names_changed_only_native_identity_source_qnames_exact(self):
        names = _supported_capabilities()
        self.assertEqual(len(names), 100)
        self.assertEqual(len(RENAMES), 11)
        self.assertFalse(set(RENAMES) & names)
        self.assertTrue(set(RENAMES.values()) <= names)
        self.assertEqual(len(set(RENAMES.values())), 11)
        for old, new in RENAMES.items():
            with self.subTest(capability=new):
                pinned = json.loads((PRESERVED / (old + '.json')).read_text())
                current = json.loads((MAPPINGS / (new + '.json')).read_text())
                self.assertEqual(current, rename_native_identities(pinned))
                self.assertEqual(current['source'], pinned['source'])
                # Every generated contract differs only by the approved name projection.
                self.assertEqual(generate(current, ROOT), rename_native_identities(generate(pinned, ROOT)))
                if new in CONTRACTS:
                    self.assertEqual(sha256((PRESERVED / (old + '.json')).read_bytes()).hexdigest(),
                                     contract(new)['mapping_sha256'])

    def test_solaris_ips_and_svr4_remain_distinct_source_collections(self):
        ips = json.loads((MAPPINGS / 'solaris.package.ips.json').read_text())
        svr4 = json.loads((MAPPINGS / 'solaris.package.json').read_text())
        self.assertEqual(ips['source']['test'], 'package511_test')
        self.assertEqual(svr4['source']['test'], 'package_test')
        self.assertIn('publisher', ips['native']['selector_map'])
        self.assertEqual(svr4['native']['selector_map'], {'pkginst': 'pkginst'})

    def test_old_native_names_are_not_current_compiler_aliases(self):
        for old in RENAMES:
            with self.subTest(capability=old), self.assertRaisesRegex(ValueError, 'unknown native 0.4 capability'):
                _validate_capability_identities({'unit': {'assessment': {
                    'mode': 'automated', 'tests': {'example-test': {'capability': old}}}}})
            with self.subTest(direct_compiler=old), self.assertRaisesRegex(ValueError, 'unknown native 0.4 capability'):
                compile_test_instruction('example-test', {'capability': old, 'reported_elements': 'all',
                                                          'require': {'items_found': 'one_or_more'}})

    def test_archival_decoder_never_rewrites_expected_text(self):
        old = 'independent.textfilecontent54'
        source = {'tests': {'example-test': {'capability': old,
            'object': {'pattern': {'equals': old}}, 'require': {'fields': {'text': {'equals': old}}}}}}
        result = archival_witness_identities(source)
        self.assertEqual(result['tests']['example-test']['capability'], RENAMES[old])
        self.assertEqual(result['tests']['example-test']['object']['pattern']['equals'], old)
        self.assertEqual(result['tests']['example-test']['require']['fields']['text']['equals'], old)
        self.assertEqual(source['tests']['example-test']['capability'], old)

    def test_identity_projection_cannot_reauthorize_semantic_mapping_changes(self):
        name = next(new for new in RENAMES.values() if new in CONTRACTS)
        contract.cache_clear()
        read = Path.read_text
        def changed(path, *args, **kwargs):
            text = read(path, *args, **kwargs)
            if path == MAPPINGS / (name + '.json'):
                data = json.loads(text)
                data['native']['selector_map']['unexpected_source'] = 'unexpected_native'
                return json.dumps(data)
            return text
        try:
            with patch.object(Path, 'read_text', changed), self.assertRaisesRegex(ValueError, 'beyond approved identity'):
                contract(name)
        finally:
            contract.cache_clear()


if __name__ == '__main__': unittest.main()
