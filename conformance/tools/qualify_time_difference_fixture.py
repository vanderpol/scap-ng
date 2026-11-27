#!/usr/bin/env python3
"""Compare the pinned OVAL time_difference Definition with current RI Test evaluation."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
from hashlib import sha256
from itertools import product
import json
import re
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from qualify_merge_fixture import INDEPENDENT, OVAL, require_equal
from runner import CONFORMANCE, load, validator

FIXTURE = CONFORMANCE / "variable-time-difference"
DATE_PATTERNS = {
    "year_month_day": ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"),
    "month_day_year": ("%m-%d-%Y", "%m/%d/%Y", "%b, %d %Y", "%B, %d %Y"),
    "day_month_year": ("%d-%m-%Y", "%d/%m/%Y"),
}
OPERATIONS = {"equals": "equals", "greater than": "greater_than"}


def unix_seconds(value, format_name):
    if format_name == "seconds_since_epoch":
        return int(value)
    if format_name == "win_filetime":
        return int(value, 16) // 10_000_000 + int(datetime(1601, 1, 1, tzinfo=UTC).timestamp())
    for date_pattern in DATE_PATTERNS[format_name]:
        for time_pattern in ("", " %H:%M:%S", "T%H%M%S"):
            try:
                parsed = datetime.strptime(value, date_pattern + time_pattern)
            except ValueError:
                continue
            return int(parsed.replace(tzinfo=UTC).timestamp())
    raise ValueError(f"Unrecognized source date {value!r} for {format_name}")


def object_variable(nodes, object_ref):
    obj = nodes[object_ref]
    require_equal(obj.tag, INDEPENDENT + "variable_object", object_ref)
    return obj.findtext(INDEPENDENT + "var_ref")


def operand(nodes, component):
    if component.tag == OVAL + "literal_component":
        return None, [component.text]
    require_equal(component.tag, OVAL + "object_component", "time_difference component")
    require_equal(component.attrib["item_field"], "value", "time_difference Object component")
    variable_ref = object_variable(nodes, component.attrib["object_ref"])
    constant = nodes[variable_ref]
    require_equal(constant.tag, OVAL + "constant_variable", variable_ref)
    return variable_ref, [value.text for value in constant.findall(OVAL + "value")]


def source_tests(raw, expected):
    root = ET.fromstring(raw)
    nodes = {node.attrib["id"]: node for node in root.iter() if "id" in node.attrib}
    definition = nodes[expected["definition"]]
    criteria = definition.find(OVAL + "criteria")
    require_equal(criteria.get("operator", "AND"), "AND", "source Definition operator")
    tests = [row.attrib["test_ref"] for row in criteria]
    require_equal(sorted(tests), sorted([*expected["static_expected_seconds"], expected["clock_case"]["test"]]),
                  "source Definition Tests")
    for source_id in tests:
        test = nodes[source_id]
        require_equal(test.tag, INDEPENDENT + "variable_test", source_id)
        variable = object_variable(nodes, test.find(INDEPENDENT + "object").attrib["object_ref"])
        function = nodes[variable].find(OVAL + "time_difference")
        state_node = nodes[test.find(INDEPENDENT + "state").attrib["state_ref"]]
        value = state_node.find(INDEPENDENT + "value")
        formats = {key: function.get(key, "year_month_day") for key in ("format_1", "format_2")}
        operands = [operand(nodes, component) for component in function]
        yield source_id, variable, formats, operands, OPERATIONS[value.get("operation", "equals")], int(value.text)


def check_conversion(assessment, variable_ids, test_id, variable, formats, operands, operation, target):
    test = assessment["tests"][test_id]
    require_equal(test["capability"], "variable.value", test_id)
    require_equal(test["variable"], variable_ids[variable], test_id)
    require_equal(test["require"]["fields"]["value"], {operation: target}, test_id)
    variables = assessment["variables"]
    function = variables[test["variable"]]["expression"]["time_difference"]
    for name, value in formats.items():
        require_equal(function.get(name, "year_month_day"), value, f"{test_id} {name}")
    for (source_ref, source_values), native_value in zip(operands, function["values"], strict=True):
        if source_ref is None:
            value = native_value["literal"]["value"]
            require_equal([str(value)], source_values, test_id)
        else:
            require_equal(native_value, {"variable": variable_ids[source_ref]}, test_id)
            value = variables[native_value["variable"]]["expression"]["literal"]["value"]
            require_equal(value, source_values, test_id)


def qualify(self_assertion, converted, ri, go):
    expected = load(FIXTURE / "expected.json")
    raw = (self_assertion / expected["source_path"]).read_bytes()
    digest = sha256(raw).hexdigest()
    require_equal(digest, expected["source_sha256"], "source XML bytes")
    trace = load(converted / "source-trace.json")
    require_equal(trace["source_commit"], expected["source_pin"], "source trace commit")
    require_equal(trace["source_sha256"], digest, "source trace XML bytes")
    require_equal(trace["definition_id"], expected["definition"], "source trace Definition")
    test_ids = {row["source_id"]: row["native_id"]
                for row in trace["native_identities"] if row["kind"] == "test"}
    variable_ids = {row["source_id"]: row["native_id"]
                    for row in trace["native_identities"] if row["kind"] == "variable"}
    document = load(converted / "assessment.json")
    validator().validate(document)

    cases = []
    outcomes = []
    clock_case = expected["clock_case"]
    for source_id, variable, formats, operands, operation, target in source_tests(raw, expected):
        test_id = test_ids[source_id]
        check_conversion(document["assessment"], variable_ids, test_id, variable, formats, operands,
                         operation, target)
        if source_id == clock_case["test"]:
            require_equal(operands, [(None, [str(clock_case["operand_seconds_since_epoch"])])], source_id)
            require_equal((formats["format_2"], operation, target),
                          ("seconds_since_epoch", "greater_than", clock_case["strictly_greater_than"]), source_id)
            for clock, row in clock_case["variants"].items():
                delta = int(datetime.fromisoformat(clock).timestamp()) - clock_case["operand_seconds_since_epoch"]
                require_equal(row, {"seconds": delta, "outcome": str(delta > target).lower()}, clock)
                cases.append({"test": test_id, "clock": clock})
                outcomes.append((source_id, delta, row["outcome"], 1))
        else:
            left, right = operands
            values = [unix_seconds(a, formats["format_1"]) - unix_seconds(b, formats["format_2"])
                      for a, b in product(left[1], right[1])]
            require_equal(set(values), {expected["static_expected_seconds"][source_id]}, source_id)
            cartesian = expected["cartesian_case"]
            require_equal(len(values), cartesian["values"] if source_id == cartesian["test"] else 1, source_id)
            require_equal((operation, target), ("equals", values[0]), source_id)
            cases.append({"test": test_id})
            outcomes.append((source_id, values[0], "true", len(values)))
    require_equal({source_id for source_id, _, _, _ in outcomes}, set(test_ids), "converted source Tests")

    package = {"request": {"schema_family_sha256": trace["assessment_closure_sha256"],
                           "assessment_document": document, "bindings": {}}, "cases": cases}
    run = subprocess.run([go, "run", str(FIXTURE / "ri-replay.go")], cwd=ri, input=json.dumps(package),
                         capture_output=True, text=True, timeout=120)
    if run.returncode != 0:
        raise ValueError(f"RI replay failed: {run.stderr}")
    leaves = {}
    clock_results = {}
    for case, (source_id, seconds, outcome, value_count), decision in zip(
        cases, outcomes, json.loads(run.stdout), strict=True
    ):
        require_equal(decision["technical_outcome"], outcome, source_id)
        require_equal(decision["test_pointer"], "/assessment/tests/" + case["test"], source_id)
        explanation = decision["explanation"]
        if value_count == 1 and not re.search(rf'\bvalue {seconds}\b', explanation):
            raise ValueError(f"RI did not report the independently computed value for {source_id}: {explanation}")
        cardinality = decision["cardinality"]
        require_equal(cardinality["values_found"], value_count, source_id)
        require_equal(cardinality["values_matching"], value_count if outcome == "true" else 0, source_id)
        entry = {"native_test": case["test"], "outcome": outcome, "explanation": explanation,
                 "values_found": cardinality["values_found"], "values_matching": cardinality["values_matching"]}
        if "clock" in case:
            clock_results[case["clock"]] = entry
        else:
            leaves[source_id] = entry
    return {
        "format": "scap-ng-time-difference-source-witness-receipt-1",
        "source_sha256": digest,
        "native_assessment_sha256": sha256((converted / "assessment.json").read_bytes()).hexdigest(),
        "converter_revision": trace["converter_commit"],
        "schema_commit": trace["schema_commit"],
        "ri_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ri, text=True).strip(),
        "leaves": leaves,
        "fixed_clock": clock_results,
        "scope": "Direct RI Test evaluation of the pinned static and unary clock cases. No Assessment rollup.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-assertion", type=Path, required=True)
    parser.add_argument("--converted", type=Path, required=True)
    parser.add_argument("--ri", type=Path, required=True)
    parser.add_argument("--go", default="go")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = qualify(args.self_assertion, args.converted, args.ri, args.go)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check and (FIXTURE / "ri-receipt.json").read_text(encoding="utf-8") != rendered:
        raise SystemExit("time_difference receipt differs from the replay")
    print(rendered, end="")
