#!/usr/bin/env python3
"""Research #235: make one existing English-first AST less repetitive.

Only changes *presentation*: removes duplicated collector capability from
inline gathered data, lifts ordinary collector fields alongside inspect, and
uses 'from' for a named shared source. The inverse is deterministic.
Reconstruct whole original source for every admitted Assessment.

Not a normative grammar, scanner, or readability-user study.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

import yaml
from research_english_first_04_complex import to_human, to_native

PINNED = "03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"
LIFTABLE = {"where", "collect", "filesystem", "traversal", "description"}
BASE_CHECK = {"check", "inspect", "require", "report_elements", "all_state_fields_exist", "all_state_fields_when_present", "input_from"}
EXTENDED = {"gather", "from"} | LIFTABLE


def compact(original):
    """Same AST contract, mobile-friendlier layout. No comparisons altered."""
    doc = deepcopy(original)
    if set(doc) != {"metadata", "sources", "checks", "evaluate"}:
        raise ValueError("unrecognized source grammar")
    for name, check in doc["checks"].items():
        if set(check) - BASE_CHECK - {"gather"}:
            raise ValueError("unrecognized input check keys: " + name)
        if "gather" not in check:
            continue
        gather = check["gather"]
        if not isinstance(gather, dict):
            raise ValueError("gather not mapping")
        if set(gather) == {"source"}:
            ref = gather["source"]
            if not isinstance(ref, str) or not ref:
                raise ValueError("invalid source ref")
            check["from"] = ref
            del check["gather"]
            continue
        if gather.get("inspect") == check["inspect"]:
            del gather["inspect"]
            # Ordinary selector/collector options are part of the same check.
            if set(gather).issubset(LIFTABLE) and gather:
                for key in LIFTABLE:
                    if key in gather:
                        if key in check:
                            raise ValueError("duplicate flattened option")
                        check[key] = gather[key]
                del check["gather"]
        # If gather is complex (Set or for_each) retain it visibly, but
        # without duplicating its inspect when both capabilities agree.
    return doc


def expand(compact_doc):
    """Reconstruct exactly the original verbose research AST."""
    doc = deepcopy(compact_doc)
    if set(doc) != {"metadata", "sources", "checks", "evaluate"}:
        raise ValueError("unexpected document keys")
    for name, check in doc["checks"].items():
        if set(check) - BASE_CHECK - EXTENDED:
            raise ValueError("unexpected check property " + name)
        flat = set(check) & LIFTABLE
        has_from = "from" in check
        has_gather = "gather" in check
        if (has_from and (flat or has_gather)) or (flat and has_gather):
            raise ValueError("multiple conflicting acquisition declarations")
        if has_from:
            reference = check.pop("from")
            if not isinstance(reference, str) or not reference:
                raise ValueError("invalid source reference")
            if reference not in doc["sources"]:
                raise ValueError("undefined named source " + reference)
            check["gather"] = {"source": reference}
        elif flat:
            restored = {"inspect": check["inspect"]}
            for key in LIFTABLE:
                if key in check:
                    restored[key] = check.pop(key)
            check["gather"] = restored
        elif has_gather:
            gather = check["gather"]
            if not isinstance(gather, dict):
                raise ValueError("invalid gather map")
            if "inspect" not in gather:
                gather["inspect"] = check["inspect"]
            if set(gather) == {"source", "inspect"}:
                raise ValueError("ambiguous reference collector")
    return doc


def inspect(archive, examples_dir=None):
    digest = hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest != PINNED:
        raise ValueError("unexpected source archive")
    results = Counter()
    total_verbose = total_compact = 0
    saved_by_category = Counter()
    exact = []
    rejections = []
    if examples_dir:
        Path(examples_dir).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise ValueError("archive CRC error")
        for path in sorted(z.namelist()):
            if not (path.startswith("authoring/") and "/assessments/" in path
                    and path.endswith(".yaml")):
                continue
            ass = (yaml.safe_load(z.read(path)) or {}).get("assessment") or {}
            if ass.get("mode") != "automated" or not ass.get("tests"):
                continue
            results["source_assessments"] += 1
            try:
                verbose = to_human(ass)
                compacted = compact(verbose)
                restored = expand(compacted)
                if restored != verbose or to_native(restored) != ass:
                    raise AssertionError("changed source data")
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                results["unconverted_source_assessments"] += 1
                if len(rejections) < 20:
                    rejections.append({"path": path, "reason": str(exc)[:180]})
                continue

            results["exact_source_assessments"] += 1
            short = yaml.safe_dump(compacted, sort_keys=False, allow_unicode=True)
            long = yaml.safe_dump(verbose, sort_keys=False, allow_unicode=True)
            total_verbose += len(long)
            total_compact += len(short)
            for key, item in compacted["checks"].items():
                source = verbose["checks"][key]
                if "from" in item:
                    saved_by_category["named_source_refs"] += 1
                if "gather" in source and "gather" not in item and "from" not in item:
                    saved_by_category["flat_native_gather"] += 1
                if "gather" in source and "gather" in item and (
                    "inspect" in source["gather"] and
                    "inspect" not in item["gather"]
                ):
                    saved_by_category["deduplicated_nested_inspect"] += 1
            if len(exact) < 8:
                exact.append({"path": path, "tests": len(ass["tests"])})
            if examples_dir:
                example_map = {
                    "authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml": "win11-role-rights",
                    "authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml": "apache-keepalive",
                    "authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml": "dns-zone-signing",
                    "authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml": "linux-initialization",
                }
                if path in example_map:
                    label = example_map[path]
                    (Path(examples_dir) / (label+".research.yaml")).write_text(
                        "# EXPERIMENT ONLY; reconstructs the pinned Assessment exactly.\n"
                        "# Not normative SCAP-NG v0.4 or independently validated OVAL execution.\n"
                        + short, encoding="utf-8")
    if results["source_assessments"] != 872 or results["exact_source_assessments"] < 865:
        raise AssertionError("Regression from previous source-exact coverage")
    if results["source_assessments"] != (results["exact_source_assessments"] +
                                        results["unconverted_source_assessments"]):
        raise AssertionError("unaccounted source Assesments")
    # Ambiguous/conflicting collection declarations must fail closed.
    negative = 0
    for candidate in [
        {"where": {}, "from": "shared"},
        {"collect": {}, "gather": {}},
        {"from": "missing-source"},
    ]:
        obj = {"metadata": {}, "sources": {}, "evaluate": {"test": "dummy"},
               "checks": {"dummy": {"check": "dummy", "inspect": "unix.file",
                                    "require": {}, "report_elements": "all", **candidate}}}
        try:
            expand(obj)
        except ValueError:
            negative += 1
        else:
            raise AssertionError("ambiguous acquisition unexpectedly accepted")
    return {
        "source_sha256": digest,
        "status": "EXACT WHOLE-ASSESSMENT SOURCE ROUND-TRIP, NOT SCANNER PROOF",
        "counts": dict(results),
        "source_chars_before": total_verbose,
        "source_chars_after": total_compact,
        "source_char_reduction_percent": round((total_verbose - total_compact)*100/total_verbose, 2),
        "source_deduplication_counts": dict(saved_by_category),
        "exact_samples": exact,
        "rejected_examples": rejections,
        "negative_acquisition_guards": negative,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--output")
    p.add_argument("--examples-dir")
    args = p.parse_args()
    results = inspect(args.archive, args.examples_dir)
    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2, sort_keys=True)+"\n")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
