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

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
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
    # Reference scopes must remain local to each 0.4 schema document. A
    # native nested Set traverses traversal/collector schemas that themselves
    # reference other $defs; legacy RefResolver can bind those to the wrong
    # document, so use a proper Draft 2020-12 resource Registry.
    registry=Registry().with_resources(
        (uri,Resource.from_contents(doc))
        for uri,doc in {**STORE,schema["$id"]:schema}.items()
    )
    v=Draft202012Validator(
        {"$id":schema["$id"],"$defs":schema["$defs"],
         "$ref":f"#/$defs/{definition}"},registry=registry
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

    def test_no_object_native_capability_still_has_state_and_match_requirement(self):
        # windows.passwordpolicy has no Object source but *does* evaluate an
        # observed State. It is not a fixed-result/presence-only capability.
        schema=materialize("windows.passwordpolicy")
        self.assertNotIn("object",schema["$defs"])
        self.assertIn("state_predicate",schema["$defs"])
        mapping=json.loads(
            (VERSION/"capability-mappings"/"supported"/"windows.passwordpolicy.json")
            .read_text(encoding="utf-8")
        )
        field_name=next(iter(mapping["native"]["state_field_map"].values()))
        valid={
            "test_title":"policy State check",
            "reported_elements":"all",
            "capability":"windows.passwordpolicy",
            "states":[{field_name:{
                "equals":14,"require":"at_least_one_exists_and_all_match"
            }}],
            "require":"at_least_one_exists_and_all_match",
        }
        self.assertFalse(validate(schema,"test",valid))
        bad=deepcopy(valid)
        bad["require"]="only_one_exists"
        self.assertTrue(validate(schema,"test",bad))

    def test_nested_set_uses_native_selector_names_not_open_generic_object(self):
        schema=materialize("unix.file")
        nested={
            "capability":"unix.file",
            "object_title":"Directories",
            "select":{
                "directory":{
                    "equals":["/lib","/lib64"],
                    "datatype":"string","value_match":"one"
                },
                "name":None,
            },
            "filesystem":"all",
            "traversal":{"max_depth":None,"recurse":"symlinks_and_directories"},
        }
        top={
            "capability":"unix.file",
            "set":{"operator":"union","operands":[
                {"object":nested,"filters":[]}
            ]},
        }
        self.assertFalse(validate(schema,"object",top))
        bad=deepcopy(top)
        bad["set"]["operands"][0]["object"]["select"]["made_up"]={"equals":"x"}
        self.assertTrue(validate(schema,"object",bad))

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


    def test_reviewed_enum_object_selectors_do_not_accept_arbitrary_values(self):
        schema=materialize("windows.userright")
        def selected(value):
            return test_object("windows.userright",{"userright":value})
        self.assertFalse(validate(schema,"object",selected(
            {"equals":"SE_NETWORK_LOGON_NAME"}
        )))
        self.assertFalse(validate(schema,"object",selected({
            "equals":["SE_NETWORK_LOGON_NAME","SE_DENY_NETWORK_LOGON_NAME"],
            "datatype":"string","value_match":"one",
        })))
        self.assertFalse(validate(schema,"object",selected({
            "equals":{"variable":"enumerated-rights-variable"},
            "datatype":"string","value_match":"one",
        })))
        for bad in (
            {"equals":"FICTIONAL_RIGHT"},
            {"equals":["SE_NETWORK_LOGON_NAME","FICTIONAL_RIGHT"],
             "datatype":"string","value_match":"one"},
            {"matches_regex":"SE_.*"},
            {"not_equal":"SE_NETWORK_LOGON_NAME"},
            {"variable":"enumerated-rights-variable"},
            {"equals":{"variable":"enumerated-rights-variable"},
             "datatype":"string"},
        ):
            with self.subTest(bad=bad):
                self.assertTrue(validate(schema,"object",selected(bad)))

if __name__=="__main__":
    unittest.main()
