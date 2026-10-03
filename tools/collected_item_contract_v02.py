#!/usr/bin/env python3
"""Bounded 0.2.0 Item result draft; never changes 0.1.0 authoring schemas."""
import argparse
import copy
import json
from datetime import datetime
from pathlib import Path

from generate_capability_schema import generate, collected_value_schema

ROOT = Path(__file__).resolve().parents[1]
ITEM_ID = "https://scap-ng.dev/experimental/0.2.0/collected-item.schema.json"
TYPES_ID = "https://scap-ng.dev/experimental/0.2.0/result-types.schema.json"
STATUSES = ["exists", "does_not_exist", "error", "not_collected"]
# New fields are result-only. Values are resolved in the observed target namespace.
NAMES = json.loads((ROOT / "schema/v0.2.0/result-field-extensions.json").read_text())["capabilities"]


def shared(root=ROOT):
    item = json.loads((root / "schema/v0.1.0/collected-item.schema.json").read_text())
    types = json.loads((root / "schema/v0.1.0/result-types.schema.json").read_text())
    item["$id"], types["$id"] = ITEM_ID, TYPES_ID
    item["title"] = "Experimental collected Item 0.2.0 result slice"
    item["properties"]["status"] = {"enum": STATUSES}
    types["title"] = "Experimental collected Item 0.2.0 value types"
    typed = types["$defs"]["typed_value"]
    typed["properties"]["status"] = {"enum": STATUSES}
    # Status omission retains the existing observed-value convention.
    typed["allOf"].insert(0, {
        "if": {"required": ["status"], "properties": {"status": {"enum": STATUSES[1:]}}},
        "then": {"not": {"required": ["value"]}},
    })
    # A missing/error record has no payload; recurse only for observed records.
    typed["allOf"][-1]["if"]["allOf"].append({
        "not": {"required": ["status"], "properties": {"status": {"enum": STATUSES[1:]}}}
    })
    text = {"type": "string", "minLength": 1}
    resolution = {
        "type": "object", "required": ["source_field", "target_context_ref", "source_ref", "observed_at"],
        "properties": {k: text for k in ["source_field", "target_context_ref", "source_ref", "observed_at"]},
        "additionalProperties": False,
    }
    resolution["properties"]["observed_at"] = {"type": "string", "format": "date-time"}
    locator = {
        "type": "object", "required": ["kind", "source_ref"],
        "properties": {
            "kind": {"enum": ["text", "structured", "record"]}, "source_ref": text,
            "line": {"type": "integer", "minimum": 1},
            "column": {"type": "integer", "minimum": 1},
            "path": text, "path_language": text,
            "index": {"type": "integer", "minimum": 0},
            "field": text,
            "value_index": {"type": "integer", "minimum": 0},
            "property": text,
        },
        "allOf": [
            {"if": {"properties": {"kind": {"const": "text"}}}, "then": {"required": ["line"], "not": {"anyOf": [{"required": [k]} for k in ["path", "path_language", "index"]]}}},
            {"if": {"properties": {"kind": {"const": "structured"}}}, "then": {"required": ["path", "path_language"], "not": {"anyOf": [{"required": [k]} for k in ["line", "column", "index"]]}}},
            {"if": {"properties": {"kind": {"const": "record"}}}, "then": {"required": ["index"], "not": {"anyOf": [{"required": [k]} for k in ["line", "column", "path", "path_language"]]}}},
        ], "additionalProperties": False,
    }
    locator["allOf"].extend([
        {"if": {"anyOf": [{"required": ["value_index"]}, {"required": ["property"]}]},
         "then": {"required": ["field"], "properties": {"kind": {"const": "record"}}}},
    ])
    item["properties"]["context"] = {
        "type": "object", "properties": {
            "name_resolution": {"type": "object", "additionalProperties": resolution},
            "locators": {"type": "array", "items": locator},
            "origin": {"type": "object", "required": ["result_ref", "item_ref"],
                       "properties": {"result_ref": text, "item_ref": text}, "additionalProperties": False},
        }, "additionalProperties": False,
    }
    item["allOf"] = [{
        "if": {"required": ["imported"], "properties": {"imported": {"const": True}}},
        "then": {"required": ["context"], "properties": {"context": {"required": ["origin"]}}},
    }]
    item = json.loads(json.dumps(item).replace("result-types.schema.json#", TYPES_ID + "#"))
    return item, types


def capability_schema(mapping, root=ROOT):
    generated = generate(mapping, root)
    fragment = generated.get("$defs", {}).get("collected_item")
    if fragment is None:
        return None
    fragment = copy.deepcopy(fragment)
    fragment["allOf"][0]["$ref"] = ITEM_ID
    fields = fragment["allOf"][1]["properties"]["fields"]["properties"]
    for name, source in NAMES.get(mapping["capability"], {}).items():
        if source not in fields or name in fields:
            raise ValueError(f"Invalid result extension {mapping['capability']}.{name}")
        fields[name] = collected_value_schema(["string"])
        fields[name]["allOf"].append({"properties": {"value": {"type": "string"}}})
    fragment = json.loads(json.dumps(fragment).replace(
        "https://scap-ng.dev/schema/v0.1.0/result-types.schema.json", TYPES_ID))
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", **fragment}


def context_errors(item):
    """Cross-field constraints beyond JSON Schema; call after structural validation."""
    fields = item["fields"]
    resolutions = item.get("context", {}).get("name_resolution", {})
    names = NAMES.get(item["capability"], {})
    errors = []
    for name in resolutions:
        if name not in names or name not in fields:
            errors.append(f"Unrecognized or absent resolved field: {name}")
    for name, source in names.items():
        if name not in fields:
            continue
        if source not in fields:
            errors.append(f"{name} requires numeric source {source}")
        metadata = resolutions.get(name)
        if metadata is None or metadata["source_field"] != source:
            errors.append(f"{name} requires resolution provenance for {source}")
        if metadata is not None:
            try:
                timestamp = datetime.fromisoformat(metadata["observed_at"].replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    raise ValueError("Missing timezone")
            except ValueError:
                errors.append(f"{name} requires a timestamp with timezone")
        original = fields.get(source, {})
        resolved = fields[name]
        if "value" in resolved and (original.get("redacted") or original.get("status", "exists") != "exists" or "value" not in original):
            errors.append(f"{name} cannot expose a name for an unavailable/redacted identity")
    for locator in item.get("context", {}).get("locators", []):
        if "field" in locator and locator["field"] not in fields:
            errors.append(f"Locator references absent field: {locator['field']}")
            continue
        value = fields.get(locator.get("field"), {})
        if "value_index" in locator:
            index = locator["value_index"]
            if not isinstance(value, list) or index >= len(value):
                errors.append("Locator value_index does not reference an emitted value")
                continue
            value = value[index]
        if "property" in locator:
            if not isinstance(value, dict) or value.get("datatype") != "record" or locator["property"] not in value.get("value", {}):
                errors.append("Locator property does not reference an emitted record property")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    item, types = shared()
    files = {"collected-item.schema.json": item, "result-types.schema.json": types}
    for path in sorted((ROOT / "schema/v0.1.0/capability-mappings").glob("*.json")):
        mapping = json.loads(path.read_text())
        if "capability" in mapping:
            schema = capability_schema(mapping)
            if schema is not None:
                files[mapping["capability"] + ".schema.json"] = schema
    for name, data in files.items():
        (args.output / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(files) - 2} experimental Item contracts; no authoring schemas changed")


if __name__ == "__main__":
    main()
