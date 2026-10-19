#!/usr/bin/env python3
"""#245 C/A shared-backend prototype: real source-backed structural tests.

This is a read-only compatibility experiment, not a scanner, performance
benchmark, normative grammar, or end-to-end original-OVAL parity proof.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_c_shared_engine import (simple_c_home_to_a_test,
                                      source_a_home_descriptor,
                                      present_c_variable_steps,
                                      compile_c_variable_steps)
from v04_a_dataflow_index import index_assessment_dataflow
from research_b_variable_schedule import plan_source_variables
from research_b_variable_plan_evaluator import evaluate_source_variable_plan
from research_b_source_shell_snapshot import normalize, PROVIDER

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "research/assessment-simplification/compact-authoring-04/runtime-slice/home-nosuid.assessment.json"
SPECIMENS = ROOT / "research/requirements-first-language/contract-candidate/corpus/source-specimens"
APACHE_SIMPLE = SPECIMENS / "independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml"
APACHE_COMPLEX = SPECIMENS / "independent-shellcommand-1-3d964d126ca8.source.yaml"


def home_source():
    import json
    return json.loads(HOME.read_text(encoding="utf-8"))


def c_home(source):
    """Independent C-authored fixture; never synthesize it from the A source."""
    fixture = ROOT / ("research/assessment-simplification/compact-authoring-04/"
                      "c-source-exact-home-nosuid.research.yaml")
    parsed = yaml.safe_load(fixture.read_text(encoding="utf-8"))
    if parsed["id"] != "research-c-source-exact-rhel-home-nosuid":
        raise ValueError("unrecognized authored C source witness")
    return parsed["require"]


def apache(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))["assessment"]


def fixtures_for(doc, *, lines=None, status="complete"):
    shared = doc["shared_objects"]["gather-unique-apache-http-installation-paths-object"]
    collect = shared["collect"]
    using = {key: collect[key] for key in (
        "command", "shell", "error_if_exit_status_not_0", "error_if_stderr_exists")}
    snap = normalize({"query":using,"status":status,
                      "records":[{"stdout_line":lines or [],
                                  "stderr_line":[],"exit_status":0}]}, **using)
    return {PROVIDER: {"acquisitions":[snap]}}


class SharedACollectionTests(unittest.TestCase):
    def test_real_rhel_home_source_matches_C_collection_and_item_field_scopes(self):
        original = home_source()
        lowered = simple_c_home_to_a_test(c_home(original), original)
        self.assertEqual(lowered, source_a_home_descriptor(original))
        self.assertEqual(lowered["acquisition"]["capability"], "linux.partition")
        self.assertEqual(lowered["acquisition"]["select"]["mount_point"],
                         {"matches_regex": r".*\/home"})
        self.assertEqual(lowered["item_requirement"], "at_least_one_exists_and_all_match")
        self.assertEqual(lowered["field_predicates"][0]["mount_options"]["require"],
                         "at_least_one_exists_and_some_match")
        self.assertFalse(lowered["scanner_executed"])

    def test_source_selector_cannot_be_silently_simplified(self):
        source = home_source()
        c = c_home(source)
        c["where"] = {"mount_point": {"equals": "/home"}}
        with self.assertRaisesRegex(ValueError,"preserve source mount regex"):
            simple_c_home_to_a_test(c, source)
        self.assertEqual(source["assessment"]["tests"][
            "home-mounted-nosuid-option-test"]["object"]["select"]["mount_point"],
            {"matches_regex": r".*\/home"})

    def test_population_and_field_existence_are_independent(self):
        source=home_source()
        for change in (
            {"minimum_items":0},
            {"minimum_items":True},
            {"all_found_items":{"mount_options":{"equals":"nosuid"}}},
            {"all_found_items":{"mount_options":{"contains":"nodev"}}},
            {"extra":None},
        ):
            with self.subTest(change=change):
                c=c_home(source)
                c.update(change)
                with self.assertRaises(ValueError):
                    simple_c_home_to_a_test(c,source)
        original=deepcopy(source)
        original["assessment"]["tests"]["home-mounted-nosuid-option-test"]["require"]=(
            "at_least_one_exists_and_some_match")
        with self.assertRaisesRegex(ValueError,"source Item or field existence"):
            simple_c_home_to_a_test(c_home(source),original)


class SharedAVariableGraphTests(unittest.TestCase):
    def test_real_apache_two_step_C_view_reconstructs_source(self):
        doc=apache(APACHE_SIMPLE)
        self.assertEqual(len(doc["variables"]),2)
        view=present_c_variable_steps(doc)
        self.assertEqual({next(iter(s["derive"])) for s in view["steps"]},
                         {"extract","combine"})
        rebuilt=compile_c_variable_steps(view,doc)
        self.assertEqual(rebuilt,doc)
        self.assertEqual(index_assessment_dataflow(doc),
                         index_assessment_dataflow(rebuilt))
        self.assertFalse(view["execution_supported"])
        self.assertFalse(view["original_source_parity_verified"])

    def test_real_apache_nineteen_step_C_view_keeps_A_graph_and_acquisitions(self):
        doc=apache(APACHE_COMPLEX)
        self.assertEqual(len(doc["variables"]),19)
        before=deepcopy(doc)
        view=present_c_variable_steps(doc)
        self.assertEqual(len(view["steps"]),19)
        ops={next(iter(s["derive"])) for s in view["steps"]}
        self.assertTrue({"extract","combine","merge_values","distinct"} <= ops)
        after=compile_c_variable_steps(view,doc)
        self.assertEqual(before,doc)
        self.assertEqual(after,doc)
        index=index_assessment_dataflow(after)
        self.assertEqual(index["status"],"SOURCE_DATAFLOW_ONLY_NOT_EXECUTABLE")
        self.assertTrue(any(e["role"]=="variable_value" for e in index["edges"]))
        self.assertTrue(any(e["role"]=="object_acquisition" for e in index["edges"]))

    def test_same_precollected_items_produce_identical_fixture_variables_and_status(self):
        original=apache(APACHE_COMPLEX)
        view=present_c_variable_steps(original)
        after=compile_c_variable_steps(view,original)
        # The same already-written fixture-only evaluator is reused by both
        # inputs. This is NOT an independent variable semantics oracle.
        for status,lines in [
            ("complete",["/usr/sbin/httpd -DFOREGROUND"]),
            ("complete",["/usr/sbin/apache2 -DFOREGROUND"]),
            ("complete",["/usr/sbin/httpd -DFOREGROUND",
                         "/opt/httpd -DFOREGROUND"]),
            ("incomplete",["/usr/sbin/httpd -DFOREGROUND"]),
        ]:
            with self.subTest(status=status,lines=lines):
                evidence=fixtures_for(original,lines=lines,status=status)
                a=evaluate_source_variable_plan(plan_source_variables(original),evidence)
                c=evaluate_source_variable_plan(plan_source_variables(after),evidence)
                self.assertEqual(a["variable_values"],c["variable_values"])
                self.assertEqual(a["trace"],c["trace"])
                self.assertEqual(a["nodes_evaluated"],19)
                self.assertFalse(c["original_source_parity_verified"])

    def test_edits_that_would_change_a_source_fail_closed(self):
        doc=apache(APACHE_SIMPLE)
        view=present_c_variable_steps(doc)
        mutate=deepcopy(view)
        mutate["steps"][0]["derive"]={"constant":{"datatype":"string","value":"/bin/false"}}
        with self.assertRaisesRegex(ValueError,"cannot claim lossless"):
            compile_c_variable_steps(mutate,doc)
        mutate=deepcopy(view)
        mutate["steps"][1]["derive"]={"combine":[{"use":"missing_alias"},{"constant":{"datatype":"string","value":" -V"}}]}
        with self.assertRaisesRegex(ValueError,"unresolved C Variable alias"):
            compile_c_variable_steps(mutate,doc)
        mutate=deepcopy(view)
        mutate["steps"][1]["name"]=mutate["steps"][0]["name"]
        with self.assertRaisesRegex(ValueError,"non-bijective"):
            compile_c_variable_steps(mutate,doc)
        mutate=deepcopy(view)
        mutate["source_variables_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"cannot claim lossless"):
            compile_c_variable_steps(mutate,doc)

    def test_acquisition_mutations_and_lost_source_nodes_are_detected(self):
        doc=apache(APACHE_COMPLEX)
        view=present_c_variable_steps(doc)
        missing=deepcopy(view)
        missing["steps"].pop()
        with self.assertRaisesRegex(ValueError,"loss or duplication"):
            compile_c_variable_steps(missing,doc)
        modified=deepcopy(doc)
        modified["shared_objects"]["gather-unique-apache-http-installation-paths-object"][
            "collect"]["pattern"]=".*"
        with self.assertRaisesRegex(ValueError,"dependency graph changed"):
            compile_c_variable_steps(view,modified)
        with self.assertRaisesRegex(ValueError,"unresolved"):
            bad=deepcopy(doc)
            first=next(iter(bad["variables"]))
            bad["variables"][first]["expression"]={"variable":"missing-variable"}
            present_c_variable_steps(bad)


if __name__=="__main__":
    unittest.main()
