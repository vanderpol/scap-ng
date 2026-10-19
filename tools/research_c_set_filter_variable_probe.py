#!/usr/bin/env python3
"""Refs #245: post-collection C Set/Filter/Variable research probe.

Preserves A source references and Test documentation, and exercises a bounded
subset on explicit COMPLETE provider Items. Does not collect, compile complete
A/OVAL sources, evaluate Tests, or certify six-state SCAP 1.4 semantics.
Unsupported cases fail closed; no implicit result on incomplete evidence.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from v04_a_authoring_graph_index import canonical_json
from v04_a_dataflow_index import index_assessment_dataflow


class UnsupportedSourceSemantics(ValueError):
    """No runtime compliance conclusion can be inferred for this input."""


def probe_complete_dataflow(assessment, snapshots):
    source = deepcopy(assessment)
    if not isinstance(source, dict) or source.get("mode") != "automated":
        raise ValueError("automated source Assessment required")
    if not isinstance(snapshots, dict):
        raise ValueError("named provider snapshots required")
    graph = index_assessment_dataflow(source)
    objects = source.get("shared_objects") or {}
    variables = source.get("variables") or {}
    tests = source.get("tests") or {}
    if not isinstance(tests, dict) or not tests:
        raise ValueError("named source Tests required")
    if any(not isinstance(t, dict) or not isinstance(t.get("test_title"), str)
           or not t["test_title"].strip() for t in tests.values()):
        raise UnsupportedSourceSemantics("source Test description must be retained")
    if set(snapshots) - set(objects):
        raise ValueError("unknown snapshot source")
    acquired, derived, visiting = {}, {}, set()

    def normalize_items(raw, name):
        if not isinstance(raw, dict) or raw.get("status") != "complete":
            raise UnsupportedSourceSemantics(name + ": incomplete/error/not_collected source; no fabricated Boolean")
        if not isinstance(raw.get("items"), list):
            raise ValueError("item population must be a list")
        found = {}
        for item in raw["items"]:
            if (not isinstance(item, dict) or set(item) != {"id", "fields"}
                or type(item["id"]) is not str or not item["id"]
                or not isinstance(item["fields"], dict)):
                raise UnsupportedSourceSemantics("explicit Item identity and fields required")
            if item["id"] in found:
                raise UnsupportedSourceSemantics("duplicate Item identity in snapshot")
            found[item["id"]] = deepcopy(item)
        return found

    def merge(first, latter):
        for identity, item in latter.items():
            if identity in first and first[identity] != item:
                raise UnsupportedSourceSemantics("same Item identity with conflicting fields")
            first.setdefault(identity, deepcopy(item))
        return first

    def compare(actual, operation, expected):
        if type(actual) is not type(expected):
            raise UnsupportedSourceSemantics("incompatible comparison datatypes")
        if operation == "equals":
            return actual == expected
        if operation == "not_equal":
            return actual != expected
        if operation in ("less_than", "greater_than") and type(actual) is int:
            return actual < expected if operation == "less_than" else actual > expected
        raise UnsupportedSourceSemantics("unsupported Filter comparator")

    def filter_one(item, fields):
        if not isinstance(fields, dict) or len(fields) != 1:
            raise UnsupportedSourceSemantics("single explicit filter field required")
        field, predicate = next(iter(fields.items()))
        if (not isinstance(predicate, dict) or
            predicate.get("require") != "at_least_one_exists_and_all_match"):
            raise UnsupportedSourceSemantics("unproven Filter field requirement")
        operators = set(predicate) - {"require", "value_match"}
        if len(operators) != 1:
            raise UnsupportedSourceSemantics("exactly one Filter comparator required")
        operation = next(iter(operators))
        if field not in item["fields"]:
            raise UnsupportedSourceSemantics("missing observed field needs six-state treatment")
        actual = item["fields"][field]
        if isinstance(actual, (list, dict)):
            raise UnsupportedSourceSemantics("record/multi-valued Item field not supported")
        expected = predicate[operation]
        if isinstance(expected, dict):
            if set(expected) != {"variable"}:
                raise UnsupportedSourceSemantics("only named Variable expected operand supported")
            values = from_variable(expected["variable"])
        elif isinstance(expected, list):
            values = expected
        else:
            if "value_match" in predicate:
                raise UnsupportedSourceSemantics("scalar expected operand has multi-value quantifier")
            values = [expected]
        if not values:
            raise UnsupportedSourceSemantics("empty expected values require source semantics")
        matches = sum(compare(actual, operation, v) for v in values)
        mode = predicate.get("value_match")
        if mode is None and not isinstance(expected, (dict, list)):
            return matches == 1
        if mode == "all":
            return matches == len(values)
        if mode == "one":
            return matches == 1
        if mode == "one_or_more":
            return matches > 0
        if mode == "none":
            return matches == 0
        raise UnsupportedSourceSemantics("explicit value_match required for Variable/array")

    def apply_filters(items, filters):
        if not isinstance(filters, list):
            raise UnsupportedSourceSemantics("Filters must be explicit list")
        result = dict(items)
        for f in filters:
            if not isinstance(f, dict) or len(f) != 1:
                raise UnsupportedSourceSemantics("ambiguous Filter action")
            action, fields = next(iter(f.items()))
            if action not in ("include", "exclude"):
                raise UnsupportedSourceSemantics("unsupported Filter action")
            result = {k: v for k, v in result.items()
                      if filter_one(v, fields) == (action == "include")}
        return result

    def from_set(s):
        if not isinstance(s, dict) or set(s) != {"operator", "operands"}:
            raise UnsupportedSourceSemantics("unsupported Set shape")
        operation, operands = s["operator"], s["operands"]
        if (operation not in ("union", "intersection", "difference")
            or not isinstance(operands, list) or not operands):
            raise UnsupportedSourceSemantics("unsupported Set operation")
        populations = []
        for operand in operands:
            if not isinstance(operand, dict) or set(operand) not in (
                {"object"}, {"object", "filters"}, {"set"}, {"set", "filters"}
            ):
                raise UnsupportedSourceSemantics("ambiguous Set operand")
            population = (from_object(operand["object"]) if "object" in operand
                          else from_set(operand["set"]))
            populations.append(apply_filters(population, operand.get("filters", [])))
        result = dict(populations[0])
        for population in populations[1:]:
            for identity in result.keys() & population.keys():
                if result[identity] != population[identity]:
                    raise UnsupportedSourceSemantics("Set Item identity conflict")
            if operation == "union":
                merge(result, population)
            elif operation == "intersection":
                result = {k: v for k, v in result.items() if k in population}
            else:
                result = {k: v for k, v in result.items() if k not in population}
        return result

    def from_object(name):
        if name in acquired:
            return deepcopy(acquired[name])
        if name not in objects:
            raise ValueError("unresolved named Object")
        ident = ("object", name)
        if ident in visiting:
            raise ValueError("cyclic source Object")
        visiting.add(ident)
        try:
            obj = objects[name]
            if any(x in obj for x in ("for_each", "variable", "filters")):
                raise UnsupportedSourceSemantics("foreach/dynamic Object/filter requires independent proof")
            if "set" in obj:
                if name in snapshots or "select" in obj or "collect" in obj:
                    raise UnsupportedSourceSemantics("Set Object cannot also be collected")
                result = from_set(obj["set"])
            else:
                if name not in snapshots:
                    raise UnsupportedSourceSemantics("missing provider acquisition snapshot")
                result = normalize_items(snapshots[name], name)
            acquired[name] = result
            return deepcopy(result)
        finally:
            visiting.remove(ident)

    def from_variable(name):
        if name in derived:
            return deepcopy(derived[name])
        if name not in variables:
            raise ValueError("unresolved Variable")
        ident = ("variable", name)
        if ident in visiting:
            raise ValueError("cyclic source Variable")
        visiting.add(ident)
        try:
            v = variables[name]
            if v.get("datatype") not in ("string", "integer"):
                raise UnsupportedSourceSemantics("unsupported Variable datatype")
            if v.get("kind") == "constant" and "value" in v:
                literal = v["value"]
                values = deepcopy(literal) if isinstance(literal, list) else [literal]
            elif v.get("kind") == "local" and isinstance(v.get("expression"), dict):
                e = v["expression"]
                if set(e) == {"values"} and isinstance(e["values"], dict) and (
                    set(e["values"]) == {"object", "field"}
                ):
                    ref, field = e["values"]["object"], e["values"]["field"]
                    items = from_object(ref)
                    if any(field not in item["fields"] for item in items.values()):
                        raise UnsupportedSourceSemantics("missing source Item field")
                    values = [item["fields"][field] for item in items.values()]
                elif set(e) == {"variable"}:
                    values = from_variable(e["variable"])
                elif set(e) == {"arithmetic"}:
                    ar = e["arithmetic"]
                    if (not isinstance(ar, dict) or set(ar) != {"operation", "operands"}
                        or ar["operation"] != "add" or not isinstance(ar["operands"], list)
                        or len(ar["operands"]) != 2 or any(
                            not isinstance(x, dict) or set(x) != {"variable"}
                            for x in ar["operands"])):
                        raise UnsupportedSourceSemantics("unsupported Variable arithmetic")
                    left, right = (from_variable(x["variable"]) for x in ar["operands"])
                    if any(type(x) is not int for x in left + right):
                        raise UnsupportedSourceSemantics("integer arithmetic requires integer operands")
                    values = [a + b for a in left for b in right]
                else:
                    raise UnsupportedSourceSemantics("unsupported Variable expression")
            else:
                raise UnsupportedSourceSemantics("unsupported Variable kind")
            datatype = str if v["datatype"] == "string" else int
            if any(type(x) is not datatype for x in values):
                raise UnsupportedSourceSemantics("Variable datatype mismatch")
            derived[name] = values
            return deepcopy(values)
        finally:
            visiting.remove(ident)

    # Force evaluation of every source node: C must not silently drop any
    # shared Objects or Variables from a source-converted Assessment.
    for name in sorted(objects):
        from_object(name)
    for name in sorted(variables):
        from_variable(name)
    return {
        "stage": "C_BOUNDED_COMPLETE_ITEM_DATAFLOW_ONLY_NOT_OVAL_PARITY",
        "source_sha256": sha256(canonical_json(source)).hexdigest(),
        "source_graph": graph,
        "source_tests_unchanged": deepcopy(tests),
        "source_evaluate_unchanged": deepcopy(source.get("evaluate")),
        "item_populations": {k: list(acquired[k].values()) for k in sorted(acquired)},
        "variable_values": {k: derived[k] for k in sorted(derived)},
        "original_source_unchanged": source == assessment,
        "scanner_executed": False,
        "oval_semantics_proven": False,
        "six_state_semantics_proven": False,
    }
