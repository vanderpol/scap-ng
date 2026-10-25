"""Inventory denominators do not become conversion proof by schema validity (#251)."""
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
import zipfile

from audit_v04_original_source_ledger import inventory

XML = b'''<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5">
<definitions><definition id="oval:sample:def:1" version="2"><criteria>
<criterion test_ref="oval:sample:tst:1"/><extend_definition definition_ref="oval:sample:def:2"/>
</criteria></definition><definition id="oval:sample:def:2" version="1"><criteria>
<criterion test_ref="oval:sample:tst:1"/></criteria></definition></definitions>
<tests><sample_test id="oval:sample:tst:1" version="3" check="all" check_existence="all_exist">
<object object_ref="oval:sample:obj:1"/></sample_test></tests></oval_definitions>'''


class OriginalLedgerTests(unittest.TestCase):
    def test_complete_original_inventory_keeps_unverified_and_reference_denominators(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'source.zip'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('source.xml', XML)
            before = path.read_bytes()
            report, _ = inventory(path, sha256(before).hexdigest())
            self.assertEqual(len(report['records']), 3)
            self.assertTrue(all(r['status'].startswith('unverified_') for r in report['records']))
            definition, _, test = report['records']
            self.assertEqual(definition['definition_refs'], ['oval:sample:def:2'])
            self.assertEqual(test['check_existence'], 'all_exist')
            self.assertEqual(test['object_refs'], ['oval:sample:obj:1'])
            self.assertEqual(path.read_bytes(), before)

    def test_source_pin_drift_rejected_before_any_coverage_claim(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'source.zip'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('source.xml', XML)
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                inventory(path, '0' * 64)


if __name__ == '__main__':
    unittest.main()
