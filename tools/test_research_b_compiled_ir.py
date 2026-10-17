#!/usr/bin/env python3
"""#235: single B compiled fixture JSON contract, not SCAP 1.4 scanner parity."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from oval_result_truth_tables import (TRUE, FALSE, ERROR, UNKNOWN,
                                      NOT_EVALUATED, NOT_APPLICABLE)
from research_b_compiled_ir import decode, encode, evaluate_json, FORMAT, SCOPE
from research_native_contract_candidate import EXAMPLES, read

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SOURCE = (ROOT / "research/requirements-first-language/"
                   "contract-candidate/corpus/source-specimens/"
                   "windows-registry-0-de183f784659.source.yaml")


def mount_evidence(*values, status="complete"):
    return {"linux.mounts": {
        "status":status, "items":[
            {"id":f"m{i}","fields":{"mount_point":"/home",
                                     "mount_options":x}}
            for i,x in enumerate(values)
        ]}}


def source_test(*results, flag="complete"):
    return {"kind":"compat_oval_test",
            "source_test_id":"bluetooth-radio-turned-off-test",
            "test":{"flag":flag,
                    "existence":"at_least_one_exists",
                    "check":"only one",
                    "has_state":True,
                    "exists":len(results),
                    "item_results":list(results)}}


class CompiledFixtureIRTests(unittest.TestCase):
    def test_all_native_examples_have_same_typed_ast_after_json_roundtrip(self):
        paths=sorted(EXAMPLES.glob("*.yaml"))
        self.assertGreaterEqual(len(paths),10)
        for p in paths:
            with self.subTest(p=p.name):
                c=read(p)
                raw=encode(c["id"], c["ast"])
                decoded=decode(raw)
                self.assertEqual(decoded["format"],FORMAT)
                self.assertEqual(decoded["scope"],SCOPE)
                self.assertEqual(decoded["source_kind"],"native")
                self.assertEqual(decoded["root"],c["ast"])
                self.assertEqual(raw,encode(c["id"],decoded["root"]))
                self.assertNotIn(b"source_test_id",raw)

    def test_required_home_pass_fail_unknown_same_pre_and_post_serialization(self):
        c=read(EXAMPLES/"01-required-home.yaml")
        raw=encode(c["id"],c["ast"])
        from research_native_contract_evaluator import evaluate
        cases=((mount_evidence(["rw","nosuid"]),TRUE),
               (mount_evidence(["rw"]),FALSE),
               (mount_evidence(),FALSE),
               (mount_evidence(status="incomplete"),UNKNOWN))
        for fixtures,expected in cases:
            with self.subTest(expected=expected,fixtures=fixtures):
                self.assertEqual(evaluate_json(raw,fixtures).result,expected)
                self.assertEqual(evaluate_json(raw,fixtures).result,
                                 evaluate(c["ast"],fixtures).result)

    def test_real_w11_registry_source_requires_separate_match_one_semantics(self):
        original=yaml.safe_load(REGISTRY_SOURCE.read_text())["assessment"]
        test=original["tests"]["bluetooth-radio-turned-off-test"]
        self.assertEqual((test["existence"],test["match"]),("one_or_more","one"))
        self.assertEqual(test["states"][0]["value"],"0")
        self.assertIs(type(test["states"][0]["value"]),str)
        self.assertNotIn("view",test["object"]["select"])

        # OVAL reference combiners: a source Test check of "only one"
        # matching Item can be TRUE when two Items exist but only one matches.
        # This is a PRE-EVALUATED TEST bridge; source Item/State lowering
        # is NOT implemented and the source's 'one' mapping still needs raw XML.
        compatible=source_test(TRUE,FALSE)
        compiled=encode(original["id"],compatible)
        self.assertEqual(decode(compiled)["source_kind"],"compiler-compatibility")
        self.assertEqual(evaluate_json(compiled,{}).result,TRUE)
        self.assertEqual(evaluate_json(
            encode(original["id"],source_test(TRUE,TRUE)),{}).result,FALSE)

        # A native B named singleton is *not* equivalent: duplicate records
        # violate provider identity instead of choosing one matching State.
        native=read(EXAMPLES/"03-named-registry.yaml")
        fixtures={"windows.registry_value":{
            "using":native["ast"]["using"],"status":"complete",
            "items":[{"id":"reg-a","fields":{"value":0}},
                     {"id":"reg-b","fields":{"value":1}}]}}
        self.assertEqual(evaluate_json(
            encode(native["id"],native["ast"]),fixtures).result,ERROR)

    def test_all_six_outcomes_can_cross_compiled_reference_boundary(self):
        scenarios=[
            (source_test(TRUE),TRUE),
            (source_test(FALSE),FALSE),
            (source_test(ERROR),ERROR),
            (source_test(UNKNOWN),UNKNOWN),
            (source_test(NOT_EVALUATED),NOT_EVALUATED),
            (source_test(flag="not applicable"),NOT_APPLICABLE),
        ]
        for node,expected in scenarios:
            with self.subTest(expected=expected):
                self.assertEqual(evaluate_json(
                    encode("source-compatibility",node),{}).result,expected)

    def test_mixed_compiler_ir_keeps_native_and_compatibility_outcomes_distinct(self):
        native=read(EXAMPLES/"01-required-home.yaml")["ast"]
        root={"kind":"logic","operator":"any",
              "children":[native,source_test(flag="error")]}
        payload=encode("mixed-fixture",root)
        self.assertEqual(decode(payload)["source_kind"],"mixed")
        self.assertEqual(evaluate_json(
            payload,mount_evidence(["nosuid"])).result,TRUE)
        self.assertEqual(evaluate_json(
            payload,mount_evidence(["rw"])).result,ERROR)

    def test_json_version_digest_and_shape_fail_closed(self):
        native=read(EXAMPLES/"01-required-home.yaml")
        raw=encode(native["id"],native["ast"])
        good=json.loads(raw)
        modifications=(
            {"format":"scap-ng-b-fixture-ir/9"},
            {"scope":"production-scanner-ready"},
            {"catalog_version":"fake"},
            {"source_kind":"compiler-compatibility"},
            {"assessment_id":"rewritten-id"},
            {"extra":"unexpected"},
        )
        for change in modifications:
            d=dict(good,**change)
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    decode(json.dumps(d).encode())
        tampered=copy.deepcopy(good)
        tampered["root"]["mode"]="invented"
        with self.assertRaises(ValueError):
            decode(json.dumps(tampered).encode())
        with self.assertRaises(ValueError):
            decode(b'{"format":NaN}')
        with self.assertRaises(ValueError):
            decode(b"not JSON")

    def test_recomputed_hash_cannot_authorize_unrecognized_operation(self):
        native=read(EXAMPLES/"01-required-home.yaml")
        tampered=json.loads(encode(native["id"],native["ast"]))
        tampered["root"]["predicates"][0]["operator"]="does_all_the_things"
        supplied=tampered.pop("payload_sha256")
        tampered["payload_sha256"]=hashlib.sha256(json.dumps(
            tampered,sort_keys=True,separators=(",",":"),ensure_ascii=False,
            allow_nan=False).encode()).hexdigest()
        self.assertNotEqual(tampered["payload_sha256"],supplied)
        with self.assertRaisesRegex(ValueError,"unknown predicate operation"):
            decode(json.dumps(tampered).encode())

    def test_compiler_only_oval_nodes_not_native_authorable(self):
        with self.assertRaisesRegex(ValueError,"cannot be native authored"):
            from research_b_compiled_ir import _node
            _node(source_test(TRUE),"native")
        with self.assertRaises(ValueError):
            encode("bad-test",{"kind":"compat_oval_test",
                                "source_test_id":"x","test":{"flag":"complete",
                                                             "check":"mystery",
                                                             "existence":"all_exist",
                                                             "exists":1}})
        with self.assertRaises(ValueError):
            encode("bad-unknown",{"kind":"opaque_vendor_custom"})

if __name__=="__main__":
    unittest.main()
