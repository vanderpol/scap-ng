#!/usr/bin/env python3
"""Validate OVAL XML against Schematron patterns embedded in authoritative XSDs.

Adapted for the SCAP-NG round-trip harness from the schema-extraction approach
used by vanderpol/scap-content/tools/scap_schematron.py.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from pathlib import Path
from lxml import etree as E, isoschematron

SCH="http://purl.oclc.org/dsdl/schematron"
SVRL="http://purl.oclc.org/dsdl/svrl"

def q(ns, local):
    return f"{{{ns}}}{local}"

def build_schema(paths):
    schema=E.Element(q(SCH,"schema"),nsmap={"sch":SCH},queryBinding="xslt")
    sources=[E.parse(str(path)) for path in paths]

    # ISO Schematron requires namespace declarations before pattern elements.
    # Collect namespaces across all embedded-schema sources first, then append
    # patterns in a second pass.
    seen={}
    for source in sources:
        for e in source.iter(q(SCH,"ns")):
            prefix=e.get("prefix"); uri=e.get("uri")
            if prefix in seen and seen[prefix]!=uri:
                raise ValueError(f"namespace prefix conflict for {prefix}: {seen[prefix]} != {uri}")
            if prefix not in seen:
                n=E.SubElement(schema,q(SCH,"ns"))
                n.set("prefix",prefix); n.set("uri",uri); seen[prefix]=uri

    index=0
    for source in sources:
        for e in source.iter(q(SCH,"pattern")):
            c=deepcopy(e)
            c.set("id",f"roundtrip-{index}-{c.get('id') or 'unnamed'}")
            schema.append(c); index+=1
    return schema

def findings(v):
    rows=[]
    for e in v.validation_report.iter():
        if e.tag not in (q(SVRL,"failed-assert"),q(SVRL,"successful-report")):
            continue
        rows.append({
            "kind":E.QName(e).localname,
            "id":e.get("id"),
            "test":e.get("test"),
            "location":e.get("location"),
            "message":" ".join("".join(e.itertext()).split()),
        })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schemas",type=Path,required=True)
    ap.add_argument("xml",type=Path,nargs="+")
    args=ap.parse_args()
    names=[
        "oval-common-schema.xsd",
        "oval-definitions-schema.xsd",
        "independent-definitions-schema.xsd",
        "unix-definitions-schema.xsd",
        "linux-definitions-schema.xsd",
    ]
    paths=[args.schemas/n for n in names]
    schema=build_schema(paths)
    validator=isoschematron.Schematron(schema,store_report=True)
    failed=False
    for xml in args.xml:
        tree=E.parse(str(xml))
        ok=validator.validate(tree)
        rows=findings(validator)
        failed_asserts=[r for r in rows if r["kind"]=="failed-assert"]
        deprecated_reports=[r for r in rows if r["kind"]=="successful-report" and "DEPRECATED" in r["message"].upper()]
        if ok and not deprecated_reports:
            print(f"{xml}: Schematron PASS")
        else:
            failed=True
            print(f"{xml}: Schematron FAIL")
            for row in failed_asserts+deprecated_reports:
                print(row)
    raise SystemExit(1 if failed else 0)

if __name__=="__main__":
    main()
