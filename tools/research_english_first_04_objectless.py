#!/usr/bin/env python3
"""Prove English-first native system-wide Objectless Test patterns.

No hidden Object is synthesized; source source_Test has none. Research only.
Candidate macros include exactly proven Test/field existence & all-match
quantifiers and explicit reported_elements; not approved grammar.
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
COMPARE_TO_READABLE = {
    "equals": "equals",
    "case_insensitive_equals": "equals_ignoring_case",
    "greater_than_or_equal": "at_least",
    "less_than_or_equal": "at_most",
    "greater_than": "greater_than",
    "less_than": "less_than",
    "not_equal": "not_equal",
    "matches_regex": "matches_regex",
}
READABLE_TO_COMPARE = {v: k for k,v in COMPARE_TO_READABLE.items()}
EXPECT_ITEM = "at_least_one_exists_and_all_match"
EXPECT_FIELD = "at_least_one_exists_and_all_match"


def source_candidate(test):
    if "object" in test:
        return None, "has_explicit_object"
    if set(test) != {"test_title", "capability", "states", "reported_elements", "collected_items_require"}:
        return None, "unexpected_test_keys"
    if test["collected_items_require"] != EXPECT_ITEM or test["reported_elements"] != "all":
        return None, "item_requirement_or_reporting_not_proven"
    if not isinstance(test["test_title"], str) or not test["test_title"]:
        return None, "missing_test_title"
    if not isinstance(test["capability"], str) or not test["capability"]:
        return None, "missing_capability"
    states = test["states"]
    if not isinstance(states, list) or len(states) != 1 or not isinstance(states[0], dict) or len(states[0]) != 1:
        return None, "complex_states"
    name, node = next(iter(states[0].items()))
    if not isinstance(node, dict) or set(node) - {"require"} not in ({k} for k in COMPARE_TO_READABLE):
        return None, "complex_field_comparison"
    if node.get("require") != EXPECT_FIELD:
        return None, "field_requirement_not_proven"
    op = next(iter(set(node) - {"require"}))
    operand = node[op]
    if not isinstance(operand, (str, int, float, bool)) or (isinstance(operand, str) and not operand):
        return None, "nonliteral_operand"
    return {"check": test["test_title"], "inspect": test["capability"],
            "require": {name: {COMPARE_TO_READABLE[op]: operand}},
            "report_elements": "all"}, None


def lower(candidate):
    if not isinstance(candidate, dict) or set(candidate) != {"check", "inspect", "require", "report_elements"}:
        raise ValueError("invalid native check")
    if not candidate["check"] or not isinstance(candidate["check"], str):
        raise ValueError("missing title")
    if not candidate["inspect"] or not isinstance(candidate["inspect"], str):
        raise ValueError("missing native capability")
    if candidate["report_elements"] != "all":
        raise ValueError("unsupported result reporting mode")
    req = candidate["require"]
    if not isinstance(req, dict) or len(req) != 1:
        raise ValueError("single field requirement only")
    field, expr = next(iter(req.items()))
    if not isinstance(field, str) or not field:
        raise ValueError("field name required")
    if not isinstance(expr, dict) or len(expr) != 1:
        raise ValueError("expected one typed comparison")
    op, value = next(iter(expr.items()))
    if op not in READABLE_TO_COMPARE:
        raise ValueError("unsupported natural comparison")
    if not isinstance(value, (str, int, float, bool)) or (isinstance(value, str) and not value):
        raise ValueError("unsupported nonliteral")
    return {
        "test_title": candidate["check"],
        "capability": candidate["inspect"],
        "states": [{field: {"require": EXPECT_FIELD, READABLE_TO_COMPARE[op]: value}}],
        "reported_elements": candidate["report_elements"],
        "collected_items_require": EXPECT_ITEM,
    }


def run(archive):
    checksum = hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if checksum != PIN:
        raise ValueError("wrong source ZIP")
    counts, cap, examples, negatives = Counter(), Counter(), [], 0
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise ValueError("corrupt source ZIP")
        for path in sorted(z.namelist()):
            if not path.startswith("authoring/") or "/assessments/" not in path or not path.endswith(".yaml"):
                continue
            doc = yaml.safe_load(z.read(path))
            ass = (doc or {}).get("assessment") or {}
            if ass.get("mode") != "automated":
                continue
            for test_id, test in (ass.get("tests") or {}).items():
                if "object" in test:
                    continue
                counts["all_objectless_tests"] += 1
                candidate, reason = source_candidate(test)
                if candidate is None:
                    counts["rejected_"+reason] += 1
                    continue
                if lower(candidate) != test:
                    raise AssertionError("source mismatch at "+path+" "+test_id)
                counts["exact_objectless_test_inversion"] += 1
                cap[candidate["inspect"]] += 1
                if len(examples) < 14:
                    examples.append({"source": path, "test": test_id, "candidate": candidate})
                wrong = deepcopy(candidate)
                wrong["require"][next(iter(wrong["require"]))] = {"contains": "wrong"}
                try:
                    lower(wrong)
                except ValueError:
                    negatives += 1
                else:
                    raise AssertionError("unproven operator accepted")
                wrong = deepcopy(candidate)
                del wrong["report_elements"]
                try:
                    lower(wrong)
                except ValueError:
                    negatives += 1
                else:
                    raise AssertionError("implicit reported_elements accepted")
    if counts["all_objectless_tests"] != 114:
        raise AssertionError("original objectless count changed")
    classified = counts["exact_objectless_test_inversion"] + sum(n for k,n in counts.items() if k.startswith("rejected_"))
    if classified != counts["all_objectless_tests"]:
        raise AssertionError("Incomplete objectless classification")
    return {"status": "TYPED SOURCE GRAPH INVERSION; NOT 0.4 GRAMMAR OR SCANNER PROOF",
            "counts": dict(counts), "capabilities": dict(cap.most_common()), "examples": examples,
            "negative_guards": negatives, "source_sha256": checksum,
            "warning": "Operator macros encode source Item and field quantifiers; their readability still needs review"}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output")
    a=p.parse_args()
    rep=run(a.archive)
    if a.output:
        Path(a.output).write_text(json.dumps(rep, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"counts": rep["counts"],"capabilities": rep["capabilities"],
                      "examples":[{"source":e["source"],"test":e["test"],
                                   "candidate":e["candidate"]} for e in rep["examples"][:3]],
                      "negative_guards":rep["negative_guards"]},indent=2))


if __name__=="__main__":
    main()
