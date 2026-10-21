#!/usr/bin/env python3
"""#237 preserve source plan-only accounting separate from actual conversion."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_variable_plan_coverage import coverage,markdown

ROOT=Path(__file__).resolve().parents[1]/(
    "research/requirements-first-language/contract-candidate/corpus/source-specimens")
SIMPLE=ROOT/"independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml"
COMPLEX=ROOT/"independent-shellcommand-1-3d964d126ca8.source.yaml"


def cap(doc,path):
    return {"source_document":{"assessment":doc},"source_path":path}


class PlanCensusTests(unittest.TestCase):
    def test_simple_complex_and_unbound_separated_with_no_executable_claim(self):
        simple=yaml.safe_load(SIMPLE.read_text())["assessment"]
        large=yaml.safe_load(COMPLEX.read_text())["assessment"]
        broken=copy.deepcopy(large)
        broken["id"]="broken-source-shared-ref"
        broken["shared_objects"].clear()
        examples={
            "simple":cap(simple,"authoring/apache_server_2-4_unix_server/simple.yaml"),
            "complex":cap(large,"authoring/apache_server_2-4_unix_server/complex.yaml"),
            "broken":cap(broken,"authoring/apache_server_2-4_unix_server/broken.yaml"),
            "manual":cap({"mode":"manual","variables":{"not-executable":{}}},
                         "authoring/shared/manual.yaml"),
            "plain":cap({"mode":"automated","variables":{}},
                        "authoring/rhel_9/plain.yaml"),
        }
        r=coverage(examples)
        self.assertEqual(r["total_automated_assessments_with_variables"],3)
        self.assertEqual(r["structurally_planned"],2)
        self.assertEqual(r["blocked"],1)
        self.assertFalse(r["scanner_executable"])
        self.assertFalse(r["source_parity_verified"])
        row=next(x for x in r["assessments"] if x["assessment_id"]==large["id"])
        self.assertEqual(row["variable_nodes"],19)
        self.assertEqual(row["max_variable_depth"],9)
        self.assertIn("gather-unique-apache-http-installation-paths-object",
                      row["shared_object_refs"])
        self.assertTrue(row["source_variables_sha256"])
        self.assertNotIn("fixture_ir_compiled",markdown(r))
        self.assertIn("Plan failures",markdown(r))

    def test_publisher_logical_id_and_duplicate_collision_fail_closed(self):
        source=yaml.safe_load(SIMPLE.read_text())["assessment"]
        first=cap(source,"authoring/apache_server_2-4_unix_server/a.yaml")
        report=coverage({"transport-key-not-logical-id":first})
        self.assertEqual(
            report["assessments"][0]["assessment_id"], source["id"]
        )
        with self.assertRaisesRegex(ValueError,"Duplicate Variable Assessment"):
            coverage({"a":first,"b":cap(
                copy.deepcopy(source),"authoring/apache_server_2-4_unix_server/b.yaml"
            )})

    def test_zero_source_variable_checks_not_a_compiled_assessment(self):
        report=coverage({"simple":{"source_document":{"assessment":{
            "id":"x","mode":"automated","tests":{},
            "variables":{},"evaluate":{}}},
            "source_path":"a.yaml"}})
        self.assertEqual(report["total_automated_assessments_with_variables"],0)
        self.assertEqual(report["structurally_planned"],0)
        self.assertEqual(report["assessments"],[])
        self.assertIn("None",markdown(report))


if __name__=="__main__":
    unittest.main()
