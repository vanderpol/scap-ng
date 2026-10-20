#!/usr/bin/env python3
"""Build a source-roundtrippable Windows 11 0.4-A + all_items_must review ZIP.
Input is the pinned six-STIG r3 JSON authoring release. No native 0.4-A
schema amendment, scanner-runtime parity, or formal 0.4.0 ratification.
Refs #227 #232 #246.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

TOKEN_TO_EXISTENCE = {
    "at_least_one_exists_and_all_match": "one_or_more",
    "may_be_absent_and_all_match": "may_be_absent",
}
EXISTENCE_TO_TOKEN = {v: k for k, v in TOKEN_TO_EXISTENCE.items()}

def transform(doc):
    candidate = deepcopy(doc)
    edits = 0
    root = candidate.get("assessment")
    if not isinstance(root, dict) or root.get("mode") != "automated":
        return candidate, edits
    tests = root.get("tests") or {}
    for test in tests.values():
        if not isinstance(test, dict):
            raise ValueError("Test is not an object")
        token = test.get("collected_items_require", test.get("require"))
        if token not in TOKEN_TO_EXISTENCE or not isinstance(test.get("states"), list) or not test["states"]:
            continue
        if "collected_items_require" in test and "require" in test:
            raise ValueError("Ambiguous mixed requirement dialect")
        old_key = "collected_items_require" if "collected_items_require" in test else "require"
        states = test.pop("states")
        test.pop(old_key)
        test["require"] = {"items": TOKEN_TO_EXISTENCE[token], "all_items_must": states}
        edits += 1
    return candidate, edits

def restore(candidate, original):
    restored = deepcopy(candidate)
    orig = original.get("assessment")
    if not isinstance(orig, dict) or orig.get("mode") != "automated":
        if restored != original:
            raise ValueError("Modified non-automated document")
        return restored
    for name, test in (restored["assessment"].get("tests") or {}).items():
        source_test = orig["tests"][name]
        req = test.get("require")
        if not isinstance(req, dict):
            continue
        if set(req) != {"items", "all_items_must"}:
            raise ValueError("Unexpected proposed authoring keys")
        existence, states = req["items"], req["all_items_must"]
        if not isinstance(existence, str) or existence not in EXISTENCE_TO_TOKEN:
            raise ValueError("Unsupported existence token")
        if not isinstance(states, list) or not states:
            raise ValueError("State list required for all_items_must")
        target = "collected_items_require" if "collected_items_require" in source_test else "require"
        if target not in source_test:
            raise ValueError("Original Test has no recognized requirement")
        test.pop("require")
        test[target] = EXISTENCE_TO_TOKEN[existence]
        test["states"] = states
    if restored != original:
        raise ValueError("Full source-equivalence check failed")
    return restored

def run(source, out):
    counts = Counter()
    originals, candidates = {}, {}
    with zipfile.ZipFile(source) as z:
        for member in z.namelist():
            if member.endswith("/") or not member.startswith("authoring/") or not member.endswith(".json"):
                continue
            raw = z.read(member)
            doc = json.loads(raw)
            originals[member] = doc
            if "/ms_windows_11/" in member:
                candidate, n = transform(doc)
                counts["windows_source_documents"] += 1
                counts["changed_tests"] += n
                if n:
                    counts["changed_documents"] += 1
            else:
                candidate = deepcopy(doc)
            restore(candidate, doc)
            candidates[member] = candidate
    if not counts["windows_source_documents"] or not counts["changed_tests"]:
        raise ValueError("No actual Windows 11 Test transformations; inspect archive layout")
    if len(originals) != 4001:
        raise ValueError("Unexpected complete r3 source document count")
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for path, doc in sorted(candidates.items()):
            z.writestr(path, json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=False)+"\n")
        z.writestr("RESEARCH-ONLY-ALL-ITEMS-MUST.txt", (
            "0.4-A Windows 11 all_items_must review overlay. NOT native schema-valid 0.4-A, "
            "NOT signed, NOT scanner parity. Other STIG content is included unchanged "
            "at parsed-document level to retain cross-benchmark references. "
            "Only source-known one_or_more/all and may_be_absent/all Item requirements "
            "are rewritten, with original State payloads moved inline.\n"))
    manifest = {
        "source_archive": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "document_count": len(candidates),
        "scope": "Windows 11 Item requirements only; complete source AST reversible",
        "counts": dict(counts),
        "candidate_is_native_0_4a": False,
        "scanner_equivalence_tested": False,
    }
    out.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    run(args.source, args.out)
