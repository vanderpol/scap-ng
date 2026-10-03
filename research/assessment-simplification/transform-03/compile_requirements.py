#!/usr/bin/env python3
"""EXPERIMENTAL, bounded authoring transform; not a production converter/scanner."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys

import jsonschema
from referencing import Registry, Resource
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from generate_capability_schema import generate
from validate_generated_capability_semantics import validate_assessment_capability_semantics

FORMAT = "experimental-permission-authoring-v1"
RIGHTS = {
    "owner": {"read": "owner_read", "write": "owner_write", "execute": "owner_execute"},
    "group": {"read": "group_read", "write": "group_write", "execute": "group_execute"},
    "other": {"read": "other_read", "write": "other_write", "execute": "other_execute"},
    "special": {"setuid": "setuid", "setgid": "setgid", "sticky": "sticky"},
}


class AuthoringError(ValueError):
    pass


class UniqueLoader(yaml.SafeLoader):
    """Do not let repeated YAML keys silently replace executable policy."""


def unique_mapping(loader, node, deep=False):
    output = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in output:
            raise AuthoringError("mapping keys must be unique strings; YAML merge keys are unsupported")
        output[key] = loader.construct_object(value_node, deep=deep)
    return output


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load_author(path):
    return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=UniqueLoader)


def shape(value, required, optional=(), label="value"):
    if not isinstance(value, dict):
        raise AuthoringError(f"{label}: expected mapping")
    missing, extra = set(required) - value.keys(), value.keys() - set(required) - set(optional)
    if missing or extra:
        raise AuthoringError(f"{label}: missing {sorted(missing)}, unsupported {sorted(extra)}")


def name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", value):
        raise AuthoringError("names must be lower-case stable identifiers, independent of titles")
    return value


def text(value, label):
    if not isinstance(value, str) or not value:
        raise AuthoringError(f"{label}: expected nonempty literal string")
    return value


def permission_fields(allowance):
    shape(allowance, RIGHTS, label="permissions_at_most")
    forbidden = []
    for category, rights in RIGHTS.items():
        allowed = allowance[category]
        if (not isinstance(allowed, list) or any(not isinstance(r, str) for r in allowed)
                or len(set(allowed)) != len(allowed) or set(allowed) - rights.keys()):
            raise AuthoringError(f"{category}: use unique rights from {list(rights)}")
        forbidden.extend(field for right, field in rights.items() if right not in allowed)
    if not forbidden:
        raise AuthoringError("unrestricted allowance: use a native existence-only Test; not implemented here")
    return forbidden


def entity(value, operation="equal"):
    return {"value": value, "operation": operation, "datatype": "string"}


def file_object(identifier, files):
    if not isinstance(files, dict):
        raise AuthoringError("files: expected mapping")
    if "path" in files:
        shape(files, ("path", "filesystem"), label="files")
        select = {"full_path": entity(text(files["path"], "path"))}
        traversal = None
    else:
        shape(files, ("directory", "names_matching", "depth", "recurse", "filesystem"), label="files")
        select = {"directory": entity(text(files["directory"], "directory")),
                  "name": entity(text(files["names_matching"], "names_matching"), "match")}
        # Regex is passed unchanged to the native matcher, not interpreted by Python.
        if type(files["depth"]) is not int or files["depth"] < 0:
            raise AuthoringError("depth: expected nonnegative integer")
        traversal = {"max_depth": files["depth"], "recurse": files["recurse"]}
    obj = {"object_title": identifier, "capability": "unix.file", "select": select}
    if traversal is not None:
        obj["traversal"] = traversal
    obj["filesystem"] = files["filesystem"]
    return obj


def validate_native(document):
    """Generic schema + reviewed deep unix.file mapping + cross-node rules."""
    jsonschema.Draft202012Validator(json.loads(
        (ROOT / "schema/v0.1.0/assessment.schema.json").read_text())).validate(document)
    mapping = json.loads((ROOT / "schema/v0.1.0/capability-mappings/unix.file.json").read_text())
    generated = generate(mapping, ROOT)
    common = json.loads((ROOT / "schema/v0.1.0/capability-common.schema.json").read_text())
    registry = Registry().with_resource(common["$id"], Resource.from_contents(common))
    assessment = document["assessment"]
    for plural, kind in (("objects", "object"), ("states", "state"), ("tests", "test")):
        validator = jsonschema.Draft202012Validator(generated["$defs"][kind], registry=registry)
        for node in assessment[plural].values():
            validator.validate(node)
    diagnostics = validate_assessment_capability_semantics(document)
    if diagnostics:
        raise AuthoringError(json.dumps(diagnostics))
    # The prototype emits only a fixed conjunction; explicitly verify reference closure.
    for test in assessment["tests"].values():
        if test["object"] not in assessment["objects"]:
            raise AuthoringError("missing Object reference")
        if any(s not in assessment["states"] for s in test["states"]):
            raise AuthoringError("missing State reference")
    expected = [{"test": key} for key in assessment["tests"]]
    if assessment["evaluate"] != {"all": expected}:
        raise AuthoringError("evaluation references differ from the authored fixed Test set")


def compile_author(author):
    shape(author, ("format", "id", "title", "objects", "tests"), label="author document")
    if author["format"] != FORMAT:
        raise AuthoringError("unsupported authoring format or runtime method")
    if not isinstance(author["objects"], dict) or not author["objects"]:
        raise AuthoringError("objects: expected nonempty named Objects")
    if not isinstance(author["tests"], dict) or not author["tests"]:
        raise AuthoringError("tests: expected nonempty fixed Tests")
    assessment = {"id": text(author["id"], "id"), "version": 1,
                  "assessment_title": text(author["title"], "title"), "mode": "automated",
                  "class": "compliance", "purpose": "assessment",
                  "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.1.0"}, "objects": {},
                  "states": {}, "tests": {}}
    source_map = {"status": "experimental_compiler_mapping_not_scan_evidence", "objects": {}, "tests": {}, "states": {}}
    for identifier, payload in author["objects"].items():
        name(identifier)
        shape(payload, ("files",), label=f"Object {identifier}")
        native_id = f"object-{identifier}"
        assessment["objects"][native_id] = file_object(identifier, payload["files"])
        source_map["objects"][identifier] = native_id
    for identifier, payload in author["tests"].items():
        name(identifier)
        shape(payload, ("every", "missing", "permissions_at_most"), label=f"Test {identifier}")
        if not isinstance(payload["every"], str) or payload["every"] not in author["objects"]:
            raise AuthoringError(f"Test {identifier}: unknown Object")
        if payload["missing"] not in ("allowed", "violation"):
            raise AuthoringError("missing: use allowed or violation")
        native_id = f"test-{identifier}"
        refs = []
        for field in permission_fields(payload["permissions_at_most"]):
            state_id = f"state-{identifier}-{field.replace('_', '-')}"
            refs.append(state_id)
            assessment["states"][state_id] = {
                "state_title": f"{identifier}: {field} must be false",
                "capability": "unix.file", "state": {
                    "field": field, "value": False, "operation": "equal", "datatype": "boolean",
                    "match": "all", "existence": "some"}}
            category, right = next((category, right) for category, rights in RIGHTS.items()
                                   for right, mapped_field in rights.items() if mapped_field == field)
            source_map["states"][state_id] = {
                "test": identifier, "author_path": f"tests.{identifier}.permissions_at_most.{category}",
                "forbidden_right": right, "field": field,
                "message": f"{category} {right} is outside the allowed permissions"}
        assessment["tests"][native_id] = {
            "test_title": identifier, "capability": "unix.file", "object": f"object-{payload['every']}",
            "existence": "optional" if payload["missing"] == "allowed" else "some", "match": "all",
            "states_match": "all", "states": refs}
        source_map["tests"][identifier] = {"test": native_id, "states": refs}
    assessment["evaluate"] = {"all": [{"test": key} for key in assessment["tests"]]}
    document = {"assessment": assessment}
    try:
        validate_native(document)
    except jsonschema.ValidationError as exc:
        raise AuthoringError(f"invalid native contract: {exc.message}") from exc
    return deepcopy(document), source_map


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-map", type=Path, required=True)
    args = parser.parse_args()
    document, source_map = compile_author(load_author(args.source))
    args.output.write_text("# EXPERIMENTAL compiled authoring; unchanged native target.\n" +
                           yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    args.source_map.write_text(json.dumps(source_map, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
