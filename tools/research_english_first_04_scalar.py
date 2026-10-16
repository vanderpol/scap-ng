#!/usr/bin/env python3
"""One reusable English-first scalar authoring template for source-exact Tests.

Research #235: no schema promotion and no scanner proof. Keep original
acquisition and fail closed unless Test and State semantics fit this class.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile
import yaml

PIN = "03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"
ITEM_PAIR = "at_least_one_exists_and_all_match"
FIELD_PAIR = "at_least_one_exists_and_all_match"
OPERATORS = {
    "equals": "has_only_values_equal_to",
    "matches_regex": "has_only_values_matching_regex",
    "case_insensitive_equals": "has_only_values_equal_to_ignoring_case",
    "not_equal": "has_only_values_not_equal_to",
    "greater_than_or_equal": "has_only_values_at_least",
    "less_than_or_equal": "has_only_values_at_most",
    "greater_than": "has_only_values_greater_than",
    "less_than": "has_only_values_less_than",
}
INVERSE = {v: k for k, v in OPERATORS.items()}


def resolved_object(test, ass):
    obj = test.get("object")
    if isinstance(obj, str):
        obj = (ass.get("shared_objects") or {}).get(obj)
    if not isinstance(obj, dict):
        return None
    obj = deepcopy(obj)
    obj.pop("object_title", None)
    return obj


def candidate_for(test, ass):
    obj = resolved_object(test, ass)
    if obj is None:
        return None, "no_typed_object"
    if set(obj) - {"capability", "select", "collect"} or not ({"select", "collect"} & set(obj)):
        return None, "complex_object_or_set"
    if obj.get("capability") != test.get("capability"):
        return None, "capability_mismatch"
    if set(test) - {"test_title", "capability", "object", "states", "reported_elements", "collected_items_require"}:
        return None, "extra_test_state_scope_or_properties"
    if test.get("reported_elements") != "all" or test.get("collected_items_require") != ITEM_PAIR:
        return None, "item_cardinality_or_evidence_not_covered"
    if not isinstance(test.get("test_title"), str) or not test.get("test_title"):
        return None, "missing_title"
    states = test.get("states")
    if not isinstance(states, list) or len(states) != 1:
        return None, "multi_or_no_state"
    if not isinstance(states[0], dict) or len(states[0]) != 1:
        return None, "grouped_or_multi_field_state"
    field, pred = next(iter(states[0].items()))
    if not isinstance(field, str) or not isinstance(pred, dict):
        return None, "unrecognized_field"
    if pred.get("require") != FIELD_PAIR or set(pred) - {"require"} not in ({op} for op in OPERATORS):
        return None, "field_cardinality_or_operation_not_covered"
    comparator = next(iter(set(pred) - {"require"}))
    val = pred[comparator]
    if not isinstance(val, (str, int, float, bool)) or (isinstance(val, str) and not val):
        return None, "nonliteral_comparison"
    result = {
        "check": test["test_title"], "inspect": test["capability"],
        "require": {
            "at_least_one_item_exists": True,
            "every_collected_item": {field: {OPERATORS[comparator]: val}},
        },
        "report_elements": "all",
    }
    if "select" in obj:
        result["where"] = deepcopy(obj["select"])
    if "collect" in obj:
        result["collect"] = deepcopy(obj["collect"])
    return result, None


def lower(c):
    if not isinstance(c, dict):
        raise ValueError("scalar check must be a YAML map")
    valid = {"check", "inspect", "where", "collect", "require", "report_elements"}
    if set(c) - valid or not {"check", "inspect", "require", "report_elements"}.issubset(c):
        raise ValueError("unexpected or missing Test properties")
    if not ({"where", "collect"} & set(c)):
        raise ValueError("acquisition must be present")
    if not isinstance(c["check"], str) or not c["check"]:
        raise ValueError("missing title")
    if not isinstance(c["inspect"], str) or not c["inspect"]:
        raise ValueError("missing capability")
    if c["report_elements"] != "all":
        raise ValueError("source evidence not proven")
    req = c["require"]
    if not isinstance(req, dict) or set(req) != {"at_least_one_item_exists", "every_collected_item"}:
        raise ValueError("Item existence or all-matching not explicit")
    if req["at_least_one_item_exists"] is not True:
        raise ValueError("Item presence Boolean not true")
    match = req["every_collected_item"]
    if not isinstance(match, dict) or len(match) != 1:
        raise ValueError("one field expected")
    field, opmap = next(iter(match.items()))
    if not isinstance(field, str) or not field or not isinstance(opmap, dict) or len(opmap) != 1:
        raise ValueError("field predicate invalid")
    verb, val = next(iter(opmap.items()))
    if verb not in INVERSE:
        raise ValueError("unsupported field verb")
    if not isinstance(val, (str, int, float, bool)) or (isinstance(val, str) and not val):
        raise ValueError("nonliteral comparison")
    obj = {"capability": c["inspect"]}
    if "where" in c:
        if not isinstance(c["where"], dict):
            raise ValueError("selector must be mapping")
        obj["select"] = deepcopy(c["where"])
    if "collect" in c:
        if not isinstance(c["collect"], dict):
            raise ValueError("collector must be mapping")
        obj["collect"] = deepcopy(c["collect"])
    return {
        "test_title": c["check"], "capability": c["inspect"],
        "object": obj,
        "states": [{field: {"require": FIELD_PAIR, INVERSE[verb]: val}}],
        "reported_elements": c["report_elements"],
        "collected_items_require": ITEM_PAIR,
    }


def audit(path):
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != PIN:
        raise ValueError("source content changed")
    stats, caps, samples, negatives = Counter(), Counter(), [], 0
    with zipfile.ZipFile(path) as z:
        if z.testzip():
            raise ValueError("corrupt archive")
        for member in sorted(z.namelist()):
            if not member.startswith("authoring/") or "/assessments/" not in member or not member.endswith(".yaml"):
                continue
            doc = yaml.safe_load(z.read(member))
            ass = (doc or {}).get("assessment") or {}
            if ass.get("mode") != "automated":
                continue
            for test_id, test in (ass.get("tests") or {}).items():
                stats["all_named_tests"] += 1
                cand, reason = candidate_for(test, ass)
                if cand is None:
                    stats["rejected_"+reason] += 1
                    continue
                original = deepcopy(test)
                original["object"] = resolved_object(test, ass)
                rebuilt = lower(cand)
                if rebuilt != original:
                    raise AssertionError("lossy source reconstruction "+member+" "+test_id)
                stats["exact_generic_scalar_tests"] += 1
                caps[cand["inspect"]] += 1
                if len(samples) < 20:
                    samples.append({"source": member, "test": test_id, "candidate": cand})
                wrong = deepcopy(cand)
                wrong["require"]["at_least_one_item_exists"] = False
                try: lower(wrong)
                except ValueError: negatives += 1
                else: raise AssertionError("false exists accepted")
                wrong = deepcopy(cand)
                v = next(iter(wrong["require"]["every_collected_item"].values()))
                op = next(iter(v))
                val = v.pop(op)
                v["includes"] = val
                try: lower(wrong)
                except ValueError: negatives += 1
                else: raise AssertionError("undefined operator accepted")
                wrong = deepcopy(cand)
                wrong.pop("collect", None); wrong.pop("where", None)
                try: lower(wrong)
                except ValueError: negatives += 1
                else: raise AssertionError("missing acquisition accepted")
    if stats["all_named_tests"] != 1375:
        raise AssertionError("corpus scope changed")
    classified = stats["exact_generic_scalar_tests"] + sum(n for k,n in stats.items() if k.startswith("rejected_"))
    if classified != stats["all_named_tests"]:
        raise AssertionError("unaccounted source Test")
    return {"status":"EXACT COMMON SCALAR NODE STRUCTURE; NO RUNTIME OR READABILITY VALIDATION",
            "source_sha256": digest, "counts": dict(stats), "capabilities": dict(caps.most_common()),
            "examples": samples, "negative_guards": negatives,
            "semantic_scope":"requires both source Test Item and field value one_or_more/all; all reported elements"}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output")
    a=p.parse_args()
    report=audit(a.archive)
    if a.output:
        Path(a.output).write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"counts":report["counts"],"top_capabilities":list(report["capabilities"].items())[:18],
                       "samples":[{"source":x["source"],"test":x["test"],
                                   "check":x["candidate"]["check"]} for x in report["examples"][:8]],
                       "negative_guards":report["negative_guards"]},indent=2))


if __name__=="__main__":
    main()
