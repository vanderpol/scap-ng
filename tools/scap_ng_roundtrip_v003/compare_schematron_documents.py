#!/usr/bin/env python3
"""Compare embedded OVAL Schematron findings between two complete documents."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from lxml import etree as E, isoschematron
from validate_embedded_schematron import build_schema, findings

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
OVAL_ID_RE=re.compile(r"oval:[A-Za-z0-9_.-]+:(?:def|tst|obj|ste|var):[A-Za-z0-9_.-]+")
QNAME_PREFIX_RE=re.compile(r"\b[A-Za-z_][A-Za-z0-9_.-]*:([A-Za-z_][A-Za-z0-9_.-]*)\b")

def normalize(row):
    message=OVAL_ID_RE.sub("<oval-id>",row.get("message") or "")
    # Namespace-prefix spelling in a Schematron diagnostic is not semantic.
    message=QNAME_PREFIX_RE.sub(r"<ns>:\1",message)
    return (
        row.get("kind"),
        row.get("test"),
        message,
    )

def families(tree):
    result=set()
    for el in tree.getroot().iter():
        if not isinstance(el.tag,str) or not el.tag.startswith("{"):
            continue
        ns=E.QName(el).namespace or ""
        if ns.startswith(OD+"#"):
            result.add(ns)
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schemas",type=Path,required=True)
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--regenerated",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    source_tree=E.parse(str(args.source))
    regen_tree=E.parse(str(args.regenerated))
    needed=families(source_tree)|families(regen_tree)

    paths=[args.schemas/"oval-common-schema.xsd",args.schemas/"oval-definitions-schema.xsd"]
    for path in sorted(args.schemas.glob("*-definitions-schema.xsd")):
        if path.name=="oval-definitions-schema.xsd":
            continue
        root=E.parse(str(path)).getroot()
        if root.get("targetNamespace") in needed:
            paths.append(path)

    validator=isoschematron.Schematron(build_schema(paths),store_report=True)

    validator.validate(source_tree)
    source=[normalize(x) for x in findings(validator)]
    validator.validate(regen_tree)
    regenerated=[normalize(x) for x in findings(validator)]

    source_set=set(source)
    introduced=[item for item in regenerated if item not in source_set]
    report={
        "source_findings":len(source),
        "regenerated_findings":len(regenerated),
        "introduced_findings":introduced,
        "introduced_count":len(introduced),
    }
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 1 if introduced else 0

if __name__=="__main__":
    raise SystemExit(main())
