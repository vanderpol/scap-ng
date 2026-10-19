#!/usr/bin/env python3
"""Refs #245: independently authored C value steps compile to pinned Apache A graph.

Graph identity and B fixture outcomes are separate gates; neither demonstrates
original OVAL runtime or deployed scanner parity.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_derived_values_compiler import compile_c_derived_values
from research_c_shared_engine import present_c_variable_steps
from research_b_variable_schedule import plan_source_variables
from research_b_variable_plan_evaluator import evaluate_source_variable_plan
from research_b_source_shell_snapshot import normalize, PROVIDER
from v04_a_dataflow_index import index_assessment_dataflow

ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/"research/requirements-first-language/contract-candidate/corpus/source-specimens"
SMALL=SOURCES/"independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml"
FULL=SOURCES/"independent-shellcommand-1-3d964d126ca8.source.yaml"
CFILE=ROOT/"research/assessment-simplification/compact-authoring-04/c-derived-apache-version.research.yaml"

def authored():
    return yaml.safe_load(CFILE.read_text(encoding="utf-8"))

def source(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))["assessment"]

def evidence(doc, lines=(), status="complete"):
    collect=doc["variables"]["apache-path-httpd-or-apache2-variable"][
        "expression"]["regex_capture"]["value"]["values"]["object"]["collect"]
    using={k:collect[k] for k in (
        "command","shell","error_if_exit_status_not_0","error_if_stderr_exists")}
    snapshot=normalize({"query":using,"status":status,"records":[
        {"stdout_line":list(lines),"stderr_line":[],"exit_status":0}]},**using)
    return {PROVIDER:{"acquisitions":[snapshot]}}

class DerivedValuesCompilerTests(unittest.TestCase):
    def test_manually_authored_two_step_without_source_document(self):
        document=authored()
        before=deepcopy(document)
        compiled=compile_c_derived_values(document)
        self.assertEqual(document,before)
        self.assertEqual(len(compiled["variables"]),2)
        self.assertEqual(compiled["variables"]["command-gather-apache-version-variable"][
            "expression"],{"concat":[
                {"variable":"apache-path-httpd-or-apache2-variable"},
                {"literal":{"datatype":"string","value":" -V"}}]})
        self.assertFalse(compiled["collector_executed"])
        self.assertFalse(compiled["native_c_language_accepted"])
        self.assertFalse(compiled["oval_execution_parity_proven"])

    def test_real_apache_small_exact_source_variable_graph(self):
        src=source(SMALL)
        compiled=compile_c_derived_values(authored())
        self.assertEqual(compiled["variables"],src["variables"])
        self.assertEqual(compiled["shared_objects"],src.get("shared_objects",{}))

    def test_real_apache_nineteen_step_lowering_without_original_variable_input(self):
        src=source(FULL)
        self.assertEqual(len(src["variables"]),19)
        view=present_c_variable_steps(src)
        doc={"assessment_id":src["id"],
             "shared_objects":deepcopy(src["shared_objects"]),
             "steps":deepcopy(view["steps"]),
             "expected_source_variables_sha256":view["source_variables_sha256"]}
        src_copy=deepcopy(src)
        compiled=compile_c_derived_values(doc)
        self.assertEqual(src,src_copy)
        self.assertEqual(compiled["variables"],src["variables"])
        self.assertTrue(compiled["original_source_reconstructed_if_pinned"])
        self.assertEqual(len(compiled["dependency_first_source_order"]),20)
        rebuilt=deepcopy(src)
        rebuilt["variables"]=compiled["variables"]
        self.assertEqual(index_assessment_dataflow(rebuilt),index_assessment_dataflow(src))

    def test_hand_written_two_step_values_match_independent_expected(self):
        src=source(SMALL)
        clone=deepcopy(src)
        clone["variables"]=compile_c_derived_values(authored())["variables"]
        for lines, expected in [
            (["/usr/sbin/httpd -DFOREGROUND"],["/usr/sbin/httpd -V"]),
            (["/usr/sbin/apache2 -DFOREGROUND"],["/usr/sbin/apache2 -V"]),
            (["/usr/sbin/httpd -DFOREGROUND","/opt/httpd -DFOREGROUND"],
             ["/usr/sbin/httpd -V","/opt/httpd -V"]),
        ]:
            with self.subTest(lines=lines):
                snapshot=evidence(src,lines=lines)
                observed=evaluate_source_variable_plan(
                    plan_source_variables(clone),snapshot)["variable_values"]
                original=evaluate_source_variable_plan(
                    plan_source_variables(src),snapshot)["variable_values"]
                self.assertEqual(observed,original)
                self.assertEqual(observed["command-gather-apache-version-variable"],
                                 {"status":"values","values":expected})

    def test_unavailable_partial_and_empty_never_become_values(self):
        src=source(SMALL)
        clone=deepcopy(src)
        clone["variables"]=compile_c_derived_values(authored())["variables"]
        for snap,expected in (
            ({}, "unknown"),
            (evidence(src,lines=["/usr/sbin/httpd -DFOREGROUND"],status="incomplete"),"unknown"),
            (evidence(src,lines=[],status="complete"),"error"),
            (evidence(src,lines=["not an Apache process"]), "error"),
        ):
            with self.subTest(expected=expected):
                got=evaluate_source_variable_plan(
                    plan_source_variables(clone),snap)["variable_values"]
                self.assertEqual(got["command-gather-apache-version-variable"]["status"],
                                 expected)

    def test_forward_references_and_duplicate_source_ids(self):
        doc=authored()
        doc["steps"].reverse()
        self.assertEqual(len(compile_c_derived_values(doc)["variables"]),2)
        doc["steps"][1]["source_id"]=doc["steps"][0]["source_id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            compile_c_derived_values(doc)

    def test_cycle_and_unresolved_source_fail_closed(self):
        doc=authored()
        doc["steps"][0]["derive"]={"use":"apache_version_command"}
        with self.assertRaisesRegex(ValueError,"cyclic"):
            compile_c_derived_values(doc)
        doc=authored()
        doc["steps"][1]["derive"]["combine"][0]["use"]="nonexistent"
        with self.assertRaisesRegex(ValueError,"unknown"):
            compile_c_derived_values(doc)

    def test_source_pin_and_bad_private_acquisition_fail_closed(self):
        doc=authored()
        doc["expected_source_variables_sha256"]=compile_c_derived_values(doc)[
            "source_variables_sha256"]
        self.assertTrue(compile_c_derived_values(doc)["original_source_reconstructed_if_pinned"])
        changed=deepcopy(doc)
        changed["steps"][0]["derive"]["extract"]["pattern"]="different"
        with self.assertRaisesRegex(ValueError,"pinned source"):
            compile_c_derived_values(changed)
        changed=deepcopy(doc)
        obj=changed["steps"][0]["derive"]["extract"]["value"]["read_field"]["object"]
        obj["filters"]=[{"exclude":{"type":{"equals":"directory"}}}]
        with self.assertRaisesRegex(ValueError,"complex private Object"):
            compile_c_derived_values(changed)

    def test_no_hidden_types_ops_or_titles(self):
        for change in ("type","title","operator","extra","missing_id"):
            d=authored()
            step=d["steps"][0]
            if change=="type":step["datatype"]="integer"
            if change=="title":step["title"]=""
            if change=="operator":step["derive"]={"guess_paths":"shell"}
            if change=="extra":step["extra_semantics"]=True
            if change=="missing_id":step.pop("source_id")
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    compile_c_derived_values(d)

if __name__=="__main__":
    unittest.main()
