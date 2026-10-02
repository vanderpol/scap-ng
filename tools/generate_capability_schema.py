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


def deprecated_restriction_values(node):
    rows = []
    for child in node.iter():
        if child.tag != XSD + "enumeration" or child.get("value") is None:
            continue
        deprecated = [
            n for n in child.iter()
            if local(n.tag) == "deprecated_info"
        ]
        if deprecated:
            rows.append({
                "value": child.get("value"),
                "evidence": " ".join(docs(n) or " ".join("".join(n.itertext()).split())
                                     for n in deprecated).strip(),
            })
    return rows


def source_datatypes(element):
    typed = element.get("type") or ""
    suffix_map = {
        "EntityStateStringType": ["string"],
        "EntityStateIntType": ["int"],
        "EntityStateBoolType": ["boolean"],
        "EntityStateFloatType": ["float"],
        "EntityStateVersionType": ["version"],
        "EntityStateIPAddressStringType": ["string"],
        "EntityObjectStringType": ["string"],
        "EntityObjectIntType": ["int"],
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
                return values
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


def behavior_contract(root, type_name, *, reject_deprecated_values=False):
    node = direct_global(root, "complexType", type_name)
    props = {}
    required = []
    for attr in node:
        if attr.tag != XSD + "attribute" or not attr.get("name"):
            continue
        name = attr.get("name")
        schema = {"description": docs(attr)}
        values = restriction_values(attr)
        if values:
            schema["type"] = "string"
            deprecated_values = deprecated_restriction_values(attr)
            deprecated_set = {row["value"] for row in deprecated_values}
            schema["enum"] = [
                value for value in values
                if not (reject_deprecated_values and value in deprecated_set)
            ]
            if deprecated_values:
                schema["x-oval-deprecated-enum-values"] = deprecated_values
                schema["x-scap-ng-deprecated-enum-policy"] = (
                    "reject" if reject_deprecated_values else "allow_with_warning"
                )
        else:
            # FileBehaviors max_depth is the current integer case.
            has_integer = any(
                x.tag == XSD + "restriction" and (x.get("base") or "").endswith("integer")
                for x in attr.iter()
            )
            schema["type"] = "integer" if has_integer else "string"
            mins = [
                int(x.get("value"))
                for x in attr.iter()
                if x.tag == XSD + "minInclusive" and x.get("value") is not None
            ]
            if mins:
                schema["minimum"] = min(mins)
        if attr.get("default") is not None:
            raw = attr.get("default")
            if schema.get("type") == "integer":
                raw = int(raw)
            schema["default"] = raw
            schema["x-oval-default"] = raw
        if attr.get("use") == "required":
            required.append(name)
        props[name] = schema
    out = {
        "type": "object",
        "properties": props,
        "additionalProperties": False,
    }
    if required:
        out["required"] = required
    return out


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
    behavior = behavior_contract(
        root,
        source["behavior_type"],
        reject_deprecated_values=(
            mapping.get("native", {}).get("deprecated_enum_policy") == "reject"
        ),
    )

    selector_props = {}
    selector_field_meta = {}
    for alternative in mapping["native"]["object_selector_alternatives"]:
        for name in alternative:
            field = object_fields[name]
            dtypes = source_datatypes(field)
            selector_props[name] = generic_entity_schema(dtypes, state=False)
            selector_props[name]["description"] = docs(field)
            selector_field_meta[name] = {
                "source_type": field.get("type"),
                "datatypes": dtypes,
            }

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

    state_names = []
    state_meta = {}
    for name, field in state_fields.items():
        if name in {"signature"}:
            continue
        # The direct inline traversal may see helper elements in nested custom
        # types; only fields whose nearest semantic owner is the State sequence
        # are retained by the mapping's source State. For the first vertical
        # slice, drop known XML helper names.
        if name in {"value"}:
            continue
        dtypes = source_datatypes(field)
        state_names.append(name)
        state_meta[name] = {
            "source_type": field.get("type"),
            "datatypes": dtypes,
            "description": docs(field),
        }

    state_field_branches = [
        {
            "properties": {
                "field": {"const": name},
                "datatype": {
                    "type": "string",
                    "enum": sorted(set(meta["datatypes"])),
                },
            },
            "required": ["field"],
        }
        for name, meta in sorted(state_meta.items())
    ]

    controls = mapping["native"]["test_result_controls"]
    capability = mapping["capability"]
    generated = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://scap-ng.dev/schema/v0.1.0/generated/capabilities/{capability}.schema.json",
        "title": f"Generated SCAP-NG capability fragment: {capability}",
        "description": docs(test_el),
        "x-scap-ng-generated": {
            "generator": "tools/generate_capability_schema.py",
            "mapping_format": mapping["format"],
            "source_language": source["language"],
            "source_schema": source["definitions_schema"],
            "source_namespace": source["namespace"],
            "source_test": source["test"],
            "source_object": source["object"],
            "source_state": source["state"],
        },
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
                        "type": "string",
                        "enum": controls["check_existence"],
                    },
                    "check": {
                        "type": "string",
                        "enum": controls["check"],
                    },
                    "state_operator": {
                        "type": "string",
                        "enum": controls["state_operator"],
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
                    "behaviors": behavior,
                    "set": {"type": "object"},
                    "filters": {
                        "type": "array",
                        "items": {
                            "$ref": f"{COMMON_CAPABILITY_SCHEMA_ID}#/$defs/state_filter"
                        },
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
        "x-source-field-catalog": {
            "object_selectors": selector_field_meta,
            "state_fields": state_meta,
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
        "state_fields": len(generated["x-source-field-catalog"]["state_fields"]),
        "object_selectors": sorted(generated["x-source-field-catalog"]["object_selectors"]),
        "semantic_rules": len(generated["x-semantic-validator-rules"]),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
