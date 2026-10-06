#!/usr/bin/env python3
"""Draft Test reporting controls and derived Item projections, never evaluation."""
from __future__ import annotations
import copy
import argparse
import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
import yaml
from generate_capability_schema import generate
from capability_registry import load_mapping

ROOT = Path(__file__).resolve().parents[1]
@lru_cache(maxsize=None)
def control_schema(version="0.2.0"):
    return json.loads(
        (ROOT / f"schema/v{version}/reported-elements.schema.json").read_text()
    )


@lru_cache(maxsize=None)
def result_extensions(version="0.2.0"):
    return json.loads(
        (ROOT / f"schema/v{version}/result-field-extensions.json").read_text()
    )["capabilities"]


# Backward-compatible public 0.2 constants. Version-aware code uses the
# accessors above, but existing 0.2 callers/tests still import these names.
CONTROL = control_schema("0.2.0")
EXTENSIONS = result_extensions("0.2.0")


@lru_cache(maxsize=None)
def capability_fields(capability, version="0.2.0"):
    if not isinstance(capability, str) or not capability:
        raise ValueError("A capability identifier is required")
    mapping = load_mapping(capability, version)
    generated = generate(mapping, ROOT, schema_version=version)
    item = generated.get("$defs", {}).get("collected_item")
    fields = set()
    for fragment in (item or {}).get("allOf", []):
        fields.update(fragment.get("properties", {}).get("fields", {}).get("properties", {}))
    names = result_extensions(version).get(capability, {})
    if not set(names.values()) <= fields or set(names) & fields:
        raise ValueError(f"Invalid reviewed result-only extensions for {capability}")
    return frozenset(fields | set(names))


def validate_control(control, capability, version="0.2.0"):
    Draft202012Validator(control_schema(version)).validate(control)
    # "all" and "compared" do not name capability fields, so they remain valid
    # for explicitly permitted conversion-only capability vocabulary. Only an
    # authored field list needs capability-specific field-name validation.
    if not isinstance(control, list):
        return
    known = capability_fields(capability, version)
    if not set(control) <= known:
        raise ValueError(f"Unknown reported elements for {capability}: {sorted(set(control) - known)}")


def source_errors(assessment):
    """Validate all authored Test controls, including unexecuted Tests."""
    errors = []
    version = assessment.get("specification", {}).get("version")
    modern = version in {"0.2.0", "0.3.0"}
    for identity, test in assessment.get("tests", {}).items():
        if modern and "reported_elements" not in test:
            errors.append(f"{identity}: reported_elements is required in {version}")
            continue
        if "reported_elements" not in test:
            continue
        if not modern:
            errors.append(f"{identity}: reported_elements requires the draft 0.2.0 specification")
            continue
        try:
            validate_control(test["reported_elements"], test["capability"], version)
        except (ValueError, KeyError, ValidationError) as exc:
            errors.append(f"{identity}: {exc}")
    return errors


def generate_reporting_capability(mapping, root=ROOT, version=None):
    """Versioned Test-schema overlay; Object and State contracts stay identical."""
    version = version or mapping.get("specification_version", "0.2.0")
    generated = generate(mapping, root, schema_version=version)
    schema = copy.deepcopy(generated)
    schema["$id"] = f"https://scap-ng.dev/schema/v{version}/capabilities/{mapping['capability']}.schema.json"
    known = sorted(capability_fields(mapping["capability"], version))
    schema["$defs"]["test"]["properties"]["reported_elements"] = {
        "oneOf": [{"enum": ["all", "compared"]},
                  {"type": "array", "items": {"enum": known} if known else False, "uniqueItems": True}],
    }
    return schema


def _check_redaction(value):
    if isinstance(value, dict):
        if value.get("redacted") is True and "value" in value:
            raise ValueError("Redacted typed value must not carry value")
        for child in value.values():
            _check_redaction(child)
    elif isinstance(value, list):
        for child in value:
            _check_redaction(child)


