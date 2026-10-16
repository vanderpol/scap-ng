#!/usr/bin/env python3
"""Narrow source-exact English-first command check proof (research #235).

Protects complete source command, its error/collection settings, source Test
outcome quantification, and field presence/value quantification.
Does NOT replace dynamic Variable provenance or prove scanner results.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import json

import yaml

FIXTURE_ROOT = "focused-fixtures/source-backed/authoring"
FIXTURES = [
    {
        "id": "dns_signed",
        "path": "ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml",
        "test": "all-forward-lookup-zones-dnssec-signed-test",
        "verb": "exactly_one_value_equals",
        "expected_requirement": "only_one_exists_and_matches",
        "comparator": "equals",
    },
    {
        "id": "apache_required_keepalive",
        "path": "apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml",
        "test": "verify-that-keepalive-directive-defined-configured-on-in-httpd-conf-test",
        "verb": "has_only_values_matching_regex",
        "expected_requirement": "at_least_one_exists_and_all_match",
        "comparator": "matches_regex",
    },
    {
        "id": "apache_optional_keepalive",
        "path": "apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml",
        "test": "if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test",
        "verb": "if_present_all_values_match_regex",
        "expected_requirement": "may_be_absent_and_all_match",
        "comparator": "matches_regex",
    },
]


def exact(node, keys, message):
    if not isinstance(node, dict) or set(node) != set(keys):
        raise ValueError(f"invalid {message}, expected {sorted(keys)}")


def lower(candidate):
    exact(candidate, ("check", "inspect", "collect", "require"), "command check")
    if candidate["inspect"] != "independent.shellcommand":
        raise ValueError("unsupported collector")
    collect = candidate["collect"]
    if not isinstance(collect, dict):
        raise ValueError("invalid collection")
    if set(collect) not in (
        {"shell", "command", "error_if_exit_status_not_0", "error_if_stderr_exists"},
        {"shell", "command", "pattern", "error_if_exit_status_not_0", "error_if_stderr_exists"},
    ):
        raise ValueError("unproven shell collection fields")
    if collect["shell"] not in {"powershell", "bash"}:
        raise ValueError("unexpected shell")
    if not isinstance(collect["command"], (str, dict)) or not collect["command"]:
        raise ValueError("no command")
    if isinstance(collect["command"], dict):
        exact(collect["command"], ("variable",), "command variable ref")
    for k in ("error_if_exit_status_not_0", "error_if_stderr_exists"):
        if type(collect[k]) is not bool:
            raise ValueError(f"missing explicit Boolean {k}")

    req = candidate["require"]
    exact(req, ("at_least_one_item_exists", "every_collected_item"), "Test requirement")
    if req["at_least_one_item_exists"] is not True:
        raise ValueError("item existence not explicitly required")
    exact(req["every_collected_item"], ("stdout_line",), "per-command-result field")
    field = req["every_collected_item"]["stdout_line"]
    if not isinstance(field, dict) or len(field) != 1:
        raise ValueError("expected one documented stdout_line operator")
    operator, value = next(iter(field.items()))
    macros = {
        "exactly_one_value_equals": ("only_one_exists_and_matches", "equals"),
        "has_only_values_matching_regex": ("at_least_one_exists_and_all_match", "matches_regex"),
        "if_present_all_values_match_regex": ("may_be_absent_and_all_match", "matches_regex"),
    }
    if operator not in macros:
        raise ValueError("unsupported stdout_line operator")
    if not isinstance(value, str) or not value:
        raise ValueError("requires nonempty literal comparator operand")
    existence_and_match, comparison = macros[operator]
    if not isinstance(candidate["check"], str) or not candidate["check"]:
        raise ValueError("missing check title")
    return {
        "test_title": candidate["check"],
        "capability": "independent.shellcommand",
        "object": {"capability": "independent.shellcommand", "collect": deepcopy(collect)},
        "states": [{"stdout_line": {"require": existence_and_match, comparison: value}}],
        "reported_elements": "all",
        "collected_items_require": "at_least_one_exists_and_all_match",
    }


def sample(root, row):
    path = Path(root) / FIXTURE_ROOT / row["path"]
    with path.open(encoding="utf8") as f:
        test = yaml.safe_load(f)["assessment"]["tests"][row["test"]]
    actual = deepcopy(test)
    obj = actual["object"]
    if not isinstance(obj, dict):
        raise ValueError("expected real inline command Object")
    obj.pop("object_title", None)
    exact(actual["states"][0], ("stdout_line",), "source State field")
    field = actual["states"][0]["stdout_line"]
    if field.get("require") != row["expected_requirement"]:
        raise AssertionError("wrong source field requirement for " + row["id"])
    if set(field) != {"require", row["comparator"]}:
        raise AssertionError("unhandled field operator for " + row["id"])
    return actual, {
        "check": actual["test_title"],
        "inspect": actual["capability"],
        "collect": deepcopy(obj["collect"]),
        "require": {
            "at_least_one_item_exists": True,
            "every_collected_item": {"stdout_line": {row["verb"]: field[row["comparator"]]}},
        },
    }


def run(root):
    results = []
    negatives = 0
    for row in FIXTURES:
        original, candidate = sample(root, row)
        if lower(candidate) != original:
            raise AssertionError("non-identical Test reconstruction " + row["id"])
        # Test/State/execution flags are required; no silent omission or default.
        wrong = deepcopy(candidate)
        wrong["require"]["at_least_one_item_exists"] = False
        try:
            lower(wrong)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError("false existence accepted")
        wrong = deepcopy(candidate)
        wrong["collect"].pop("error_if_stderr_exists")
        try:
            lower(wrong)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError("missing source error flag accepted")
        wrong = deepcopy(candidate)
        wrong["require"]["every_collected_item"]["stdout_line"] = {"contains": "irrelevant"}
        try:
            lower(wrong)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError("ambiguous operator accepted")
        changed = deepcopy(original)
        changed["states"][0]["stdout_line"]["require"] = "none_exist"
        if lower(candidate) == changed:
            raise AssertionError("wrong field cardinality reconstructed")
        negatives += 1
        results.append({"id": row["id"], "source": row["path"], "test": row["test"],
                        "command": candidate["collect"]["command"],
                        "field_macro": row["verb"], "field_requirement": row["expected_requirement"],
                        "result": "exact Test source inversion"})
    return {"status": "THREE SOURCE-EXACT COMMAND TESTS; NOT SCANNER RUNTIME PARITY",
            "source_fixture_commit": "99cbceae8d594c44cb509df95975ac1676a2b44a",
            "results": results, "negative_guards": negatives,
            "limits": "No dynamic variable recomputation, scanner run or full Assessment equality claimed"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture-root", required=True)
    p.add_argument("--report")
    a = p.parse_args()
    result = run(a.fixture_root)
    if a.report:
        Path(a.report).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
