#!/usr/bin/env python3
"""Research-only renderer for a local, Ansible-inspired SCAP-NG authoring form.

This is NOT a converter and NOT an accepted SCAP-NG grammar. It intentionally
fails closed when the existing converted Assessment uses dataflow or structures
that this research renderer has not proven safe to simplify.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import yaml


MODULE_NAMES = {
    "unix.file": "file",
    "unix.symlink": "symlink",
    "unix.password": "password",
    "unix.shadow": "shadow",
    "unix.sysctl": "sysctl",
    "unix.interface": "interface",
    "linux.systemdunitproperty": "systemd",
    "linux.partition": "partition",
    "linux.rpminfo": "rpm",
    "linux.selinuxsecuritycontext": "selinux_context",
    "independent.textfilecontent54": "text",
    "independent.variable": "variable",
    "independent.shellcommand": "command",
}

FUNCTION_KEYS = {
    "concat","split","count","unique","substring","begin","end","arithmetic",
    "time_difference","escape_regex","regex_capture","glob_to_regex","merge",
    "object_values","variable_component","object_component",
}

OP_NAMES = {
    "equals": None,
    "equal": None,
    "pattern match": "matches",
    "match": "matches",
    "not equal": "not_equal",
    "not_equal": "not_equal",
    "case insensitive equals": "equals_ci",
    "case_insensitive_equal": "equals_ci",
    "greater than": "gt",
    "greater_than": "gt",
    "greater than or equal": "gte",
    "greater_than_or_equal": "gte",
    "less than": "lt",
    "less_than": "lt",
    "less than or equal": "lte",
    "less_than_or_equal": "lte",
}


class Unsupported(Exception):
    pass


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def typed_value(value, datatype):
    if not isinstance(value, str):
        return value
    if datatype == "int":
        try:
            return int(value)
        except ValueError:
            return value
    if datatype == "float":
        try:
            return float(value)
        except ValueError:
            return value
    if datatype == "boolean":
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
    return value


def predicate(spec):
    if not isinstance(spec, dict):
        raise Unsupported("predicate_not_mapping")
    if spec.get("mask") is True:
        raise Unsupported("masked_predicate")
    if isinstance(spec.get("value"), dict):
        raise Unsupported("variable_or_structured_value")
    op = spec.get("operation")
    if op not in OP_NAMES:
        raise Unsupported("unsupported_operation:" + str(op))
    value = typed_value(spec.get("value"), spec.get("datatype"))
    short = OP_NAMES[op]
    if short is None:
        return value

    out = {short: value}
    # These alter evaluation and cannot disappear merely for prettiness.
    if spec.get("entity_check") not in {None, "all"}:
        out["entity_check"] = spec["entity_check"]
    if spec.get("entity_existence") not in {None, "at_least_one_exists"}:
        out["entity_existence"] = spec["entity_existence"]
    return out


def state_expr(state):
    if state is None:
        return None
    if not isinstance(state, dict):
        raise Unsupported("state_not_mapping")
    if "field" in state:
        return {state["field"]: predicate(state)}
    for op in ("all", "any"):
        if op in state:
            values = state[op]
            if not isinstance(values, list):
                raise Unsupported("state_boolean_not_list")
            return {op: [state_expr(x) for x in values]}
    raise Unsupported("unsupported_state_shape")


def collect_expr(collect):
    if not isinstance(collect, dict):
        raise Unsupported("collect_not_mapping")
    if collect.get("filters"):
        raise Unsupported("filters")
    cap = collect.get("capability")
    module = MODULE_NAMES.get(cap, cap.replace(".", "_") if isinstance(cap, str) else None)
    if not module:
        raise Unsupported("missing_capability")

    if "set" in collect:
        spec = collect["set"]
        if not isinstance(spec, dict):
            raise Unsupported("set_not_mapping")
        operator = (spec.get("operator") or "").lower()
        if operator != "union":
            raise Unsupported("set:" + (operator or "missing_operator"))
        members = spec.get("members") or []
        if not isinstance(members, list) or not members:
            raise Unsupported("set_union_members")
        sources = []
        for member in members:
            if not isinstance(member, dict) or set(member) != {"collect"}:
                raise Unsupported("set_union_noncollect_member")
            child_module, child = collect_expr(member["collect"])
            if child_module != module:
                raise Unsupported("set_union_mixed_capability")
            sources.append(child)
        result = {"sources": sources}
    else:
        result = {}
        select = collect.get("select") or {}
        if not isinstance(select, dict):
            raise Unsupported("select_not_mapping")
        for field, spec in select.items():
            result[field] = predicate(spec)

    if collect.get("behaviors"):
        # Keep behavior explicit in the research rendering. It is collection
        # semantics, not OVAL-only noise.
        result["behavior"] = collect["behaviors"]

    return module, result


def leaf(check_id, check):
    if not isinstance(check, dict):
        raise Unsupported("check_not_mapping")
    cap = check.get("capability")
    module, selection = collect_expr(check.get("collect"))
    if cap and MODULE_NAMES.get(cap, cap.replace(".", "_")) != module:
        raise Unsupported("check_collect_capability_mismatch")

    assertion = check.get("assert") or {}
    if not isinstance(assertion, dict):
        raise Unsupported("assert_not_mapping")

    expect = {}
    existence = assertion.get("existence")
    if existence is not None:
        expect["exists"] = existence
    check_quantifier = assertion.get("check")
    if check_quantifier is not None:
        expect["match"] = check_quantifier

    named_states = assertion.get("states")
    if named_states:
        if not isinstance(named_states, list):
            raise Unsupported("multiple_named_states_not_list")
        operator = (assertion.get("state_operator") or "AND").lower()
        if operator not in {"and", "or"}:
            raise Unsupported("state_operator:" + operator)
        key = "all" if operator == "and" else "any"
        values = []
        for item in named_states:
            if not isinstance(item, dict) or "state" not in item:
                raise Unsupported("named_state_shape")
            values.append(state_expr(item["state"]))
        expect[key] = values
    else:
        state = state_expr(assertion.get("state"))
        if state is not None:
            expect.update(state)

    return {
        module: selection,
        "expect": expect,
        "_source_check": check_id,
    }


def eval_expr(node, rendered):
    if not isinstance(node, dict):
        raise Unsupported("evaluate_not_mapping")
    if set(node) == {"check"}:
        ref = node["check"]
        if ref not in rendered:
            raise Unsupported("unknown_check_ref")
        return rendered[ref]
    for op in ("all", "any"):
        if set(node) == {op}:
            if not isinstance(node[op], list):
                raise Unsupported("evaluate_boolean_not_list")
            return {op: [eval_expr(x, rendered) for x in node[op]]}
    if set(node) == {"not"}:
        return {"not": eval_expr(node["not"], rendered)}
    raise Unsupported("unsupported_evaluate_shape")


def has_dataflow(assessment):
    if assessment.get("variables"):
        return "variables"
    for node in walk(assessment):
        keys = set(node)
        hit = sorted(keys & FUNCTION_KEYS)
        if hit:
            return "function:" + hit[0]
        # Set handling is delegated to collect_expr so simple UNION collection
        # can be rendered while complement/intersection continue to fail closed.
        if node.get("filters"):
            return "filters"
    return None


def render(assessment):
    if assessment.get("mode") != "automated":
        raise Unsupported("manual")
    reason = has_dataflow(assessment)
    if reason:
        raise Unsupported(reason)

    checks = assessment.get("checks") or assessment.get("tests") or {}
    rendered = {cid: leaf(cid, c) for cid, c in checks.items()}
    root = eval_expr(assessment.get("evaluate"), rendered)

    return {
        "research_assessment": {
            "status": "research_only_not_accepted_design",
            "source_assessment": assessment.get("id"),
            "title": assessment.get("assessment_title"),
            "check": root,
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    rules_dir = args.root / "rules"
    assessments_dir = args.root / "assessments"
    assessment_index = {}
    for path in assessments_dir.rglob("*.yaml"):
        doc = yaml.safe_load(path.read_text())
        a = (doc or {}).get("assessment")
        if isinstance(a, dict) and a.get("id"):
            assessment_index[a["id"]] = (path, a)

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "rendered").mkdir(exist_ok=True)

    rows = []
    counts = Counter()
    for rule_path in sorted(rules_dir.glob("*.yaml")):
        rule = yaml.safe_load(rule_path.read_text())["rule"]
        target = (rule.get("checks") or {}).get(rule.get("default_check"))
        if not target or target not in assessment_index:
            rows.append({"rule": rule.get("id"), "status": "blocked", "reason": "default_assessment_missing"})
            counts["blocked"] += 1
            continue
        assessment_path, assessment = assessment_index[target]
        try:
            doc = render(assessment)
        except Unsupported as exc:
            rows.append({
                "rule": rule["id"],
                "status": "not_rendered",
                "reason": str(exc),
                "assessment": assessment_path.as_posix(),
            })
            counts["not_rendered"] += 1
            counts["reason:" + str(exc)] += 1
            continue

        out = args.output / "rendered" / f"{rule['id']}.research.yaml"
        out.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        rows.append({
            "rule": rule["id"],
            "status": "rendered",
            "assessment": assessment_path.as_posix(),
            "output": out.as_posix(),
        })
        counts["rendered"] += 1

    summary = {
        "status": "research_only_not_accepted_design",
        "rules": len(rows),
        "counts": dict(counts),
        "rendered_percent": round(100 * counts["rendered"] / len(rows), 1) if rows else 0,
        "note": "Rendering success means only that the conservative local syntax could represent the serialized shape. It is not proof of source semantic equivalence.",
    }
    report = {"summary": summary, "rules": rows}
    (args.output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
