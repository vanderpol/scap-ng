#!/usr/bin/env python3
"""#238: read-only execution of one pinned 0.4-A Linux mount Assessment.

Research prototype: not equivalent to OVAL linux.partition, a full scanner,
a Benchmark Result or a release-quality signed bundle.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from research_provider_linux_mounts import collect_current_linux_mounts, parse_mountinfo_text

ASSESSMENT_ID = "ng.shared.home-is-mounted-with-the-nosuid-option"


class UnsupportedAssessment(ValueError):
    """The pilot will not guess at unimplemented authoring semantics."""


def keys(obj, allowed, required, name):
    if not isinstance(obj, dict) or not required.issubset(obj) or not set(obj).issubset(allowed):
        raise UnsupportedAssessment(f"unsupported {name} structure (required {sorted(required)})")


def compile_assessment(doc):
    """Require precisely the pinned A Test shape; no implicit quantifier defaults."""
    keys(doc, {"assessment"}, {"assessment"}, "document")
    a = doc["assessment"]
    keys(a, {"id", "version", "assessment_title", "mode", "class",
             "purpose", "specification", "tests", "evaluate"},
         {"id", "version", "mode", "class", "purpose", "specification", "tests", "evaluate"},
         "Assessment")
    if (a["id"] != ASSESSMENT_ID or a["version"] != 1 or a["mode"] != "automated"
            or a["class"] != "compliance" or a["purpose"] != "assessment"):
        raise UnsupportedAssessment("only the pinned RHEL 9 /home Assessment is implemented")
    keys(a["specification"], {"id", "version"}, {"id", "version"}, "specification")
    if a["specification"] != {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}:
        raise UnsupportedAssessment("not the 0.4-A pre-alpha Assessment")
    tests = a["tests"]
    if not isinstance(tests, dict) or len(tests) != 1:
        raise UnsupportedAssessment("only one named Test can run")
    tid, t = next(iter(tests.items()))
    if a["evaluate"] != {"test": tid}:
        raise UnsupportedAssessment("only direct single-Test evaluate is supported")
    keys(t, {"test_title", "capability", "object", "states", "reported_elements", "require"},
         {"test_title", "capability", "object", "states", "reported_elements", "require"}, "Test")
    if (t["capability"] != "linux.partition" or t["reported_elements"] != "all"
            or t["require"] != "at_least_one_exists_and_all_match"):
        raise UnsupportedAssessment("Test capability, evidence or requirement is unsupported")
    obj = t["object"]
    keys(obj, {"capability", "select", "object_title"}, {"capability", "select"}, "Object")
    if obj["capability"] != "linux.partition":
        raise UnsupportedAssessment("Object capability mismatch")
    keys(obj["select"], {"mount_point"}, {"mount_point"}, "Object selector")
    keys(obj["select"]["mount_point"], {"matches_regex"}, {"matches_regex"}, "mount selector")
    pattern = obj["select"]["mount_point"]["matches_regex"]
    if pattern != r".*\/home":
        raise UnsupportedAssessment("only the original /home regex is permitted")
    if not isinstance(t["states"], list) or len(t["states"]) != 1:
        raise UnsupportedAssessment("only one State predicate supported")
    state = t["states"][0]
    keys(state, {"mount_options"}, {"mount_options"}, "State")
    keys(state["mount_options"], {"require", "equals"}, {"require", "equals"}, "mount_options")
    if state["mount_options"] != {
        "require": "at_least_one_exists_and_some_match", "equals": "nosuid"
    }:
        raise UnsupportedAssessment("only the explicit some mount option equals nosuid State is supported")
    return {"assessment_id": a["id"], "version": a["version"], "test_id": tid, "selector": pattern}


def evaluate(compiled, observation, fixture_mode=False):
    """Keep known failures decisive; never pass when evidence is incomplete."""
    items = observation.get("items")
    status = observation.get("status")
    diagnostics = observation.get("diagnostics", [])
    if (observation.get("provider") != "linux.mounts"
            or observation.get("provider_version") != "0.1.0"
            or status not in {"complete", "incomplete", "error"}
            or not isinstance(items, list)):
        status, items, diagnostics = "error", [], [{"reason": "invalid collector identity or envelope"}]
    selected, violations = [], []
    seen = set()
    if status != "error":
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                status, diagnostics = "error", [{"reason": "invalid Item identity"}]
                break
            if item["id"] in seen:
                status, diagnostics = "error", [{"reason": "duplicate Item identity"}]
                break
            seen.add(item["id"])
            fields = item.get("fields")
            if not isinstance(fields, dict) or not isinstance(fields.get("mount_point"), str):
                status, diagnostics = "error", [{"reason": "missing mount_point field"}]
                break
            if re.search(compiled["selector"], fields["mount_point"]):
                selected.append(item)
                options = fields.get("mount_options")
                if not isinstance(options, list) or not all(isinstance(v, str) for v in options):
                    status, diagnostics = "error", [{"reason": "invalid mount_options field"}]
                    break
                if "nosuid" not in options:
                    violations.append(item)
    if status == "error":
        result, reason = "error", "collection_error"
    elif violations:
        result, reason = "false", "mount_without_nosuid"
    elif status == "incomplete":
        result, reason = "unknown", "collection_incomplete"
    elif not selected:
        result, reason = "false", "required_mount_missing"
    else:
        result, reason = "true", "all_selected_mounts_have_nosuid"
    return {
        "format": "scap-ng-a-linux-mount-prototype/0.1",
        "assessment_id": compiled["assessment_id"], "assessment_version": compiled["version"],
        "test_id": compiled["test_id"], "result": result, "reason_code": reason,
        "collector": {"provider": observation.get("provider"),
                      "version": observation.get("provider_version"),
                      "status": status, "namespace": observation.get("namespace")},
        "counts": {"observed": len(items), "selected": len(selected),
                   "violating": len(violations)},
        "evidence": [{"id": item["id"], "mount_point": item["fields"]["mount_point"],
                      "mount_options": item["fields"]["mount_options"]}
                     for item in selected[:10]],
        "evidence_truncated": len(selected) > 10,
        "diagnostics": diagnostics[:10] if isinstance(diagnostics, list)
                       else [{"reason": "invalid diagnostics"}],
        "fixture_mode": fixture_mode,
        "limitations": [
            "observes only caller's /proc/self/mountinfo namespace",
            "mountinfo VFS options are not verified OVAL linux.partition effective options",
            "no original SCAP 1.4 scanner-result parity, Benchmark/Rule result or signed bundle"
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment", required=True, type=Path)
    parser.add_argument("--fixture-mountinfo", type=Path,
                        help="opt-in offline test; default reads actual Linux host")
    parser.add_argument("--namespace", default="mnt:[fixture]",
                        help="source namespace label, only for --fixture-mountinfo")
    args = parser.parse_args(argv)
    try:
        compiled = compile_assessment(json.loads(args.assessment.read_text(encoding="utf-8")))
        if args.fixture_mountinfo:
            observation = parse_mountinfo_text(
                args.fixture_mountinfo.read_text(encoding="utf-8"), args.namespace)
        else:
            observation = collect_current_linux_mounts()
        report = evaluate(compiled, observation, fixture_mode=bool(args.fixture_mountinfo))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"unsupported Assessment or input: {exc}\n")
    report["evaluated_at"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] in {"true", "false"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
