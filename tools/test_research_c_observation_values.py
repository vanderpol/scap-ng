#!/usr/bin/env python3
"""#245 Regression: observation is C authoring, Object stays internal source IR."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_observation_values import (
    compile_c_observation_values, present_c_observation_values)
from research_b_source_shell_snapshot import normalize,PROVIDER
from research_b_variable_schedule import plan_source_variables
from research_b_variable_plan_evaluator import evaluate_source_variable_plan

ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/"research/requirements-first-language/contract-candidate/corpus/source-specimens"
SMALL=SOURCES/"independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml"
FULL=SOURCES/"independent-shellcommand-1-3d964d126ca8.source.yaml"
CFILE=ROOT/"research/assessment-simplification/compact-authoring-04/c-derived-apache-version.research.yaml"

def source(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))["assessment"]

def authored():
    return yaml.safe_load(CFILE.read_text(encoding="utf-8"))

class ObservationValueResearch(unittest.TestCase):
    def test_authoring_hides_object_key_without_erasing_A_provenance(self):
        raw=CFILE.read_text(encoding="utf-8")
        self.assertIn("observation:",raw)
        self.assertNotIn("object:",raw)
        compiled=compile_c_observation_values(authored())
        native=compiled["variables"]["apache-path-httpd-or-apache2-variable"][
            "expression"]["regex_capture"]["value"]["values"]["object"]
        self.assertEqual(native["object_title"],
                         "Gather unique apache http installation paths")
        self.assertEqual(compiled["authored_private_observation_count"],1)
        self.assertEqual(compiled["authored_named_observation_count"],0)
        self.assertFalse(compiled["collector_executed"])

    def test_full_apache_shared_observation_scope_and_source_pinning(self):
        original=source(FULL)
        view=present_c_observation_values(original)
        self.assertEqual(len(view["observations"]),1)
        alias=next(iter(view["observations"]))
        self.assertEqual(view["observations"][alias]["source_object"],
                         "gather-unique-apache-http-installation-paths-object")
        result=compile_c_observation_values(view)
        self.assertEqual(result["variables"],original["variables"])
        self.assertEqual(result["shared_objects"],original["shared_objects"])
        self.assertEqual(result["authored_named_observation_count"],1)
        self.assertEqual(result["authored_private_observation_count"],4)
        self.assertTrue(result["original_source_reconstructed_if_pinned"])
        drift=deepcopy(view)
        drift["observations"][alias]["from"][
            "independent.shellcommand"]["collect"]["pattern"]="^different"
        with self.assertRaisesRegex(ValueError,"pinned source"):
            compile_c_observation_values(drift)

    def test_unused_duplicate_and_unbound_named_observations_rejected(self):
        doc=present_c_observation_values(source(FULL))
        alias=next(iter(doc["observations"]))
        extra=deepcopy(doc)
        extra["observations"]["unused_extra"]=deepcopy(doc["observations"][alias])
        extra["observations"]["unused_extra"]["source_object"]="other-acquisition-source"
        with self.assertRaisesRegex(ValueError,"unused observation"):
            compile_c_observation_values(extra)
        duplicate=deepcopy(doc)
        duplicate["observations"]["other_alias"]=deepcopy(doc["observations"][alias])
        with self.assertRaisesRegex(ValueError,"claim one source Object"):
            compile_c_observation_values(duplicate)
        missing=deepcopy(doc)
        missing["observations"].pop(alias)
        with self.assertRaisesRegex(ValueError,"unresolved named observation"):
            compile_c_observation_values(missing)

    def test_private_observation_cannot_claim_shared_provenance_or_legacy_object(self):
        doc=authored()
        val=doc["steps"][0]["derive"]["extract"]["value"]["read_field"]
        val["object"]=val.pop("observation")
        with self.assertRaises(ValueError):
            compile_c_observation_values(doc)
        doc=authored()
        val=doc["steps"][0]["derive"]["extract"]["value"]["read_field"]
        val["observation"]["source_object"]="private-is-not-shared"
        with self.assertRaisesRegex(ValueError,"private observation"):
            compile_c_observation_values(doc)

    def test_missing_error_incomplete_and_na_evidence_do_not_become_values(self):
        src=source(SMALL)
        clone=deepcopy(src)
        clone["variables"]=compile_c_observation_values(authored())["variables"]
        collect=src["variables"]["apache-path-httpd-or-apache2-variable"][
            "expression"]["regex_capture"]["value"]["values"]["object"]["collect"]
        using={k:collect[k] for k in (
            "command","shell","error_if_exit_status_not_0","error_if_stderr_exists")}
        for status, expected in (
            ("error","error"),("not applicable","not_applicable"),
            ("not collected","unknown"),("incomplete","unknown"),
        ):
            with self.subTest(status=status):
                snapshot=normalize({"query":using,"status":status,"records":[{
                  "stdout_line":["/usr/sbin/httpd -DFOREGROUND"],
                  "stderr_line":[],"exit_status":0}]},**using)
                got=evaluate_source_variable_plan(
                    plan_source_variables(clone),
                    {PROVIDER:{"acquisitions":[snapshot]}})["variable_values"]
                self.assertEqual(
                    got["command-gather-apache-version-variable"]["status"],expected)

if __name__=="__main__":
    unittest.main()
