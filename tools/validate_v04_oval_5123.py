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


def check(schema_dir, xml_file, platform="independent"):
    schema=schema_dir/"oval-definitions-schema.xsd"
    if not schema.is_file() or not xml_file.is_file():
        raise ValueError("Missing OVAL 5.12.3 Definitions schema or XML artifact")
    parser=etree.XMLParser(resolve_entities=False,no_network=True)
    if platform not in ("independent","windows","ios","iosxe","linux","macos"):
        raise ValueError("Unsupported platform schema for current focused 0.4.0 XML gate")
    platform_schema=schema_dir/(platform+"-definitions-schema.xsd")
    if not platform_schema.is_file():
        raise ValueError("Missing pinned OVAL 5.12.3 platform schema: "+platform)
    # The base Definitions XSD has substitution points for platform typed
    # Test/Object/State declarations, but does not itself register all of
    # those namespaces. Import both in a local, pinned, no-network umbrella.
    # Validating against base-only silently misclassifies every ind:* element
    # as an unexpected subtype; do not weaken/skip validation for that.
    umbrella=('''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
       <xs:import namespace="http://oval.mitre.org/XMLSchema/oval-definitions-5"
                  schemaLocation="oval-definitions-schema.xsd"/>
       <xs:import namespace="http://oval.mitre.org/XMLSchema/oval-definitions-5#'''+platform+'''"
                  schemaLocation="'''+platform+'''-definitions-schema.xsd"/>
    </xs:schema>''').encode()
    wrapper=etree.fromstring(
        umbrella,parser,base_url=(schema_dir.resolve().as_uri()+"/"))
    validator=etree.XMLSchema(wrapper)
    document=etree.parse(str(xml_file),parser)
    valid=validator.validate(document)
    return {"status":"PASS" if valid else "FAIL",
            "oval_schema_version":"5.12.3",
            "oval_platform_schema":platform,
            "schema_sha256":hashlib.sha256(schema.read_bytes()).hexdigest(),
            "xml_sha256":hashlib.sha256(xml_file.read_bytes()).hexdigest(),
            "xml_path":str(xml_file),
            "diagnostics":[str(e) for e in validator.error_log][:30]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--schema-dir",type=Path,required=True)
    p.add_argument("--xml",type=Path,required=True)
    p.add_argument("--platform",choices=("independent","windows","ios","iosxe","linux","macos"),default="independent")
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=check(a.schema_dir,a.xml,a.platform)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)


if __name__=="__main__":
    main()
