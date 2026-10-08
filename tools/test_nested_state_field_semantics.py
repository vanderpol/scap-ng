"""Regression: intrinsic State field constraints are checked in nested 0.3 states."""
import unittest
from validate_generated_capability_semantics import validate_assessment_capability_semantics


def codes(capability, state):
    assessment={"assessment":{
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.3.0"},
        "tests":{"one-test":{
            "capability":capability,
            "states":[{"capability":capability,"state":state}],
        }}}}
    return {e.get("code") for e in validate_assessment_capability_semantics(assessment)}


def leaf(field,value,datatype):
    return {"field":field,"value":value,"datatype":datatype,
            "operation":"equals","match":"all","existence":"one_or_more"}


class NestedFieldsTests(unittest.TestCase):
    def test_lockout_negative_inside_all(self):
        self.assertIn("windows.lockoutpolicy.nonnegative_time_values",
                      codes("windows.lockoutpolicy",{"all":[leaf("lockout_duration",-1,"integer")]}))
    def test_lockout_negative_inside_any(self):
        self.assertIn("windows.lockoutpolicy.nonnegative_time_values",
                      codes("windows.lockoutpolicy",{"any":[leaf("lockout_duration",-1,"integer"),leaf("force_logoff",20,"integer")]}))
    def test_lockout_positive_inside_any(self):
        self.assertNotIn("windows.lockoutpolicy.nonnegative_time_values",
                      codes("windows.lockoutpolicy",{"any":[leaf("lockout_duration",1,"integer")]}))
    def test_wua_date_invalid_inside_all(self):
        self.assertIn("windows.wuaupdatesearcher.date_lexical_form",
                      codes("windows.wuaupdatesearcher",{"all":[leaf("last_deployment_change_time","tomorrow","string")]}))
    def test_wua_date_invalid_inside_any(self):
        self.assertIn("windows.wuaupdatesearcher.date_lexical_form",
                      codes("windows.wuaupdatesearcher",{"any":[leaf("last_deployment_change_time","2026-13-01","string")]}))
    def test_wua_date_valid(self):
        self.assertNotIn("windows.wuaupdatesearcher.date_lexical_form",
                      codes("windows.wuaupdatesearcher",leaf("last_deployment_change_time","2026-10-08","string")))


if __name__=="__main__":
    unittest.main()
