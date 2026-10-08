"""0.3 registry type literal crosswalk after static Variable folding.

The Google Chrome source corpus exposes reg_dword/reg_sz in Test-local
States only after constant-variable folding. These are source OVAL
lexical values, not native registry type enums. This test checks the
published mapping rather than allowing a permissive semantic validator.
"""
import copy
import unittest

from normalize_0_3_review_surface import normalize_scalar_tree
from validate_generated_capability_semantics import validate_assessment_capability_semantics


def state_predicate(kind,value,operation="equals"):
    return {"field":"type","value":value,"operation":operation,
            "datatype":"string","match":"all","existence":"one_or_more"}


def doc(capability,kind):
    return {"assessment":{"id":"chrome.type-test","tests":{
        "registry-value-test":{
            "capability":capability,
            "states":[{"capability":capability,"state":{"all":[
                state_predicate("type",kind),
                {"field":"value","value":"0","operation":"equals",
                 "datatype":"string","match":"all","existence":"one_or_more"},
            ]}}],
        }
    }}}


class ChromeNativeRegistryTypeTest(unittest.TestCase):
    def transformed(self,original):
        changes=[]
        output=normalize_scalar_tree(copy.deepcopy(original),(),changes)
        return output,changes

    def test_real_google_chrome_reg_dword_and_reg_sz_are_canonical(self):
        for source,native in (("reg_dword","dword"),("reg_sz","string")):
            with self.subTest(source=source):
                converted,changes=self.transformed(doc("windows.registry",source))
                predicate=(converted["assessment"]["tests"]["registry-value-test"]
                            ["states"][0]["state"]["all"][0])
                self.assertEqual(predicate["value"],native)
                self.assertTrue(any(x.get("reason")==
                    "registry type source-to-native vocabulary crosswalk"
                    for x in changes))
                findings=validate_assessment_capability_semantics(converted)
                self.assertNotIn("windows.registry.unsupported_type_value_encoding",
                                 {row["code"] for row in findings})
                rerendered,_=self.transformed(converted)
                self.assertEqual(converted,rerendered)

    def test_unverified_registry_type_remains_explicit_semantic_blocker(self):
        converted,_=self.transformed(doc("windows.registry","reg_unrecognized"))
        findings=validate_assessment_capability_semantics(converted)
        self.assertIn("windows.registry.unsupported_type_value_encoding",
                      {row["code"] for row in findings})

    def test_existing_native_enums_not_changed(self):
        for capability in ("windows.registry","windows.ntuser"):
            converted,edits=self.transformed(doc(capability,"dword"))
            predicate=converted["assessment"]["tests"]["registry-value-test"]["states"][0]["state"]["all"][0]
            self.assertEqual(predicate["value"],"dword")
            self.assertFalse(any(x.get("reason")==
                "registry type source-to-native vocabulary crosswalk" for x in edits))

    def test_never_convert_unrelated_type_predicate(self):
        unrelated=doc("unix.file","reg_dword")
        result,_=self.transformed(unrelated)
        predicate=result["assessment"]["tests"]["registry-value-test"]["states"][0]["state"]["all"][0]
        self.assertEqual(predicate["value"],"reg_dword")

    def test_no_rewriting_of_pattern_match_semantics(self):
        example=doc("windows.registry","reg_.*")
        example["assessment"]["tests"]["registry-value-test"]["states"][0]["state"]["all"][0]["operation"]="pattern_match"
        result,_=self.transformed(example)
        predicate=result["assessment"]["tests"]["registry-value-test"]["states"][0]["state"]["all"][0]
        self.assertEqual(predicate["value"],"reg_.*")


if __name__=="__main__":
    unittest.main()
