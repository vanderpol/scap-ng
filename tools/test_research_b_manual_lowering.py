#!/usr/bin/env python3
"""#237: Manual B procedure compilation and provenance-backed human response."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_manual_lowering import lower_manual_assessment
from research_b_compiled_ir import encode,decode,evaluate_json
from research_b_manual_response import complete_manual_response
from oval_result_truth_tables import TRUE,FALSE,NOT_APPLICABLE,NOT_EVALUATED


def manual_doc(response=None):
    return {"assessment":{
        "id":"SV-257777.manual","version":1,
        "assessment_title":None,"mode":"manual","class":"compliance",
        "purpose":"assessment",
        "procedure":"Review the package version. If obsolete, this is a finding.",
        "response":response}}


def answer(kind="pass"):
    return {"assessment_id":"SV-257777.manual",
            "assessment_version":1,"execution_id":"run-01",
            "answer":kind,"completed_at":"2026-10-17T16:11:00-04:00",
            "evaluator":{"scheme":"directory","value":"example-auditor"},
            "response_source":"direct","comment":None,"evidence":[]}


class ManualBTests(unittest.TestCase):
    def setUp(self):
        self.ast=lower_manual_assessment(manual_doc())
        self.compiled=encode("SV-257777.manual",self.ast)

    def test_includes_unmodified_publisher_check_and_no_automatic_finding(self):
        decoded=decode(self.compiled)
        self.assertEqual(decoded["source_kind"],"manual")
        self.assertIn("If obsolete, this is a finding",decoded["root"]["procedure"])
        self.assertEqual(evaluate_json(self.compiled,{}).result,NOT_EVALUATED)

    def test_human_completed_outcome_and_identity_retained(self):
        for response,outcome in [("pass",TRUE),("fail",FALSE),
                                 ("not_applicable",NOT_APPLICABLE)]:
            with self.subTest(response=response):
                result=complete_manual_response(self.compiled,answer(response))
                self.assertEqual(result["technical_result"],outcome)
                self.assertEqual(result["evaluator"]["scheme"],"directory")
                self.assertEqual(result["execution_id"],"run-01")
                self.assertTrue(result["source_procedure_preserved"])

    def test_missing_authentication_timestamp_or_wrong_assessment_rejected(self):
        broken=[
            {"assessment_id":"other"},
            {"assessment_version":2},
            {"execution_id":""},
            {"completed_at":"2026-10-17T16:00:00"},
            {"completed_at":"not-a-time"},
            {"evaluator":{"scheme":"","value":"a"}},
            {"evaluator":{"scheme":"x","value":""}},
            {"answer":"not_evaluated"},
            {"answer":"unsupported"},
            {"response_source":"anonymous"},
            {"evidence":[{"file":"unauthorized"}]},
        ]
        for modification in broken:
            with self.subTest(bad=modification):
                with self.assertRaises(ValueError):
                    complete_manual_response(self.compiled,dict(answer(),**modification))

    def test_unrecognized_source_manual_fields_fail_closed(self):
        doc=manual_doc()
        doc["assessment"]["variables"]={"x":"y"}
        with self.assertRaisesRegex(ValueError,"unsupported"):
            lower_manual_assessment(doc)

    def test_nonempty_source_manual_input_not_discarded(self):
        doc=manual_doc()
        doc["assessment"]["inputs"]=[{"id":"need-org-policy"}]
        with self.assertRaisesRegex(ValueError,"inputs"):
            lower_manual_assessment(doc)

    def test_richer_author_defined_choices_are_not_guessed(self):
        response={"type":"publisher.yes-no",
                  "choices":[{"value":"compliant","label":"Compliant","outcome":"true"},
                             {"value":"finding","label":"Finding","outcome":"false"},
                             {"value":"skip","outcome":"not_applicable"}],
                  "allow_comment":False,"allow_evidence":False}
        ast=lower_manual_assessment(manual_doc(response))
        compiled=encode("SV-257777.manual",ast)
        self.assertEqual(complete_manual_response(
            compiled,answer("finding"))["technical_result"],FALSE)
        with self.assertRaisesRegex(ValueError,"unknown or unfinished"):
            complete_manual_response(compiled,answer("fail"))
        bad=dict(answer("compliant"),comment="not allowed")
        with self.assertRaisesRegex(ValueError,"disallows"):
            complete_manual_response(compiled,bad)
        bad=dict(answer("compliant"),evidence=[{"ref":"attached-doc"}])
        with self.assertRaisesRegex(ValueError,"disallows"):
            complete_manual_response(compiled,bad)

    def test_author_defined_choice_not_evaluated_is_not_completed_attestation(self):
        response={"type":"publisher.custom","choices":[
                  {"value":"not-yet","outcome":"not_evaluated"}],
                  "allow_comment":True,"allow_evidence":True}
        compiled=encode("SV-257777.manual",lower_manual_assessment(manual_doc(response)))
        with self.assertRaisesRegex(ValueError,"unknown or unfinished"):
            complete_manual_response(compiled,answer("not-yet"))

    def test_manual_logic_not_mixed_into_automated_or(self):
        mixed={"kind":"logic","operator":"any","children":[self.ast,self.ast]}
        with self.assertRaisesRegex(ValueError,"cannot be embedded"):
            encode("mixed-manual",mixed)

if __name__=="__main__":
    unittest.main()
