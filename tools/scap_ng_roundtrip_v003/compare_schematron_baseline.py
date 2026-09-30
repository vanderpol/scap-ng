#!/usr/bin/env python3
"""Compare regenerated Schematron findings to the original Self-Assertion source.

A round trip must not introduce new Schematron findings. Source test content may
intentionally exercise deprecated or otherwise Schematron-reported constructs;
those source findings are treated as the baseline, not silently normalized away.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from lxml import etree as E, isoschematron

from validate_embedded_schematron import build_schema, findings

OVAL_ID_RE = re.compile(r"oval:[A-Za-z0-9_.-]+:(?:def|tst|obj|ste|var):[A-Za-z0-9_.-]+")

def normalize(row):
    message = OVAL_ID_RE.sub("<oval-id>", row.get("message") or "")
    return (
        row.get("kind"),
        row.get("test"),
        message,
    )

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"

def document_families(path):
    tree=E.parse(str(path))
    families=set()
    for el in tree.getroot().iter():
        if not isinstance(el.tag,str) or not el.tag.startswith("{"):
            continue
        ns=E.QName(el).namespace or ""
        if ns.startswith(OD+"#"):
            families.add(ns)
    return tree,frozenset(families)

def validate_tree(tree, validator):
    validator.validate(tree)
    return [normalize(x) for x in findings(validator)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schemas",type=Path,required=True)
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    core_paths=[
        args.schemas/"oval-common-schema.xsd",
        args.schemas/"oval-definitions-schema.xsd",
    ]
    schema_by_namespace={}
    for path in sorted(args.schemas.glob("*-definitions-schema.xsd")):
        if path.name=="oval-definitions-schema.xsd":
            continue
        root=E.parse(str(path)).getroot()
        ns=root.get("targetNamespace")
        if ns:
            schema_by_namespace[ns]=path
    validator_cache={}

    def validator_for(families):
        if families not in validator_cache:
            paths=list(core_paths)
            paths += [schema_by_namespace[ns] for ns in sorted(families) if ns in schema_by_namespace]
            validator_cache[families]=isoschematron.Schematron(
                build_schema(paths),store_report=True
            )
        return validator_cache[families]

    report=json.loads(args.report.read_text(encoding="utf-8"))
    source_cache={}
    rows=[]
    introduced=[]

    for row in report.get("results",[]):
        regen=row.get("regenerated")
        if not regen:
            continue
        source_rel=row["file"]
        source=args.corpus/source_rel
        if source_rel not in source_cache:
            source_tree,source_families=document_families(source)
            source_cache[source_rel]=(
                source_families,
                validate_tree(source_tree,validator_for(source_families)),
            )
        source_families,source_findings=source_cache[source_rel]
        regen_tree,regen_families=document_families(Path(regen))
        regen_findings=validate_tree(regen_tree,validator_for(regen_families))

        source_set=set(source_findings)
        new=[item for item in regen_findings if item not in source_set]
        item={
            "file":source_rel,
            "definition_id":row["definition_id"],
            "source_findings":len(source_findings),
            "regenerated_findings":len(regen_findings),
            "introduced_findings":new,
        }
        rows.append(item)
        if new:
            introduced.append(item)

    out={
        "definitions_checked":len(rows),
        "definitions_with_new_findings":len(introduced),
        "introduced":introduced,
        "results":rows,
    }
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k!="results"},indent=2,sort_keys=True))
    return 1 if introduced else 0

if __name__=="__main__":
    raise SystemExit(main())
