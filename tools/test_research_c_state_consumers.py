"""Refs #245: synthetic tests for cross-Rule source-State uses."""
import unittest
from research_c_state_consumers import inventory_state_consumers

STATE = "oval:demo:ste:42"

def sample():
    return [
        {"source_id":"one", "tests":{"test1":{"states":[STATE]}}, "objects":{}},
        {"source_id":"two", "tests":{"test2":{"states":[]}},
         "objects":{"filtered":{"set":{"filters":[{"state":STATE,"action":"exclude"}]}}}},
    ]

class ConsumerAuditTest(unittest.TestCase):
    def test_shared_filter_found(self):
        r=inventory_state_consumers(sample(),STATE,inventory_complete=True)
        self.assertEqual(len(r["known_consumers"]),2)
        self.assertEqual({c["kind"] for c in r["known_consumers"]},
                         {"test_state_reference","object_state_reference"})
        self.assertFalse(r["source_conversion_authorized"])
        self.assertFalse(r["global_source_consumers_independently_verified"])

    def test_incomplete_inventory_fails_closed(self):
        r=inventory_state_consumers(sample()[:1],STATE)
        self.assertFalse(r["inventory_claimed_complete"])
        self.assertFalse(r["source_conversion_authorized"])

    def test_unknown_test_shape_is_diagnostic(self):
        d=sample()
        d[0]["tests"]["test1"]["states"]={"dynamic":STATE}
        r=inventory_state_consumers(d,STATE)
        self.assertTrue(r["concerns"])

if __name__=="__main__":
    unittest.main()
