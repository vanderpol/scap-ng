#!/usr/bin/env python3
"""#237: composite converted-0.3 B tests with exact source query identity."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_source_boolean_lowering import lower_source_boolean_assessment
from research_b_compiled_ir import encode,decode,evaluate_json
from research_provider_textfile_matches import collect
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN,ERROR

ROOT=Path(__file__).resolve().parents[1]
PINNED=(ROOT/"research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/independent-textfilecontent54-0-4c14428014be.source.yaml")


def source_composite(operator="all"):
    original=yaml.safe_load(PINNED.read_text())["assessment"]
    chrony_name,chrony_test=next(iter(original["tests"].items()))
    group_test=copy.deepcopy(chrony_test)
    group_test["object"]["select"]["pattern"]["value"]=r"^[ \t]*ProcessSizeMax[ \t]*=[ \t]*(\w+)$"
    group_test["states"]=[{"field":"subexpression","operation":"equals","value":"0",
                          "existence":"one_or_more","match":"all"}]
    a={k:v for k,v in original.items() if k not in ("evaluate","tests")}
    a["id"]="research-chrony-and-process-size"
    a["tests"]={chrony_name:chrony_test,"process-size-disabled":group_test}
    a["evaluate"]={operator:[{"test":chrony_name},{"test":"process-size-disabled"}]}
    return {"assessment":a}


class MultiTestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"fixture.conf"
        self.doc=source_composite()
        self.ast=lower_source_boolean_assessment(self.doc)
        for child in self.ast["children"]:
            child["using"]["path"]=str(self.path)
        self.compiled=encode(self.doc["assessment"]["id"],self.ast)

    def observations(self,**limits):
        return {"linux.textfile_matches":{
            "acquisitions":[collect(**child["using"],**limits)
                            for child in self.ast["children"]]}}

    def result(self,observations):
        return evaluate_json(self.compiled,observations).result

    def test_both_tests_lower_to_source_owned_nodes_no_second_author_grammar(self):
        root=decode(self.compiled)["root"]
        self.assertEqual(root["kind"],"logic")
        self.assertEqual(root["operator"],"all")
        self.assertEqual(len(root["children"]),2)
        self.assertEqual({n["kind"] for n in root["children"]},
                         {"compat_oval_provider_existence","compat_oval_provider_state"})
        self.assertEqual(decode(self.compiled)["source_kind"],"compiler-compatibility")
        self.assertEqual({n["source_test_id"] for n in root["children"]},
            {"etc-chrony-conf-cmdport-option-set-0-test","process-size-disabled"})

    def test_typed_distinct_acquisitions_are_both_required(self):
        self.path.write_text("cmdport 0\nProcessSizeMax=0\n")
        self.assertEqual(self.result(self.observations()),TRUE)
        self.path.write_text("cmdport 0\nProcessSizeMax=1\n")
        self.assertEqual(self.result(self.observations()),FALSE)
        self.path.write_text("cmdport 1\nProcessSizeMax=0\n")
        self.assertEqual(self.result(self.observations()),FALSE)

    def test_and_preserves_unknown_if_required_query_missing(self):
        self.path.write_text("cmdport 0\nProcessSizeMax=0\n")
        fixtures=self.observations()
        fixtures["linux.textfile_matches"]["acquisitions"].pop()
        self.assertEqual(self.result(fixtures),UNKNOWN)

    def test_duplicate_acquisition_identity_is_error_not_arbitrary_first_wins(self):
        self.path.write_text("cmdport 0\nProcessSizeMax=0\n")
        fixtures=self.observations()
        fixtures["linux.textfile_matches"]["acquisitions"].append(
            copy.deepcopy(fixtures["linux.textfile_matches"]["acquisitions"][0]))
        self.assertEqual(self.result(fixtures),ERROR)

    def test_or_one_witness_overrides_second_branch_unknown(self):
        source=source_composite("any")
        ast=lower_source_boolean_assessment(source)
        for child in ast["children"]:
            child["using"]["path"]=str(self.path)
        compiled=encode(source["assessment"]["id"],ast)
        self.path.write_text("cmdport 0\n")
        evidence={"linux.textfile_matches":{
            "acquisitions":[collect(**ast["children"][0]["using"])]}}
        self.assertEqual(evaluate_json(compiled,evidence).result,TRUE)

    def test_nested_logic_and_all_source_tests_required(self):
        doc=source_composite()
        a=doc["assessment"]
        old=a["evaluate"]["all"]
        a["evaluate"]={"any":[{"all":old},
                             {"test":"process-size-disabled"}]}
        compiled=lower_source_boolean_assessment(doc)
        self.assertEqual(compiled["kind"],"logic")
        self.assertEqual(compiled["children"][0]["kind"],"logic")

    def test_unreachable_or_unsupported_check_cannot_be_dropped(self):
        cases=[]
        d=source_composite();d["assessment"]["evaluate"]={"test":"process-size-disabled"};cases.append(d)
        d=source_composite();d["assessment"]["evaluate"]={"all":[{"test":"process-size-disabled"},
                                                            {"test":"missing"}]};cases.append(d)
        d=source_composite()
        d["assessment"]["tests"]["process-size-disabled"]["states"][0]["field"]="unimplemented"
        cases.append(d)
        d=source_composite();d["assessment"]["evaluate"]={"not":{"test":"process-size-disabled"}};cases.append(d)
        d=source_composite();d["assessment"]["variables"]={"x":{"literal":"y"}};cases.append(d)
        d=source_composite();d["assessment"]["evaluate"]={"all":[{"test":"process-size-disabled"}]};cases.append(d)
        for d in cases:
            with self.subTest(changed=d["assessment"]["evaluate"]):
                with self.assertRaises(ValueError):
                    lower_source_boolean_assessment(d)

if __name__=="__main__":
    unittest.main()
