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

import yaml
from jsonschema import Draft202012Validator, RefResolver


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


def validator(schema_dir: Path, filename: str):
    schema=json.loads((schema_dir/filename).read_text(encoding="utf-8"))
    store={}
    for path in schema_dir.glob("*.schema.json"):
        doc=json.loads(path.read_text(encoding="utf-8"))
        if "$id" in doc:
            store[doc["$id"]]=doc
    resolver=RefResolver.from_schema(schema,store=store)
    return Draft202012Validator(schema,resolver=resolver)


def classify(path: Path):
    if path.name in DOCUMENTS:
        return DOCUMENTS[path.name]
    name=path.name
    if name.endswith(".rule.yaml") or (path.parent.name=="rules" and path.suffix==".yaml"):
        return "rule","rule.schema.json"
    if name.endswith(".manual.assessment.yaml") or name.endswith(".document-review.assessment.yaml"):
        return "manual-assessment","manual-assessment.schema.json"
    if name.endswith(".assessment-result.yaml"):
        return "assessment-result","assessment-result.schema.json"
    if name.endswith(".tailoring.yaml"):
        return "tailoring","tailoring.schema.json"
    if name.endswith(".organizational-input.yaml"):
        return "organizational-input","organizational-input.schema.json"
    if name.endswith(".assessment.yaml") or ("assessments" in path.parts and path.suffix==".yaml"):
        return "assessment","assessment.schema.json"
    return None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus_root",type=Path)
    ap.add_argument("--schema-dir",type=Path,required=True)
    ap.add_argument("--report",type=Path)
    args=ap.parse_args()

    validators={}
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
        v=validators.setdefault(schema_name,validator(args.schema_dir,schema_name))
        doc=load_yaml(path)
        errors=sorted(v.iter_errors(doc),key=lambda e:list(e.absolute_path))
        results.append({
            "path":path.relative_to(args.corpus_root).as_posix(),
            "kind":kind,
            "valid":not errors,
            "errors":[{
                "path":"/".join(map(str,e.absolute_path)),
                "message":e.message,
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
