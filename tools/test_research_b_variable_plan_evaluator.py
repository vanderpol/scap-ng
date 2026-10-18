#!/usr/bin/env python3
"""#237 bounded source Apache Variable graph evaluation against external Items."""
from __future__ import annotations
from pathlib import Path
import copy
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_variable_schedule import plan_source_variables
from research_b_variable_plan_evaluator import evaluate_source_variable_plan
from research_b_source_shell_snapshot import normalize,PROVIDER

SOURCE=Path(__file__).resolve().parents[1]/(
    "research/requirements-first-language/contract-candidate/corpus/source-specimens")
SIMPLE=SOURCE/"independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml"
COMPLEX=SOURCE/"independent-shellcommand-1-3d964d126ca8.source.yaml"


def collected(collect,lines,status="complete"):
    using={key:collect[key] for key in (
        "command","shell","error_if_exit_status_not_0","error_if_stderr_exists")}
    row={"stdout_line":lines,"stderr_line":[],"exit_status":0}
    return normalize({"query":using,"status":status,"records":[row]},**using)


class VariablePlanEvaluationTests(unittest.TestCase):
    def setup_plan(self,source):
        doc=yaml.safe_load(source.read_text())["assessment"]
        return doc,plan_source_variables(doc)

    def test_two_variable_apache_graph_resolves_with_typed_query_evidence(self):
        doc,plan=self.setup_plan(SIMPLE)
        process=doc["variables"]["apache-path-httpd-or-apache2-variable"][
            "expression"]["regex_capture"]["value"]["values"]["object"]["collect"]
        evidence={PROVIDER:{"acquisitions":[collected(
            process,["/usr/sbin/httpd -DFOREGROUND"])]}}
        result=evaluate_source_variable_plan(plan,evidence)
        self.assertFalse(result["execution_supported"])
        self.assertFalse(result["original_source_parity_verified"])
        self.assertEqual(result["nodes_evaluated"],2)
        self.assertEqual(result["variable_values"][
            "apache-path-httpd-or-apache2-variable"]["values"],["/usr/sbin/httpd"])
        self.assertEqual(result["variable_values"][
            "command-gather-apache-version-variable"]["values"],["/usr/sbin/httpd -V"])

    def test_nineteen_variable_real_source_evaluates_what_evidence_proves_only(self):
        doc,plan=self.setup_plan(COMPLEX)
        process=doc["shared_objects"]["gather-unique-apache-http-installation-paths-object"]["collect"]
        fixture={PROVIDER:{"acquisitions":[collected(
            process,["/usr/sbin/httpd -DFOREGROUND"])]}}
        result=evaluate_source_variable_plan(plan,fixture)
        self.assertEqual(result["nodes_evaluated"],19)
        var=result["variable_values"]
        self.assertEqual(var["apache-base-install-directories-unix-variable"]["values"],
                         ["/usr/sbin/"])
        self.assertEqual(var["apache-path-httpd-or-apache2-variable"]["values"],
                         ["/usr/sbin/httpd"])
        self.assertEqual(var["command-gather-httpd-apache2-modules-variable"]["values"],
                         ["/usr/sbin/httpd -M"])
        self.assertEqual(var["httpd-root-apachectl-v-variable"]["values"],
                         ["/usr/sbin/apachectl -V | grep -i 'httpd_root'"])
        self.assertEqual(var["merged-list-all-loaded-config-files-variable"]["status"],
                         "unknown")
        self.assertEqual(len(result["trace"]),19)
        self.assertTrue(any(t["status"]=="unknown" for t in result["trace"]))
        self.assertFalse(result["execution_supported"])

    def test_actual_apache2_regex_alternation_does_not_switch_capture_groups(self):
        doc,plan=self.setup_plan(COMPLEX)
        process=doc["shared_objects"]["gather-unique-apache-http-installation-paths-object"]["collect"]
        observed=collected(process,["/usr/sbin/apache2 -DFOREGROUND"])
        result=evaluate_source_variable_plan(plan,{PROVIDER:{"acquisitions":[observed]}})
        self.assertEqual(result["variable_values"][
            "apache-base-install-directories-unix-variable"]["values"],[""])
        self.assertEqual(result["variable_values"][
            "apache-path-httpd-or-apache2-variable"]["values"],["/usr/sbin/apache2"])

    def test_multiple_paths_not_dropped_during_concat_or_command_resolution(self):
        doc,plan=self.setup_plan(COMPLEX)
        process=doc["shared_objects"]["gather-unique-apache-http-installation-paths-object"]["collect"]
        fixture={PROVIDER:{"acquisitions":[collected(process,[
            "/usr/sbin/httpd -DFOREGROUND","/opt/httpd -DFOREGROUND"])]}}
        result=evaluate_source_variable_plan(plan,fixture)
        var=result["variable_values"]
        self.assertEqual(var["apache-path-httpd-or-apache2-variable"]["values"],
                         ["/usr/sbin/httpd","/opt/httpd"])
        self.assertEqual(var["command-gather-httpd-apache2-modules-variable"]["values"],
                         ["/usr/sbin/httpd -M","/opt/httpd -M"])
        self.assertEqual(var["filepath-httpd-root-variable"]["status"],"unknown")

    def test_missing_query_incomplete_query_duplicate_or_spoofed_source(self):
        doc,plan=self.setup_plan(SIMPLE)
        collect=doc["variables"]["apache-path-httpd-or-apache2-variable"][
            "expression"]["regex_capture"]["value"]["values"]["object"]["collect"]
        absent=evaluate_source_variable_plan(plan,{})
        self.assertEqual(absent["variable_values"][
            "apache-path-httpd-or-apache2-variable"]["status"],"unknown")
        e=collected(collect,["/usr/sbin/httpd -DFOREGROUND"],status="incomplete")
        partial=evaluate_source_variable_plan(plan,{PROVIDER:{"acquisitions":[e]}})
        self.assertEqual(partial["variable_values"][
            "apache-path-httpd-or-apache2-variable"]["status"],"unknown")
        bad=copy.deepcopy(e);bad["status"]="complete";bad["provider"]="fake"
        wrong=evaluate_source_variable_plan(plan,{PROVIDER:{"acquisitions":[bad]}})
        self.assertEqual(wrong["variable_values"][
            "apache-path-httpd-or-apache2-variable"]["status"],"error")
        many=evaluate_source_variable_plan(plan,{PROVIDER:{"acquisitions":[bad,bad]}})
        self.assertEqual(many["variable_values"][
            "apache-path-httpd-or-apache2-variable"]["status"],"error")

    def test_duplicate_source_variable_ids_and_corrupt_plan_fail(self):
        _,plan=self.setup_plan(SIMPLE)
        plan["nodes"].append(copy.deepcopy(plan["nodes"][0]))
        with self.assertRaises(ValueError):
            evaluate_source_variable_plan(plan,{})
        _,plan=self.setup_plan(SIMPLE)
        plan["execution_supported"]=True
        with self.assertRaises(ValueError):
            evaluate_source_variable_plan(plan,{})


if __name__=="__main__":
    unittest.main()
