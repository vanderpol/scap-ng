#!/usr/bin/env python3
"""Refs #245: an actual Self-Assertion-style C compiler, not a source-only view."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_original_oval_to_authored_c import (
    compile_one_original_definition, batch_convert_review_folder,
    NotNativeCConvertible,
)

def original_plist():
    # Source-verified fixture: OVAL original macos/macos-def_plist511_test.xml
    # and 0.3 v003 semantic-equal native review. Full pinned source CI checks
    # these exact values independently, not just the fixture below.
    obj="retrieve-value-darkwakebackgroundtasks-object"
    ste="state-confirm-the-value-is-true"
    tst="test-test-plist511-filepath-entity"
    return {"id":"roundtrip.oval-navy-navwar-niwcatlantic-scc-test-def-1",
      "mode":"automated","evaluate":{"test":tst},
      "objects":{obj:{"capability":"macos.plist511",
                      "object_title":"Read DarkWakeBackgroundTasks",
                      "select":{
                          "filepath":{"datatype":"string","operation":"equals",
                              "value":"/Library/Preferences/com.apple.PowerManagement.plist"},
                          "xpath":{"datatype":"string","operation":"equals",
                              "value":'boolean(plist/dict[key="AC Power"]/dict[key="DarkWakeBackgroundTasks"]/integer/text() = "0")'}}}},
      "states":{ste:{"capability":"macos.plist511","state_title":"Confirm true",
                     "state":{"datatype":"boolean","entity_check":"all",
                         "entity_existence":"at_least_one_exists","field":"value_of",
                         "operation":"equals","value":True}}},
      "tests":{tst:{"capability":"macos.plist511","check":"all",
          "check_existence":"at_least_one_exists","object":obj,"reported_elements":"all",
          "states":[ste],
          "test_title":"Test plist511_obj filepath selector"}}}

class OriginalOVALNativeCCompilationTests(unittest.TestCase):
    def test_real_macos_plist_case_lowers_into_one_existing_C_grammar(self):
        source=original_plist()
        copy=deepcopy(source)
        result=compile_one_original_definition(source)
        self.assertEqual(source,copy)
        self.assertEqual(result["stage"],"NATIVE_C_FROM_MUST_SOURCE_COMPATIBILITY_PROVED")
        authored=result["authored_c"]
        self.assertEqual(set(authored),{"from","must"})
        self.assertEqual(authored["from"]["macos.plist511"]["filepath"],
                         "/Library/Preferences/com.apple.PowerManagement.plist")
        self.assertEqual(authored["must"],{"every_item":{"value_of":True}})
        emitted=result["native_c_compiled_test"]
        self.assertEqual(emitted["require"],"at_least_one_exists_and_all_match")
        self.assertEqual(emitted["states"],[{"value_of":{
            "require":"at_least_one_exists_and_all_match","equals":True}}])
        self.assertTrue(result["A_source_semantic_projection_passed"])
        self.assertFalse(result["OVAL_actual_scanner_parity_proven"])

    def test_source_bool_not_equal_is_typed_native_not_equal_not_python_negation(self):
        source=original_plist()
        state=next(iter(source["states"].values()))["state"]
        state["operation"]="not equal"
        result=compile_one_original_definition(source)
        self.assertEqual(result["authored_c"]["must"],
            {"every_item":{"value_of":{"not_equal":True}}})
        self.assertEqual(result["native_c_compiled_test"]["states"],[
            {"value_of":{"require":"at_least_one_exists_and_all_match",
                         "not_equal":True}}])
        self.assertTrue(result["A_source_semantic_projection_passed"])

    def test_ambiguous_oval_string_equality_remains_string_not_version(self):
        source=original_plist()
        state=next(iter(source["states"].values()))["state"]
        state.update({"datatype":"string","value":"1.0"})
        result=compile_one_original_definition(source)
        self.assertEqual(result["authored_c"]["must"],{
            "every_item":{"value_of":{"equals":"1.0","datatype":"string"}}})
        self.assertEqual(result["native_c_compiled_test"]["states"],[
            {"value_of":{"require":"at_least_one_exists_and_all_match",
                         "equals":"1.0","datatype":"string"}}])
        self.assertFalse(result["OVAL_actual_scanner_parity_proven"])

    def test_original_version_and_string_have_distinct_compiled_meaning(self):
        source=original_plist()
        state=next(iter(source["states"].values()))["state"]
        state.update({"datatype":"string","value":"1.0"})
        string=compile_one_original_definition(source)
        state["datatype"]="version"
        version=compile_one_original_definition(source)
        self.assertEqual(version["authored_c"]["must"],{
            "every_item":{"value_of":{"equals":"1.0","datatype":"version"}}})
        self.assertEqual(version["native_c_compiled_test"]["states"][0][
            "value_of"]["datatype"],"version")
        self.assertNotEqual(string["native_c_compiled_test"]["states"],
                            version["native_c_compiled_test"]["states"])

    def test_original_typed_not_equal_retains_comparison_type(self):
        source=original_plist()
        state=next(iter(source["states"].values()))["state"]
        state.update({"datatype":"string","value":"1.0","operation":"not equal"})
        result=compile_one_original_definition(source)
        self.assertEqual(result["authored_c"]["must"],{
            "every_item":{"value_of":{"not_equal":"1.0","datatype":"string"}}})
        self.assertEqual(result["native_c_compiled_test"]["states"][0][
            "value_of"],{"require":"at_least_one_exists_and_all_match",
                         "not_equal":"1.0","datatype":"string"})

    def test_original_specialized_source_comparison_stays_fail_closed(self):
        source=original_plist()
        state=next(iter(source["states"].values()))["state"]
        state.update({"datatype":"version","value":"2.10",
                      "operation":"greater than"})
        with self.assertRaisesRegex(NotNativeCConvertible,
                                    "STATE_ORDERED_COMPARISON_NOT_INTEGER"):
            compile_one_original_definition(source)
        state.update({"datatype":"ipv4","value":"192.0.2.0/24",
                      "operation":"equals"})
        with self.assertRaisesRegex(NotNativeCConvertible,
                                    "STATE_FIELD_SPECIALIZED_COMPARISON"):
            compile_one_original_definition(source)

    def test_state_free_all_exist_is_exact_native_presence_token(self):
        source=original_plist()
        source["states"]={}
        test=next(iter(source["tests"].values()))
        test.pop("states")
        test["check_existence"]="all_exist"
        result=compile_one_original_definition(source)
        self.assertEqual(result["authored_c"]["must"],"all_items_exist")
        self.assertEqual(result["native_c_compiled_test"]["require"],"all_exist")
        self.assertNotIn("states",result["native_c_compiled_test"])

    def test_not_equal_selector_is_not_guessed_as_equal(self):
        source=original_plist()
        obj=next(iter(source["objects"].values()))
        obj["select"]["filepath"]["operation"]="not equal"
        with self.assertRaisesRegex(NotNativeCConvertible,
                                    "SELECTOR_OPERATOR_OR_TYPE_UNSUPPORTED"):
            compile_one_original_definition(source)

    def test_original_expectation_changed_from_bool_to_string_cannot_pass(self):
        source=original_plist()
        ste=next(iter(source["states"]))
        source["states"][ste]["state"]["value"]="True"
        with self.assertRaisesRegex(NotNativeCConvertible,
                                   "STATE_FIELD_SPECIALIZED_COMPARISON"):
            compile_one_original_definition(source)

    def test_advanced_oval_sets_and_filters_are_not_discarded(self):
        source=original_plist()
        oid=next(iter(source["objects"]))
        source["objects"][oid]["filters"]=[{"exclude":{"field":"mode"}}]
        with self.assertRaisesRegex(NotNativeCConvertible,
                                   "OBJECT_ADVANCED"):
            compile_one_original_definition(source)
        source=original_plist()
        source["variables"]={"unknown-source":{"kind":"local","datatype":"string",
                                              "expression":{"literal":"foo"}}}
        with self.assertRaisesRegex(NotNativeCConvertible,
                                   "VARIABLE_SOURCE_GRAPH"):
            compile_one_original_definition(source)

    def test_source_six_state_quantifier_scope_not_guessed(self):
        source=original_plist()
        tid=next(iter(source["tests"]))
        source["tests"][tid]["check_existence"]="any_exist"
        with self.assertRaisesRegex(NotNativeCConvertible,
                                   "TEST_ADVANCED_EXISTENCE"):
            compile_one_original_definition(source)
        source=original_plist()
        source["tests"][tid]["check"]="mystery"
        with self.assertRaisesRegex(NotNativeCConvertible,
                                   "TEST_UNKNOWN_MATCHING"):
            compile_one_original_definition(source)

    def test_source_state_existence_not_optimized_away(self):
        source=original_plist()
        name=next(iter(source["states"]))
        source["states"][name]["state"]["entity_existence"]="none_exist"
        with self.assertRaisesRegex(NotNativeCConvertible,
                                   "STATE_FIELD_CARDINALITY_COMPLEX"):
            compile_one_original_definition(source)

    def test_explicit_source_compatibility_manifest_and_yaml_content(self):
        with TemporaryDirectory() as tmp:
            input=Path(tmp)/"source";input.mkdir()
            doc={"status":"C_READ_ONLY_SOURCE_REVIEW_A_COMPATIBILITY_FALLBACK",
                 "source":{"file":"macos/macos-def_plist511_test.xml",
                           "definition_id":"oval:example:def:1"},
                 "C_read_only_view":{"C_source_independent_compilation_proven":False},
                 "A_source_compatibility_fallback":original_plist()}
            (input/"source.review.json").write_text(json.dumps(doc),encoding="utf-8")
            doc2=deepcopy(doc)
            doc2["source"]["file"]="unix/unix-def_set_test.xml"
            doc2["source"]["definition_id"]="oval:example:def:2"
            doc2["A_source_compatibility_fallback"]["variables"]={
                "complex":{"kind":"local"}}
            (input/"complex.review.json").write_text(json.dumps(doc2),encoding="utf-8")
            out=Path(tmp)/"converted"
            manifest=batch_convert_review_folder(input,out)
            self.assertEqual((manifest["native_C_Definitions"],
                              manifest["source_compatible_not_yet_native_C"]),(1,1))
            self.assertEqual(len(list(out.glob("*.c.research.yaml"))),1)
            import yaml
            with next(out.glob("*.c.research.yaml")).open() as fd:
                yaml_doc=yaml.safe_load(fd)
            self.assertEqual(yaml_doc["must"],{"every_item":{"value_of":True}})
            self.assertEqual(manifest["unsupported"][0]["reason"],
                             "VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY")
            self.assertFalse(manifest["native_C_converted"][0].get("scanner_executed",False))

if __name__=="__main__":
    unittest.main()
