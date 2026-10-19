#!/usr/bin/env python3
"""#245 independent C fused Variable pipeline differential fixtures (NOT OVAL scanner).
Uses EXACTLY the same precollected shell Items and source expression DAG.
We keep independent expected source values and statuses for bounded cases.
"""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_fused_apache import compile_fused_command_pipeline,evaluate_fused_command_pipeline,_hash
from research_b_variable_schedule import plan_source_variables
from research_b_variable_plan_evaluator import evaluate_source_variable_plan
from research_b_source_shell_snapshot import normalize,PROVIDER

SOURCE=Path(__file__).resolve().parents[1]/(
 "research/requirements-first-language/contract-candidate/corpus/source-specimens/"
 "independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml")
CAPTURE="apache-path-httpd-or-apache2-variable"
DERIVED="command-gather-apache-version-variable"


class FusedApacheCProof(unittest.TestCase):
    def setUp(self):
        self.source=yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]
        self.pinned=_hash(self.source["variables"])
        self.plan=compile_fused_command_pipeline(self.source,pinned_variables_sha256=self.pinned)
        self.assertEqual(self.plan["source_ids"],[CAPTURE,DERIVED])
        self.assertFalse(self.plan["original_scanner_parity_verified"])
        self.assertFalse(self.plan["collector_executed"])

    def fixture(self,lines=(),status="complete"):
        col=self.plan["collect"]
        using={key:col[key] for key in (
          "command","shell","error_if_exit_status_not_0","error_if_stderr_exists")}
        snap={"query":using,"status":status,"records":[
          {"stdout_line":list(lines),"stderr_line":[],"exit_status":0}]}
        return {PROVIDER:{"acquisitions":[normalize(snap,**using)]}}

    def compare(self,evidence,cap,derived):
        # Existing source graph evaluator used as a separate implementation;
        # independent hand-authored outputs below prevent same-evaluator-only proof.
        reference=evaluate_source_variable_plan(plan_source_variables(self.source),evidence)
        c=evaluate_fused_command_pipeline(self.plan,evidence)
        self.assertEqual(reference["variable_values"][CAPTURE],cap)
        self.assertEqual(reference["variable_values"][DERIVED],derived)
        self.assertEqual(c["captured"],cap)
        self.assertEqual(c["derived"],derived)

    def test_fusion_uses_one_existing_acquisition_not_second_collector(self):
        self.assertEqual(self.plan["collect"],self.source["variables"][CAPTURE][
          "expression"]["regex_capture"]["value"]["values"]["object"]["collect"])
        self.assertEqual(self.plan["append_literal"]," -V")
        self.assertEqual(self.plan["capture_first_group"],
                         self.source["variables"][CAPTURE]["expression"]["regex_capture"]["pattern"])
        self.assertNotIn("provider",self.plan)

    def test_source_independent_expected_success_with_one_and_many_paths(self):
        for lines,caps,derived in [
          (["/usr/sbin/httpd -DFOREGROUND"],["/usr/sbin/httpd"],["/usr/sbin/httpd -V"]),
          (["/usr/sbin/apache2 -DFOREGROUND"],["/usr/sbin/apache2"],["/usr/sbin/apache2 -V"]),
          (["/usr/sbin/httpd -DFOREGROUND","/opt/httpd -DFOREGROUND"],
             ["/usr/sbin/httpd","/opt/httpd"],["/usr/sbin/httpd -V","/opt/httpd -V"]),
        ]:
            with self.subTest(lines=lines):
                self.compare(self.fixture(lines),{"status":"values","values":caps},
                             {"status":"values","values":derived})

    def test_nodata_partial_unknown_and_invalid_records_fail_closed(self):
        unknown={"status":"unknown","values":[]}
        error={"status":"error","values":[]}
        self.compare({},unknown,unknown)
        self.compare(self.fixture(["/usr/sbin/httpd -DFOREGROUND"],status="incomplete"),unknown,unknown)
        self.compare(self.fixture([],status="complete"),error,error)
        self.compare(self.fixture(["not a process path"]),error,error)
        broken=self.fixture(["/usr/sbin/httpd -DFOREGROUND"])
        broken[PROVIDER]["acquisitions"][0]["provider"]="forged"
        self.compare(broken,error,error)

    def test_duplicate_identity_or_unavailable_response_not_success(self):
        error={"status":"error","values":[]}
        good=self.fixture(["/usr/sbin/httpd -DFOREGROUND"])
        duplicate=copy.deepcopy(good)
        duplicate[PROVIDER]["acquisitions"].append(copy.deepcopy(good[PROVIDER]["acquisitions"][0]))
        self.compare(duplicate,error,error)
        bad=copy.deepcopy(good)
        bad[PROVIDER]["acquisitions"][0]["items"].append(
          copy.deepcopy(bad[PROVIDER]["acquisitions"][0]["items"][0]))
        self.compare(bad,error,error)

    def test_source_dependency_changes_must_not_be_optimized_away(self):
        for broken in [
           lambda a:a["variables"][DERIVED]["expression"]["concat"][1]["literal"].update(value=" -M"),
           lambda a:a["variables"][CAPTURE]["expression"]["regex_capture"].update(pattern="\\"+"bad"),
           lambda a:a["variables"][DERIVED]["expression"]["concat"].append(
                {"literal":{"datatype":"string","value":"again"}}),
        ]:
            with self.subTest(edit=str(broken)):
                changed=copy.deepcopy(self.source)
                broken(changed)
                with self.assertRaises(ValueError):
                    compile_fused_command_pipeline(changed,pinned_variables_sha256=self.pinned)


if __name__=="__main__":
    unittest.main()
