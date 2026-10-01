#!/usr/bin/env python3
"""Inventory observed native SCAP-NG document shapes across a generated corpus.

This is evidence for schema stabilization, not a schema generator.  It records
field paths, observed types, presence counts, nullability, and bounded examples
without changing native content.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def scalar_example(value: Any):
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:160]
    return None


class Census:
    def __init__(self):
        self.docs=defaultdict(int)
        self.stats=defaultdict(lambda: {
            "present":0,
            "types":defaultdict(int),
            "examples":[],
        })

    def visit(self, kind: str, value: Any, path: str="$"):
        key=(kind,path)
        row=self.stats[key]
        row["present"]+=1
        t=type_name(value)
        row["types"][t]+=1
        example=scalar_example(value)
        if example is not None and example not in row["examples"] and len(row["examples"])<5:
            row["examples"].append(example)

        if isinstance(value, dict):
            for child_key, child in value.items():
                self.visit(kind,child,f"{path}.{child_key}")
        elif isinstance(value, list):
            # Treat array member shape as one schema path, not numeric indexes.
            for child in value:
                self.visit(kind,child,f"{path}[]")

    def add_document(self, kind: str, value: Any):
        self.docs[kind]+=1
        self.visit(kind,value)

    def report(self):
        fields=[]
        for (kind,path),row in sorted(self.stats.items()):
            total=self.docs[kind]
            fields.append({
                "document_kind":kind,
                "path":path,
                "present_documents_or_nodes":row["present"],
                "root_document_count":total,
                "observed_types":dict(sorted(row["types"].items())),
                "examples":row["examples"],
            })
        return {
            "format":"scap-ng-native-schema-census-0.1",
            "documents":dict(sorted(self.docs.items())),
            "field_paths":len(fields),
            "fields":fields,
        }


def load_yaml(path: Path):
    value=yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus_root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    census=Census()
    root=args.corpus_root.resolve()

    for path in sorted(root.rglob("benchmark.yaml")):
        doc=load_yaml(path)
        if "benchmark" in doc:
            census.add_document("benchmark",doc["benchmark"])

    for path in sorted(root.rglob("rules/*.yaml")):
        doc=load_yaml(path)
        if "rule" in doc:
            census.add_document("rule",doc["rule"])

    for path in sorted(root.rglob("assessments/**/*.yaml")):
        doc=load_yaml(path)
        if "assessment" in doc:
            census.add_document("assessment",doc["assessment"])

    for path in sorted(root.rglob("applicability.yaml")):
        doc=load_yaml(path)
        if "applicability" in doc:
            census.add_document("applicability",doc["applicability"])

    report=census.report()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "documents":report["documents"],
        "field_paths":report["field_paths"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
