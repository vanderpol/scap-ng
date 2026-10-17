#!/usr/bin/env python3
"""Research #235: fail-closed, exact-text inverse for five scoped readability samples.

This is NOT a normative SCAP-NG translator, runtime evaluator, or semantic
equivalence proof. It validates only the pinned, limited spelling/placement
transformations in field-presence-iteration/.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research" / "assessment-simplification" / "english-first-04"
SOURCE = HERE / "canonical-operators"
REVISED = HERE / "field-presence-iteration"
CASES = {
    "linux-home": "home",
    "windows-wmi-rights": "win",
    "linux-files": "linux",
    "apache": "apache",
    "dns": "dns",
}

def exactly(text: str, fragment: str, n: int, label: str) -> None:
    actual = text.count(fragment)
    if actual != n:
        raise AssertionError(f"{label}: expected {n}, found {actual}")

def forward(text: str, kind: str) -> str:
    out = re.sub(r"(?m)^      match:", "      matching_items:", text)
    out = re.sub(r"(?m)^            match:", "            matching_records:", out)
    if kind == "linux":
        exactly(out, "        presence: all\n", 2, "Linux source field policies")
        pat = (r"(    require:\n      items: (?:if_present|at_least_one)\n"
               r"      matching_items: all\n)(      fields:\n)")
        out, replaced = re.subn(pat, r"\1      state_fields_presence: required\n\2", out)
        if replaced != 2:
            raise AssertionError(f"Linux group scope count: {replaced}")
        out = out.replace("        presence: all\n", "")
    elif kind == "dns":
        exactly(out, "    all_state_fields_exist: true\n", 2, "DNS source field policies")
        out = out.replace("    all_state_fields_exist: true\n", "")
        pat = (r"(    require:\n      items: at_least_one\n"
               r"      matching_items: all\n)(      states:\n)")
        out, replaced = re.subn(pat, r"\1      state_fields_presence: required\n\2", out)
        if replaced != 2:
            raise AssertionError(f"DNS State scope count: {replaced}")
    elif kind == "apache":
        exactly(out, "when_present_matches_regex:", 1, "Apache regex")
        exactly(out, "when_present_greater_than_or_equal:", 1, "Apache bound")
        out = re.sub(r"(?m)^( *)when_present_matches_regex:",
                     r"\1presence: may_be_absent\n\1matches_regex:", out)
        out = re.sub(r"(?m)^( *)when_present_greater_than_or_equal:",
                     r"\1presence: may_be_absent\n\1greater_than_or_equal:", out)
    return out

def inverse(text: str, kind: str) -> str:
    out = text
    if kind == "linux":
        exactly(out, "      state_fields_presence: required\n", 2, "Linux alias")
        out = out.replace("      state_fields_presence: required\n", "")
        exactly(out, "    report_elements: all\n", 2, "Linux restored group anchors")
        out = out.replace("    report_elements: all\n",
                          "        presence: all\n    report_elements: all\n")
    elif kind == "dns":
        exactly(out, "      state_fields_presence: required\n", 2, "DNS alias")
        pat = (r"(    require:\n      items: at_least_one\n"
               r"      matching_items: all\n)      state_fields_presence: required\n"
               r"(      states:\n)")
        out, replaced = re.subn(pat, r"    all_state_fields_exist: true\n\1\2", out)
        if replaced != 2:
            raise AssertionError(f"DNS restored original flags: {replaced}")
    elif kind == "apache":
        exactly(out, "        presence: may_be_absent\n", 2, "Apache aliases")
        out, rcount = re.subn(r"(?m)^( *)presence: may_be_absent\n\1matches_regex:",
                              r"\1when_present_matches_regex:", out)
        out, ncount = re.subn(r"(?m)^( *)presence: may_be_absent\n\1greater_than_or_equal:",
                              r"\1when_present_greater_than_or_equal:", out)
        if (rcount, ncount) != (1, 1):
            raise AssertionError(f"Apache original operators: {(rcount,ncount)}")
    out = re.sub(r"(?m)^      matching_items:", "      match:", out)
    out = re.sub(r"(?m)^            matching_records:", "            match:", out)
    return out

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-yaml", action="store_true",
                    help="parse both files using PyYAML; fail if not installed")
    args = ap.parse_args()
    try:
        import yaml
    except ImportError:
        if args.require_yaml:
            raise
        yaml = None
    for name, kind in CASES.items():
        original = (SOURCE / f"{name}.canonical.research.yaml").read_text()
        revised = (REVISED / f"{name}.revised.research.yaml").read_text()
        expected = forward(original, kind)
        if revised != expected:
            raise AssertionError(f"{name}: revised file differs from source-derived candidate")
        if inverse(revised, kind) != original:
            raise AssertionError(f"{name}: not an exact inverse")
        if yaml is not None:
            old_ast = yaml.safe_load(original)
            new_ast = yaml.safe_load(revised)
            if sorted(old_ast["checks"]) != sorted(new_ast["checks"]):
                raise AssertionError(f"{name}: check IDs changed")
            if old_ast["evaluate"] != new_ast["evaluate"]:
                raise AssertionError(f"{name}: evaluation tree changed")
            if old_ast["sources"] != new_ast["sources"]:
                raise AssertionError(f"{name}: acquisition sources changed")
            if old_ast["metadata"] != new_ast["metadata"]:
                raise AssertionError(f"{name}: metadata/provenance changed")
        # Negative check: corruption of one quantifier must not pass validation.
        if "matching_items: all" in revised:
            bad = revised.replace("matching_items: all", "matching_items: at_least_one", 1)
            if bad == expected:
                raise AssertionError(f"{name}: negative mutation escaped")
        digest = hashlib.sha256(revised.encode()).hexdigest()[:12]
        print(f"PASS {name}: exact text inverse, candidate unchanged, "
              f"YAML parsed={yaml is not None}, sha256-prefix={digest}")
    print("Structural alias validation only; six-state runtime parity NOT verified.")

if __name__ == "__main__":
    main()
