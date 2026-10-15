#!/usr/bin/env python3
"""One-grammar generated-capability 0.4 draft checks; not scanner conformity.

The frozen 0.3 generator is never modified. Validate representative native
Linux/Windows capability field names, Object operators and Test/State semantics
using fully v0.4.0-local JSON Schema identifiers and explicit negative cases.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, RefResolver
from generate_capability_schema_v04 import generate

ROOT=Path(__file__).resolve().parents[1]
VERSION=ROOT/"schema"/"v0.4.0"
SCHEMAS={
    p.name:json.loads(p.read_text(encoding="utf-8"))
    for p in VERSION.glob("*.schema.json")
}
STORE={s["$id"]:s for s in SCHEMAS.values()}


def materialize(capability):
    mapping=json.loads(
        (VERSION/"capability-mappings"/"supported"/f"{capability}.json").read_text()
    )
    output=generate(mapping,ROOT)
    Draft202012Validator.check_schema(output)
    assert output["$id"].startswith("https://scap-ng.dev/schema/v0.4.0/")
    assert "/v0.3.0/" not in json.dumps(output)
    return output


def validate(schema,definition,value):
    resolver=RefResolver.from_schema(schema,store={**STORE,schema["$id"]:schema})
    v=Draft202012Validator(
        {"$ref":schema["$id"]+f"#/$defs/{definition}"},resolver=resolver
    )
    return list(v.iter_errors(value))


def test_object(capability,select,**extra):
    return {"capability":capability,"select":select,**extra}


class CapabilityV04Tests(unittest.TestCase):
    def test_capabilities_generate_natively(self):
        for cap in ("linux.partition","unix.file","windows.registry"):
            with self.subTest(cap=cap):
                generated=materialize(cap)
                self.assertIn("state_predicate",generated["$defs"])
                self.assertIn("object",generated["$defs"])
                self.assertNotIn("state",generated["$defs"])
                self.assertIn("require",generated["$defs"]["test"]["required"])
                self.assertNotIn("existence",generated["$defs"]["test"]["required"])
                self.assertNotIn("match",generated["$defs"]["test"]["properties"])
                self.assertEqual(generated["x-specification-version"],"0.4.0")

    def test_linux_partition_object_selector_known_field(self):
        schema=materialize("linux.partition")
        valid=test_object("linux.partition",{
            "mount_point":{"equals":"/home","datatype":"string"}
        })
        self.assertFalse(validate(schema,"object",valid))
        for selector in (
            {"mount_point":{"value":"/home","operation":"equals"}},
            {"made_up_field":{"equals":"/home"}},
            {"mount_point":{"equals":["/","/home"]}},
            {"mount_point":{"equals":"/home","require":"none_exist"}},
            {"mount_point":{"equals":{"input":"organization-mount-input"},
                            "datatype":"string","value_match":"all"}},
        ):
            with self.subTest(selector=selector):
                bad=test_object("linux.partition",selector)
                self.assertTrue(validate(schema,"object",bad))

    def test_linux_partition_state_field_names_and_cardinality(self):
        schema=materialize("linux.partition")
        valid={"mount_options":{
            "equals":"nosuid",
            "require":"at_least_one_exists_and_some_match",
            "datatype":"string",
        }}
        self.assertFalse(validate(schema,"state_predicate",valid))
        for candidate in (
            {"not_a_real_field":{
                "equals":"nosuid","require":"at_least_one_exists_and_some_match"}},
            {"mount_options":{"value":"nosuid","operation":"equals",
                              "existence":"one_or_more","match":"all"}},
            {"mount_options":{"equals":"nosuid"}},
        ):
            with self.subTest(candidate=candidate):
                self.assertTrue(validate(schema,"state_predicate",candidate))

    def test_registry_literal_value_field_keeps_its_name(self):
        schema=materialize("windows.registry")
        state={"value":{"equals":"4",
                        "require":"at_least_one_exists_and_all_match",
                        "datatype":"string"}}
        self.assertFalse(validate(schema,"state_predicate",state))
        self.assertTrue(validate(schema,"state_predicate",{
            "fabricated_field":state["value"]
        }))

    def test_generated_test_enforces_native_collection_and_requirement(self):
        schema=materialize("linux.partition")
        valid={
            "test_title":"home mounted with nosuid",
            "reported_elements":"all",
            "capability":"linux.partition",
            "object":test_object("linux.partition",{
                "mount_point":{"equals":"/home"}
            }),
            "states":[{"mount_options":{
                "equals":"nosuid","require":"at_least_one_exists_and_some_match"
            }}],
            "require":"at_least_one_exists_and_all_match",
        }
        self.assertFalse(validate(schema,"test",valid))
        missing=deepcopy(valid)
        del missing["require"]
        self.assertTrue(validate(schema,"test",missing))
        legacy=deepcopy(valid)
        legacy["existence"]="one_or_more"
        self.assertTrue(validate(schema,"test",legacy))
        legacy_object=deepcopy(valid)
        legacy_object["object"]["select"]["mount_point"]={
            "value":"/home","operation":"equals"
        }
        self.assertTrue(validate(schema,"test",legacy_object))


if __name__=="__main__":
    unittest.main()
