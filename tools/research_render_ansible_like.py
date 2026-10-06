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


def predicate(spec, variables=None):
    if not isinstance(spec, dict):
        raise Unsupported("predicate_not_mapping")
    if spec.get("mask") is True:
        raise Unsupported("masked_predicate")
    allowed={
        "operation","datatype","mask","value","entity_check","entity_existence",
        "variable_check","nil","field",
    }
    extra=set(spec)-allowed
    if extra:
        raise Unsupported("predicate_attributes:" + ",".join(sorted(extra)))

    raw=spec.get("value")
    if isinstance(raw, dict):
        if set(raw)!={"variable"} or variables is None:
            raise Unsupported("variable_or_structured_value")
        var_id=raw["variable"]
        var=variables.get(var_id)
        if not isinstance(var,dict) or var.get("kind")!="constant":
            raise Unsupported("variable_nonconstant")
        expr=var.get("expression")
        if not isinstance(expr,dict) or set(expr)!={"literal"}:
            raise Unsupported("variable_nonliteral")
        values=expr["literal"]
        if not isinstance(values,list):
            values=[values]
        values=[typed_value(v,spec.get("datatype")) for v in values]
        op=spec.get("operation")
        if op not in OP_NAMES:
            raise Unsupported("constant_variable_operation:" + str(op))
        check=spec.get("variable_check")
        quant={
            "at least one":"any",
            "any":"any",
            "all":"all",
            "only one":"exactly_one",
            "none satisfy":"none",
        }.get(check)
        if quant is None:
            raise Unsupported("constant_variable_check:" + str(check))
        short=OP_NAMES[op]
        if short is None:
            key={
                "any":"one_of",
                "all":"all_of",
                "exactly_one":"exactly_one_of",
                "none":"none_of",
            }[quant]
        else:
            key=f"{short}_{quant}"
        return {key: values}

    if spec.get("variable_check") is not None:
        raise Unsupported("variable_check_without_variable")

    op = spec.get("operation")
    if op not in OP_NAMES:
        raise Unsupported("unsupported_operation:" + str(op))
    value = typed_value(raw, spec.get("datatype"))
    short = OP_NAMES[op]
    if short is None:
        out=value
    else:
        out={short:value}

    if spec.get("nil") is True:
        if not isinstance(out,dict):
            out={"value":out}
        out["nil"]=True
    # These alter evaluation and cannot disappear merely for prettiness.
    if spec.get("entity_check") not in {None, "all"}:
        if not isinstance(out,dict): out={"value":out}
        out["entity_check"] = spec["entity_check"]
    if spec.get("entity_existence") not in {None, "at_least_one_exists"}:
        if not isinstance(out,dict): out={"value":out}
        out["entity_existence"] = spec["entity_existence"]
    return out


def state_expr(state, variables=None):
    if state is None:
        return None
    if not isinstance(state, dict):
        raise Unsupported("state_not_mapping")
    if "field" in state:
        return {state["field"]: predicate(state, variables)}
    for op in ("all", "any"):
        if op in state:
            values = state[op]
            if not isinstance(values, list):
                raise Unsupported("state_boolean_not_list")
            return {op: [state_expr(x, variables) for x in values]}
    raise Unsupported("unsupported_state_shape")


def collect_expr(collect, variables=None):
    if not isinstance(collect, dict):
        raise Unsupported("collect_not_mapping")
    filters = collect.get("filters") or []
    if not isinstance(filters, list):
        raise Unsupported("filters_not_list")
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
            child_module, child = collect_expr(member["collect"], variables)
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
            result[field] = predicate(spec, variables)

    if filters:
        grouped = {"include": [], "exclude": []}
        for item in filters:
            if not isinstance(item, dict):
                raise Unsupported("filter_not_mapping")
            action = item.get("action")
            if action not in {"include", "exclude"}:
                raise Unsupported("filter_action:" + str(action))
            match = item.get("match")
            if not isinstance(match, dict):
                raise Unsupported("filter_match")
            grouped[action].append(state_expr(match, variables))
        for action, values in grouped.items():
            if values:
                result[action] = values[0] if len(values) == 1 else values

    if collect.get("behaviors"):
        # Keep behavior explicit in the research rendering. It is collection
        # semantics, not OVAL-only noise.
        result["behavior"] = collect["behaviors"]

    return module, result


def leaf(check_id, check, variables=None):
    if not isinstance(check, dict):
        raise Unsupported("check_not_mapping")
    cap = check.get("capability")
    module, selection = collect_expr(check.get("collect"), variables)
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
            values.append(state_expr(item["state"], variables))
        expect[key] = values
    else:
        state = state_expr(assertion.get("state"), variables)
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


def constant_literal_variables(assessment):
    variables=assessment.get("variables") or {}
    for var in variables.values():
        if not isinstance(var,dict) or var.get("kind")!="constant":
            return None
        expr=var.get("expression")
        if not isinstance(expr,dict) or set(expr)!={"literal"}:
            return None
    return variables


def has_dataflow(assessment):
    variables=assessment.get("variables") or {}
    if variables and constant_literal_variables(assessment) is None:
        return "variables"
    for node in walk(assessment):
        keys = set(node)
        hit = sorted(keys & FUNCTION_KEYS)
        if hit:
            return "function:" + hit[0]
        # Set handling is delegated to collect_expr so simple UNION collection
        # can be rendered while complement/intersection continue to fail closed.
        # Filters are handled locally by collect_expr and remain explicit as
        # include/exclude clauses in the research rendering.
    return None


def render(assessment):
    if assessment.get("mode") != "automated":
        raise Unsupported("manual")
    reason = has_dataflow(assessment)
    if reason:
        raise Unsupported(reason)

    checks = assessment.get("checks") or assessment.get("tests") or {}
    variables = constant_literal_variables(assessment) or {}
    rendered = {cid: leaf(cid, c, variables) for cid, c in checks.items()}
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
