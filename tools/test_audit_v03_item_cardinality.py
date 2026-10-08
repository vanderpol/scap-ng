"""Source-backed spot checks for the full 0.3 Item cardinality inventory."""
import unittest
from pathlib import Path
from audit_v03_item_cardinality import audit

ROOT=Path(__file__).resolve().parents[1]


class OVALItemCardinalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit(ROOT,ROOT/"schema/v0.3.0/capability-mappings/supported")
    def test_source_oval_schema_audit_has_no_loader_errors(self):
        self.assertEqual([],self.report["failures"])
    def test_registry_value_is_repeated_item_field(self):
        entries=[row for row in self.report["repeatable_fields"]
                 if row["capability"]=="windows.registry" and row["source_field"]=="value"]
        self.assertEqual(1,len(entries))
        self.assertEqual("unbounded",entries[0]["max_occurs"])
        self.assertEqual("value",entries[0]["native_state_field"])
    def test_every_repeated_entity_has_source_trace(self):
        for entry in self.report["repeatable_fields"]:
            self.assertTrue(entry["source_schema"])
            self.assertTrue(entry["source_item"])
            self.assertTrue(entry["source_field"])


if __name__=="__main__":
    unittest.main()
