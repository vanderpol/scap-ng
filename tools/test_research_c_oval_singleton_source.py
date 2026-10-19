#!/usr/bin/env python3
"""#245 Validate objectless singleton original OVAL -> one C from/must grammar.

Tests stay faithful to the known Self-Assertion examples and deliberately
reject guessed collection semantics. Full original corpus is separately gated.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_original_oval_to_authored_c import (
    compile_one_original_definition,NotNativeCConvertible)
from test_research_c_original_oval_to_authored_c import original_plist

def singleton(capability, *, title, state=None, check="all", existence="at_least_one_exists"):
    source=original_plist()
    oid=next(iter(source["objects"]))
    tid=next(iter(source["tests"]))
    source["objects"]={oid:{"capability":capability,"object_title":title}}
    source["tests"][tid]["capability"]=capability
    source["tests"][tid]["check"]=check
    source["tests"][tid]["check_existence"]=existence
    if state is None:
        source["tests"][tid].pop("states")
        source["states"]={}
    else:
        sid=next(iter(source["states"]))
        source["states"][sid]={"capability":capability,
                              "state_title":"Original OVAL source State description",
                              "state":state}
    return source

def field(name,datatype,operation,value):
    return {"datatype":datatype,"entity_check":"all",
            "entity_existence":"at_least_one_exists",
            "field":name,"operation":operation,"value":value}

class OriginalOVALSingletonC(unittest.TestCase):
    def test_real_filevault_source_existence_without_fabricated_object(self):
        source=singleton("macos.filevault",title="The singleton filevault object.")
        previous=deepcopy(source)
        got=compile_one_original_definition(source)
        self.assertEqual(source,previous)
        self.assertEqual(got["authored_c"],{
            "from":{"macos.filevault":{}},"must":"present"})
        self.assertTrue(got["source_singleton_objectless_mapping_proved"])
        self.assertNotIn("object",got["native_c_compiled_test"])
        self.assertEqual(got["native_c_compiled_test"]["require"],"at_least_one_exists")
        self.assertFalse(got["OVAL_actual_scanner_parity_proven"])

    def test_original_apparmorstatus_integer_bound_is_not_string_comparison(self):
        source=singleton("linux.apparmorstatus",
                         title="The singleton apparmorstatus_object",
                         state=field("loaded_profiles_count","integer",
                                     "greater than or equal",0))
        got=compile_one_original_definition(source)
        self.assertEqual(got["authored_c"]["must"],{
            "every_item":{"loaded_profiles_count":{"greater_than_or_equal":0}}})
        self.assertEqual(got["native_c_compiled_test"]["states"],[
            {"loaded_profiles_count":{"require":"at_least_one_exists_and_all_match",
                                      "greater_than_or_equal":0}}])

    def test_original_softwareupdate_boolean_uses_actual_type(self):
        source=singleton("macos.softwareupdate",
                         title="Retrieve status scheduler and list available packages.",
                         state=field("schedule","boolean","equals",True))
        got=compile_one_original_definition(source)
        self.assertIs(got["authored_c"]["must"]["every_item"]["schedule"],True)
        self.assertEqual(got["native_c_compiled_test"]["capability"],"macos.softwareupdate")

    def test_singleton_with_multiple_approved_field_predicates_stays_all(self):
        source=singleton("macos.systemsetup",title="Retrieve system setup information.",
                         state={"all":[field("computersleep","integer",
                                             "greater than or equal",0),
                                       field("computername","string",
                                             "pattern match",r"\S+")]})
        got=compile_one_original_definition(source)
        self.assertEqual(got["native_c_compiled_test"]["states_match"],"all")
        self.assertEqual(len(got["native_c_compiled_test"]["states"]),2)

    def test_singleton_provider_not_a_blank_selector_for_regular_capability(self):
        source=singleton("macos.plist511",title="pretend uncollected singleton")
        with self.assertRaisesRegex(NotNativeCConvertible,"SINGLETON_SOURCE_NOT_PROVEN"):
            compile_one_original_definition(source)

    def test_arbitrary_observation_metadata_does_not_disappear(self):
        source=singleton("macos.filevault",title="Original singleton")
        oid=next(iter(source["objects"]))
        source["objects"][oid]["filters"]=[{"exclude":{"field":"status"}}]
        with self.assertRaisesRegex(NotNativeCConvertible,"OBJECT_ADVANCED"):
            compile_one_original_definition(source)

    def test_various_source_existence_must_not_be_reinterpreted(self):
        for mode in ["any_exist","only_one_exists","none_exist"]:
            with self.subTest(mode=mode):
                source=singleton("macos.filevault",title="source",state=field(
                    "status","string","equals","enabled"),existence=mode)
                with self.assertRaisesRegex(NotNativeCConvertible,"TEST_ADVANCED_EXISTENCE"):
                    compile_one_original_definition(source)

    def test_noninteger_version_compare_remains_unsupported(self):
        source=singleton("asa.version",title="source",state=field(
            "asa_major_release","version","greater than or equal","9.0"))
        with self.assertRaises(NotNativeCConvertible):
            compile_one_original_definition(source)

if __name__=="__main__":
    unittest.main()
