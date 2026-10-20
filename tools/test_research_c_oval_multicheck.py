#!/usr/bin/env python3
"""#245 Verify actual A/OVAL objectless multiple-Test integer comparison parity."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_oval_multicheck import convert_objectless_many, convert_selected_shared_many, convert_distinct_selected_many, alias_of
from research_c_original_oval_to_authored_c import NotNativeCConvertible
from test_research_c_original_oval_to_authored_c import original_plist


def source():
    doc=original_plist()
    doc["id"]="original.oval.linux.apparmorstatus.audit"
    oid=next(iter(doc["objects"]))
    base=doc["objects"][oid]
    doc["objects"][oid]={"capability":"linux.apparmorstatus",
                         "object_title":"Original singleton AppArmor status"}
    first=next(iter(doc["tests"]))
    old=doc["tests"][first]
    old["capability"]="linux.apparmorstatus"
    old["check"]="all"
    old["check_existence"]="at_least_one_exists"
    old["test_title"]="Ensure AppArmor has loaded profiles"
    second="test-ensure-enforce-mode"
    doc["tests"][second]={
        **deepcopy(old),"test_title":"Ensure AppArmor enforces profiles",
        "states":["state-enforce-count"]}
    doc["states"]={
        "state-load-count":{"capability":"linux.apparmorstatus",
                            "state_title":"Original loaded profiles",
                            "state":{"datatype":"integer",
                                     "entity_check":"all",
                                     "entity_existence":"at_least_one_exists",
                                     "field":"loaded_profiles_count",
                                     "operation":"greater than","value":0}},
        "state-enforce-count":{"capability":"linux.apparmorstatus",
                               "state_title":"Original enforcing profiles",
                               "state":{"datatype":"integer",
                                        "entity_check":"all",
                                        "entity_existence":"at_least_one_exists",
                                        "field":"enforce_mode_profiles_count",
                                        "operation":"greater than or equal","value":1}},
    }
    old["states"]=["state-load-count"]
    doc["evaluate"]={"all":[{"test":first},{"test":second}]}
    return doc


class OriginalCOVALMultiNumeric(unittest.TestCase):
    def test_two_original_ordered_integer_checks_one_singleton_observation(self):
        doc=source()
        before=deepcopy(doc)
        out=convert_objectless_many(doc)
        self.assertEqual(doc,before)
        self.assertEqual(out["stage"],"NATIVE_C_MULTICHECK_SOURCE_COMPATIBILITY_PROVED")
        self.assertEqual(len(out["authored_c"]["checks"]),2)
        self.assertEqual(set(out["source_test_crosswalk"].values()),set(doc["tests"]))
        self.assertEqual(out["authored_c"]["require"],{
            "every":[{"check":"ensure_apparmor_has_loaded_profiles"},
                     {"check":"ensure_apparmor_enforces_profiles"}]})
        checks=out["authored_c"]["checks"]
        self.assertEqual(
            checks["ensure_apparmor_has_loaded_profiles"]["must"],
            {"every_item":{"loaded_profiles_count":{"greater_than":0}}})
        self.assertEqual(
            checks["ensure_apparmor_enforces_profiles"]["must"],
            {"every_item":{"enforce_mode_profiles_count":{"greater_than_or_equal":1}}})
        self.assertTrue(out["C_uses_one_shared_observation"])
        self.assertFalse(out["OVAL_actual_scanner_parity_proven"])

    def test_ordering_operator_is_not_implicitly_string_order(self):
        doc=source()
        first=next(iter(doc["tests"]))
        doc["states"]["state-load-count"]["state"]["datatype"]="string"
        doc["states"]["state-load-count"]["state"]["value"]="0"
        with self.assertRaisesRegex(NotNativeCConvertible,"STATE_ORDERED_COMPARISON_NOT_INTEGER"):
            convert_objectless_many(doc)

    def test_original_field_names_prevent_truncated_opaque_aliases(self):
        self.assertEqual(alias_of(
            "Test if the passwordpolicy_test is supported. reversible_encryption",
            {"reversible_encryption":False}), "reversible_encryption")
        self.assertEqual(alias_of(
            "Test iosxe version test 'major_release' with operation greater than",
            {"major_release":{"greater_than":0}}), "major_release")
        self.assertEqual(alias_of(
            "Test current_mode",
            {"selinux_status":"enabled","current_mode":"enforcing"}),
            "test_current_mode")
        with self.assertRaisesRegex(NotNativeCConvertible,"UNSUITABLE"):
            alias_of("Test "+"very long source title "*20,{"other_field":True})

    def test_duplicate_source_test_in_require_fails_closed(self):
        doc=source()
        first=next(iter(doc["tests"]))
        doc["evaluate"]={"all":[{"test":first},{"test":first}]}
        with self.assertRaisesRegex(NotNativeCConvertible,"DUPLICATE_OR_MISSING"):
            convert_objectless_many(doc)

    def test_original_source_advanced_existence_not_assumed(self):
        doc=source()
        first=next(iter(doc["tests"]))
        doc["tests"][first]["check_existence"]="any_exist"
        with self.assertRaisesRegex(NotNativeCConvertible,"SOURCE_TEST_UNSUPPORTED_QUANTIFIER"):
            convert_objectless_many(doc)




def two_test_selected_source():
    doc=original_plist()
    tid=next(iter(doc["tests"]))
    old=doc["tests"][tid]
    old["test_title"]="Check DarkWake value_of is true"
    sid=old["states"][0]
    doc["states"][sid]["state_title"]="Expected enabled"
    other="test-darkwake-value-of-not-true"
    other_state="state-darkwake-not-true"
    doc["tests"][other]={**deepcopy(old),
        "test_title":"Check DarkWake value_of is not true",
        "states":[other_state]}
    doc["states"][other_state]={**deepcopy(doc["states"][sid]),
        "state_title":"Expected not enabled",
        "state":{**deepcopy(doc["states"][sid]["state"]),
                 "operation":"not equal"}}
    doc["evaluate"]={"all":[{"test":tid},{"test":other}]}
    return doc

class OriginalOVALSelectedSharedC(unittest.TestCase):
    def test_two_source_tests_share_original_selected_object_id(self):
        doc=two_test_selected_source()
        before=deepcopy(doc)
        result=convert_selected_shared_many(doc)
        self.assertEqual(doc,before)
        self.assertEqual(result["stage"],
                         "NATIVE_C_SHARED_SELECTED_MULTI_SOURCE_COMPATIBILITY_PROVED")
        c=result["authored_c"]
        self.assertEqual(len(c["observations"]),1)
        self.assertEqual(len(c["checks"]),2)
        self.assertEqual(len(c["require"]["every"]),2)
        self.assertEqual(set(result["source_test_crosswalk"].values()),set(doc["tests"]))
        self.assertEqual(set(result["source_test_documentation"]),set(c["checks"]))
        self.assertTrue(all(x["description"].startswith("Check") for x in
                            [{"description":x} for x in
                             result["source_test_documentation"].values()]))
        self.assertEqual({x["object"] for x in
                          result["native_c_compiled_tests"].values()},
                         set(doc["objects"]))
        self.assertTrue(result["A_source_semantic_projection_passed"])
        self.assertFalse(result["OVAL_actual_scanner_parity_proven"])

    def test_shared_selected_polymorphic_string_does_not_become_version(self):
        doc=two_test_selected_source()
        source_states=list(doc["states"].values())
        source_states[0]["state"].update({"datatype":"string","value":"1.0"})
        source_states[1]["state"].update({"datatype":"string","value":"1.0.0"})
        result=convert_selected_shared_many(doc)
        checks=result["native_c_compiled_tests"]
        self.assertEqual(len(checks),2)
        comparisons=[t["states"][0]["value_of"] for t in checks.values()]
        self.assertEqual({s["datatype"] for s in comparisons},{"string"})
        self.assertEqual({s["require"] for s in comparisons},
                         {"at_least_one_exists_and_all_match"})
        self.assertEqual({tuple((k,str(v)) for k,v in sorted(s.items()))
                          for s in comparisons}.__len__(),2)
        self.assertFalse(result["OVAL_actual_scanner_parity_proven"])

    def test_must_keep_original_set_filter_and_unsupported_scope(self):
        doc=two_test_selected_source()
        oid=next(iter(doc["objects"]))
        doc["objects"][oid]["filters"]=[{"action":"exclude","state":"a-state"}]
        with self.assertRaises(NotNativeCConvertible):
            convert_selected_shared_many(doc)
        doc=two_test_selected_source()
        tid=next(iter(doc["tests"]))
        doc["tests"][tid]["check_existence"]="any_exist"
        with self.assertRaisesRegex(NotNativeCConvertible,
                                    "DIFFERENT_SOURCE_SCOPE"):
            convert_selected_shared_many(doc)

    def test_missing_test_or_reused_state_never_vanishes(self):
        doc=two_test_selected_source()
        keys=list(doc["tests"])
        doc["evaluate"]={"all":[{"test":keys[0]},{"test":keys[0]}]}
        with self.assertRaisesRegex(NotNativeCConvertible,
                                    "CHECK_INVENTORY_CHANGED"):
            convert_selected_shared_many(doc)
        doc=two_test_selected_source()
        a,b=list(doc["tests"].values())
        b["states"]=a["states"]
        with self.assertRaisesRegex(NotNativeCConvertible,"STATE_REUSE"):
            convert_selected_shared_many(doc)



def two_test_distinct_source():
    doc=two_test_selected_source()
    oid=next(iter(doc["objects"]))
    other_obj="retrieve-second-power-management-plist-object"
    doc["objects"][other_obj]=deepcopy(doc["objects"][oid])
    doc["objects"][other_obj]["object_title"]="Second original power setting"
    doc["objects"][other_obj]["select"]["filepath"]["value"]=(
        "/Library/Preferences/com.apple.OtherSettings.plist")
    tid=next(tid for tid in doc["tests"] if tid!="test-test-plist511-filepath-entity")
    doc["tests"][tid]["object"]=other_obj
    return doc

class OriginalOVALDistinctSelectedMultiC(unittest.TestCase):
    def test_two_source_selected_objects_remain_independent_and_typed(self):
        doc=two_test_distinct_source()
        before=deepcopy(doc)
        out=convert_distinct_selected_many(doc)
        self.assertEqual(doc,before)
        self.assertEqual(out["stage"],
            "NATIVE_C_DISTINCT_MULTI_SOURCE_COMPATIBILITY_PROVED")
        self.assertEqual(len(out["authored_c"]["checks"]),2)
        self.assertEqual(len(out["authored_c"]["require"]["every"]),2)
        self.assertEqual(set(out["source_test_crosswalk"].values()),set(doc["tests"]))
        self.assertEqual(len(out["source_test_documentation"]),2)
        self.assertEqual({t["object"]["select"]["filepath"]["equals"]
            for t in out["native_c_compiled_tests"].values()},
            {"/Library/Preferences/com.apple.PowerManagement.plist",
             "/Library/Preferences/com.apple.OtherSettings.plist"})
        self.assertTrue(out["A_source_semantic_projection_passed"])
        self.assertFalse(out["OVAL_actual_scanner_parity_proven"])

    def test_source_long_descriptions_get_meaningful_nontruncated_aliases(self):
        source=two_test_distinct_source()
        tids=list(source["tests"])
        source["tests"][tids[0]]["test_title"]=(
            "Test that the plist511_object is supported with the filepath entity "
            "equal to some value.")
        source["tests"][tids[1]]["test_title"]=(
            "Test that the plist511_object is supported with the filepath entity "
            "not equal to some value.")
        result=convert_distinct_selected_many(source)
        checks=result["authored_c"]["checks"]
        self.assertEqual(set(checks),{"filepath_equals","filepath_not_equals"})
        self.assertEqual(set(result["source_test_crosswalk"].values()),set(tids))
        self.assertEqual(len(result["native_c_compiled_tests"]),2)
        self.assertFalse(result["OVAL_actual_scanner_parity_proven"])

    def test_source_title_alias_never_guesses_unknown_purpose(self):
        source=two_test_distinct_source()
        tids=list(source["tests"])
        source["tests"][tids[0]]["test_title"]=(
            "Test that the plist511_object does something unclear to the host "
            "and somehow ignores the comparison.")
        source["tests"][tids[1]]["test_title"]=(
            "Test that the plist511_object is supported with the filepath entity "
            "equal to some value.")
        with self.assertRaisesRegex(NotNativeCConvertible,
                                    "MULTI_DISTINCT_SOURCE_ALIAS_UNSAFE"):
            convert_distinct_selected_many(source)

    def test_shared_selected_object_requires_different_proven_scope(self):
        doc=two_test_distinct_source()
        first=next(iter(doc["tests"]))
        other=next(t for t in doc["tests"] if t!=first)
        doc["tests"][other]["object"]=doc["tests"][first]["object"]
        with self.assertRaisesRegex(NotNativeCConvertible,
                                    "OBJECT_MISSING_OR_SHARED"):
            convert_distinct_selected_many(doc)

    def test_set_filter_or_orphan_source_object_cannot_disappear(self):
        doc=two_test_distinct_source()
        oid=next(iter(doc["objects"]))
        doc["objects"][oid]["filters"]=[{"exclude":{"state":"unknown"}}]
        with self.assertRaisesRegex(NotNativeCConvertible,"SET_FILTER"):
            convert_distinct_selected_many(doc)
        doc=two_test_distinct_source()
        doc["objects"]["orphan"]={
            "capability":"macos.plist511","object_title":"Unreferenced data"}
        with self.assertRaisesRegex(NotNativeCConvertible,"EXTRA_SOURCE"):
            convert_distinct_selected_many(doc)

    def test_boolean_tree_or_missing_check_never_rewritten_as_and(self):
        doc=two_test_distinct_source()
        doc["evaluate"]={"any":deepcopy(doc["evaluate"]["all"])}
        with self.assertRaisesRegex(NotNativeCConvertible,"EXPLICIT_AND"):
            convert_distinct_selected_many(doc)
        doc=two_test_distinct_source()
        doc["evaluate"]["all"].pop()
        with self.assertRaisesRegex(NotNativeCConvertible,"TEST_COVERAGE_DRIFT"):
            convert_distinct_selected_many(doc)

if __name__=="__main__":
    unittest.main()
