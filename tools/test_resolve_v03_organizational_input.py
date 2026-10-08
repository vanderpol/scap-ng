import copy
import unittest
from resolve_v03_organizational_input import (
    InputResolutionError, bind_assessment_inputs, resolve_input_sets,
)


def fixtures():
    benchmark={"id":"b","version":{"value":"V1"},
               "parameters":[{"id":"approved_fs","resolution":"organization",
                   "datatype":"string","cardinality":"one_or_more",
                   "required":True,"constraints":{"min_items":1,"unique_items":True}}]}
    src={"organizational_input":{"id":"site","version":1,
         "benchmark":{"id":"b","version":"V1"},
         "values":{"approved_fs":["ext4","xfs"]},
         "effective_from":"2026-10-01T00:00:00-04:00",
         "expires_at":None,
         "provenance":{"authorization_status":"approved","supplied_by":"staff"}}}
    rule={"assessment_choices":{"automated":{
        "assessment":"a","inputs":{"approved-types-input":{"parameter":"approved_fs"}}}}}
    assessment={"id":"a","inputs":{"approved-types-input":{
        "required":True,"datatype":"string","cardinality":"one_or_more"}}}
    return benchmark,src,rule,assessment


class ResolutionTests(unittest.TestCase):
    RUN="2026-10-08T11:00:00-04:00"

    def test_frozen_authorized_values_and_metadata(self):
        b,s,r,a=fixtures()
        result=resolve_input_sets(b,[s],run_start=self.RUN)
        self.assertEqual(result["readiness"]["outcome"],"ready")
        self.assertEqual(result["effective_values"]["approved_fs"],["ext4","xfs"])
        projected=bind_assessment_inputs(r,"automated",a,result)
        self.assertEqual(projected["bindings"]["approved-types-input"],["ext4","xfs"])
        s["organizational_input"]["values"]["approved_fs"].append("changed")
        self.assertEqual(result["effective_values"]["approved_fs"],["ext4","xfs"])
        self.assertEqual(result["value_provenance"]["approved_fs"]["input_set_id"],"site")

    def test_missing_and_expired_do_not_create_pass_or_fail(self):
        b,s,r,a=fixtures()
        for sources,reason in (
            ([],"missing_organizational_input"),
            ([dict(organizational_input={**s["organizational_input"],
                  "expires_at":"2026-10-02T00:00:00-04:00"})],
             "expired_or_not_yet_effective_input")):
            with self.subTest(reason=reason):
                context=resolve_input_sets(b,sources,run_start=self.RUN)
                self.assertEqual(context["readiness"]["outcome"],"not_evaluated")
                self.assertEqual(context["readiness"]["unresolved_parameters"][0]["code"],reason)
                self.assertEqual(bind_assessment_inputs(r,"automated",a,context)["outcome"],
                                 "not_evaluated")

    def test_invalid_bindings_fail_closed(self):
        mutations=[
            lambda b,s:s["organizational_input"]["benchmark"].update({"id":"other"}),
            lambda b,s:s["organizational_input"]["provenance"].update(
                {"authorization_status":"draft"}),
            lambda b,s:s["organizational_input"]["values"].update({"approved_fs":["ext4","ext4"]}),
            lambda b,s:s["organizational_input"]["values"].update({"approved_fs":[]}),
            lambda b,s:s["organizational_input"]["values"].update({"approved_fs":[1]}),
            lambda b,s:b["parameters"][0].update({"resolution":"publisher"}),
            lambda b,s:s["organizational_input"]["values"].update({"unrecognized":["xfs"]}),
        ]
        for i,mutate in enumerate(mutations):
            b,s,*_=copy.deepcopy(fixtures())
            mutate(b,s)
            with self.subTest(case=i),self.assertRaises(InputResolutionError):
                resolve_input_sets(b,[s],run_start=self.RUN)

    def test_no_implicit_binding_or_precedence(self):
        b,s,*_=fixtures()
        with self.assertRaisesRegex(InputResolutionError,"ambiguous_input"):
            resolve_input_sets(b,[s,copy.deepcopy(s)],run_start=self.RUN)
        with self.assertRaisesRegex(InputResolutionError,"implicit_input_selection"):
            resolve_input_sets(b,s,run_start=self.RUN)
        with self.assertRaisesRegex(InputResolutionError,"invalid_time"):
            resolve_input_sets(b,[s],run_start="2026-10-08T11:00:00")

    def test_optional_unbound_input_is_not_fabricated(self):
        b,s,r,a=fixtures()
        a["inputs"]["optional-input"]={
            "required":False,"datatype":"string","cardinality":"zero_or_one"}
        context=resolve_input_sets(b,[s],run_start=self.RUN)
        result=bind_assessment_inputs(r,"automated",a,context)
        self.assertNotIn("optional-input",result["bindings"])
        self.assertEqual(result["outcome"],"ready")

    def test_non_finite_numeric_input_is_rejected(self):
        b,s,r,a=fixtures()
        b["parameters"][0]["datatype"]="float"
        s["organizational_input"]["values"]["approved_fs"]=[float("nan")]
        with self.assertRaisesRegex(InputResolutionError,"invalid_datatype"):
            resolve_input_sets(b,[s],run_start=self.RUN)

    def test_unknown_choice_does_not_inject_bindings(self):
        b,s,r,a=fixtures()
        context=resolve_input_sets(b,[s],run_start=self.RUN)
        with self.assertRaisesRegex(InputResolutionError,"invalid_assessment_choice"):
            bind_assessment_inputs(r,"manual",a,context)


if __name__=="__main__":
    unittest.main()
