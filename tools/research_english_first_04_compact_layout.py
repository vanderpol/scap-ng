#!/usr/bin/env python3
"""Research #235: make one existing English-first AST less repetitive.

Only changes *presentation*: removes duplicated collector capability from
inline gathered data, lifts ordinary collector fields alongside inspect, and
uses 'from' for a named shared source. The inverse is deterministic.
Reconstruct whole original source for every admitted Assessment.

The direct union/difference/intersection/complement spelling is a reversible
experiment: it never drops a one-operand Set or alters filter order.

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
READABLE_MATCH_KEYS = {
    "every_collected_item": "every_item_must_match",
    "some_collected_item": "at_least_one_item_matches",
    "exactly_one_collected_item": "exactly_one_item_matches",
    "no_collected_item": "no_item_may_match",
}
NATIVE_MATCH_KEYS = {v: k for k, v in READABLE_MATCH_KEYS.items()}
SET_OPERATIONS = {"union", "difference", "intersection", "complement"}

# Deliberate human reading order, independent of YAML mapping semantics.
# Define data acquisition before criteria. Preserve all keys and values.
DISPLAY_ORDER = (
    "check", "inspect", "description", "from", "gather", "where",
    "collect", "filesystem", "traversal", "input_from",
    "all_state_fields_exist", "all_state_fields_when_present",
    "require", "report_elements",
)


def in_reading_order(check):
    unknown = set(check) - set(DISPLAY_ORDER)
    if unknown:
        raise ValueError("unrecognized human display keys: " + repr(sorted(unknown)))
    return {key: check[key] for key in DISPLAY_ORDER if key in check}


def require_acquisition_before_criteria(check):
    keys = list(check)
    if keys != list(in_reading_order(check)):
        raise AssertionError("check keys not in canonical top-down reading order")
    if "require" not in check:
        raise AssertionError("check lost its requirement")
    for key in ("from", "gather", "where", "collect", "filesystem",
                "traversal", "input_from"):
        if key in check and keys.index(key) > keys.index("require"):
            raise AssertionError("data source appears after State requirements")



def compact_source(original):
    """Remove the redundant 'combine' wrapper, retaining every Set operand."""
    source = deepcopy(original)
    if not isinstance(source, dict):
        raise ValueError("collection source must be a mapping")
    if "combine" not in source:
        return source
    spec = source.pop("combine")
    if not isinstance(spec, dict) or len(spec) != 1:
        raise ValueError("Set must have exactly one operation")
    op, operands = next(iter(spec.items()))
    if op not in SET_OPERATIONS or any(x in source for x in SET_OPERATIONS):
        raise ValueError("invalid or duplicate Set operation")
    if not isinstance(operands, list) or not operands:
        raise ValueError("Set operands must be a nonempty list")
    converted = []
    for operand in operands:
        if not isinstance(operand, dict) or "from" not in operand:
            raise ValueError("Set operand lacks source")
        part = deepcopy(operand)
        reference = part["from"]
        if isinstance(reference, dict) and set(reference) == {"source"}:
            if not isinstance(reference["source"], str) or not reference["source"]:
                raise ValueError("invalid referenced collection")
            part["from"] = reference["source"]
        elif isinstance(reference, dict):
            part["from"] = compact_source(reference)
        else:
            raise ValueError("unsupported Set operand reference")
        converted.append(part)
    source[op] = converted
    return source


def expand_source(compacted, names):
    """Restore the exact original Set tree; reject ambiguous sources."""
    source = deepcopy(compacted)
    if not isinstance(source, dict):
        raise ValueError("collection source must be a mapping")
    if "combine" in source:
        raise ValueError("noncanonical combine wrapper")
    operators = SET_OPERATIONS & set(source)
    if len(operators) > 1:
        raise ValueError("multiple Set operations")
    if not operators:
        return source
    op = next(iter(operators))
    operands = source.pop(op)
    if not isinstance(operands, list) or not operands:
        raise ValueError("Set operands must be a nonempty list")
    restored = []
    for operand in operands:
        if not isinstance(operand, dict) or "from" not in operand:
            raise ValueError("Set operand lacks source")
        part = deepcopy(operand)
        reference = part["from"]
        if isinstance(reference, str):
            if not reference or reference not in names:
                raise ValueError("undefined named Set source " + reference)
            part["from"] = {"source": reference}
        elif isinstance(reference, dict):
            part["from"] = expand_source(reference, names)
        else:
            raise ValueError("invalid Set operand reference")
        restored.append(part)
    source["combine"] = {op: restored}
    return source



def compact(original):
    """Same AST contract, mobile-friendlier layout. No comparisons altered."""
    doc = deepcopy(original)
    if set(doc) != {"metadata", "sources", "checks", "evaluate"}:
        raise ValueError("unrecognized source grammar")
    doc["sources"] = {name: compact_source(src) for name, src in doc["sources"].items()}
    for name, check in doc["checks"].items():
        if set(check) - BASE_CHECK - {"gather"}:
            raise ValueError("unrecognized input check keys: " + name)
        requirement = check.get("require")
        if not isinstance(requirement, dict):
            raise ValueError("missing requirement map")
        for source, readable in READABLE_MATCH_KEYS.items():
            if source in requirement:
                if readable in requirement:
                    raise ValueError("ambiguous Item matching")
                requirement[readable] = requirement.pop(source)
        if "gather" not in check:
            continue
        gather = compact_source(check["gather"])
        check["gather"] = gather
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
    doc["checks"] = {name: in_reading_order(check)
                     for name, check in doc["checks"].items()}
    for check in doc["checks"].values():
        require_acquisition_before_criteria(check)
    return doc


def expand(compact_doc):
    """Reconstruct exactly the original verbose research AST."""
    doc = deepcopy(compact_doc)
    if set(doc) != {"metadata", "sources", "checks", "evaluate"}:
        raise ValueError("unexpected document keys")
    source_names = set(doc["sources"])
    for name, check in doc["checks"].items():
        if set(check) - BASE_CHECK - EXTENDED:
            raise ValueError("unexpected check property " + name)
        requirement = check.get("require")
        if not isinstance(requirement, dict):
            raise ValueError("missing Item requirements")
        for readable, source in NATIVE_MATCH_KEYS.items():
            if readable in requirement:
                if source in requirement:
                    raise ValueError("ambiguous Item matching")
                requirement[source] = requirement.pop(readable)
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
            gather = expand_source(gather, source_names)
            if "inspect" not in gather:
                gather["inspect"] = check["inspect"]
            if set(gather) == {"source", "inspect"}:
                raise ValueError("ambiguous reference collector")
            check["gather"] = gather
    doc["sources"] = {name: expand_source(src, source_names)
                      for name, src in doc["sources"].items()}
    return doc



def verify_self_test():
    """Source-shaped fixtures catch lossy Set and named-source rewrites."""
    linux_operand = {
        "from": {
            "inspect": "unix.file",
            "for_each_source": {"item": "user", "in": "non-system-users"},
            "where": {"directory": {"from": "user.home_dir"}},
            "filesystem": "all",
            "traversal": {"max_depth": 1, "recurse": "symlinks"},
        },
        "exclude_if": [{"type": {"is": "directory"}}],
    }
    one_operand_union = {
        "inspect": "unix.file",
        "combine": {"union": [linux_operand]},
    }
    named_difference = {
        "inspect": "unix.password",
        "combine": {"difference": [{
            "from": {"source": "users"},
            "exclude_if": [
                {"user_id": {"less_than": 1000}},
                {"home_dir": {"equals": "/"}},
            ],
        }]},
    }
    sources = {"users": {"inspect": "unix.password"},
               "non-system-users": named_difference}
    checks = {
        "file-check": {
            "check": "Check initialization file permissions",
            "inspect": "unix.file",
            "gather": one_operand_union,
            "require": {"items_may_be_absent": True,
                        "every_collected_item": {"setuid": {"is": False}}},
            "report_elements": "all",
        },
        "named-check": {
            "check": "Check collected user accounts",
            "inspect": "unix.password",
            "gather": {"source": "non-system-users"},
            "require": {"every_collected_item": {"user_id": {"at_least": 1000}}},
            "report_elements": "all",
        },
    }
    doc = {"metadata": {}, "sources": sources, "checks": checks,
           "evaluate": {"test": "file-check"}}
    compacted = compact(doc)
    if expand(compacted) != doc:
        raise AssertionError("complex Set and references did not round trip")
    if "combine" in compacted["checks"]["file-check"]["gather"]:
        raise AssertionError("redundant Set wrapper still present")
    if "union" not in compacted["checks"]["file-check"]["gather"]:
        raise AssertionError("one-operand Set was erased")
    if "difference" not in compacted["sources"]["non-system-users"]:
        raise AssertionError("shared-source Set was erased")
    if compacted["checks"]["named-check"].get("from") != "non-system-users":
        raise AssertionError("named check source not normalized")
    for illegal in [
        {"union": [], "difference": [linux_operand]},
        {"union": []},
        {"union": [{"from": "unknown"}]},
        {"union": [{"from": {"inspect": "unix.file", "combine": {"union": []}}}]},
    ]:
        try:
            expand_source(illegal, set(sources))
        except ValueError:
            pass
        else:
            raise AssertionError("noncanonical/undefined Set accepted")
    return True


def inspect(archive, examples_dir=None):
    verify_self_test()
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
            for check in compacted["checks"].values():
                require_acquisition_before_criteria(check)
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
                if "gather" in item and any(op in item["gather"] for op in SET_OPERATIONS):
                    saved_by_category["direct_check_set_ops"] += 1
            for src in compacted["sources"].values():
                if any(op in src for op in SET_OPERATIONS):
                    saved_by_category["direct_shared_set_ops"] += 1
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
        {"gather": {"union": [], "difference": []}},
        {"gather": {"union": []}},
        {"gather": {"union": [{"from": "missing-source"}]}},
        {"gather": {"union": [{"from": 123}]}},
        {"gather": {"combine": {"union": [{"from": "x"}]}}},
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
