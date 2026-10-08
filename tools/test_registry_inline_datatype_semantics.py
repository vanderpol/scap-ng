"""Regression coverage for Registry type/value compatibility in inline States."""
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
    def test_dword_string_rejected(self):
        self.assertTrue(mismatches(fixture(value="1", datatype="string")))
    def test_qword_string_rejected(self):
        self.assertTrue(mismatches(fixture(kind="qword", value="1", datatype="string")))
    def test_string_string_accepted(self):
        self.assertEqual([], mismatches(fixture(kind="string", value="hello", datatype="string")))
    def test_ntuser_dword_string_rejected(self):
        self.assertTrue(mismatches(fixture(capability="windows.ntuser", value="1", datatype="string")))
    def test_named_compound_state_rejected(self):
        f=fixture(value="1",datatype="string")
        state=f["assessment"]["tests"]["registry-type-value-test"]["states"][0]
        f["assessment"]["states"]={"registry-expected-state":state}
        f["assessment"]["tests"]["registry-type-value-test"]["states"]=["registry-expected-state"]
        self.assertTrue(mismatches(f))
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

    def test_conjunctive_states_preserve_cross_field_validation(self):
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
        self.assertTrue(mismatches(f))

    def test_conflicting_types_in_same_conjunction_rejected(self):
        f=fixture()
        state=f["assessment"]["tests"]["registry-type-value-test"]["states"][0]["state"]
        state["all"].append({
            "field":"type","value":"string","operation":"equals",
            "datatype":"string","match":"all","existence":"one_or_more"})
        diagnostics=validate_assessment_capability_semantics(f)
        self.assertIn("windows.registry.conflicting_registry_types",
                      [e.get("code") for e in diagnostics])

    def test_disjunction_does_not_infer_type(self):
        f=fixture(value="1",datatype="string")
        f["assessment"]["tests"]["registry-type-value-test"]["states"][0]["state"]["any"]=(
            f["assessment"]["tests"]["registry-type-value-test"]["states"][0]["state"].pop("all"))
        self.assertEqual([], mismatches(f))


if __name__ == "__main__":
    unittest.main()
