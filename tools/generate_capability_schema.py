#!/usr/bin/env python3
"""Generate disposable SCAP-NG deep capability schema fragments from a reviewed mapping.

This is deliberately NOT a mechanical XSD->JSON Schema translator. A reviewed
mapping selects the native capability and source OVAL Test/Object/State family.
The generator extracts source-backed field names, datatypes, behavior
defaults/enumerations and documentation, while cross-field/Schematron semantics
remain explicit semantic-validator rules from the mapping.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

XSD = "{http://www.w3.org/2001/XMLSchema}"
COMMON_CAPABILITY_SCHEMA_ID = "https://scap-ng.dev/schema/v0.1.0/capability-common.schema.json"


def local(tag):
    return tag.rsplit("}", 1)[-1]


def docs(node):
    values = []
    for child in node.iter():
        if child.tag == XSD + "documentation":
            text = " ".join("".join(child.itertext()).split())
            if text:
                values.append(text)
    return " ".join(values)


def direct_global(root, kind, name):
    for child in root:
        if child.tag == XSD + kind and child.get("name") == name:
            return child
    raise KeyError(f"missing global {kind} {name!r}")


def restriction_values(node):
    values = []
    for child in node.iter():
        if child.tag == XSD + "enumeration" and child.get("value") is not None:
            values.append(child.get("value"))
    return values


def source_datatypes(element):
    typed = element.get("type") or ""
    suffix_map = {
        "EntityStateStringType": ["string"],
        "EntityStateIntType": ["integer"],
        "EntityStateBoolType": ["boolean"],
        "EntityStateFloatType": ["float"],
        "EntityStateVersionType": ["version"],
        "EntityStateIPAddressStringType": ["string"],
        "EntityObjectStringType": ["string"],
        "EntityObjectIntType": ["integer"],
        "EntityObjectBoolType": ["boolean"],
    }
    short = typed.split(":")[-1]
    if short in suffix_map:
        return suffix_map[short]

    # Some OVAL fields use an inline restriction with a narrowed datatype
    # attribute. Prefer that explicit enumeration when present.
    for attr in element.iter():
        if attr.tag == XSD + "attribute" and attr.get("name") == "datatype":
            values = restriction_values(attr)
            if values:
                return [
                    {
                        "int": "integer",
                        "ipv4_address": "ipv4",
                        "ipv6_address": "ipv6",
                        "evr_string": "rpm_evr",
                        "debian_evr_string": "debian_evr",
                    }.get(value, value)
                    for value in values
                ]
            if attr.get("default"):
                return [attr.get("default")]
    return ["string"]


def immediate_payload_elements(global_element):
    """Return direct semantic elements under extension/sequence/choice payload.

    For State this returns direct State entities. For Object it discovers named
    selector entities while avoiding nested annotation/schema helper elements.
    """
    result = {}
    for node in global_element.iter():
        if node.tag != XSD + "element" or not node.get("name"):
            continue
        name = node.get("name")
        if name in result:
            continue
        result[name] = node
    return result


def generic_entity_schema(allowed_datatypes, *, state=False):
    """Compose a capability entity from shared authored-Assessment primitives.

    Common value/reference/quantifier semantics live in capability-common.schema.json.
    The generated capability fragment contributes only datatype narrowing and closes
    the composed object with unevaluatedProperties.
    """
    base = "state_entity_base" if state else "object_entity_base"
    return {
        "allOf": [
            {"$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/{base}"},
            {
                "type": "object",
                "properties": {
                    "datatype": {
                        "type": "string",
                        "enum": sorted(set(allowed_datatypes)),
                    }
                },
            },
        ],
        "unevaluatedProperties": False,
    }


def generate(mapping, repo_root):
    source = mapping["source"]
    xsd_path = repo_root / source["definitions_schema"]
    root = ET.parse(xsd_path).getroot()

    test_el = direct_global(root, "element", source["test"])
    object_el = (
        direct_global(root, "element", source["object"])
        if source.get("object") else None
    )
    state_el = direct_global(root, "element", source["state"])
    object_fields = immediate_payload_elements(object_el) if object_el is not None else {}
    state_fields = immediate_payload_elements(state_el)
    traversal_definition = mapping.get("native", {}).get("traversal_definition")
    if traversal_definition is None and mapping.get("native", {}).get("uses_file_traversal", False):
        traversal_definition = "file_traversal"
    traversal_schema = (
        {"$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/{traversal_definition}"}
        if traversal_definition else None
    )

    test_source = mapping.get("native", {}).get(
        "test_source", {"kind": "object", "field": "object"}
    )
    test_source_kind = test_source.get("kind", "object")
    test_source_field = test_source.get("field", test_source_kind)

    selector_props = {}
    selector_alternatives = []
    if test_source_kind == "object" and mapping["native"].get("selector_map"):
        selector_map = mapping["native"]["selector_map"]
        reverse_selector_map = {native: source for source, native in selector_map.items()}
        optional_selectors = set(mapping["native"].get("optional_selectors", []))
        selected_names = {
            name
            for alternative in mapping["native"].get("object_selector_alternatives", [])
            for name in alternative
        } | optional_selectors
        for name in selected_names:
            source_name = reverse_selector_map[name]
            field = object_fields[source_name]
            dtypes = source_datatypes(field)
            enum_values = mapping["native"].get("selector_value_enums", {}).get(name)
            if enum_values:
                selector_schema = {
                    "oneOf": [
                        {"type": "string", "enum": list(enum_values)},
                        {"$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/variable_reference"},
                    ]
                }
            else:
                selector_schema = generic_entity_schema(dtypes, state=False)
            if name in mapping["native"].get("nullable_selectors", ["name"]):
                selector_schema = {
                    "oneOf": [
                        selector_schema,
                        {"type": "null"},
                    ]
                }
            selector_props[name] = selector_schema

        for alternative in mapping["native"].get("object_selector_alternatives", []):
            disallowed = [
                other for other in selector_props
                if other not in alternative and other not in optional_selectors
            ]
            selector_alternatives.append({
                "required": list(alternative),
                "not": {
                    "anyOf": [
                        {"required": [other]}
                        for other in disallowed
                    ]
                } if disallowed else {},
            })
        for alt in selector_alternatives:
            if alt.get("not") == {}:
                alt.pop("not", None)

    collect_properties = {}
    collect_required = []
    for name, spec in mapping.get("native", {}).get("collection_parameters", {}).items():
        literal = {
            "type": spec.get("type", "string"),
        }
        if spec.get("enum"):
            literal["enum"] = list(spec["enum"])
        if spec.get("description"):
            literal["description"] = spec["description"]
        prop = (
            {
                "oneOf": [
                    literal,
                    {"$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/variable_reference"},
                ]
            }
            if spec.get("allow_variable", False)
            else literal
        )
        collect_properties[name] = prop
        if spec.get("required", False):
            collect_required.append(name)

    collect_schema = None
    if collect_properties:
        collect_schema = {
            "type": "object",
            "properties": collect_properties,
            "additionalProperties": False,
        }
        if collect_required:
            collect_schema["required"] = collect_required

    state_names = []
    state_meta = {}
    field_map = mapping["native"].get("state_field_map", {})
    datatype_overrides = mapping["native"].get("field_datatypes", {})
    for source_name, native_name in field_map.items():
        field = state_fields.get(source_name)
        if field is None:
            raise KeyError(
                f"mapping references missing source State field {source_name!r}"
            )
        dtypes = datatype_overrides.get(native_name) or source_datatypes(field)
        state_names.append(native_name)
        state_meta[native_name] = {
            "datatypes": dtypes,
        }

    state_value_enums = mapping["native"].get("state_value_enums", {})
    record_state_fields = set(mapping["native"].get("record_state_fields", []))
    scalar_state_branches = []
    record_state_branches = []
    for name, meta in sorted(state_meta.items()):
        if name in record_state_fields:
            record_state_branches.append({
                "type": "object",
                "required": ["field", "record"],
                "properties": {
                    "field": {"const": name},
                    "record": {
                        "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/record_predicate"
                    },
                },
                "additionalProperties": False,
            })
            continue

        props = {
            "field": {"const": name},
            "datatype": {
                "type": "string",
                "enum": sorted(set(meta["datatypes"])),
            },
        }
        if name in state_value_enums:
            props["value"] = {
                "oneOf": [
                    {"type": "string", "enum": list(state_value_enums[name])},
                    {"$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/variable_reference"},
                ]
            }
        scalar_state_branches.append({
            "properties": props,
            "required": ["field"],
        })

    object_required = ["object_title", "capability"]

    capability = mapping["capability"]
    test_required = [
        "test_title", "capability",
        "existence", "match",
    ]
    test_properties = {
        "test_title": {"type": ["string", "null"]},
        "capability": {"const": capability},
        "existence": {
            "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/existence_requirement"
        },
        "match": {
            "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/match_quantifier"
        },
        "states_match": {
            "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/logical_operator"
        },
        "states": {
            "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/test_reference_set"
        },
    }
    if test_source_kind != "none":
        test_required.insert(2, test_source_field)
        test_properties[test_source_field] = {"type": "string", "minLength": 1}

    defs = {
        "test": {
            "type": "object",
            "required": test_required,
            "properties": test_properties,
            "additionalProperties": False,
        },
        "state": {
            "type": "object",
            "required": ["state_title", "capability", "state"],
            "properties": {
                "state_title": {"type": ["string", "null"]},
                "capability": {"const": capability},
                "state": {
                    "oneOf": (
                        [
                            {
                                "type": "object",
                                "required": ["field"],
                                "properties": {
                                    "field": {
                                        "type": "string",
                                        "enum": sorted(
                                            name for name in state_names
                                            if name not in record_state_fields
                                        ),
                                    }
                                },
                                "allOf": [
                                    {
                                        "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/state_entity_base"
                                    },
                                    {"oneOf": scalar_state_branches},
                                ],
                                "unevaluatedProperties": False,
                            }
                        ] if scalar_state_branches else []
                    ) + record_state_branches,
                },
            },
            "additionalProperties": False,
        },
    }

    if test_source_kind == "object":
        object_properties = {
            "object_title": {"type": ["string", "null"]},
            "capability": {"const": capability},
            **({"traversal": traversal_schema} if traversal_schema else {}),
            **({"collect": collect_schema} if collect_schema else {}),
            "set": {
                "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/set_expression"
            },
        }
        object_alternatives = []
        if selector_props:
            object_properties["select"] = {
                "type": "object",
                "properties": selector_props,
                "additionalProperties": False,
                "oneOf": selector_alternatives,
            }
            direct_required = ["select"] + (["collect"] if collect_required else [])
            object_alternatives.append({
                "required": direct_required,
                "not": {"required": ["set"]},
            })
        elif collect_schema:
            object_alternatives.append({
                "required": ["collect"],
                "not": {"required": ["set"]},
            })
        object_alternatives.append({
            "required": ["set"],
            "not": {
                "anyOf": [
                    {"required": ["select"]},
                    {"required": ["collect"]},
                ]
            },
        })
        defs["object"] = {
            "type": "object",
            "required": object_required,
            "properties": object_properties,
            "additionalProperties": False,
            "oneOf": object_alternatives,
        }

    generated = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://scap-ng.dev/schema/v0.1.0/generated/capabilities/{capability}.schema.json",
        "title": f"Generated SCAP-NG capability fragment: {capability}",
        "description": f"Native SCAP-NG capability schema for {capability}.",
        "x-semantic-validator-rules": mapping.get("semantic_validator_rules", []),
        "$defs": defs,

    }
    return generated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()

    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    generated = generate(mapping, args.repo_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "capability": mapping["capability"],
        "output": str(args.output),
        "state_fields": len(mapping.get("native", {}).get("state_field_map", {})),
        "object_selectors": sorted({
            name
            for alternative in mapping.get("native", {}).get("object_selector_alternatives", [])
            for name in alternative
        }),
        "semantic_rules": len(generated["x-semantic-validator-rules"]),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
