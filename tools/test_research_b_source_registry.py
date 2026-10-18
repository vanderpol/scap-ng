#!/usr/bin/env python3
"""#237: pin source registry Item/Test/State and unresolved view boundaries."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN,ERROR,NOT_APPLICABLE
from research_b_source_registry_lowering import lower_source_registry_assessment
from research_b_source_registry_snapshot import normalize,PROVIDER
from research_b_compiled_ir import encode,decode,evaluate_json

SOURCE=(Path(__file__).resolve().parents[1]/
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/windows-registry-0-de183f784659.source.yaml")


class RegistrySourceTests(unittest.TestCase):
    def setUp(self):
        self.doc=yaml.safe_load(SOURCE.read_text())
        self.ast=lower_source_registry_assessment(self.doc)
        self.raw=encode(self.doc["assessment"]["id"],self.ast)

    def records(self,view,values=(),status="complete",source_kind="REG_SZ"):
        using={**self.ast["using"],"view":view}
        source={"query":using,"status":status,"records":[
                {"value_kind":source_kind,"raw_value":v} for v in values]}
        return normalize(source,**using)

    def verdict(self,views):
        return evaluate_json(self.raw,{PROVIDER:{"views":views}}).result

    def test_bluetooth_source_provenance_and_no_assumed_registry_view(self):
        self.assertEqual(self.doc["assessment"]["id"],"SV-253291.automated")
        ir=decode(self.raw)
        self.assertEqual(ir["source_kind"],"compiler-compatibility")
        self.assertEqual(ir["root"]["source_test_id"],"bluetooth-radio-turned-off-test")
        self.assertEqual(ir["root"]["source_view"],"unspecified_requires_xml_parity")
        self.assertEqual(ir["root"]["check"],"only one")
        self.assertEqual(ir["root"]["state"]["expected"],"0")
        self.assertIs(type(ir["root"]["state"]["expected"]),str)
        self.assertEqual(ir["root"]["using"]["hive"],"HKLM")
        self.assertEqual(ir["root"]["using"]["name"],"AllowBluetooth")

    def test_one_match_is_not_the_same_as_one_collected_item(self):
        two=[self.records(v,["0","1"]) for v in ("32bit","64bit")]
        self.assertEqual(self.verdict(dict(zip(("32bit","64bit"),two))),TRUE)
        too_many={v:self.records(v,["0","0"]) for v in ("32bit","64bit")}
        self.assertEqual(self.verdict(too_many),FALSE)
        none={v:self.records(v,[]) for v in ("32bit","64bit")}
        self.assertEqual(self.verdict(none),FALSE)

    def test_registry_views_disagree_then_result_is_unknown_not_64bit_default(self):
        self.assertEqual(self.verdict({
            "32bit":self.records("32bit",["0"]),
            "64bit":self.records("64bit",["1"])}),UNKNOWN)
        self.assertEqual(self.verdict({
            "32bit":self.records("32bit",["0"])}),UNKNOWN)

    def test_incomplete_sources_cannot_claim_a_matched_clean_state(self):
        data={v:self.records(v,["0"],"incomplete") for v in ("32bit","64bit")}
        self.assertEqual(self.verdict(data),UNKNOWN)
        complete={v:self.records(v,["0"]) for v in ("32bit","64bit")}
        self.assertEqual(self.verdict(complete),TRUE)

    def test_numeric_zero_is_not_source_lexical_string_zero(self):
        data={v:self.records(v,[0],source_kind="REG_DWORD") for v in ("32bit","64bit")}
        self.assertEqual(self.verdict(data),ERROR)
        # Conversely a source Assessment with an explicitly integer-valued
        # State can be evaluated as typed integer *only* in this pilot.
        doc=copy.deepcopy(self.doc)
        t=next(iter(doc["assessment"]["tests"].values()))
        t["states"][0]["value"]=0
        typed=lower_source_registry_assessment(doc)
        payload=encode(doc["assessment"]["id"],typed)
        self.assertEqual(evaluate_json(payload,{PROVIDER:{"views":data}}).result,TRUE)

    def test_wrong_view_identity_untrusted_types_and_duplicates_fail_closed(self):
        broken={v:self.records(v,["0"]) for v in ("32bit","64bit")}
        broken["64bit"]["using"]["view"]="32bit"
        self.assertEqual(self.verdict(broken),ERROR)
        broken={v:self.records(v,["0"]) for v in ("32bit","64bit")}
        broken["32bit"]["items"].append(copy.deepcopy(broken["32bit"]["items"][0]))
        self.assertEqual(self.verdict(broken),ERROR)
        broken={v:self.records(v,["0"]) for v in ("32bit","64bit")}
        broken["64bit"]["items"][0]["fields"]["value"]=0
        self.assertEqual(self.verdict(broken),ERROR)

    def test_terminal_statuses_and_missing_snapshot_are_not_equivalent_to_absence(self):
        for state,expected in (("error",ERROR),("not collected",UNKNOWN),
                               ("not applicable",NOT_APPLICABLE)):
            with self.subTest(state=state):
                evidence={v:self.records(v,[],state) for v in ("32bit","64bit")}
                self.assertEqual(self.verdict(evidence),expected)
        self.assertEqual(evaluate_json(self.raw,{}).result,UNKNOWN)
        broken=self.records("32bit",["0"],"error")
        self.assertEqual(broken["status"],"error")
        self.assertEqual(broken["items"],[])

    def test_source_metadata_or_dynamic_operators_fail_closed(self):
        transformations=(
            lambda d: next(iter(d["assessment"]["tests"].values()))["states"][0].update(
                operation="pattern_match"),
            lambda d: next(iter(d["assessment"]["tests"].values()))["object"]["select"].update(
                windows_view="32bit"),
            lambda d: next(iter(d["assessment"]["tests"].values()))["states"][0].update(
                value={"variable":"0"}),
            lambda d: next(iter(d["assessment"]["tests"].values()))["states"].append(
                {"field":"type","operation":"equals","value":"reg_sz"}),
            lambda d: d["assessment"].update(variables={"x":{"kind":"local"}}),
        )
        for transform in transformations:
            with self.subTest(transform=transform):
                a=copy.deepcopy(self.doc)
                transform(a)
                with self.assertRaises((ValueError,TypeError)):
                    lower_source_registry_assessment(a)

    def test_invalid_snapshot_row_does_not_prove_absence(self):
        using={**self.ast["using"],"view":"64bit"}
        for kind,value in (("REG_DWORD","0"),("REG_SZ",0),("REG_MULTI_SZ",["0"])):
            with self.subTest(kind=kind):
                blob=normalize({"query":using,"status":"complete","records":[
                    {"value_kind":kind,"raw_value":value}]},**using)
                self.assertEqual(blob["status"],"error")
                self.assertEqual(blob["items"],[])


if __name__=="__main__":
    unittest.main()
