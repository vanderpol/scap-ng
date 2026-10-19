#!/usr/bin/env python3
"""Refs #245: source-backed origin and consumer role census, no migration."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_variable_roles import audit_value_roles
from test_research_c_set_filter_variable_probe import fixture as complex_source
ROOT=Path(__file__).resolve().parents[1]
APACHE=(ROOT/"research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")
ORIGINAL=ROOT/"board/review-content/0.2.0/sources/filter.xml"

class SourceVariableRoleTests(unittest.TestCase):
    def test_complete_real_apache_nineteen_variable_uses(self):
        source=yaml.safe_load(APACHE.read_text(encoding="utf-8"))["assessment"]
        original=deepcopy(source)
        report=audit_value_roles(source)
        self.assertEqual(source,original)
        self.assertEqual(report["variable_count"],19)
        self.assertEqual(len(report["roles"]),19)
        self.assertEqual(report["role_summary"]["origin_system_derived"],19)
        self.assertGreater(report["role_summary"].get("used_acquisition_parameter",0),0)
        self.assertGreater(report["role_summary"].get("used_value_transformation",0),0)
        self.assertFalse(report["C_language_decision_made"])
        self.assertFalse(report["source_semantic_parity_proven"])
        self.assertTrue(all(not row["can_auto_remove_or_duplicate"] for row in report["roles"]))

    def test_literals_are_not_real_collection_derived_variables(self):
        fixture=complex_source()
        before=deepcopy(fixture)
        report=audit_value_roles(fixture)
        self.assertEqual(before,fixture)
        by_id={r["source_variable_id"]:r for r in report["roles"]}
        for name in ("uid-step-variable","uid-band-offsets-variable"):
            self.assertEqual(by_id[name]["origin"],"publisher_literal")
            self.assertEqual(by_id[name]["consumer_roles"],["value_transformation"])
            self.assertFalse(by_id[name]["can_auto_remove_or_duplicate"])
        self.assertEqual(by_id["excluded-owner-uids-variable"]["consumer_roles"],
                         ["population_filter"])
        self.assertEqual(by_id["reference-owner-uid-variable"]["origin"],
                         "system_derived")

    def test_variable_can_feed_collection_and_comparison_at_once(self):
        doc=complex_source()
        doc["shared_objects"]["target-a-object"]["select"]["full_path"]={
            "equals":{"variable":"reference-owner-uid-variable"}}
        doc["tests"]["exactly-one-surviving-file-test"]["states"]=[
            {"field":"owner_uid","equals":{
                "variable":"reference-owner-uid-variable"}}]
        report=audit_value_roles(doc)
        by_id={r["source_variable_id"]:r for r in report["roles"]}
        val=by_id["reference-owner-uid-variable"]
        self.assertEqual(set(val["consumer_roles"]),
                         {"acquisition_parameter","assertion_expected_value",
                          "value_transformation"})
        self.assertEqual(report["role_summary"]["mixed_acquisition_and_evaluation"],1)
        self.assertFalse(val["can_auto_remove_or_duplicate"])

    def test_external_oval_value_is_not_organization_authority(self):
        doc=complex_source()
        doc["variables"]["uid-step-variable"]["kind"]="external"
        r=audit_value_roles(doc)
        val=next(x for x in r["roles"] if x["source_variable_id"]=="uid-step-variable")
        self.assertEqual(val["origin"],
                         "external_oval_value_not_automatically_organizational_policy")

    def test_original_self_assertion_multivalue_constant_not_a_policy_input(self):
        root=ET.parse(ORIGINAL).getroot()
        tags={x.tag.rsplit("}",1)[-1] for x in root.iter()}
        self.assertIn("constant_variable",tags)
        var=next(x for x in root.iter() if x.tag.endswith("}constant_variable")
                 and x.get("id")=="oval:org.mitre.oval.test:var:134")
        values=[(x.text or "").strip() for x in var if x.tag.endswith("}value")]
        self.assertEqual(values,["/opt/support/txt/txtfile",
                                 "/opt/support/txt/txtfile/subtxtfile"])
        references=[x for x in root.iter() if x.attrib.get("var_ref")==var.get("id")]
        self.assertEqual(len(references),1)
        self.assertEqual(references[0].get("var_check"),"only one")

    def test_cycles_still_rejected_through_original_index(self):
        doc=complex_source()
        doc["variables"]["reference-owner-uid-variable"]["expression"]={
            "variable":"excluded-owner-uids-variable"}
        with self.assertRaisesRegex(ValueError,"cyclic source dataflow"):
            audit_value_roles(doc)

if __name__=="__main__":
    unittest.main()
