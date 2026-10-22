#!/usr/bin/env python3
"""Pinned original OVAL 5.12.3 Set/Filter placement vs native 0.4.0.

This is a source/schema and synthetic-Item semantic regression, NOT a
scanner-on-host proof or a complete 167-Definition round-trip certification.
The XML Set operators and filters come from SCAP Self-Assertion, not a
handwritten restatement of the intended behavior.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from lxml import etree

from test_generate_capability_schema_v04 import materialize, validate
from validate_v04_oval_5123 import check as validate_original


ROOT = Path(__file__).resolve().parents[1]
OVAL = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
SOURCE_SHAS = {
    "windows": "352a0b99e0df90cc3ddf9f7e410f3d9a8b44659a6a12c38c938ab861be595262",
    "unix": "ca472ba6709eb0290284287897bd7a976c8634f9107de7e29fd1eae21001e808",
}
XSD_SHA = "06b79e8683d6b9dcaad3ab074a456588ed82c4edd2e8fff209def10aa0a366cc"
OPERATORS = {"UNION": "union", "INTERSECTION": "intersection", "COMPLEMENT": "difference"}

# Distinct synthetic observed Items exercise the source Set algebra and the
# filter's original two string values without claiming to have scanned Windows.
ITEMS_WINDOWS = {
    "a": r"C:\support\txt",
    "b": r"C:\support\txt\txtfile",
    "c": r"C:\support\txt\txtfile\subtxtfile",
    "d": r"C:\support\xml",
}
ITEMS_UNIX = {
    "a": "/opt/support/txt",
    "b": "/opt/support/txt/txtfile",
    "c": "/opt/support/txt/txtfile/subtxtfile",
    "d": "/opt/support/xml",
}
LEAVES = {
    "189": {"a", "b", "c"}, "262": {"b", "c"},
    "520": {"a", "b"}, "190": {"d"},
}


def local(node):
    return etree.QName(node).localname


def object_name(oval_id):
    return "file-obj-" + oval_id.rsplit(":", 1)[-1] + "-object"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_source(source):
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    doc = etree.parse(str(source), parser)
    objects = {
        node.get("id"): node
        for node in doc.findall(f".//{{{OVAL}}}objects/*")
    }
    states = {
        node.get("id"): node
        for node in doc.findall(f".//{{{OVAL}}}states/*")
    }
    variables = {
        node.get("id"): node
        for node in doc.findall(f".//{{{OVAL}}}variables/*")
    }
    require(len(objects) == 11 and len(states) == 4 and len(variables) == 3,
            "Pinned Windows Set source inventory changed")
    return doc, objects, states, variables


def source_filter_filter_state(node, states, variables):
    """Read source State and var_check rather than inventing filter criteria."""
    state = states[node.text.strip()]
    path = next(child for child in state if local(child) == "path")
    require(path.get("var_check") == "only one", "Unsupported source var_check")
    var = variables[path.get("var_ref")]
    require(local(var) == "constant_variable" and var.get("datatype") == "string",
            "Set source must contain an OVAL string constant Variable")
    values = [v.text for v in var if local(v) == "value"]
    require(len(values) == 2, "Expected both original filter values")
    action = node.get("action", "exclude")
    require(action in ("include", "exclude"), "Unexpected OVAL Filter action")
    var_name = "filter-path-var-" + var.get("id").rsplit(":", 1)[-1]
    native_filter = {action: {"directory": {
        "equals": {"variable": var_name},
        "value_match": "one",
        "require": "at_least_one_exists_and_all_match",
    }}}
    return native_filter, (var_name, tuple(values))


def translate_source_set(source_set, states, variables, names):
    """Convert XML structure, explicitly putting each Set Filter on each Object.

    Recursive Sets do not accept filters in the OVAL XSD; filters can only
    accompany object_reference children. Native 0.4 does not add a post-Set
    filter position, which would misrepresent that source structure.
    """
    op = OPERATORS[source_set.get("set_operator", "UNION")]
    children = list(source_set)
    nested = [node for node in children if local(node) == "set"]
    refs = [node for node in children if local(node) == "object_reference"]
    filters = [node for node in children if local(node) == "filter"]
    require(bool(nested) != bool(refs), "Set must have either nested Sets or refs")
    require(1 <= len(nested or refs) <= 2, "OVAL Set source arity altered")
    if nested:
        require(not filters, "The OVAL XSD cannot filter a nested Set")
        operands = [{"set": translate_source_set(n, states, variables, names)}
                    for n in nested]
    else:
        ordered = []
        for filt in filters:
            native, var = source_filter_filter_state(filt, states, variables)
            ordered.append(native)
            names[var[0]] = var[1]
        operands = [{"object": object_name(ref.text.strip()),
                     "filters": deepcopy(ordered)} for ref in refs]
    return {"operator": op, "operands": operands}


def source_item_set(source_set, states, variables, items):
    """Independent synthetic Item interpretation directly over source XML."""
    op = source_set.get("set_operator", "UNION")
    nested = [n for n in source_set if local(n) == "set"]
    if nested:
        parts = [source_item_set(n, states, variables, items) for n in nested]
    else:
        refs = [n for n in source_set if local(n) == "object_reference"]
        filters = [n for n in source_set if local(n) == "filter"]
        parts = []
        for ref in refs:
            part = set(LEAVES[ref.text.strip().rsplit(":", 1)[-1]])
            for filt in filters:
                native, named = source_filter_filter_state(filt, states, variables)
                action = next(iter(native))
                matching = {key for key in part if items[key] in named[1]}
                part = part & matching if action == "include" else part - matching
            parts.append(part)
    if op == "UNION":
        return set().union(*parts)
    if op == "INTERSECTION":
        return set.intersection(*parts)
    if op == "COMPLEMENT":
        require(len(parts) == 2, "COMPLEMENT needs two sources")
        return parts[0] - parts[1]
    raise AssertionError("Invalid original Set operator: " + op)


def native_item_set(native_set, names, items):
    parts = []
    for operand in native_set["operands"]:
        if "set" in operand:
            parts.append(native_item_set(operand["set"], names, items))
        else:
            part = set(LEAVES[operand["object"].split("-obj-")[1].split("-")[0]])
            for filt in operand["filters"]:
                action, state = next(iter(filt.items()))
                selector = state["directory"]
                require(selector["value_match"] == "one",
                        "Source only-one var_check was lost")
                values = names[selector["equals"]["variable"]]
                match = {key for key in part if items[key] in values}
                part = part & match if action == "include" else part - match
            parts.append(part)
    op = native_set["operator"]
    if op == "union":
        return set().union(*parts)
    if op == "intersection":
        return set.intersection(*parts)
    if op == "difference":
        return parts[0] - parts[1]
    raise AssertionError("Invalid native Set operator: " + op)


def source_set_depth(element):
    children = [n for n in element if local(n) == "set"]
    return 1 + max([source_set_depth(n) for n in children], default=0)


def prove(source, xsd_root, platform="windows"):
    require(platform in SOURCE_SHAS, "Unsupported Set source platform")
    source_sha = SOURCE_SHAS[platform]
    items = ITEMS_WINDOWS if platform == "windows" else ITEMS_UNIX
    require(hashlib.sha256(source.read_bytes()).hexdigest() == source_sha,
            "Original pinned SCAP Self-Assertion " + platform + " Set source changed")
    xsd = xsd_root / "oval-definitions-schema.xsd"
    require(hashlib.sha256(xsd.read_bytes()).hexdigest() == XSD_SHA,
            "OVAL 5.12.3 base Definitions XSD changed")
    doc_text = xsd.read_text(encoding="utf-8")
    require("Each filter is applied to the items identified by each OVAL Object before the set_operator is applied" in doc_text,
            "Lost authoritative OVAL pre-operator Set Filter semantics")
    require('name="action" type="oval-def:FilterActionEnumeration" use="optional" default="exclude"' in doc_text,
            "Lost OVAL Filter default-exclude contract")
    xsd_result = validate_original(xsd_root, source, platform)
    require(xsd_result["status"] == "PASS", str(xsd_result["diagnostics"]))
    xml, objects, states, variables = load_source(source)
    schema = materialize(platform + ".file")
    require(len({object_name(name) for name in objects}) == len(objects),
            "Native Object name collision")
    tests = xml.findall(f".//{{{OVAL}}}tests/*")
    require(len(tests) == 7, "Original Set Test count changed")
    defined = [node for node in objects.values() if any(local(c) == "set" for c in node)]
    require(len(defined) == 7, "Original Set Object count changed")
    report = []
    seen = Counter()
    depths = []
    for obj in defined:
        source_set = next(c for c in obj if local(c) == "set")
        names = {}
        translated = translate_source_set(source_set, states, variables, names)
        candidate = {"capability": platform + ".file", "set": translated}
        errors = validate(schema, "object", candidate)
        require(not errors, "Invalid native Set: " + str(errors[0] if errors else ""))
        before = source_item_set(source_set, states, variables, items)
        after = native_item_set(translated, names, items)
        require(before == after, "Native Set Item result differs: " + obj.get("id"))
        seen[translated["operator"]] += 1
        depths.append(source_set_depth(source_set))
        report.append({"source_object": obj.get("id"),
                       "native_object": object_name(obj.get("id")),
                       "native_operation": translated["operator"],
                       "maximum_set_depth": depths[-1],
                       "synthetic_item_count": len(after),
                       "filter_variable_count": len(names)})
        malformed = deepcopy(candidate)
        malformed["set"]["filters"] = [{"exclude": {"directory": {
            "equals": "bad", "require": "at_least_one_exists_and_all_match"}}}]
        require(bool(validate(schema, "object", malformed)),
                "Native post-operation Set Filter unexpectedly accepted")
    require(set(seen) == {"union", "intersection", "difference"},
            "Original operator coverage shrank")
    require(max(depths) >= 3, "Original nested Set coverage shrank")
    with_filter = next(o for o in defined if o.get("id", "").endswith(":373"))
    filter_set = next(c for c in with_filter if local(c) == "set")
    names = {}
    converted = translate_source_set(filter_set, states, variables, names)
    require(converted["operands"][0]["filters"][0].get("exclude") is not None,
            "OVAL default exclude was not materialized")
    unfiltered = deepcopy(converted)
    unfiltered["operands"][0]["filters"] = []
    require(native_item_set(converted, names, items) != native_item_set(unfiltered, names, items),
            "Synthetic Item fixture did not detect a lost filter")
    included = deepcopy(converted)
    original_filter = included["operands"][0]["filters"][0]
    original_filter["include"] = original_filter.pop("exclude")
    require(native_item_set(converted, names, items) != native_item_set(included, names, items),
            "Synthetic Item fixture did not detect reversed include/exclude")
    return {
        "status": "PASS", "original_xsd_5123_valid": True,
        "source_file_sha256": source_sha, "base_schema_sha256": XSD_SHA,
        "original_platform": platform,
        "original_set_tests": len(tests), "native_set_objects_valid": len(defined),
        "operators": dict(seen), "maximum_nesting": max(depths),
        "filters_evaluated_before_set_operator": True,
        "original_filter_default_exclude": True,
        "synthetic_item_semantics_equal": True,
        "scanner_runtime_parity_proven": False,
        "full_definition_roundtrip_certified": False,
        "cases": report,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--xsd-root", required=True, type=Path)
    parser.add_argument("--platform", choices=("windows", "unix"),
                        default="windows")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = prove(args.source, args.xsd_root, args.platform)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
