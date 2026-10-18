#!/usr/bin/env python3
"""#237 regression: source Windows 11 WDigest type=DWORD AND value=0 same Item."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN,ERROR
from research_b_compiled_ir import encode,decode,evaluate_json
from research_b_source_registry_lowering import lower_source_registry_assessment
from research_b_source_registry_snapshot import normalize,PROVIDER

SOURCE=(Path(__file__).resolve().parents[1]/
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/windows-registry-state-all-0fef40d33c90.source.yaml")


class RegistryAndSourceTests(unittest.TestCase):
    def setUp(self):
        self.doc=yaml.safe_load(SOURCE.read_text())
        self.ast=lower_source_registry_assessment(self.doc)
        self.payload=encode(self.doc["assessment"]["id"],self.ast)

    def evidence(self, records, *, status="complete", different_views=None):
        if different_views is None:different_views={}
        views={}
        for view in ("32bit","64bit"):
            using={**self.ast["using"],"view":view}
            raw=different_views.get(view,records)
            query={"query":using,"status":status,"records":[
                {"value_kind":kind,"raw_value":value} for kind,value in raw]}
            views[view]=normalize(query,**using)
        return {PROVIDER:{"views":views}}

    def verdict(self,records,**kwargs):
        return evaluate_json(self.payload,self.evidence(records,**kwargs)).result

    def test_real_wdigest_source_and_same_item_field_identity(self):
        self.assertEqual(self.doc["assessment"]["id"],"SV-253358.automated")
        ir=decode(self.payload)
        self.assertEqual(ir["source_kind"],"compiler-compatibility")
        self.assertEqual(ir["root"]["source_test_id"],"wdigest-authentication-disabled-test")
        fields=ir["root"]["state"]["all"]
        self.assertEqual({f["field"] for f in fields},{"type","value"})
        self.assertEqual({f["expected"] for f in fields},{"dword",0})
        self.assertEqual(ir["root"]["check"],"all")
        self.assertEqual(ir["root"]["source_view"],"unspecified_requires_xml_parity")

    def test_type_and_value_must_both_match_on_each_collected_item(self):
        self.assertEqual(self.verdict([("REG_DWORD",0)]),TRUE)
        self.assertEqual(self.verdict([("REG_DWORD",1)]),FALSE)
        self.assertEqual(self.verdict([("REG_SZ","0")]),FALSE)
        self.assertEqual(self.verdict([("REG_QWORD",0)]),FALSE)
        self.assertEqual(self.verdict([]),FALSE)
        # Two individually failing Items cannot combine to form a compliant
        # typed value by borrowing the type from a different record.
        self.assertEqual(self.verdict([("REG_DWORD",1),("REG_SZ","0")]),FALSE)
        self.assertEqual(self.verdict([("REG_DWORD",0),("REG_SZ","0")]),FALSE)
        self.assertEqual(self.verdict([("REG_DWORD",0),("REG_DWORD",0)]),TRUE)

    def test_incomplete_and_conflicting_views_do_not_claim_complete_success(self):
        self.assertEqual(self.verdict([("REG_DWORD",0)],status="incomplete"),UNKNOWN)
        self.assertEqual(self.verdict([("REG_DWORD",1)],status="incomplete"),FALSE)
        self.assertEqual(self.verdict([],status="incomplete"),UNKNOWN)
        self.assertEqual(self.verdict([],different_views={
            "32bit":[("REG_DWORD",0)],
            "64bit":[("REG_DWORD",1)],
        }),UNKNOWN)

    def test_compound_state_rejects_extra_unknown_required_fields(self):
        for mutate in (
            lambda d: d["states"][0]["all"].append({
                "field":"expanded_value","operation":"equals",
                "existence":"one_or_more","match":"all","value":"0"}),
            lambda d: d["states"][0]["all"][0].update(operation="not_equals"),
            lambda d: d["states"][0]["all"][1].update(value="0"),
            lambda d: d["states"][0]["all"][0].update(field="value"),
        ):
            with self.subTest(transform=mutate):
                altered=copy.deepcopy(self.doc)
                test=next(iter(altered["assessment"]["tests"].values()))
                mutate(test)
                if test["states"][0]["all"][1]["value"]=="0":
                    # Lexically distinct but still schema-valid: it is a
                    # different comparison and remains typed text on decode.
                    lowered=lower_source_registry_assessment(altered)
                    self.assertIs(type(lowered["state"]["all"][1]["expected"]),str)
                else:
                    with self.assertRaises(ValueError):
                        lower_source_registry_assessment(altered)

    def test_ir_validation_refuses_split_item_bypass(self):
        broken=copy.deepcopy(self.ast)
        broken["state"]["all"][0]["field"]="unknown"
        with self.assertRaises(ValueError):
            encode("forged-registry-type",broken)
        broken=copy.deepcopy(self.ast)
        broken["state"]["all"].append(copy.deepcopy(broken["state"]["all"][0]))
        with self.assertRaises(ValueError):
            encode("forged-registry-matching",broken)


if __name__=="__main__":
    unittest.main()
