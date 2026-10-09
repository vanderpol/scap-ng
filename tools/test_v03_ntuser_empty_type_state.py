"""OVAL NTUSER State type may contain an explicit empty comparison value.

The empty lexical value is NOT a collected Registry Item type.
"""
import json
import unittest
from pathlib import Path
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.3.0/capability-mappings/supported/windows.ntuser.json"


def type_predicate_properties(value):
    if isinstance(value,dict):
        props=value.get("properties")
        if isinstance(props,dict) and props.get("field",{}).get("const")=="type":
            yield props
        for child in value.values():
            yield from type_predicate_properties(child)
    elif isinstance(value,list):
        for child in value:
            yield from type_predicate_properties(child)


class NTUserEmptyTypeStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT,schema_version="0.3.0")

    def test_empty_string_allowed_for_state_type_comparison(self):
        predicates=list(type_predicate_properties(self.schema["$defs"]["state"]))
        self.assertTrue(predicates)
        # Native 0.3 distinguishes an enum-backed literal comparison from
        # a regex pattern_match. The literal enum is in the else-branch of
        # the operation guard, not necessarily properties.value directly.
        def enum_members(node):
            if isinstance(node,dict):
                if isinstance(node.get("enum"),list):
                    yield from node["enum"]
                for value in node.values():
                    yield from enum_members(value)
            elif isinstance(node,list):
                for value in node:
                    yield from enum_members(value)
        self.assertIn("",list(enum_members(self.schema["$defs"]["state"])))

    def test_empty_sentinel_not_claimed_as_real_registry_type(self):
        from validate_generated_capability_semantics import REGISTRY_TYPE_VALUE_DATATYPES
        self.assertNotIn("",REGISTRY_TYPE_VALUE_DATATYPES)


if __name__=="__main__":
    unittest.main()
