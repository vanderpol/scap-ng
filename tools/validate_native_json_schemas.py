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
        from capability_registry import draft_capabilities, load_mapping
        from generate_capability_schema import generate
        from reported_elements import generate_reporting_capability
        draft = draft_capabilities()
        declared_version = (assessment.get("specification") or {}).get("version")
        for section, kind in [("objects", "object"), ("states", "state"), ("tests", "test")]:
            nodes = assessment.get(section, {})
            if not isinstance(nodes, dict):
                continue
            for identity, node in nodes.items():
                capability = node.get("capability") if isinstance(node, dict) else None
                if not isinstance(capability, str):
                    continue
                if declared_version != "0.2.0":
                    if capability in draft:
                        yield ValidationError("New capability requires specification 0.2.0", path=["assessment", section, identity])
                    continue
                try:
                    mapping = load_mapping(capability, "0.2.0")
                except ValueError:
                    mapping = None
                    if allow_unpromoted_conversion_vocabulary:
                        # The converter bridge may preserve explicitly known publisher
                        # extensions losslessly without promoting them into the frozen
                        # native 0.2.0 capability catalog. Strict authoring still rejects
                        # these names when the bridge flag is absent.
                        conversion_only_extensions = {"independent.sqlext"}
                        if capability in conversion_only_extensions:
                            continue
                        from capability_registry import mappings
                        from scap_upconvert_v003.native_capability_mapping import source_capability
                        candidates = [
                            candidate for candidate in mappings("0.2.0")
                            if source_capability(candidate) == capability
                            and not (candidate.get("native") or {}).get("post_alignment_ready", False)
                        ]
                        if len(candidates) == 1:
                            continue
                    yield ValidationError(f"Unknown 0.2.0 capability: {capability}", path=["assessment", section, identity, "capability"])
                    continue
                if (
                    allow_unpromoted_conversion_vocabulary
                    and not (mapping.get("native") or {}).get("post_alignment_ready", False)
                ):
                    continue
                generated = generate_reporting_capability(mapping) if kind == "test" else generate(mapping, Path(__file__).resolve().parents[1], schema_version="0.2.0")
                if kind not in generated["$defs"]:
                    yield ValidationError("Capability does not support this source node", path=["assessment", section, identity])
                    continue
                root = Path(__file__).resolve().parents[1]
                store = schema_store(root / "schema/v0.2.0")
                from referencing import Registry, Resource
                registry = Registry().with_resources((uri, Resource.from_contents(schema)) for uri, schema in store.items())
                validator = Draft202012Validator(generated["$defs"][kind], registry=registry)
                for error in validator.iter_errors(node):
                    error.path.extendleft(reversed(["assessment", section, identity]))
                    yield error
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
