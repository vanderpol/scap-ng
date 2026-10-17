#!/usr/bin/env python3
"""#235: JSON Schema autocomplete grounded in the actual capability mappings.

The pilot enforces top-level State field names for four real capabilities.
It does not yet validate all 100 mapped capabilities or arbitrary record
subfields/operators. No scanner parity is claimed.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"research/assessment-simplification/english-first-04/fixed-require.editor.schema.json"
MAPPINGS=ROOT/"schema/v0.4.0/capability-mappings/supported"
CAPS=("linux.partition","windows.registry","windows.userright","windows.wmi.query")

def check(capability,condition):
    return {"check":"Manual author test","inspect":capability,
            "require":{"items":"at_least_one_all_match",
                       "condition":condition},"report_elements":"all"}

class CapabilityCompletionResearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator=Draft202012Validator({
            "$schema":"https://json-schema.org/draft/2020-12/schema",
            "$defs":cls.schema["$defs"],
            "$ref":"#/$defs/check"
        })

    def valid(self,cap,condition):
        self.validator.validate(check(cap,condition))

    def invalid(self,cap,condition):
        with self.assertRaises(Exception):
            self.validator.validate(check(cap,condition))

    def test_field_autocomplete_matches_capability_mapping(self):
        for cap in CAPS:
            with self.subTest(capability=cap):
                mapping=json.loads((MAPPINGS/(cap+".json")).read_text())
                key="capStateNode__"+cap.replace(".","_")
                proposals=self.schema["$defs"][key]["oneOf"][2]["properties"]
                self.assertEqual(set(mapping["native"]["state_field_map"]),set(proposals))

    def test_linux_mount_options(self):
        self.valid("linux.partition",{"mount_options":{"at_least_one_value_is":"nosuid"}})
        self.invalid("linux.partition",{"mount_optoins":{"at_least_one_value_is":"nosuid"}})
        self.invalid("linux.partition",{"trustee_name":{"is":"Guests"}})

    def test_windows_right_names_and_scope(self):
        self.valid("windows.userright",{"trustee_name":{"equals_ignoring_case":"Guests"}})
        self.invalid("windows.userright",{"mount_options":{"is":"nosuid"}})
        self.valid("windows.userright",{"scope":"fields","and":[
            {"trustee_name":{"is":"Administrators"}},
            {"trustee_sid":{"matches_regex":"S-1-5-.+"}}
        ]})
        self.invalid("windows.userright",{"scope":"fields","and":[
            {"trustee_name":{"is":"Guests"}},
            {"mount_options":{"is":"nosuid"}}
        ]})

    def test_windows_registry_fields(self):
        self.valid("windows.registry",{"value":{"is":1}})
        self.invalid("windows.registry",{"registry_value":{"is":1}})

    def test_wmi_whole_states_have_explicit_scope(self):
        good={"scope":"states","or":[
            {"result":{"at_least_one_record_exists":True,
                        "every_record":{"domainrole":{"is":"1"}}}},
            {"result":{"at_least_one_record_exists":True,
                        "every_record":{"domainrole":{"is":"3"}}}}
        ]}
        self.valid("windows.wmi.query",good)
        bad=deepcopy(good)
        bad["or"][0]["hive"]=bad["or"][0].pop("result")
        self.invalid("windows.wmi.query",bad)
        missing_scope={"or":good["or"]}
        self.invalid("windows.wmi.query",missing_scope)

if __name__=="__main__":
    unittest.main()
