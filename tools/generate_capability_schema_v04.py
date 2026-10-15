#!/usr/bin/env python3
"""Pre-alpha 0.4 generated native capability schemas (single authored grammar).

This adapter reuses the reviewed OVAL 5.12.3 source mapping/metadata extraction
of the frozen 0.3 generator, and then creates an *independent version-local*
0.4-only authored Test/Object/State contract. It DOES NOT change the old generator
or any 0.3 schema, and never falls back to a 0.3 reference at validation time.

Pending gates are documented in #228: exhaustive enum/datatype narrowing,
WMI/cmdlet collector variants, and full 100-capability deep migration validation.
"""
from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from generate_capability_schema import (
    generate as generate_v03, direct_global, immediate_payload_elements,
    source_datatypes,
)

VERSION = "0.4.0"
ROOT_ID = f"https://scap-ng.dev/schema/v{VERSION}/"
LANG = ROOT_ID + "assessment-language.schema.json"
COMMON = ROOT_ID + "capability-common.schema.json"
LOGIC = ("all", "any", "one", "odd")


def _field_expression(name: str, child: dict) -> dict:
    return {
        "type": "object", "required": [name],
        "properties": {name: child},
        "additionalProperties": False,
    }


def _generated_state_fields(mapping: dict, root: Path) -> tuple[dict, set]:
    source = mapping["source"]
    document = ET.parse(root / source["definitions_schema"]).getroot()
    state = direct_global(document, "element", source["state"])
    entities = immediate_payload_elements(state)
    overrides = mapping["native"].get("state_field_datatypes", {})
    datatypes = mapping["native"].get("field_datatypes", {})
    fields = {}
    for source_name, output_name in mapping["native"].get("state_field_map", {}).items():
        if source_name not in entities:
            raise KeyError(f"Unmapped State entity {source_name!r}")
        fields[output_name] = overrides.get(
            output_name, datatypes.get(output_name, source_datatypes(entities[source_name]))
        )
    for source_name, spec in mapping["native"].get("native_added_state_fields", {}).items():
        output_name = spec.get("native_name", source_name)
        if source_name not in entities:
            # Native-added fields correspond to Item-only fields and may have
            # no equivalent source State entity. Use reviewed override first.
            fields[output_name] = overrides.get(
                output_name, datatypes.get(output_name, ["string"])
            )
        else:
            fields[output_name] = overrides.get(
                output_name, datatypes.get(output_name, source_datatypes(entities[source_name]))
            )
    records = set(mapping["native"].get("record_state_fields", []))
    return fields, records


def _selector_fields(mapping: dict, root: Path) -> dict:
    source = mapping["source"]
    if not source.get("object"):
        return {}
    document = ET.parse(root / source["definitions_schema"]).getroot()
    obj = direct_global(document, "element", source["object"])
    native_to_source = {
        output: name for name, output in mapping["native"].get("selector_map", {}).items()
    }
    entities = immediate_payload_elements(obj)
    overrides = mapping["native"].get("selector_datatypes", {})
    return {
        output: overrides.get(output,source_datatypes(entities[source_name]))
        for output,source_name in native_to_source.items()
    }


