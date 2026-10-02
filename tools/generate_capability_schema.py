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
    object_el = direct_global(root, "element", source["object"])
    state_el = direct_global(root, "element", source["state"])
    object_fields = immediate_payload_elements(object_el)
    state_fields = immediate_payload_elements(state_el)
    traversal_schema = (
        {"$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/file_traversal"}
        if mapping.get("native", {}).get("uses_file_traversal", False)
        else None
    )

    selector_props = {}
    selector_map = mapping["native"]["selector_map"]
    reverse_selector_map = {native: source for source, native in selector_map.items()}
    for alternative in mapping["native"]["object_selector_alternatives"]:
        for name in alternative:
            source_name = reverse_selector_map[name]
            field = object_fields[source_name]
            dtypes = source_datatypes(field)
            selector_schema = generic_entity_schema(dtypes, state=False)
            if name == "name":
                selector_schema = {
                    "oneOf": [
                        selector_schema,
                        {"type": "null"},
                    ]
                }
            selector_props[name] = selector_schema

    selector_alternatives = []
    for alternative in mapping["native"]["object_selector_alternatives"]:
        selector_alternatives.append({
            "required": list(alternative),
            "not": {
                "anyOf": [
                    {"required": [other]}
                    for other in selector_props
                    if other not in alternative
                ]
            } if any(other not in alternative for other in selector_props) else {},
        })
    # Remove empty 'not' helper if there is only one possible field set.
    for alt in selector_alternatives:
        if alt.get("not") == {}:
            alt.pop("not", None)

    collect_properties = {}
    collect_required = []
    for name, spec in mapping.get("native", {}).get("collection_parameters", {}).items():
        prop = {
            "type": spec.get("type", "string"),
        }
        if spec.get("enum"):
            prop["enum"] = list(spec["enum"])
        if spec.get("description"):
            prop["description"] = spec["description"]
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
    state_field_branches = []
    for name, meta in sorted(state_meta.items()):
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
        state_field_branches.append({
            "properties": props,
            "required": ["field"],
        })

    capability = mapping["capability"]
    generated = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://scap-ng.dev/schema/v0.1.0/generated/capabilities/{capability}.schema.json",
        "title": f"Generated SCAP-NG capability fragment: {capability}",
        "description": f"Native SCAP-NG capability schema for {capability}.",
        "x-semantic-validator-rules": mapping.get("semantic_validator_rules", []),
        "$defs": {
            "test": {
                "type": "object",
                "required": [
                    "test_title", "capability", "object",
                    "check_existence", "check",
                ],
                "properties": {
                    "test_title": {"type": ["string", "null"]},
                    "capability": {"const": capability},
                    "object": {"type": "string", "minLength": 1},
                    "check_existence": {
                        "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/existence_requirement"
                    },
                    "check": {
                        "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/match_quantifier"
                    },
                    "state_operator": {
                        "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/logical_operator"
                    },
                    "states": {
                        "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/test_reference_set"
                    },
                },
                "additionalProperties": False,
            },
            "object": {
                "type": "object",
                "required": ["object_title", "capability"],
                "properties": {
                    "object_title": {"type": ["string", "null"]},
                    "capability": {"const": capability},
                    "select": {
                        "type": "object",
                        "properties": selector_props,
                        "additionalProperties": False,
                        "oneOf": selector_alternatives,
                    },
                    **({"traversal": traversal_schema} if traversal_schema else {}),
                    **({"collect": collect_schema} if collect_schema else {}),
                    "set": {
                        "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/set_expression"
                    },
                },
                "additionalProperties": False,
                "oneOf": [
                    {"required": ["select"], "not": {"required": ["set"]}},
                    {"required": ["set"], "not": {"required": ["select"]}},
                ],
            },
            "state": {
                "type": "object",
                "required": ["state_title", "capability", "state"],
                "properties": {
                    "state_title": {"type": ["string", "null"]},
                    "capability": {"const": capability},
                    "state": {
                        "type": "object",
                        "required": ["field"],
                        "properties": {
                            "field": {
                                "type": "string",
                                "enum": sorted(state_names),
                            }
                        },
                        "allOf": [
                            {
                                "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/state_entity_base"
                            },
                            {"oneOf": state_field_branches}
                        ],
                        "unevaluatedProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        },

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
