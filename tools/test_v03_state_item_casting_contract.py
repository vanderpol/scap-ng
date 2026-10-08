"""Verify source-equivalent State comparisons and collected Item datatypes differ.

OVAL Entity State datatype governs comparison (cast observed data first).
System-characteristics Item datatype governs captured evidence representation.
"""
import json
import unittest
from pathlib import Path

from generate_capability_schema import generate

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "schema/v0.3.0/capability-mappings/supported/independent.shellcommand.json"


def find_fields(node, field):
    if isinstance(node, dict):
        props=node.get("properties")
        if isinstance(props, dict) and props.get("field", {}).get("const")==field:
            yield props
        for value in node.values():
            yield from find_fields(value,field)
    elif isinstance(node, list):
        for value in node:
            yield from find_fields(value,field)


class StateItemCastingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.generated=generate(cls.mapping,ROOT,schema_version="0.3.0")

    def test_state_stdout_line_allows_explicit_integer_comparison(self):
        nodes=list(find_fields(self.generated["$defs"]["state"],"stdout_line"))
        self.assertEqual(1,len(nodes),nodes)
        datatypes=nodes[0]["datatype"]["enum"]
        self.assertIn("integer",datatypes)
        self.assertIn("string",datatypes)

    def test_item_stdout_line_remains_string_only(self):
        item=self.generated["$defs"]["collected_item"]
        # Traverse schema to locate collected field datatype restrictions.
        text=json.dumps(item,sort_keys=True)
        self.assertIn('"stdout_line"',text)
        self.assertIn('"string"',text)
        self.assertNotIn('"integer"',text)

    def test_mapping_explicitly_separates_two_datatype_contracts(self):
        native=self.mapping["native"]
        self.assertEqual(["string"],native["field_datatypes"]["stdout_line"])
        self.assertIn("integer",native["state_field_datatypes"]["stdout_line"])
        self.assertNotEqual(native["field_datatypes"]["stdout_line"],native["state_field_datatypes"]["stdout_line"])


if __name__=="__main__":
    unittest.main()
