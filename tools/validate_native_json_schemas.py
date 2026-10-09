#!/usr/bin/env python3
"""Validate native SCAP-NG YAML documents against versioned JSON Schemas.

This harness deliberately keeps JSON-Schema validation separate from semantic
graph validation.  YAML is loaded into the ordinary JSON data model before
validation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import deque

import yaml
from jsonschema import Draft202012Validator, RefResolver, ValidationError


DOCUMENTS = {
    "benchmark.yaml": ("benchmark", "benchmark.schema.json"),
    "applicability.yaml": ("applicability", "applicability.schema.json"),
    "organizational-input.yaml": ("organizational-input", "organizational-input.schema.json"),
    "package-manifest.yaml": ("package-manifest", "package-manifest.schema.json"),
}


def load_yaml(path: Path):
    value=yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def schema_store(schema_dir: Path):
    store={}
    paths = list(schema_dir.glob("*.schema.json"))
    for path in paths:
        doc=json.loads(path.read_text(encoding="utf-8"))
        if "$id" in doc:
            store[doc["$id"]]=doc
    return store


def validator(schema_dir: Path, filename: str, store):
    schema=json.loads((schema_dir/filename).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    resolver=RefResolver.from_schema(schema,store=store)
    return Draft202012Validator(schema,resolver=resolver)



def build_validators(schema_dir: Path):
    """Build each document validator once over one shared reference store."""
    store=schema_store(schema_dir)
    validators={}
    for _, schema_name in sorted(set(DOCUMENTS.values())):
        if (schema_dir/schema_name).exists():
            validators[schema_name]=validator(schema_dir,schema_name,store)
    for schema_name in (
        "rule.schema.json", "manual-assessment.schema.json",
        "assessment-result.schema.json", "tailoring.schema.json",
        "assessment.schema.json",
    ):
        if (schema_dir/schema_name).exists() and schema_name not in validators:
            validators[schema_name]=validator(schema_dir,schema_name,store)
    return validators

def classify(path: Path):
    if path.name in DOCUMENTS:
        return DOCUMENTS[path.name]
    name=path.name
    if name.endswith(".rule.yaml") or (path.parent.name=="rules" and path.suffix==".yaml"):
        return "rule","rule.schema.json"
    if name.endswith(".assessment-result.yaml"):
        return "assessment-result","assessment-result.schema.json"
    if name.endswith(".tailoring.yaml"):
        return "tailoring","tailoring.schema.json"
    if name.endswith(".organizational-input.yaml"):
        return "organizational-input","organizational-input.schema.json"
    if name.endswith(".assessment.yaml") or ("assessments" in path.parts and path.suffix==".yaml"):
        return "assessment","assessment.schema.json"
    return None


def document_errors(v, doc, *, allow_unpromoted_conversion_vocabulary=False):
    """Structural errors plus required semantic uniqueness of manual answers.

    JSON Schema uniqueItems cannot enforce uniqueness by one object property.
    Reject both exact and conflicting duplicates, preserving distinct answers
    that intentionally share an outcome. Invalid shapes remain schema errors.
    """
    yield from v.iter_errors(doc)
    # New versioned capability contracts are checked even in skipped branches.
    assessment = doc.get("assessment")
    if isinstance(assessment, dict):
        from capability_registry import draft_capabilities, load_mapping, mappings
        from generate_capability_schema import generate
        from reported_elements import generate_reporting_capability
        from referencing import Registry, Resource

        declared_version = (assessment.get("specification") or {}).get("version")
        modern_versions = {"0.2.0", "0.3.0"}
        draft = (
            draft_capabilities(version=declared_version)
            if declared_version in modern_versions
            else draft_capabilities(version="0.2.0")
        )
        legacy_v02_drafts = draft_capabilities(version="0.2.0")
        root = Path(__file__).resolve().parents[1]
        version_store = (
            schema_store(root / f"schema/v{declared_version}")
            if declared_version in modern_versions
            else {}
        )
        registry = Registry().with_resources(
            (uri, Resource.from_contents(schema))
            for uri, schema in version_store.items()
        )

        def capability_node_errors(kind, node, path):
            capability = node.get("capability") if isinstance(node, dict) else None
            if not isinstance(capability, str):
                return []
            if declared_version not in modern_versions:
                if capability in legacy_v02_drafts:
                    return [ValidationError(
                        "New capability requires specification 0.2.0",
                        path=deque(path),
                    )]
                return []

            try:
                mapping = load_mapping(capability, declared_version)
            except ValueError:
                mapping = None
                if allow_unpromoted_conversion_vocabulary:
                    from scap_upconvert_v003.native_capability_mapping import source_capability
                    candidates = [
                        candidate for candidate in mappings(declared_version)
                        if source_capability(candidate) == capability
                        and not (candidate.get("native") or {}).get("post_alignment_ready", False)
                    ]
                    if len(candidates) == 1:
                        return []
                return [ValidationError(
                    f"Unknown {declared_version} capability: {capability}",
                    path=deque(path + ["capability"]),
                )]

            if (
                allow_unpromoted_conversion_vocabulary
                and not (mapping.get("native") or {}).get("post_alignment_ready", False)
            ):
                return []

            generated = (
                generate_reporting_capability(mapping, version=declared_version)
                if kind == "test"
                else generate(
                    mapping,
                    root,
                    schema_version=declared_version,
                )
            )
            if kind not in generated["$defs"]:
                return [ValidationError(
                    "Capability does not support this source node",
                    path=deque(path),
                )]
            validator = Draft202012Validator(
                generated["$defs"][kind],
                registry=registry,
            )
            errors=[]
            for error in validator.iter_errors(node):
                error.path.extendleft(reversed(path))
                errors.append(error)
            return errors

        # 0.3 predicates have no independent capability or State ID. Validate
        # each embedded expression against the generated schema for its actual
        # Test or collected Item capability. General assessment JSON Schema
        # checks only the shape; this pass checks allowable typed fields.
        if declared_version == "0.3.0":
            predicate_validators = {}

            def validate_local_predicate(predicate, capability, path):
                if not isinstance(capability, str):
                    yield ValidationError("Cannot resolve predicate capability", path=deque(path))
                    return
                if capability not in predicate_validators:
                    try:
                        mapping = load_mapping(capability, declared_version)
                        fragment = generate(mapping, root, schema_version=declared_version)
                        if "state_expression" not in fragment.get("$defs", {}):
                            predicate_validators[capability] = None
                        else:
                            fragment = dict(fragment, **{"$ref": "#/$defs/state_expression"})
                            predicate_validators[capability] = Draft202012Validator(
                                fragment, registry=registry
                            )
                    except (ValueError, KeyError) as exc:
                        yield ValidationError(
                            f"Cannot load predicate capability {capability}: {exc}",
                            path=deque(path)
                        )
                        return
                pred_validator = predicate_validators[capability]
                if pred_validator is None:
                    yield ValidationError(
                        f"Capability {capability} has no State/predicate expression",
                        path=deque(path)
                    )
                    return
                for error in pred_validator.iter_errors(predicate):
                    error.path.extendleft(reversed(path))
                    yield error

                # JSON Schema cannot express every cross-field native type
                # dependency. Preserve the same explicit scalar/array datatype
                # validation performed by the semantic pipeline, for both
                # consumer-local Tests and observed-Item Filters.
                from validate_generated_capability_semantics import (
                    _native_literal_or_collection_matches_datatype,
                )
                pending = [(predicate, path)]
                while pending:
                    node, local_path = pending.pop()
                    if not isinstance(node, dict):
                        continue
                    if "datatype" in node and "value" in node:
                        value, datatype = node["value"], node["datatype"]
                        if not isinstance(value, dict) and not _native_literal_or_collection_matches_datatype(
                            value, datatype
                        ):
                            yield ValidationError(
                                f"Predicate literal {value!r} does not match authored datatype {datatype!r}",
                                validator="native_literal_datatype",
                                path=deque(local_path + ["value"]),
                            )
                    for operator in ("all", "any", "one", "odd"):
                        if isinstance(node.get(operator), list):
                            for index, child in enumerate(node[operator]):
                                pending.append((child, local_path + [operator, index]))

            object_registry = {
                **(assessment.get("objects") or {}),
                **(assessment.get("shared_objects") or {}),
            }
            for test_name, test in (assessment.get("tests") or {}).items():
                if not isinstance(test, dict):
                    continue
                for i, predicate in enumerate(test.get("states") or []):
                    yield from validate_local_predicate(
                        predicate, test.get("capability"),
                        ["assessment", "tests", test_name, "states", i]
                    )

            def filter_uses(value, path, capability=None):
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        yield from filter_uses(item, path + [i], capability)
                elif isinstance(value, dict):
                    current_cap = value.get("capability", capability)
                    object_use = value.get("object")
                    if "filters" in value:
                        if isinstance(object_use, str):
                            ref = object_registry.get(object_use)
                            current_cap = ref.get("capability") if isinstance(ref, dict) else None
                        elif isinstance(object_use, dict):
                            current_cap = object_use.get("capability", current_cap)
                        for i, flt in enumerate(value.get("filters") or []):
                            if not isinstance(flt, dict):
                                continue
                            predicate = {k: v for k, v in flt.items() if k != "action"}
                            yield predicate, current_cap, path + ["filters", i]
                    for key, child in value.items():
                        if key == "filters":
                            continue
                        if isinstance(child, (dict, list)):
                            yield from filter_uses(child, path + [key], current_cap)

            for predicate, cap, path in filter_uses(assessment, ["assessment"]):
                yield from validate_local_predicate(predicate, cap, path)

        named_sections = [
            ("tests", "test"),
        ]
        if declared_version != "0.3.0":
            named_sections.insert(0, ("states", "state"))
        if declared_version == "0.3.0":
            named_sections.insert(0, ("shared_objects", "object"))
        else:
            named_sections.insert(0, ("objects", "object"))

        for section, kind in named_sections:
            nodes = assessment.get(section, {})
            if not isinstance(nodes, dict):
                continue
            for identity, node in nodes.items():
                yield from capability_node_errors(
                    kind, node, ["assessment", section, identity]
                )

        # Consumer-local 0.3 components still require the exact same generated
        # capability contracts as named components. Locate them structurally by
        # typed object/state use sites rather than by an Assessment registry.
        if declared_version == "0.3.0":
            def inline_nodes(value, path=()):
                if isinstance(value, dict):
                    for key, child in value.items():
                        child_path = path + (key,)
                        if (
                            key == "object"
                            and isinstance(child, dict)
                            and isinstance(child.get("capability"), str)
                        ):
                            yield "object", child, child_path
                        elif (
                            key == "state"
                            and isinstance(child, dict)
                            and isinstance(child.get("capability"), str)
                        ):
                            yield "state", child, child_path
                        yield from inline_nodes(child, child_path)
                elif isinstance(value, list):
                    for index, child in enumerate(value):
                        yield from inline_nodes(child, path + (index,))

            for kind, node, path in inline_nodes(assessment, ("assessment",)):
                yield from capability_node_errors(kind, node, list(path))
    assessment = doc.get("assessment")
    if not isinstance(assessment, dict) or assessment.get("mode") != "manual":
        return
    response = assessment.get("response")
    if not isinstance(response, dict) or not isinstance(response.get("choices"), list):
        return
    seen = {}
    for index, choice in enumerate(response["choices"]):
        if not isinstance(choice, dict) or not isinstance(choice.get("value"), str):
            continue
        value = choice["value"]
        if value in seen:
            yield ValidationError(
                f"Duplicate manual response value {value!r}; first declared at choices/{seen[value]}",
                validator="unique_response_value",
                path=deque(["assessment", "response", "choices", index, "value"]),
            )
        else:
            seen[value] = index


def diagnostic_value(value):
    """Return a stable JSON-safe representation for jsonschema diagnostics."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [diagnostic_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): diagnostic_value(item) for key, item in value.items()}
    return str(value)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus_root",type=Path)
    ap.add_argument("--schema-dir",type=Path,required=True)
    ap.add_argument("--report",type=Path)
    ap.add_argument("--allow-unpromoted-conversion-vocabulary", action="store_true",
                    help="Accept lossless aligned OVAL vocabulary only for known 0.2.0 mappings not yet promoted by the legacy converter; strict native validation remains the default.")
    args=ap.parse_args()

    validators=build_validators(args.schema_dir)
    results=[]
    unclassified=[]
    for path in sorted(args.corpus_root.rglob("*.yaml")):
        info=classify(path)
        if not info:
            unclassified.append(path.relative_to(args.corpus_root).as_posix())
            continue
        kind,schema_name=info
        if not (args.schema_dir/schema_name).exists():
            continue
        v=validators[schema_name]
        doc=load_yaml(path)
        errors=sorted(document_errors(
            v, doc,
            allow_unpromoted_conversion_vocabulary=args.allow_unpromoted_conversion_vocabulary,
        ),key=lambda e:tuple(map(str,e.absolute_path)))
        results.append({
            "path":path.relative_to(args.corpus_root).as_posix(),
            "kind":kind,
            "valid":not errors,
            "errors":[{
                "path":"/".join(map(str,e.absolute_path)),
                "schema_path":"/".join(map(str,e.absolute_schema_path)),
                "validator":diagnostic_value(e.validator),
                "message":e.message,
                "classification":"semantic" if e.validator == "unique_response_value" else "untriaged",
            } for e in errors[:50]],
        })

    summary={
        "documents_checked":len(results),
        "valid":sum(x["valid"] for x in results),
        "invalid":sum(not x["valid"] for x in results),
        "unclassified_yaml":len(unclassified),
        "unclassified_paths":unclassified,
        "results":results,
    }
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="results"},indent=2))
    return 1 if summary["invalid"] else 0


if __name__=="__main__":
    raise SystemExit(main())
