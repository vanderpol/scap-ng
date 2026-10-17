#!/usr/bin/env python3
"""#235: single require.items + require.condition authoring pilot.

Native 0.4 r3 Assessment -> existing reversible human AST -> fixed requirement
-> inverse -> byte-independent exact parsed source dictionary.

Research only. The source-exact *legacy distinctions* are not all desirable
native authoring choices; we retain them here until semantic normalization
is separately approved. This does NOT prove OVAL scanner/evidence parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import yaml
from jsonschema import Draft202012Validator

from research_english_first_04_complex import to_human, to_native
from research_english_first_04_compact_layout import compact, expand, PINNED
from research_english_first_04_auditor_candidate import to_auditor, from_auditor

SOURCE_PAIRS = {
    ("at_least_one", "every_item"): "at_least_one_all_match",
    ("at_least_one", "at_least_one_item"): "at_least_one_some_match",
    ("may_be_absent", "every_item"): "if_present_all_match",
    ("all_must_exist", "every_item"): "all_exist_all_match",
    ("at_least_one", "exactly_one_item"): "at_least_one_one_match",
    ("exactly_one", "exactly_one_item"): "exactly_one_one_match",
    ("exactly_one", "every_item"): "exactly_one_all_match",
    ("may_be_absent", "no_item"): "if_present_none_match",
    ("may_be_absent", "at_least_one_item"): "if_present_some_match",
    ("all_must_exist", "no_item"): "all_exist_none_match",
}
REVERSE_PAIRS = {value: key for key, value in SOURCE_PAIRS.items()}
STATE_FREE = {
    "at_least_one": "at_least_one",
    "exactly_one": "exactly_one",
    "none": "none",
    "all_must_exist": "all_exist",
    "may_be_absent": "if_present",
}
REVERSE_STATE_FREE = {v: k for k, v in STATE_FREE.items()}
CANONICAL_REDUCE = {
    "exactly_one_one_match": "exactly_one",
    "exactly_one_all_match": "exactly_one",
}

SAMPLES = {
    "linux-home": "authoring/shared/assessments/linux/other/home-mounted-nosuid-option.assessment.yaml",
    "linux-files": "authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml",
    "windows-wmi-rights": "authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml",
    "dns": "authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml",
    "apache": "authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml",
}

def to_fixed_requirement(node):
    if not isinstance(node, dict) or not node:
        raise ValueError("require must be an object")
    if set(node) == {"at_least_one_item_matches"}:
        if not isinstance(node["at_least_one_item_matches"], dict) or not node["at_least_one_item_matches"]:
            raise ValueError("State predicate missing")
        return {"items": "at_least_one_some_match",
                "condition": deepcopy(node["at_least_one_item_matches"])}
    if "items" not in node or not isinstance(node["items"], str):
        raise ValueError("require.items is mandatory")
    other = set(node) - {"items"}
    if not other:
        mode = STATE_FREE.get(node["items"])
        if mode is None:
            raise ValueError("invalid State-free Items choice")
        return {"items": mode}
    if len(other) != 1:
        raise ValueError("multiple conflicting Item match modes")
    predicate_key = next(iter(other))
    pair = (node["items"], predicate_key)
    if pair not in SOURCE_PAIRS:
        raise ValueError("unrecognized Item-match combination " + str(pair))
    predicate = node[predicate_key]
    if not isinstance(predicate, dict) or not predicate:
        raise ValueError("nonempty State condition is mandatory")
    return {"items": SOURCE_PAIRS[pair], "condition": deepcopy(predicate)}

def from_fixed_requirement(node):
    if not isinstance(node, dict) or "items" not in node:
        raise ValueError("require.items is mandatory")
    mode = node["items"]
    if set(node) == {"items"} and mode in REVERSE_STATE_FREE:
        return {"items": REVERSE_STATE_FREE[mode]}
    if set(node) != {"items", "condition"}:
        raise ValueError("require is exactly items and condition for State-bearing checks")
    if mode not in REVERSE_PAIRS:
        raise ValueError("unsupported Items mode or missing State condition " + str(mode))
    condition = node["condition"]
    if not isinstance(condition, dict) or not condition:
        raise ValueError("condition must be a nonempty predicate")
    if mode == "at_least_one_some_match":
        return {"at_least_one_item_matches": deepcopy(condition)}
    existence, match = REVERSE_PAIRS[mode]
    return {"items": existence, match: deepcopy(condition)}

def to_fixed(source):
    doc = to_auditor(compact(to_human(source)))
    for check in doc["checks"].values():
        check["require"] = to_fixed_requirement(check["require"])
    return doc

def from_fixed(candidate):
    if not isinstance(candidate, dict) or set(candidate) != {"metadata", "sources", "checks", "evaluate"}:
        raise ValueError("whole document has an invalid root")
    out = deepcopy(candidate)
    if not isinstance(out["checks"], dict) or not out["checks"]:
        raise ValueError("checks must be nonempty")
    for check in out["checks"].values():
        if "require" not in check:
            raise ValueError("a check must have require")
        check["require"] = from_fixed_requirement(check["require"])
    return to_native(expand(from_auditor(out)))

def check_negative_guards(doc, validator):
    first = next(iter(doc["checks"].values()))
    negatives = []
    malformed = deepcopy(doc)
    next(iter(malformed["checks"].values()))["require"]["unknown"] = True
    negatives.append(malformed)
    malformed = deepcopy(doc)
    next(iter(malformed["checks"].values()))["require"].pop("items")
    negatives.append(malformed)
    malformed = deepcopy(doc)
    check = next(iter(malformed["checks"].values()))
    check["require"]["items"] = "unlisted_choice"
    negatives.append(malformed)
    malformed = deepcopy(doc)
    next(iter(malformed["checks"].values()))["unexpected"] = 1
    negatives.append(malformed)
    for mutated in negatives:
        if validator.is_valid(mutated):
            raise AssertionError("editor schema admitted invalid requirement or key: " + str(mutated)[:140])
        try:
            from_fixed(mutated)
        except (ValueError, KeyError, TypeError):
            pass
        else:
            raise AssertionError("converter admitted invalid requirement")
    return len(negatives)

def census(archive, schema, examples=None):
    digest = hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest != PINNED:
        raise ValueError("unexpected pinned six-STIG SHA")
    contract = json.loads(Path(schema).read_text())
    Draft202012Validator.check_schema(contract)
    validator = Draft202012Validator(contract)
    counts = Counter()
    failures = []
    modes = Counter()
    sample_paths = {path: label for label, path in SAMPLES.items()}
    sample_data = {}
    per_folder = {}
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("source archive is corrupt")
        for path in sorted(z.namelist()):
            if not (path.startswith("authoring/") and "/assessments/" in path and path.endswith(".yaml")):
                continue
            src = (yaml.safe_load(z.read(path)) or {}).get("assessment") or {}
            if src.get("mode") != "automated" or not isinstance(src.get("tests"), dict) or not src["tests"]:
                continue
            counts["assessments"] += 1
            counts["source_tests"] += len(src["tests"])
            folder = path.split("/")[1]
            per_folder.setdefault(folder, Counter())["total"] += 1
            try:
                candidate = to_fixed(src)
                errors = list(validator.iter_errors(candidate))
                if errors:
                    err = errors[0]
                    raise ValueError("editor schema " + "/".join(str(x) for x in err.path) + ": " + err.message[:180])
                restored = from_fixed(candidate)
                if restored != src:
                    raise ValueError("source Assessment dictionary differed on reconstruction")
                counts["exact_documents"] += 1
                counts["exact_tests"] += len(src["tests"])
                counts["negative_guards"] += check_negative_guards(candidate, validator)
                per_folder[folder]["exact"] += 1
                for check in candidate["checks"].values():
                    modes[check["require"]["items"]] += 1
                if path in sample_paths:
                    sample_data[sample_paths[path]] = candidate
            except (ValueError, AssertionError, KeyError, TypeError) as exc:
                per_folder[folder]["rejected"] += 1
                counts["rejected"] += 1
                failures.append({"source": path, "error": str(exc)[:320]})
    if counts["assessments"] != 872 or counts["source_tests"] != 1375:
        raise AssertionError("corpus size mismatch")
    if examples:
        root=Path(examples)
        root.mkdir(parents=True,exist_ok=True)
        for label,doc in sample_data.items():
            (root/(label+".research.yaml")).write_text(
                "# yaml-language-server: $schema=../fixed-require.editor.schema.json\n"
                "# EXPERIMENTAL 0.4: not normative SCAP-NG; source exact if admitted.\n"
                +yaml.safe_dump(doc,sort_keys=False,allow_unicode=True,width=104))
    return {
       "source_sha256": digest,
       "status": "COMPLETE SOURCE-DICTIONARY EXACT INVERSION + JSON SCHEMA VALIDITY; NOT SCANNER PARITY",
       "counts": dict(counts),
       "per_source_folder": {k:dict(v) for k,v in sorted(per_folder.items())},
       "requirement_mode_distribution": dict(modes),
       "review_aliases": CANONICAL_REDUCE,
       "samples": sorted(sample_data),
       "rejects": failures,
       "limitations": [
           "Legacy exact-one and all_exist variants retained separately for source-dictionary exactness; not endorsed as author dropdowns.",
           "Condition predicates in the pilot schema are not capability-constrained to all 100 mappings; inverse parser must validate them.",
           "Source-exact structural inversion is not evidence of running scanner, OVAL XML source equivalence, or human readability.",
           "The source 0.4 native corpus contains one known contradictory none_exist-with-attached-State Assessment; no guess or quiet repair.",
       ],
    }

def markdown(report):
    c=report["counts"]
    lines=["# Fixed `items` + `condition` six-STIG editor pilot", "",
           "**Research-only. The authoring syntax is not approved.**", "",
           f"**{c['exact_documents']} of {c['assessments']}** complete automated Assessments reconstructed exactly",
           f"(**{c['exact_tests']} of {c['source_tests']}** Tests); {c['negative_guards']} malformed-input rejection checks passed.",
           "This is source-data structural equality only, **not OVAL scanner parity or independently demonstrated author usability**.",
           "",
           "## One consistent requirement form", "",
           "```yaml",
           "require:",
           "  items: at_least_one_all_match",
           "  condition: {mount_options: {at_least_one_value_is: nosuid}}",
           "```",
           "",
           "The `items` field is a **documented editor-dropdown enum**, `condition` is mandatory",
           "when the chosen Item mode evaluates a State, and absent for State-free checks.",
           "",
           "## Per source folder", "",
           "| Folder | Exact Assessments | Rejected |",
           "| --- | ---: | ---: |"]
    for folder,counts in report["per_source_folder"].items():
        lines.append(f"| {folder} | {counts.get('exact',0)} | {counts.get('rejected',0)} |")
    lines+=["", "## Remaining blockers", ""]
    for failure in report["rejects"]:
        lines.append("- `"+failure["source"]+"` — "+failure["error"])
    lines+=["", "## Meaning of this result", ""]
    lines.extend("- "+x for x in report["limitations"])
    lines+=["", "## Next acceptance gates", "",
            "1. Blind reading and hand-editing of these files by a security auditor.",
            "2. Enforce capability-specific State field/operator completions for all 100 capabilities, including WMI record fields and dynamic sources.",
            "3. Resolve/reject the single source contradiction with original DISA/NAVWAR provenance and six-state proof, not conversion guessing.",
            "4. Independently compile and execute representative native scanner results; validate error, unknown and incomplete behavior.",
            "5. Decide whether to retire legacy `all_exist` and collapse source-exact duplicate `exactly_one` labels under the native real-Item contract.",
            ""]
    return "\n".join(lines)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--schema",required=True)
    p.add_argument("--json",required=True)
    p.add_argument("--markdown",required=True)
    p.add_argument("--samples")
    a=p.parse_args()
    result=census(a.archive,a.schema,a.samples)
    Path(a.json).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    Path(a.markdown).write_text(markdown(result))
    print(json.dumps({"counts":result["counts"],"rejects":result["rejects"][:8],
                      "samples":result["samples"]},indent=2))
