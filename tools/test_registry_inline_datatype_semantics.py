"""State comparison datatypes are independent of collected Registry Item datatypes."""
import copy
import unittest
from validate_generated_capability_semantics import validate_assessment_capability_semantics


def fixture(capability="windows.registry", kind="dword", value=1, datatype="integer"):
    return {"assessment": {
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.3.0"},
        "tests": {"registry-type-value-test": {
            "capability": capability,
            "states": [{"capability": capability, "state": {"all": [
                {"field": "type", "operation": "equals", "value": kind, "datatype": "string", "match": "all", "existence": "one_or_more"},
                {"field": "value", "operation": "equals", "value": value, "datatype": datatype, "match": "all", "existence": "one_or_more"},
            ]}}],
        }}
    }}


def mismatches(document):
    return [d for d in validate_assessment_capability_semantics(document)
            if d.get("code", "").endswith(".value_type_datatype")]


class InlineRegistryTypeTests(unittest.TestCase):
    def test_dword_integer_accepted(self):
        self.assertEqual([], mismatches(fixture()))
    def test_dword_string_state_cast_is_not_forbidden(self):
        self.assertEqual([], mismatches(fixture(value="1", datatype="string")))
    def test_qword_string_state_cast_is_not_forbidden(self):
        self.assertEqual([], mismatches(fixture(kind="qword", value="1", datatype="string")))
    def test_real_cached_logons_reg_sz_numeric_comparison_is_valid(self):
        # Both real Windows 11 SV-253447 and Server 2025 SV-278181
        # explicitly compare numeric limits against collected REG_SZ text.
        for limit in (10, 4):
            with self.subTest(limit=limit):
                f=fixture(kind="string", value=limit, datatype="integer")
                leaf=f["assessment"]["tests"]["registry-type-value-test"]["states"][0]["state"]["all"][1]
                leaf["operation"]="less_than_or_equal"
                findings=validate_assessment_capability_semantics(f)
                self.assertNotIn("windows.registry.value_type_datatype",
                                 {d.get("code") for d in findings})

    def test_string_string_accepted(self):
        self.assertEqual([], mismatches(fixture(kind="string", value="hello", datatype="string")))
    def test_ntuser_dword_string_state_cast_is_not_forbidden(self):
        self.assertEqual([], mismatches(fixture(capability="windows.ntuser", value="1", datatype="string")))
    def test_named_compound_state_comparison_cast_is_not_forbidden(self):
        f=fixture(value="1",datatype="string")
        state=f["assessment"]["tests"]["registry-type-value-test"]["states"][0]
        f["assessment"]["states"]={"registry-expected-state":state}
        f["assessment"]["tests"]["registry-type-value-test"]["states"]=["registry-expected-state"]
        self.assertEqual([],mismatches(f))
    def test_alternative_states_do_not_infer_one_global_type(self):
        f=fixture()
        test=f["assessment"]["tests"]["registry-type-value-test"]
        test["states"]=[
            {"capability":"windows.registry","state":{
                "field":"type","value":"dword","operation":"equals",
                "datatype":"string","match":"all","existence":"one_or_more"}},
            {"capability":"windows.registry","state":{
                "field":"value","value":"hello","operation":"equals",
                "datatype":"string","match":"all","existence":"one_or_more"}},
        ]
        test["states_match"]="any"
        self.assertEqual([],mismatches(f))

    def test_conjunctive_states_preserve_casting_permission(self):
        f=fixture()
        test=f["assessment"]["tests"]["registry-type-value-test"]
        test["states"]=[
            {"capability":"windows.registry","state":{
                "field":"type","value":"dword","operation":"equals",
                "datatype":"string","match":"all","existence":"one_or_more"}},
            {"capability":"windows.registry","state":{
                "field":"value","value":"1","operation":"equals",
                "datatype":"string","match":"all","existence":"one_or_more"}},
        ]
        test["states_match"]="all"
        self.assertEqual([],mismatches(f))

    def test_conflicting_types_in_same_conjunction_rejected(self):
        f=fixture()
        state=f["assessment"]["tests"]["registry-type-value-test"]["states"][0]["state"]
        state["all"].append({
            "field":"type","value":"string","operation":"equals",
            "datatype":"string","match":"all","existence":"one_or_more"})
        diagnostics=validate_assessment_capability_semantics(f)
        self.assertIn("windows.registry.conflicting_registry_types",
                      [e.get("code") for e in diagnostics])

    def test_unmodelled_registry_type_and_value_is_explicit_error(self):
        for kind in ("none","resource_list","full_resource_descriptor",
                     "resource_requirements_list"):
            with self.subTest(kind=kind):
                f=fixture(kind=kind,value="opaque",datatype="string")
                codes={entry.get("code") for entry in
                       validate_assessment_capability_semantics(f)}
                self.assertIn("windows.registry.unsupported_type_value_encoding",codes)

    def test_unmodelled_registry_type_alone_is_still_comparable(self):
        f=fixture(kind="none")
        state=f["assessment"]["tests"]["registry-type-value-test"]["states"][0]["state"]
        state["all"]=[state["all"][0]]
        codes={entry.get("code") for entry in
               validate_assessment_capability_semantics(f)}
        self.assertNotIn("windows.registry.unsupported_type_value_encoding",codes)

    def test_disjunction_does_not_infer_type(self):
        f=fixture(value="1",datatype="string")
        f["assessment"]["tests"]["registry-type-value-test"]["states"][0]["state"]["any"]=(
            f["assessment"]["tests"]["registry-type-value-test"]["states"][0]["state"].pop("all"))
        self.assertEqual([], mismatches(f))


if __name__ == "__main__":
    unittest.main()
