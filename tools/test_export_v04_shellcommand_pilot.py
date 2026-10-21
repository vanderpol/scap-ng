#!/usr/bin/env python3
"""Strict 0.4.0 shellcommand pilot export and source Filter boundary tests."""
import copy
import unittest
from export_v04_oval_shellcommand_pilot import emit, IND, OD
from oval_result_truth_tables import apply_filter_state_result, evaluate_collected_object_test


def native():
    return {"assessment":{
        "id":"condition.bluetooth-installation.assessment",
        "version":18,"assessment_title":"Bluetooth Installation",
        "mode":"automated","class":"inventory","purpose":"applicability",
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.4.0"},
        "tests":{"bluetooth-test":{
            "test_title":"Report true if bluetooth installed",
            "capability":"independent.shellcommand",
            "object":{"object_title":"Run command: Bluetooth",
                "shell":"powershell","command":"(Get-PnpDevice -class bluetooth -status OK).class",
                "error_if_exit_status_not_0":False,"error_if_stderr_exists":False,
                "filters":[{"include":{"stdout_line":{
                    "require":"at_least_one_exists_and_all_match",
                    "case_insensitive_equals":"Bluetooth"}}}]},
            "reported_elements":"all","require":{"items":"one_or_more"}}},
        "evaluate":{"test":"bluetooth-test"}}}


class PilotExporterTests(unittest.TestCase):
    def test_independent_xml_export_does_not_need_any_original_xml(self):
        tree,ident=emit(native())
        root=tree.getroot()
        self.assertEqual(ident,"oval:scap-ng.v04.pilot:def:1")
        tests=list(root.iter("{"+IND+"}shellcommand_test"))
        self.assertEqual(len(tests),1)
        self.assertEqual(tests[0].get("comment"),"Report true if bluetooth installed")
        self.assertEqual(tests[0].get("check_existence"),"at_least_one_exists")
        objects=list(root.iter("{"+IND+"}shellcommand_object"))
        self.assertEqual(len(objects),1)
        self.assertEqual(list(objects[0].iter("{"+OD+"}set")),[])
        filters=list(objects[0].iter("{"+OD+"}filter"))
        self.assertEqual(len(filters),1)
        self.assertEqual(filters[0].get("action"),"include")
        self.assertEqual(list(root.iter("{"+IND+"}stdout_line"))[0].get("operation"),
                         "case insensitive equals")

    def test_unsupported_filter_and_collector_variants_are_hard_errors(self):
        for mutant in (
            lambda d:d["assessment"]["tests"]["bluetooth-test"]["object"]["filters"][0].update(exclude=d["assessment"]["tests"]["bluetooth-test"]["object"]["filters"][0].pop("include")),
            lambda d:d["assessment"]["tests"]["bluetooth-test"]["object"].update(set={"operator":"union","operands":[]}),
            lambda d:d["assessment"]["tests"]["bluetooth-test"]["object"].update(collect={"shell":"powershell"}),
            lambda d:d["assessment"]["tests"]["bluetooth-test"]["object"].update(error_if_stderr_exists=True),
            lambda d:d["assessment"]["tests"]["bluetooth-test"].update(require={"items":"exactly_one"}),
            lambda d:d["assessment"]["tests"]["bluetooth-test"].update(test_title=""),
            lambda d:d["assessment"].update(evaluate={"all":[{"test":"bluetooth-test"}]}),
            lambda d:d["assessment"]["specification"].update(version="0.3.0"),
        ):
            d=native()
            with self.subTest(mutant=str(mutant)):
                mutant(d)
                with self.assertRaises(ValueError):
                    emit(d)

    def test_include_filter_six_state_reference_contract(self):
        # Reference model, NOT actual scanner execution.
        expected={
            "true":True,"false":False,
            "error":"error","unknown":"error",
            "not evaluated":"error","not applicable":"error",
        }
        for state,result in expected.items():
            with self.subTest(state=state):
                self.assertEqual(apply_filter_state_result("include",state),result)
        # Non-Boolean Filter state outcomes MUST NOT silently turn into
        # empty, passing collections. Actual collector flags are a separate
        # implementation requirement.
        self.assertEqual(evaluate_collected_object_test(
            "complete", existence="at_least_one_exists",has_state=False,
            exists=0),"false")
        self.assertEqual(evaluate_collected_object_test(
            "complete", existence="at_least_one_exists",has_state=False,
            exists=1),"true")
        self.assertEqual(evaluate_collected_object_test(
            "does not exist",existence="at_least_one_exists",has_state=False),"false")
        self.assertEqual(evaluate_collected_object_test(
            "error",existence="at_least_one_exists",has_state=False),"error")
        self.assertEqual(evaluate_collected_object_test(
            "not collected",existence="at_least_one_exists",has_state=False),"unknown")


if __name__=="__main__":
    unittest.main()
