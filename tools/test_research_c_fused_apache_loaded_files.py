#!/usr/bin/env python3
"""#245 hard Apache 19-Variable source graph: genuine three-operator C fusion.

No shell is run. Acquisitions and dynamic Variable selector come from
original source. Independent expected lists preserve source doc-order, scoped
dependencies, error vs unknown, duplicate removal and no-values statuses.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_fused_apache_loaded_files import (
    compile_loaded_files_fusion,evaluate_loaded_files_fusion,
    _hash,A,B,COMMAND)
from research_b_variable_schedule import plan_source_variables
from research_b_variable_plan_evaluator import evaluate_source_variable_plan
from research_b_source_shell_snapshot import normalize,PROVIDER

SOURCE=Path(__file__).resolve().parents[1]/(
    "research/requirements-first-language/contract-candidate/corpus/"
    "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")


class ComplexApacheSourceVariableFusion(unittest.TestCase):
    def setUp(self):
        self.doc=yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]
        self.hash=_hash(self.doc["variables"])
        self.compiled=compile_loaded_files_fusion(self.doc,pinned_source_sha256=self.hash)
        self.plan=plan_source_variables(self.doc)
        self.assertEqual(len(self.doc["variables"]),19)
        self.assertEqual(len(self.plan["nodes"]),19)
        self.assertFalse(self.compiled["scanner_executed"])

    def shell(self,collect,command,lines,*,status="complete"):
        using={k:collect[k] for k in ("shell","error_if_exit_status_not_0",
                                      "error_if_stderr_exists")}
        using["command"]=command
        snapshot={"query":using,"status":status,"records":[
            {"stdout_line":list(lines),"stderr_line":[],"exit_status":0}] if status in (
            "complete","incomplete") else []}
        return normalize(snapshot,**using)

    def acquisition(self,paths,*,loaded=(),second_status="complete"):
        original=self.doc["shared_objects"][
            "gather-unique-apache-http-installation-paths-object"]["collect"]
        process=self.shell(original,original["command"],paths)
        cmd=["/usr/sbin/httpd -t -D DUMP_INCLUDES"]
        if len(paths)==2:
            cmd=["/usr/sbin/httpd -t -D DUMP_INCLUDES",
                 "/opt/httpd -t -D DUMP_INCLUDES"]
        acquired=[process]
        if second_status!="missing":
            acquired.append(self.shell(self.compiled["collect"],cmd[0],loaded,
                                       status=second_status))
        return {PROVIDER:{"acquisitions":acquired}}

    def compare(self,evidence,expected_paths,expected_merged):
        source=evaluate_source_variable_plan(self.plan,evidence)
        command={"source_variable":COMMAND,
                 **source["variable_values"][COMMAND]}
        c=evaluate_loaded_files_fusion(self.compiled,evidence,
                                       resolved_command=command)
        self.assertEqual(source["variable_values"][A],expected_paths)
        self.assertEqual(source["variable_values"][B],expected_merged)
        self.assertEqual(c["paths"],expected_paths)
        self.assertEqual(c["merged"],expected_merged)
        return source,c

    def test_two_real_source_operations_are_combined_without_another_collector(self):
        self.assertEqual(self.compiled["dynamic_command_source_id"],COMMAND)
        self.assertEqual(self.compiled["collect"]["command"],{"variable":COMMAND})
        self.assertEqual(self.compiled["join_with"]," ")
        self.assertEqual(self.compiled["original_source_ids"],[A,B])
        self.assertEqual(self.compiled["extract_first"],
             self.doc["variables"][A]["expression"]["unique"]["regex_capture"]["pattern"])

    def test_source_order_and_duplicate_paths_with_external_expected_values(self):
        lines=[
            " (42) /etc/httpd/conf/httpd.conf",
            " (99) /etc/httpd/conf.d/ssl.conf",
            " (12) /etc/httpd/conf/httpd.conf",
        ]
        self.compare(self.acquisition(["/usr/sbin/httpd -DFOREGROUND"],loaded=lines),
                     {"status":"values","values":[
                         "/etc/httpd/conf/httpd.conf","/etc/httpd/conf.d/ssl.conf"]},
                     {"status":"values","values":[
                         "/etc/httpd/conf/httpd.conf /etc/httpd/conf.d/ssl.conf"]})

    def test_incomplete_missing_and_unmatched_source_data(self):
        unknown={"status":"unknown","values":[]}
        error={"status":"error","values":[]}
        lines=[" (42) /etc/httpd/conf/httpd.conf"]
        self.compare(self.acquisition(["/usr/sbin/httpd -DFOREGROUND"],
                     loaded=lines,second_status="incomplete"),unknown,unknown)
        self.compare(self.acquisition(["/usr/sbin/httpd -DFOREGROUND"],
                     second_status="missing"),unknown,unknown)
        self.compare(self.acquisition(["/usr/sbin/httpd -DFOREGROUND"],
                     loaded=[]),error,error)

    def test_multiple_discovered_executables_cannot_pick_first_command(self):
        source,c=self.compare(self.acquisition([
            "/usr/sbin/httpd -DFOREGROUND","/opt/httpd -DFOREGROUND"],
            loaded=[" (11) /etc/httpd/conf/httpd.conf"]),
            {"status":"unknown","values":[]},
            {"status":"unknown","values":[]})
        self.assertEqual(source["variable_values"][COMMAND]["status"],"values")
        self.assertEqual(len(source["variable_values"][COMMAND]["values"]),2)

    def test_duplicate_acquisition_and_wrong_variable_lineage_fail_closed(self):
        evidence=self.acquisition(["/usr/sbin/httpd -DFOREGROUND"],
                                  loaded=[" (1) /etc/httpd/conf/httpd.conf"])
        source=evaluate_source_variable_plan(self.plan,evidence)
        cmd={"source_variable":COMMAND,**source["variable_values"][COMMAND]}
        broken=deepcopy(evidence)
        broken[PROVIDER]["acquisitions"].append(
            deepcopy(broken[PROVIDER]["acquisitions"][1]))
        self.assertEqual(evaluate_loaded_files_fusion(
            self.compiled,broken,resolved_command=cmd)["paths"]["status"],"error")
        bad=dict(cmd,source_variable="a-different-source")
        self.assertEqual(evaluate_loaded_files_fusion(
            self.compiled,evidence,resolved_command=bad)["paths"]["status"],"error")

    def test_fingerprint_prevents_source_operator_or_collection_mismatch(self):
        for action in (
            lambda d:d["variables"][A]["expression"]["unique"]["regex_capture"].update(
                pattern="wrong"),
            lambda d:d["variables"][B]["expression"]["merge"].update(delimiter=";"),
            lambda d:d["variables"][A]["expression"]["unique"]["regex_capture"][
                "value"]["values"]["object"]["collect"].update(shell="powershell"),
        ):
            doc=deepcopy(self.doc)
            action(doc)
            with self.assertRaisesRegex(ValueError,"source Variable DAG changed"):
                compile_loaded_files_fusion(doc,pinned_source_sha256=self.hash)


if __name__=="__main__":
    unittest.main()
