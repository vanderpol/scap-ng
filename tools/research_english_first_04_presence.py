#!/usr/bin/env python3
"""Fail-closed, source-exact English-first presence-only Assessment research.

This is NOT a normative compiler and NOT a scanner result proof. Covers only
Test nodes without States and with simple native inline/shared Objects whose
selector/collector specs can be represented unchanged.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

import yaml

PINNED_SHA256 = "03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"
NATIVE_TO_READABLE = {
    "none_exist": "none",
    "only_one_exists": "exactly_one",
    "at_least_one_exists": "at_least_one",
    "all_exist": "all_exist",
    "may_be_absent": "may_be_absent",
}
READABLE_TO_NATIVE = {v: k for k, v in NATIVE_TO_READABLE.items()}


def eligible(test, ass):
    if "states" in test:
        return None, "has_states"
    obj = test.get("object")
    if isinstance(obj, str):
        obj = (ass.get("shared_objects") or {}).get(obj)
    if not isinstance(obj, dict):
        return None, "no_native_inline_or_resolved_object"
    obj = deepcopy(obj)
    obj.pop("object_title", None)
    allowed = {"capability", "select", "collect"}
    if not set(obj).issubset(allowed) or "capability" not in obj:
        return None, "complex_object_set_or_metadata"
    if not ({"select", "collect"} & set(obj)):
        return None, "object_without_selector_or_collector"
    if test.get("capability") != obj.get("capability"):
        return None, "capability_mismatch"
    title = test.get("test_title")
    if not isinstance(title, str) or not title:
        return None, "no_title"
    extra = set(test) - {"test_title", "capability", "object", "reported_elements", "collected_items_require"}
    if extra:
        return None, "unexpected_test_properties"
    native_req = test.get("collected_items_require")
    if native_req not in NATIVE_TO_READABLE:
        return None, "unproven_presence_mode"
    if test.get("reported_elements") != "all":
        return None, "other_result_report_mode"
    candidate = {
        "check": title,
        "inspect": test["capability"],
        "require": {"collected_items": NATIVE_TO_READABLE[native_req]},
        "report": {"elements": "all"},
    }
    if "select" in obj:
        candidate["where"] = deepcopy(obj["select"])
    if "collect" in obj:
        candidate["collect"] = deepcopy(obj["collect"])
    return candidate, None


def lower(candidate):
    if not isinstance(candidate, dict):
        raise ValueError("candidate not mapping")
    permitted = {"check", "inspect", "where", "collect", "require", "report"}
    if set(candidate) - permitted:
        raise ValueError("unexpected candidate property")
    if not {"check", "inspect", "require", "report"}.issubset(candidate):
        raise ValueError("required check/inspect/require/report not provided")
    if not {"where", "collect"} & set(candidate):
        raise ValueError("no data selection or collection")
    if not isinstance(candidate["check"], str) or not candidate["check"]:
        raise ValueError("missing check title")
    if not isinstance(candidate["inspect"], str) or not candidate["inspect"]:
        raise ValueError("unknown collector capability")
    if not isinstance(candidate["require"], dict) or set(candidate["require"]) != {"collected_items"}:
        raise ValueError("invalid presence requirement")
    human = candidate["require"]["collected_items"]
    if human not in READABLE_TO_NATIVE:
        raise ValueError("unsupported collection existence term")
    if candidate["report"] != {"elements": "all"}:
        raise ValueError("only source reporting all is modeled")
    obj = {"capability": candidate["inspect"]}
    if "where" in candidate:
        if not isinstance(candidate["where"], dict):
            raise ValueError("invalid where selector")
        obj["select"] = deepcopy(candidate["where"])
    if "collect" in candidate:
        if not isinstance(candidate["collect"], dict):
            raise ValueError("invalid collect parameters")
        obj["collect"] = deepcopy(candidate["collect"])
    return {
        "test_title": candidate["check"],
        "capability": candidate["inspect"],
        "object": obj,
        "reported_elements": "all",
        "collected_items_require": READABLE_TO_NATIVE[human],
    }


def audit(archive):
    checksum = hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if checksum != PINNED_SHA256:
        raise ValueError("unexpected original source ZIP digest")
    counts, examples, caps = Counter(), [], Counter()
    negative = 0
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise ValueError("source archive has errors")
        for path in sorted(z.namelist()):
            if not path.startswith("authoring/") or "/assessments/" not in path or not path.endswith(".yaml"):
                continue
            doc = yaml.safe_load(z.read(path))
            ass = (doc or {}).get("assessment") or {}
            if ass.get("mode") != "automated":
                continue
            for test_id, test in (ass.get("tests") or {}).items():
                if "states" in test:
                    continue
                counts["source_state_free_tests"] += 1
                candidate, reason = eligible(test, ass)
                if candidate is None:
                    counts["rejected_"+reason] += 1
                    continue
                reconstructed = lower(candidate)
                source = deepcopy(test)
                if isinstance(source["object"], str):
                    source["object"] = deepcopy(ass["shared_objects"][source["object"]])
                source["object"].pop("object_title", None)
                if reconstructed != source:
                    counts["source_structure_mismatch"] += 1
                    if len(examples) < 5:
                        examples.append({"source": path, "test": test_id, "problem": "not source-identical"})
                    continue
                counts["exact_state_free_test_inversion"] += 1
                caps[test["capability"]] += 1
                if len(examples) < 16:
                    examples.append({
                        "source": path, "test": test_id,
                        "collection": sorted(set(candidate) & {"where", "collect"}),
                        "readable": candidate,
                    })
                wrong = deepcopy(candidate)
                wrong["require"]["collected_items"] = "unknown_alias"
                try:
                    lower(wrong)
                except ValueError:
                    negative += 1
                else:
                    raise AssertionError("unsupported presence accepted")
                wrong = deepcopy(candidate)
                wrong["report"].pop("elements")
                try:
                    lower(wrong)
                except ValueError:
                    negative += 1
                else:
                    raise AssertionError("report default silently assumed")
    if counts["source_state_free_tests"] != 387:
        raise AssertionError("Pinned state-free Test count changed")
    if counts["exact_state_free_test_inversion"] + sum(
        n for k, n in counts.items() if k.startswith("rejected_") or k == "source_structure_mismatch"
    ) != counts["source_state_free_tests"]:
        raise AssertionError("Missing source classifications")
    return {
        "status": "STATE-FREE TEST STRUCTURE INVERSION; NO SCANNER SEMANTIC PROOF",
        "source_archive_sha256": checksum, "counts": dict(counts),
        "capabilities_proven": dict(caps.most_common()),
        "examples": examples, "negative_guards": negative,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--output")
    a = p.parse_args()
    report = audit(a.archive)
    if a.output:
        Path(a.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "counts": report["counts"],
        "capabilities_proven": report["capabilities_proven"],
        "source_examples": [{"source": x["source"], "test": x["test"]}
                            for x in report["examples"][:8]],
        "negative_guards": report["negative_guards"],
    }, indent=2))


if __name__ == "__main__":
    main()
