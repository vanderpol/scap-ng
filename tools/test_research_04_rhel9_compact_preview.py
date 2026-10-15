#!/usr/bin/env python3
"""0.4 RHEL9 staged compact syntax: exact reversible, no hidden defaults."""
import unittest
from copy import deepcopy
from research_04_rhel9_compact_preview import (
    compact_assessment,canonical_assessment,
    state_shorten,state_expand,maybe_require,expand_require
)
from collections import Counter

class CompactPreview(unittest.TestCase):
    def fixture(self):
        return {"assessment":{
            "mode":"automated","tests":{
                "demo-test":{
                    "capability":"unix.file",
                    "object":{"capability":"unix.file","select":{
                        "directory":{"value":["/lib","/lib64"],"operation":"equals",
                                     "datatype":"string","value_match":"one"}}},
                    "states":[
                        {"field":"value","value":[0,1000],"operation":"equals",
                         "datatype":"integer","value_match":"one",
                         "existence":"one_or_more","match":"all"},
                        {"all":[
                           {"field":"owner_uid","value":0,"operation":"equals",
                            "existence":"one_or_more","match":"one_or_more"},
                           {"field":"owner_uid","value":1000,"operation":"not_equal",
                            "existence":"optional","match":"all"}]}],
                    "states_match":"all",
                    "reported_elements":"all",
                    "existence":"one_or_more","match":"all"}},
            "evaluate":{"test":"demo-test"}}}

    def test_both_stages_preserve_exact_03_document(self):
        before=self.fixture()
        for stage in (1,2):
            with self.subTest(stage=stage):
                compact,counts=compact_assessment(before,stage)
                self.assertEqual(canonical_assessment(compact),before)
                t=compact["assessment"]["tests"]["demo-test"]
                self.assertEqual(t["object"]["select"]["directory"]["value_match"],"one")
                self.assertEqual(t["states"][0]["value"]["value_match"],"one")
                self.assertEqual(t["states"][0]["value"]["require"],"at_least_one_all_match")
                self.assertEqual(t["states"][1]["all"][0]["owner_uid"]["require"],
                                 "at_least_one_some_match")
                self.assertEqual(t["states"][1]["all"][1]["owner_uid"]["existence"],"optional")
                self.assertIn("match",t["states"][1]["all"][1]["owner_uid"])
                # Array-valued comparisons remain fully explicit: unlike a
                # scalar, they require datatype and independent value_match.
                self.assertIn("operation",t["states"][0]["value"])
                self.assertEqual(t["states"][0]["value"]["datatype"],"integer")
                if stage==2:
                    # Only an eligible direct scalar may use equals:.
                    self.assertIn("equals",t["states"][1]["all"][0]["owner_uid"])
                else:
                    self.assertIn("operation",t["states"][1]["all"][0]["owner_uid"])
                self.assertEqual(before,self.fixture())

    def test_none_exist_only_state_free_exact(self):
        original={"assessment":{"mode":"automated","tests":{"absence":{
            "capability":"windows.registry","existence":"none","match":"all",
            "reported_elements":"all","object":{"capability":"windows.registry"}}},
            "evaluate":{"test":"absence"}}}
        short,c=compact_assessment(original,1)
        self.assertEqual(short["assessment"]["tests"]["absence"]["require"],"none_exist")
        self.assertEqual(canonical_assessment(short),original)
        with self.assertRaisesRegex(ValueError,"not enabled"):
            expand_require({"require":"none_exist"},scope="field")
        with self.assertRaisesRegex(ValueError,"requires a Test without States"):
            expand_require({"require":"none_exist"},scope="test",state_free=False)

    def test_explicit_field_none_exist_is_not_test_absence_or_no_state_matching(self):
        import research_04_rhel9_compact_preview as preview
        original={"assessment":{"mode":"automated","tests":{"field-absent":{
            "capability":"independent.textfilecontent54",
            "existence":"one_or_more","match":"all",
            "states":[{"field":"stdout_line",
                       "value":"forbidden output","operation":"equals",
                       "existence":"none","match":"all"}]}}}}
        old=preview.FIELD_ABSENCE_ENABLED
        try:
            preview.FIELD_ABSENCE_ENABLED=True
            short,stats=compact_assessment(original,2)
            test=short["assessment"]["tests"]["field-absent"]
            self.assertEqual(test["states"][0]["stdout_line"]["require"],"none_exist")
            self.assertEqual(test["require"],"at_least_one_all_match")
            self.assertEqual(stats["field_require:none_exist"],1)
            self.assertEqual(canonical_assessment(short),original)
            with self.assertRaisesRegex(ValueError,"requires a Test without States"):
                expand_require({"require":"none_exist"},scope="test",state_free=False)
            # Negative match is not missing entities; it is never rewritten.
            negative={"field":"stdout_line","value":"forbidden",
                      "operation":"equals","existence":"one_or_more","match":"none"}
            original["assessment"]["tests"]["field-absent"]["states"].append(negative)
            short,stats=compact_assessment(original,2)
            state=short["assessment"]["tests"]["field-absent"]["states"][1]["stdout_line"]
            self.assertEqual(state["match"],"none")
            self.assertNotIn("require",state)
            self.assertEqual(canonical_assessment(short),original)
        finally:
            preview.FIELD_ABSENCE_ENABLED=old

    def test_odd_none_pair_kept_explicit_for_exact_source(self):
        original={"assessment":{"mode":"automated","tests":{"absence":{
            "existence":"none","match":"one","reported_elements":"all"}}}}
        short,c=compact_assessment(original,1)
        self.assertEqual(short["assessment"]["tests"]["absence"]["existence"],"none")
        self.assertNotIn("require",short["assessment"]["tests"]["absence"])
        self.assertEqual(canonical_assessment(short),original)

    def test_conflict_and_unknown_require_rejected(self):
        for node in ({"require":"at_least_one_all_match","match":"all"},
                     {"require":"impossible"}):
            with self.subTest(node=node):
                with self.assertRaises(ValueError):
                    expand_require(node,scope="test",state_free=False)

    def test_nested_logical_with_field_all(self):
        src={"all":[{"field":"value","value":"x","operation":"equals",
                      "existence":"one_or_more","match":"all"},
                     {"field":"all","value":"y","operation":"equals",
                      "existence":"one_or_more","match":"all"}]}
        folded,_=compact_assessment({"assessment":{"mode":"automated",
                               "tests":{"x":{"states":[src]}}}},1)
        self.assertEqual(canonical_assessment(folded)["assessment"]["tests"]["x"]["states"],[src])

if __name__=="__main__":
    unittest.main()
