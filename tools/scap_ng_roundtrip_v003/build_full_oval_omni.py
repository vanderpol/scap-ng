#!/usr/bin/env python3
"""Build an aggregate OVAL Definitions XSD importing every platform schema."""
from __future__ import annotations

import argparse
from pathlib import Path
from lxml import etree as E

XS="http://www.w3.org/2001/XMLSchema"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--schemas",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    root=E.Element(f"{{{XS}}}schema",nsmap={"xs":XS})
    root.set("elementFormDefault","qualified")

    core=args.schemas/"oval-definitions-schema.xsd"
    tree=E.parse(str(core))
    target=tree.getroot().get("targetNamespace")
    imp=E.SubElement(root,f"{{{XS}}}import")
    imp.set("namespace",target)
    imp.set("schemaLocation",core.name)

    seen={target}
    for path in sorted(args.schemas.glob("*-definitions-schema.xsd")):
        if path.name=="oval-definitions-schema.xsd":
            continue
        tree=E.parse(str(path))
        ns=tree.getroot().get("targetNamespace")
        if not ns or ns in seen:
            continue
        seen.add(ns)
        imp=E.SubElement(root,f"{{{XS}}}import")
        imp.set("namespace",ns)
        imp.set("schemaLocation",path.name)

    ref=E.SubElement(root,f"{{{XS}}}element")
    ref.set("ref","oval-def:oval_definitions")
    # Add the namespace declaration expected by the ref QName.
    root.set("{http://www.w3.org/2000/xmlns/}oval-def",target)

    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(E.tostring(root,xml_declaration=True,encoding="UTF-8",pretty_print=True))

if __name__=="__main__":
    main()