def generate(mapping: dict, repo_root: Path) -> dict:
    if mapping.get("specification_version") != VERSION:
        raise ValueError("0.4 generator accepts only reviewed 0.4 source mappings")
    old = deepcopy(mapping)
    old["specification_version"] = "0.3.0"
    # Extract reviewed XSD semantics through a pinned 0.3 code path. The result
    # is NOT used directly and no 0.3 schema is referenced or packaged.
    base = generate_v03(old, repo_root, schema_version="0.3.0")
    result = json.loads(
        json.dumps(base).replace("/v0.3.0/", "/v0.4.0/")
    )
    result["$id"] = (
        ROOT_ID + "generated/capabilities/" + mapping["capability"] + ".schema.json"
    )
    result["description"] = (
        "DRAFT: SCAP-NG 0.4 generated native capability contract. One authored "
        "Test/Object/State grammar; derived from reviewed source OVAL 5.12.3 mappings."
    )
    result["x-specification-version"] = VERSION
    defs = result["$defs"]

    # Only a mapping with an explicit native.fixed_result is a fixed-result
    # capability. Ordinary native no-Object capabilities such as
    # windows.passwordpolicy, audit subcategories and independent.family have
    # normal State predicates and paired requirements; they SHALL go through
    # the full common path below even though no Object schema exists.
    if mapping.get("native",{}).get("fixed_result") is not None:
        old_test = defs["test"]
        old_test["required"] = sorted(
            (set(old_test["required"]) - {"existence", "match"}) | {"require"}
        )
        old_test["properties"]["require"] = {
            "$ref": LANG + "#/$defs/presence_requirement"
        }
        old_test["properties"]["reported_elements"] = {
            "$ref": ROOT_ID + "reported-elements.schema.json"
        }
        old_test["properties"].pop("existence",None)
        old_test["properties"].pop("match",None)
        # Fixed-result native capabilities have no authored Object or State
        # predicate. Drop 0.3's legacy named State wrapper and do not provide
        # a second authoring spelling through unused schema definitions.
        defs.pop("state",None)
        return result

    native_selector_fields = _selector_fields(mapping,repo_root)
    select = defs.get("object",{}).get("properties",{}).get("select")
    if select is not None:
        for name in list(select.get("properties", {})):
            if name not in native_selector_fields:
                raise ValueError(f"No source Object selector mapping for {name}")
            dtypes = native_selector_fields[name]
            selector = {
                "allOf": [
                    {"$ref": COMMON + "#/$defs/object_entity_base"},
                    {"type": "object", "properties": {
                        "datatype": {"enum": sorted(set(dtypes))}
                    }},
                ],
                "description": f"0.4 native Object selector: {name} (type checked)",
            }
            # Nullable native selector values, e.g. Windows registry name,
            # retain their original existence/absence meaning.
            if name in mapping["native"].get("nullable_selectors",["name"]):
                selector = {"oneOf":[selector,{"type":"null"}]}
            # Reuse only explicit 0.3 for_each binding as a distinct branch,
            # never hide it as a default Object selector comparison.
            selector = {"oneOf":[selector,{
                "$ref": COMMON + "#/$defs/foreach_selector_binding"
            }]}
            select["properties"][name] = selector

    state_fields, records = _generated_state_fields(mapping,repo_root)
    entries = []
    for name,dtypes in sorted(state_fields.items()):
        if name in records:
            child = {"$ref": LANG + "#/$defs/record_wrapper_predicate"}
        else:
            child = {
                "allOf": [
                    {"$ref": LANG + "#/$defs/scalar_field_predicate"},
                    {"type": "object", "properties": {
                        "datatype": {"enum": sorted(set(dtypes))}
                    }},
                ],
            }
        entries.append(_field_expression(name,child))
    defs["state_predicate"] = {"oneOf":entries} if entries else False
    defs["state_expression"] = {
        "oneOf": [
            {"$ref": "#/$defs/state_predicate"},
            *[
                {"type":"object","required":[logical],
                 "properties":{logical:{
                     "type":"array","minItems":1,
                     "items":{"$ref":"#/$defs/state_expression"},
                 }},"additionalProperties":False}
                for logical in LOGIC
            ],
        ]
    }
    # Named State wrappers belong to the legacy migration source, not the
    # single normative 0.4 authored grammar.
    defs.pop("state",None)

    test = defs["test"]
    required = set(test["required"]) - {"existence","match"}
    required.add("require")
    test["required"] = sorted(required)
    test["properties"].pop("existence",None)
    test["properties"].pop("match",None)
    test["properties"]["require"] = {
        # `none_exist` legitimately occurs in both the presence-only
        # and State-bearing vocabularies. oneOf would reject that overlap;
        # the central 0.4 Test schema independently enforces Test scope.
        "anyOf": [
            {"$ref": LANG + "#/$defs/presence_requirement"},
            {"$ref": LANG + "#/$defs/paired_requirement"},
        ],
    }
    test["properties"]["states"] = {
        "type":"array", "items":{"$ref":"#/$defs/state_expression"}
    }
    if "object" in test["properties"]:
        test["properties"]["object"] = {
            "oneOf":[
                {"$ref": COMMON + "#/$defs/object_reference"},
                {"$ref": "#/$defs/object"},
            ]
        }
    test.setdefault("allOf",[]).append({"$ref": LANG + "#/$defs/test"})
    # This ensures source native fields are closed and Test grammar remains one
    # representation instead of accepting old existence/match.
    test["not"] = {
        "anyOf":[{"required":["existence"]},{"required":["match"]}]
    }
    result["x-authoring-gate"] = (
        "Draft structural generation only; source enumeration and cross-field "
        "semantics require additional validation before 0.4 freeze."
    )
    # Resolver scope changes when traversing external 0.4 language schemas.
    # Use fully qualified references for generated native recursion, so local
    # State expressions cannot accidentally resolve against an external schema.
    def qualify_local_refs(node):
        if isinstance(node, dict):
            for key, val in node.items():
                if key == "$ref" and isinstance(val, str) and val.startswith("#/$defs/"):
                    node[key] = result["$id"] + val
                else:
                    qualify_local_refs(val)
        elif isinstance(node,list):
            for entry in node:qualify_local_refs(entry)
    qualify_local_refs(result)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mapping",type=Path,required=True)
    p.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    m=json.loads(args.mapping.read_text(encoding="utf-8"))
    output=generate(m,args.repo_root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "capability":m["capability"],"version":VERSION,
        "object_selector_fields":len(
            output.get("$defs",{}).get("object",{}).get("properties",{}).
            get("select",{}).get("properties",{})
        ),
        "state_predicates":len(
            output.get("$defs",{}).get("state_predicate",{}).get("oneOf",[])
        ) if isinstance(output.get("$defs",{}).get("state_predicate",{}),dict) else 0,
        "output":str(args.output),
    },sort_keys=True))
if __name__=="__main__":
    main()
