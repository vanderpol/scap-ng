#!/usr/bin/env python3
"""Refs #245: original and C compact Apache offline value-status comparisons.

Independent expected examples are derived from the original pinned Apache
source and its historical B evaluator fixtures. These are not scanner results.
No commands run; the original source and C-compiled source schedule the same
19 Variables, and both must agree on values and status without inventing a
fallback for unavailable evidence.
"""
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_apache_provenance_split import (
    present_apache_provenance_split,compile_apache_split)
from research_b_variable_schedule import plan_source_variables
from research_b_variable_plan_evaluator import evaluate_source_variable_plan
from research_b_source_shell_snapshot import normalize,PROVIDER

SOURCE=Path(__file__).resolve().parents[1]/(
    "research/requirements-first-language/contract-candidate/corpus/"
    "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")
PATH_VAR="apache-path-httpd-or-apache2-variable"
COMMAND_VAR="command-gather-httpd-apache2-modules-variable"

def snapshot(doc,lines=(),status="complete"):
    spec=doc["shared_objects"][
        "gather-unique-apache-http-installation-paths-object"]["collect"]
    using={k:spec[k] for k in (
        "command","shell","error_if_exit_status_not_0","error_if_stderr_exists")}
    records=([{"stdout_line":list(lines),"stderr_line":[],"exit_status":0}]
             if status in ("complete","incomplete") else [])
    return normalize({"query":using,"status":status,"records":records},**using)

class CompactApacheEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]
        authored,provenance=present_apache_provenance_split(cls.source)
        cls.compiled=compile_apache_split(authored,provenance)
        cls.source_plan=plan_source_variables(cls.source)
        cls.compiled_plan=plan_source_variables(cls.compiled)

    def compare_case(self,fixture,expected_status,expected_paths=None,
                     expected_command=None):
        actual=evaluate_source_variable_plan(self.source_plan,fixture)
        authored=evaluate_source_variable_plan(self.compiled_plan,fixture)
        self.assertEqual(actual["variable_values"],authored["variable_values"])
        self.assertEqual(actual["trace"],authored["trace"])
        self.assertEqual(actual["nodes_evaluated"],19)
        values=actual["variable_values"]
        self.assertEqual(values[PATH_VAR]["status"],expected_status)
        if expected_paths is not None:
            self.assertEqual(values[PATH_VAR]["values"],expected_paths)
        if expected_command is not None:
            self.assertEqual(values[COMMAND_VAR]["values"],expected_command)
        self.assertFalse(authored["execution_supported"])
        self.assertFalse(authored["original_source_parity_verified"])

    def test_missing_query_is_not_silent_empty_pass(self):
        self.compare_case({},"unknown")

    def test_complete_process_snapshot_preserves_downstream_dynamic_command(self):
        self.compare_case({PROVIDER:{"acquisitions":[
            snapshot(self.source,["/usr/sbin/httpd -DFOREGROUND"])]}},
            "values",["/usr/sbin/httpd"],["/usr/sbin/httpd -M"])

    def test_multiple_process_paths_preserve_value_multiplicity(self):
        self.compare_case({PROVIDER:{"acquisitions":[snapshot(
            self.source,["/usr/sbin/httpd -DFOREGROUND",
                         "/opt/httpd -DFOREGROUND"])]}},
            "values",["/usr/sbin/httpd","/opt/httpd"],
            ["/usr/sbin/httpd -M","/opt/httpd -M"])

    def test_incomplete_collection_is_not_treated_as_complete_evidence(self):
        self.compare_case({PROVIDER:{"acquisitions":[snapshot(
            self.source,["/usr/sbin/httpd -DFOREGROUND"],"incomplete")]}},
            "unknown")

    def test_not_collected_and_not_applicable_remain_distinct(self):
        self.compare_case({PROVIDER:{"acquisitions":[snapshot(
            self.source,status="not collected")]}}, "unknown")
        self.compare_case({PROVIDER:{"acquisitions":[snapshot(
            self.source,status="not applicable")]}}, "not_applicable")

    def test_complete_empty_population_is_an_error_in_bounded_item_evaluator(self):
        self.compare_case({PROVIDER:{"acquisitions":[snapshot(
            self.source,[],"complete")]}}, "error")

    def test_explicit_collection_error_does_not_default_to_value(self):
        self.compare_case({PROVIDER:{"acquisitions":[snapshot(
            self.source,status="error")]}}, "error")

    def test_wrong_provenance_gives_error_not_a_false_value(self):
        bad=snapshot(self.source,["/usr/sbin/httpd -DFOREGROUND"])
        bad["provider"]="untrusted.shellcommand"
        self.compare_case({PROVIDER:{"acquisitions":[bad]}},"error")

if __name__=="__main__":
    unittest.main()
