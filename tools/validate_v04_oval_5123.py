#!/usr/bin/env python3
"""Independently validate regenerated native 0.4 OVAL against 5.12.3 XSD.

Requires a local checkout of OVAL-Community/OVAL@v5.12.3. The separately
maintained roundtrip semantic graph comparator and source pin are independent
gates. Refs #248 #229.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from lxml import etree


def check(schema_dir, xml_file):
    schema=schema_dir/"oval-definitions-schema.xsd"
    if not schema.is_file() or not xml_file.is_file():
        raise ValueError("Missing OVAL 5.12.3 Definitions schema or XML artifact")
    parser=etree.XMLParser(resolve_entities=False,no_network=True)
    validator=etree.XMLSchema(etree.parse(str(schema),parser))
    document=etree.parse(str(xml_file),parser)
    valid=validator.validate(document)
    return {"status":"PASS" if valid else "FAIL",
            "oval_schema_version":"5.12.3",
            "schema_sha256":hashlib.sha256(schema.read_bytes()).hexdigest(),
            "xml_sha256":hashlib.sha256(xml_file.read_bytes()).hexdigest(),
            "xml_path":str(xml_file),
            "diagnostics":[str(e) for e in validator.error_log][:30]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--schema-dir",type=Path,required=True)
    p.add_argument("--xml",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=check(a.schema_dir,a.xml)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)


if __name__=="__main__":
    main()
