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
    return {"capability":capability,**select,**extra}


class CapabilityV04Tests(unittest.TestCase):
    def test_published_bluetooth_flat_object_inherits_capability_and_item_requirement(self):
        # The published 0.4 six-STIG Assessment uses canonical Test-scoped
        # capability and `{items: one_or_more}`. Every generated native
        # capability contract must accept this same approved authoring grammar.
        schema = materialize("independent.shellcommand")
        valid = {
            "test_title": "Report true if bluetooth installed",
            "capability": "independent.shellcommand",
            "object": {
                "shell": "powershell",
                "command": "(Get-PnpDevice -class bluetooth -status OK).class",
                "error_if_exit_status_not_0": False,
                "error_if_stderr_exists": False,
                "filters": [{"include": {"stdout_line": {
                    "case_insensitive_equals": "Bluetooth",
                    "require": "at_least_one_exists_and_all_match",
                }}}],
            },
            "reported_elements": "all",
            "require": {"items": "one_or_more"},
        }
        self.assertFalse(validate(schema, "test", valid))
        explicit = deepcopy(valid)
        explicit["object"]["capability"] = "independent.shellcommand"
        self.assertFalse(validate(schema, "test", explicit),
                         "An explicit matching Object capability is still legal")
        for name, edit in (
            ("wrong capability", lambda t: t["object"].update(capability="windows.registry")),
            ("mixed Set", lambda t: t["object"].update(set={"operator":"union","operands":[]})),
            ("bad items", lambda t: t.update(require={"items":"invented"})),
            ("legacy collect", lambda t: t["object"].update(collect={"shell":"powershell"})),
            ("empty filters", lambda t: t["object"]["filters"].clear()),
        ):
            with self.subTest(mutation=name):
                invalid = deepcopy(valid)
                edit(invalid)
                self.assertTrue(validate(schema, "test", invalid),
                                "A malformed direct-Filter source Test must fail closed")

    def test_generated_states_use_canonical_and_or_xor_with_legacy_aliases(self):
        # OVAL lockoutpolicy_state has four distinct fields whose conditions
        # are combined. The capability-specific schema must not reject the
        # canonical operators already allowed by the 0.4 language schema.
        schema = materialize("windows.lockoutpolicy")
        fields = [{name: {
            "greater_than_or_equal": -1 if name == "force_logoff" else 0,
            "datatype": "integer", "require": "at_least_one_exists_and_all_match",
        }} for name in ("force_logoff", "lockout_duration",
                        "lockout_observation_window", "lockout_threshold")]
        for operator in ("and", "or", "one", "xor", "all", "any", "odd"):
            with self.subTest(operator=operator):
                self.assertFalse(validate(schema, "state_expression",
                                          {operator: fields}))
        # This version requires an explicit operator for a group, rather
        # than silently defaulting the matching semantics of four fields.
        self.assertTrue(validate(schema, "state_expression", {
            name: leaf for field in fields for name, leaf in field.items()}))

    def test_generator_cli_reports_real_flat_object_field_counts(self):
        # After eliminating generic select/collect, CLI metadata must count
        # the direct native fields rather than an obsolete Object.select map.
        from contextlib import redirect_stdout
        from io import StringIO
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from generate_capability_schema_v04 import main
        cap = "windows.registry"
        mapping = VERSION / "capability-mappings" / "supported" / (cap + ".json")
        expected = json.loads(mapping.read_text(encoding="utf-8"))["native"]
        with TemporaryDirectory(prefix="v04-generator-cli-") as td:
            target = Path(td) / "windows.registry.schema.json"
            out = StringIO()
            with patch("sys.argv", ["generator", "--mapping", str(mapping),
                                    "--repo-root", str(ROOT), "--output", str(target)]):
                with redirect_stdout(out):
                    main()
            summary = json.loads(out.getvalue())
            generated = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(summary["object_selector_fields"],
                         len(expected["selector_map"]))
        self.assertEqual(summary["object_acquisition_parameters"],
                         len(expected.get("collection_parameters", {})))
        self.assertTrue(summary["direct_object_filters_supported"])
        self.assertIn("hive", generated["$defs"]["object"]["properties"])
        self.assertNotIn("collect", generated["$defs"]["object"]["properties"])

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

    def test_leaf_object_filters_do_not_require_synthetic_sets(self):
        schema = materialize("linux.partition")
        selector = {"mount_point": {"equals": "/home", "datatype": "string"}}
        include = {"include": {
            "mount_point": {"equals": "/home",
                            "require": "at_least_one_exists_and_all_match"}}}
        leaf = test_object("linux.partition", selector, filters=[include])
        self.assertFalse(validate(schema, "object", leaf),
                         "A filtered leaf Object must validate without a Set")

        for bad in (
            test_object("linux.partition", selector, filters=[]),
            test_object("linux.partition", selector,
                        filters=[{"not_an_action": include["include"]}]),
        ):
            with self.subTest(bad=bad):
                self.assertTrue(validate(schema, "object", bad))

        # OVAL applies every Set-level Filter to each referenced Object
        # BEFORE the set_operator; native filters belong on each operand.
        set_only = {"capability": "linux.partition", "set": {
            "operator": "union", "operands": [
                {"object": "partition-object", "filters": [include]}]}}
        self.assertFalse(validate(schema, "object", set_only))
        set_filtered = deepcopy(set_only)
        set_filtered["set"]["filters"] = [include]
        self.assertTrue(validate(schema, "object", set_filtered),
                        "No post-operation Set Filter exists in OVAL 5.12.3")
        combined = deepcopy(set_only)
        combined["filters"] = [include]
        self.assertTrue(validate(schema, "object", combined))

    def test_linux_partition_object_selector_known_field(self):
        schema=materialize("linux.partition")
        valid=test_object("linux.partition",{
            "mount_point":{"equals":"/home","datatype":"string"}
        })
        self.assertFalse(validate(schema,"object",valid))
        # The 0.4 canonical authoring grammar no longer recognizes generic
        # selector/collection wrappers, even if the underlying predicate works.
        self.assertTrue(validate(schema, "object", {
            "capability": "linux.partition",
            "select": {"mount_point": {"equals": "/home"}}}))

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
            "directory":{
                "equals":["/lib","/lib64"],
                "datatype":"string","value_match":"one"
            },
            "name":None,
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
        bad["set"]["operands"][0]["object"]["made_up"]={"equals":"x"}
        self.assertTrue(validate(schema,"object",bad))

    def test_variable_selector_nested_set_filter_and_missing_quantifier(self):
        # Schema-only proof that the 0.4 flat Object keeps Variable
        # cardinality separate from ordered Filter Item predicates and the
        # enclosing Set operation. This does not establish scanner parity.
        schema = materialize("linux.partition")
        selected = {"mount_point": {
            "equals": {"variable": "home-mount-variable"},
            "datatype": "string", "value_match": "one"}}
        filter_entry = {"include": {"mount_point": {
            "equals": "/home",
            "require": "at_least_one_exists_and_all_match"}}}
        leaf = test_object("linux.partition", selected)
        composed = {
            "capability": "linux.partition",
            "set": {"operator": "intersection", "operands": [
                {"object": leaf, "filters": [deepcopy(filter_entry)]},
                {"object": "other-mount-object", "filters": []},
            ]},
        }
        self.assertFalse(validate(schema, "object", leaf))
        self.assertFalse(validate(schema, "object", composed))
        malformed = deepcopy(composed)
        del malformed["set"]["operands"][0]["object"]["mount_point"]["value_match"]
        self.assertTrue(validate(schema, "object", malformed),
                        "Missing Variable match cardinality cannot inherit silently")
        direct_filtered = deepcopy(leaf)
        direct_filtered["filters"] = [filter_entry]
        self.assertFalse(validate(schema, "object", direct_filtered))
        bad_set_and_leaf = deepcopy(composed)
        bad_set_and_leaf["filters"] = [filter_entry]
        self.assertTrue(validate(schema, "object", bad_set_and_leaf),
                        "Filtering an entire Set must not be conflated with operand Filters")

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
        legacy_object["object"]["mount_point"]={
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