def project_items(assessment, items, uses, *, source_execution_ref, source_completeness):
    """Produce a marked, derived report from already evaluated/redacted Items.

    uses is complete execution lineage: [{test_ref, item_ref, used_elements,
    required_elements, relationship?}]. used_elements includes indirect Variable/Filter/selection
    use, not just direct State comparison. required_elements includes resource
    identity and other decisive evidence. Callers must supply actual execution
    lineage; this routine never guesses it from authored expressions.
    """
    errors = source_errors(assessment)
    version = assessment.get("specification", {}).get("version") or "0.2.0"
    if errors:
        raise ValueError("; ".join(errors))
    if not isinstance(source_execution_ref, str) or not source_execution_ref:
        raise ValueError("A source execution reference is required")
    if set(source_completeness) != {"logical_complete", "population_complete", "evidence_complete"} or any(type(v) is not bool for v in source_completeness.values()):
        raise ValueError("Explicit source completeness flags are required")
    indexed = {}
    for item in items:
        if item["id"] in indexed:
            raise ValueError(f"Duplicate Item identity: {item['id']}")
        _check_redaction(item)
        if not set(item["fields"]) <= capability_fields(item["capability"], version):
            raise ValueError(f"Unknown Item fields: {item['id']}")
        for name, source in result_extensions(version).get(item["capability"], {}).items():
            if name not in item["fields"]:
                continue
            original = item["fields"].get(source)
            if original is None:
                raise ValueError(f"{name} requires numeric source {source}")
            if "value" in item["fields"][name] and (original.get("redacted") or original["status"] != "exists" or "value" not in original):
                raise ValueError(f"{name} cannot expose an unavailable/redacted identity")
        indexed[item["id"]] = item
    requests = {identity: [] for identity in indexed}
    mandatory = {identity: set() for identity in indexed}
    for use in uses:
        if set(use) - {"test_ref", "item_ref", "used_elements", "required_elements", "relationship"} or not {"test_ref", "item_ref", "used_elements", "required_elements", "relationship"} <= set(use):
            raise ValueError("Complete Test/Item field-use lineage is required")
        test = assessment.get("tests", {}).get(use["test_ref"])
        item = indexed.get(use["item_ref"])
        if test is None or item is None:
            raise ValueError("Field-use lineage references an unknown Test or Item")
        relationship = use["relationship"]
        if relationship not in {"direct", "variable", "filter", "selection"}:
            raise ValueError("Unknown field-use relationship")
        if relationship == "direct" and test["capability"] != item["capability"]:
            raise ValueError("Field-use lineage capability mismatch")
        for key in ("used_elements", "required_elements"):
            validate_control(use[key], item["capability"], version)
            if not isinstance(use[key], list):
                raise ValueError("Field-use lineage must contain explicit arrays")
        used = set(use["used_elements"])
        mandatory[item["id"]].update(used | set(use["required_elements"]))
        control = test["reported_elements"]
        # Explicit names belong to the Test's declared capability. Upstream
        # Items of another capability retain actual use rather than interpreting
        # unrelated names in a different field vocabulary.
        selected = None if control == "all" else used if control == "compared" or test["capability"] != item["capability"] else set(control)
        requests[item["id"]].append(selected)
    projected = []
    for identity in sorted(indexed):
        original = indexed[identity]
        available = set(original["fields"])
        item_requests = requests[identity]
        # Without complete Test lineage, preserve the Item in full.
        requested = available if not item_requests or any(r is None for r in item_requests) else set().union(*item_requests)
        keep = requested | mandatory[identity]
        for name, source in result_extensions(version).get(original["capability"], {}).items():
            if name in keep and name in available:
                keep.add(source)
                mandatory[identity].add(source)
        item = copy.deepcopy(original)
        item["fields"] = {field: item["fields"][field] for field in sorted(available & keep)}
        context = item.get("context", {})
        if "name_resolution" in context:
            context["name_resolution"] = {k: v for k, v in context["name_resolution"].items() if k in item["fields"]}
        if "locators" in context:
            context["locators"] = [locator for locator in context["locators"] if "field" not in locator or locator["field"] in item["fields"]]
        projected.append({"item": item, "selection": {
            "omitted_elements": sorted(available - keep),
            "unavailable_elements": sorted(keep - available),
            "retained_required_elements": sorted(mandatory[identity] & available),
        }})
    return {"item_report": {"kind": "reported_elements_projection", "source_execution_ref": source_execution_ref,
                            "source_completeness": copy.deepcopy(source_completeness), "items": projected}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate_parser = commands.add_parser("generate", help="Generate a reviewed capability's 0.2.0 reporting overlay")
    generate_parser.add_argument("--mapping", type=Path, required=True)
    generate_parser.add_argument("--output", type=Path, required=True)
    project_parser = commands.add_parser("project", help="Project previously evaluated/redacted Items with execution lineage")
    project_parser.add_argument("--assessment", type=Path, required=True)
    project_parser.add_argument("--observations", type=Path, required=True)
    project_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        result = generate_reporting_capability(json.loads(args.mapping.read_text(encoding="utf-8")))
        Draft202012Validator.check_schema(result)
    else:
        assessment = yaml.safe_load(args.assessment.read_text(encoding="utf-8"))["assessment"]
        observations = json.loads(args.observations.read_text(encoding="utf-8"))
        result = project_items(assessment, observations["items"], observations["uses"],
                               source_execution_ref=observations["source_execution_ref"],
                               source_completeness=observations["source_completeness"])
        from validate_native_json_schemas import validator, schema_store
        schema_dir = ROOT / "schema/v0.2.0"
        validator(schema_dir, "item-report.schema.json", schema_store(schema_dir)).validate(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
