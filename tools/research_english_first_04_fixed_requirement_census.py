#!/usr/bin/env python3
"""Issue #235: pinned six-STIG requirement-vocabulary sensitivity census.

Counts source-exact Item and explicit field/record requirement ENUM use only.
This deliberately does NOT count entire Assessment grammar, scanner parity,
or validated YAML rendering. No source is rewritten.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import zipfile
import yaml

SOURCE_SHA256 = "03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"

# Hypothetical canonical entries in require.items (one dropdown).
# These are source labels, not proposed published key spellings.
ITEM_ALL = {
    "at_least_one_exists_and_all_match",
    "at_least_one_exists_and_some_match",
    "may_be_absent_and_all_match",
    "all_exist_and_all_match",
    "at_least_one_exists_and_only_one_matches",
    "only_one_exists_and_only_one_matches",
    "only_one_exists_and_matches",
    "may_be_absent_and_none_match",
    "may_be_absent_and_some_match",
    "all_exist_and_none_match",
}
STATE_FREE_ALL = {
    "at_least_one_exists", "none_exist", "all_exist",
    "any_exist", "may_be_absent", "only_one_exists",
}
FIELD_ALL = ITEM_ALL | {"at_least_one_exists_and_none_match",
                         "all_exist_and_none_match", "none_exist"}
BASIC = {"at_least_one_exists_and_all_match",
         "at_least_one_exists_and_some_match",
         "may_be_absent_and_all_match"}
PRACTICAL = BASIC | {"all_exist_and_all_match", "only_one_exists_and_matches"}
STAGES = {
    "basic": {"items": BASIC, "field": BASIC | {"none_exist"},
              "statefree": {"at_least_one_exists", "none_exist"}},
    "practical": {"items": PRACTICAL, "field": PRACTICAL | {"none_exist"},
                  "statefree": STATE_FREE_ALL},
    "exhaustive_vocabulary": {"items": ITEM_ALL, "field": FIELD_ALL,
                               "statefree": STATE_FREE_ALL},
}
COMPARISON_META = {"require", "datatype", "value_match", "redact_result"}
STATE_LOGIC = {"and", "or", "not", "all", "any", "one", "odd"}
SAMPLES = 5


def explicit_modes(node):
    """Find explicitly authored nested State/record requirement values.

    We intentionally do not assume that an unannotated field inherits
    any particular requirement. That needs its own scope/type validator.
    """
    if isinstance(node, list):
        for element in node:
            yield from explicit_modes(element)
    elif isinstance(node, dict):
        for key, value in node.items():
            if key == "require" and isinstance(value, str):
                yield value
            else:
                yield from explicit_modes(value)


def shape_flags(test):
    states = test.get("states")
    flags = set()
    if not states:
        return flags
    if isinstance(states, list) and len(states) > 1:
        flags.add("multiple_states")
    def visit(node):
        if isinstance(node, list):
            for child in node:
                visit(child)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key in STATE_LOGIC:
                    flags.add("logical_conditions")
                if key in {"record", "fields"}:
                    flags.add("nested_record")
                if key == "value_match":
                    flags.add("expected_value_quantifier")
                if key == "variable":
                    flags.add("variable_operand")
                visit(value)
    visit(states)
    return flags


def single_scalar_state(test):
    """A strict syntax shape that could fit one condition line.

    This is NOT a claim that the quantifiers for that State are valid.
    """
    states = test.get("states")
    if not isinstance(states, list) or len(states) != 1 or shape_flags(test):
        return False
    state = states[0]
    if not isinstance(state, dict) or len(state) != 1:
        return False
    field, details = next(iter(state.items()))
    if field in STATE_LOGIC or not isinstance(details, dict):
        return False
    operators = [key for key in details if key not in COMPARISON_META]
    return (len(operators) == 1 and
            isinstance(details[operators[0]], (str, int, float, bool)) and
            details[operators[0]] is not None)


def census(path):
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != SOURCE_SHA256:
        raise ValueError("unexpected six-STIG content digest: " + sha)
    totals = Counter()
    modes = Counter()
    field_modes = Counter()
    shapes = Counter()
    by_stream = defaultdict(lambda: {stage: Counter() for stage in STAGES})
    breakdown = {stage: Counter() for stage in STAGES}
    residual = {stage: [] for stage in STAGES}
    problems = []
    with zipfile.ZipFile(path) as archive:
        if archive.testzip():
            raise ValueError("corrupt source archive")
        for name in sorted(archive.namelist()):
            if not (name.startswith("authoring/") and "/assessments/" in name and
                    name.endswith(".yaml")):
                continue
            source = (yaml.safe_load(archive.read(name)) or {}).get("assessment") or {}
            tests = source.get("tests")
            if source.get("mode") != "automated" or not isinstance(tests, dict) or not tests:
                continue
            stream = name.split("/")[1]
            totals["assessments"] += 1
            assessment_admitted = {stage: True for stage in STAGES}
            for title, test in tests.items():
                totals["tests"] += 1
                source_mode = test.get("collected_items_require")
                has_state = "states" in test
                modes[str(source_mode)] += 1
                fields = list(explicit_modes(test.get("states") or []))
                if "state_fields_require" in test:
                    fields.append(test["state_fields_require"])
                for field_mode in fields:
                    field_modes[str(field_mode)] += 1
                flags = shape_flags(test)
                for flag in flags:
                    shapes[flag] += 1
                if single_scalar_state(test):
                    shapes["single_scalar_condition"] += 1
                if has_state and source_mode == "none_exist":
                    problems.append({"source": name, "test": title,
                                     "reason": "none_exist with attached State"})
                for stage, sets in STAGES.items():
                    valid_item = source_mode in sets["items" if has_state else "statefree"]
                    valid_fields = all(mode in sets["field"] for mode in fields)
                    # Known source contradiction is NOT accepted even if the enum is present.
                    source_anomaly = has_state and source_mode == "none_exist"
                    if valid_item:
                        breakdown[stage]["item_modes_covered"] += 1
                    else:
                        breakdown[stage]["item_modes_unsupported"] += 1
                    breakdown[stage]["field_modes_total"] += len(fields)
                    breakdown[stage]["field_modes_covered"] += sum(m in sets["field"] for m in fields)
                    if valid_item and valid_fields and not source_anomaly:
                        breakdown[stage]["complete_explicit_modes_tests"] += 1
                        by_stream[stream][stage]["tests_covered"] += 1
                    else:
                        assessment_admitted[stage] = False
                        by_stream[stream][stage]["tests_rejected"] += 1
                        if len(residual[stage]) < 50:
                            residual[stage].append({
                                "source": name, "test": title,
                                "item_mode": source_mode,
                                "unrecognized_field_modes": sorted({str(m) for m in fields if m not in sets["field"]}),
                                "state_attached_to_none_exist": source_anomaly,
                            })
                    by_stream[stream][stage]["tests_total"] += 1
            for stage, admitted in assessment_admitted.items():
                key = "assessments_covered" if admitted else "assessments_rejected"
                breakdown[stage][key] += 1
                by_stream[stream][stage][key] += 1

    assert totals == {"assessments": 872, "tests": 1375}, totals
    for stage, data in breakdown.items():
        assert data["assessments_covered"] + data["assessments_rejected"] == 872
        assert data["complete_explicit_modes_tests"] + sum(
            s[stage]["tests_rejected"] for s in by_stream.values()) == 1375
    return {
        "status": "READ-ONLY REQUIREMENT ENUM COVERAGE, not full syntax or scanner semantics",
        "pinned_sha256": sha,
        "counts": dict(totals),
        "stages": {s: dict(c) for s, c in breakdown.items()},
        "source_item_mode_frequency": dict(modes.most_common()),
        "source_explicit_field_mode_frequency": dict(field_modes.most_common()),
        "source_complexity": dict(shapes.most_common()),
        "per_source_folder": {k: {s: dict(c) for s, c in v.items()}
                              for k, v in sorted(by_stream.items())},
        "limited_residual_samples": residual,
        "source_anomalies": problems,
        "scope_limits": [
            "Folder 'shared' is reused across benchmarks; source-folder coverage is not Rule coverage.",
            "This experiment inventories canonical enum modes; it does not validate the proposed items/condition YAML parser or actual readability.",
            "Explicit field requirement entries are counted; implicit scoped field inheritance and record/evaluate semantics need independent full-AST validation.",
            "Collector, Object, Set, variable, evidence, error and six-state runtime behavior are NOT established by enum coverage.",
            "Do not rewrite valid STIG source to raise a percentage. Isolate defects and differential-prove any changed semantics."
        ]
    }


def markdown(result):
    lines = [
        "# Fixed requirement vocabulary — six-STIG sensitivity audit",
        "",
        "**Research only — no proposed syntax is approved.**",
        "",
        "The source is the same pinned six-STIG 0.4 r3 archive used by the English-first corpus audit.",
        "This is **requirement-choice enum coverage**, not whole language coverage or scanner validation.",
        "",
        "| Candidate dropdown size | Complete explicit modes / Tests | Complete explicit modes / Assessments |",
        "| --- | ---: | ---: |",
    ]
    for stage, data in result["stages"].items():
        lines.append(f'| {stage} | {data.get("complete_explicit_modes_tests", 0)}/1375 '
                     f'({100*data.get("complete_explicit_modes_tests",0)/1375:.2f}%) | '
                     f'{data.get("assessments_covered",0)}/872 '
                     f'({100*data.get("assessments_covered",0)/872:.2f}%) |')
    lines.extend(["", "## Coverage by source folder",
                  "", "Folder 'shared' is not a seventh STIG. Its Assessments may be used in several streams.",
                  "", "| Source folder | Practical Test modes | Practical Assessments |",
                  "| --- | ---: | ---: |"])
    for folder, stages in result["per_source_folder"].items():
        c = stages["practical"]
        lines.append(f'| {folder} | {c.get("tests_covered",0)}/{c.get("tests_total",0)} '
                     f'| {c.get("assessments_covered",0)}/'
                     f'{c.get("assessments_covered",0)+c.get("assessments_rejected",0)} |')
    lines.extend(["", "## Frequent Item requirements", "",
                  "| Source requirement | Tests |", "| --- | ---: |"])
    for mode, count in result["source_item_mode_frequency"].items():
        lines.append(f"| `{mode}` | {count} |")
    lines.extend(["", "## Frequent explicit field/record requirements", "",
                  "| Source requirement | Occurrences |", "| --- | ---: |"])
    for mode, count in result["source_explicit_field_mode_frequency"].items():
        lines.append(f"| `{mode}` | {count} |")
    lines.extend(["", "## Practical-vocabulary residual examples", ""])
    for record in result["limited_residual_samples"]["practical"][:22]:
        lines.append(f'- `{record["source"]}` — `{record["test"]}`: '
                     f'Item `{record["item_mode"]}`, field modes '
                     f'`{", ".join(record["unrecognized_field_modes"])}`; '
                     f'anomaly={record["state_attached_to_none_exist"]}')
    lines.extend(["", "## Limits and decision rule", ""])
    lines.extend("- " + x for x in result["scope_limits"])
    lines.extend(["", "**98% is a review trigger, not permission to change valid results.**",
                  "Each residual needs a source-backed classification: bad source/converter, safe authoring abstraction, "
                  "necessary vocabulary extension, or valid exception requiring explicit syntax.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--json", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()
    report = census(args.archive)
    Path(args.json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    Path(args.markdown).write_text(markdown(report))
    print(json.dumps({"stages": report["stages"],
                      "source_anomalies": report["source_anomalies"]}, indent=2))


if __name__ == "__main__":
    main()
