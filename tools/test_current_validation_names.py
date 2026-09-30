"""Names may change without changing documentary or Schematron semantics."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "scap_ng_roundtrip_v003"))
from scap_upconvert_v003.cleanliness import assert_native_clean
from compare_schematron_baseline import normalize

class ValidationNames(unittest.TestCase):
    def test_collection_title_has_same_documentary_contract_as_object_title(self):
        title = "Values from source object oval:example:obj:1"
        assert_native_clean({"assessment": {"collections": {"data": {"collection_title": title}}}})

    def test_source_reference_in_executable_selector_is_still_rejected(self):
        with self.assertRaisesRegex(ValueError, "OVAL identifier"):
            assert_native_clean({"assessment": {"collections": {"data": {
                "collection_title": "Data",
                "selectors": {"path": "oval:example:obj:1"}}}}})

    def test_deprecated_element_namespace_prefix_is_lexical(self):
        base = {"kind": "successful-report", "test": "true()"}
        self.assertEqual(
            normalize({**base, "message": "DEPRECATED ELEMENT: kerberos_ticket_events ID:"}),
            normalize({**base, "message": "DEPRECATED ELEMENT: ns3:kerberos_ticket_events ID:"}))

    def test_distinct_element_findings_remain_distinct(self):
        base = {"kind": "successful-report", "test": "true()"}
        self.assertNotEqual(
            normalize({**base, "message": "DEPRECATED ELEMENT: notes ID:"}),
            normalize({**base, "message": "DEPRECATED ELEMENT: kerberos_ticket_events ID:"}))

if __name__ == "__main__":
    unittest.main()
