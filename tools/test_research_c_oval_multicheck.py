#!/usr/bin/env python3
"""#245 Verify actual A/OVAL objectless multiple-Test integer comparison parity."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_oval_multicheck import convert_objectless_many
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


if __name__=="__main__":
    unittest.main()
