#!/usr/bin/env python3
"""#237: bounded linux.partition source Test lowering and real parsed mount Items."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,ERROR,UNKNOWN
from research_b_source_partition_lowering import lower_state_free_partition_assessment
from research_b_compiled_ir import encode,decode,evaluate_json
from research_provider_linux_mounts import parse_mountinfo_text
from research_native_contract_candidate import EXAMPLES,read

SOURCE=(Path(__file__).resolve().parents[1] /
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/linux-partition-0-88d5c4811f61.source.yaml")
NAMESPACE="mnt:[fixture]"
TARGET="21 1 8:10 / /var/tmp rw,nosuid - ext4 /dev/fixture rw"
OTHER="22 1 8:11 / /var rw - ext4 /dev/other rw"


class PartitionLoweringTests(unittest.TestCase):
    def setUp(self):
        self.source=yaml.safe_load(SOURCE.read_text())
        self.ast=lower_state_free_partition_assessment(self.source)
        self.compiled=encode(self.source["assessment"]["id"],self.ast)

    def verdict(self, collection):
        return evaluate_json(self.compiled,{"linux.mounts":collection}).result

    def test_source_identifiers_and_typed_selector_survive_b_compilation(self):
        decoded=decode(self.compiled)
        self.assertEqual(decoded["source_kind"],"compiler-compatibility")
        self.assertEqual(decoded["root"]["source_test_id"],"var-tmp-mounted-test")
        self.assertEqual(decoded["root"]["source_assessment_id"],"ng.shared.var-tmp-is-mounted")
        self.assertEqual(decoded["root"]["where"],{"field":"mount_point","equals":"/var/tmp"})

    def test_real_mountinfo_parsing_populates_source_test(self):
        self.assertEqual(self.verdict(parse_mountinfo_text(TARGET,NAMESPACE)),TRUE)
        self.assertEqual(self.verdict(parse_mountinfo_text(OTHER,NAMESPACE)),FALSE)
        self.assertEqual(self.verdict(parse_mountinfo_text("",NAMESPACE)),FALSE)
        self.assertEqual(self.verdict(parse_mountinfo_text(OTHER+"\n"+TARGET,NAMESPACE)),TRUE)

    def test_incomplete_source_oval_and_native_b_requirements_are_different(self):
        observed=parse_mountinfo_text(TARGET+"\nbroken mountinfo",NAMESPACE)
        self.assertEqual(observed["status"],"incomplete")
        self.assertEqual(self.verdict(observed),UNKNOWN)
        # B native exists has a witnessed matching resource; source
        # state-free Test uses the pinned generic incomplete OVAL contract.
        native=read(EXAMPLES/"09-linux-var-tmp-exists.yaml")
        self.assertEqual(evaluate_json(encode(native["id"],native["ast"]),
                         {"linux.mounts":observed}).result,TRUE)

    def test_missing_selector_or_namespace_cannot_prove_empty_population(self):
        one=parse_mountinfo_text(OTHER,NAMESPACE)
        del one["namespace"]
        self.assertEqual(self.verdict(one),ERROR)
        one=parse_mountinfo_text(OTHER,NAMESPACE)
        del one["items"][0]["fields"]["mount_point"]
        self.assertEqual(self.verdict(one),UNKNOWN)
        one=parse_mountinfo_text(TARGET,NAMESPACE)
        one["items"].append(copy.deepcopy(one["items"][0]))
        self.assertEqual(self.verdict(one),ERROR)

    def test_inaccessible_and_not_collected_preserve_source_outcome(self):
        for flag,expected in (("error",ERROR),("not collected",UNKNOWN),
                              ("incomplete",UNKNOWN)):
            with self.subTest(flag=flag):
                evidence={"provider":"linux.mounts","namespace":NAMESPACE,
                          "status":flag,"items":[]}
                self.assertEqual(self.verdict(evidence),expected)

    def test_source_set_and_foreach_extensions_rejected_not_ignored(self):
        amendments=[
            ("states",[{"field":"mount_options","operation":"equals","value":"nosuid"}]),
            ("variables",{"x":{"kind":"local"}}),
            ("for_each",{"in":"ref","item":"mount"}),
        ]
        for key,value in amendments:
            with self.subTest(key=key):
                doc=copy.deepcopy(self.source)
                t=next(iter(doc["assessment"]["tests"].values()))
                if key=="variables":
                    doc["assessment"][key]=value
                elif key=="for_each":
                    t["object"][key]=value
                else:
                    t[key]=value
                # The generic version rejects local changes to Test/Object
                # shape; Assessment-level Variables are unsupported too.
                with self.assertRaises(ValueError):
                    lower_state_free_partition_assessment(doc)

    def test_non_exact_selector_and_cardinality_fail_closed(self):
        cases=[]
        d=copy.deepcopy(self.source)
        next(iter(d["assessment"]["tests"].values()))["match"]="one"
        cases.append(d)
        d=copy.deepcopy(self.source)
        t=next(iter(d["assessment"]["tests"].values()))
        t["object"]["select"]["mount_point"]["operation"]="pattern_match"
        cases.append(d)
        d=copy.deepcopy(self.source)
        t=next(iter(d["assessment"]["tests"].values()))
        t["object"]["select"]["mount_point"]["value"]="$from_variable"
        cases.append(d)
        for d in cases:
            with self.subTest(d=d):
                with self.assertRaises(ValueError):
                    lower_state_free_partition_assessment(d)

if __name__=="__main__":
    unittest.main()
