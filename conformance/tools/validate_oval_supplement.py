#!/usr/bin/env python3
"""Validate supplemental OVAL XML against the pinned XSD and embedded Schematron."""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from lxml import etree
from saxonche import PySaxonProcessor

from oval_source_audit import BASE, PIN, ROOT, X, require_pin

SCH = "{http://purl.oclc.org/dsdl/schematron}"
SVRL = "{http://purl.oclc.org/dsdl/svrl}"
OVAL_COMMON = "http://oval.mitre.org/XMLSchema/oval-common-5"
SCHEMATRON_PIN = "77dcd36c53d12ed786c144ece3b2af7694abdc56"
OVAL_FILES = {
    OVAL_COMMON: "oval-common-schema.xsd",
    BASE: "oval-definitions-schema.xsd",
    BASE + "#independent": "independent-definitions-schema.xsd",
}


def validation_inputs(schemas):
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    imports = etree.Element(X + "schema")
    schematron = etree.Element(SCH + "schema", nsmap={None: SCH[1:-1]}, queryBinding="xslt2")
    prefixes = {}
    patterns = []
    for namespace, filename in OVAL_FILES.items():
        path = schemas / filename
        etree.SubElement(imports, X + "import", namespace=namespace, schemaLocation=path.as_uri())
        document = etree.parse(str(path), parser)
        for ns in document.iter(SCH + "ns"):
            prefix, uri = ns.get("prefix"), ns.get("uri")
            if prefix in prefixes and prefixes[prefix] != uri:
                raise ValueError(f"Conflicting Schematron prefix {prefix}")
            prefixes[prefix] = uri
        patterns.extend(document.iter(SCH + "pattern"))
    for prefix, uri in sorted(prefixes.items()):
        etree.SubElement(schematron, SCH + "ns", prefix=prefix, uri=uri)
    schematron.extend(deepcopy(pattern) for pattern in patterns)
    return parser, etree.XMLSchema(imports), schematron


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oval", type=Path, required=True)
    parser.add_argument("--schematron", type=Path, required=True)
    args = parser.parse_args()
    require_pin(args.oval, PIN)
    require_pin(args.schematron, SCHEMATRON_PIN)
    xml_parser, xsd, rules = validation_inputs(args.oval.resolve() / "oval-schemas")
    skeleton = args.schematron.resolve() / "trunk/schematron/code/iso_svrl_for_xslt2.xsl"
    corpus = ROOT / "conformance/oval-self-assertion"
    with PySaxonProcessor(license=False) as saxon:
        xslt = saxon.new_xslt30_processor()
        compiler = xslt.compile_stylesheet(stylesheet_file=str(skeleton))
        compiled = compiler.transform_to_string(
            xdm_node=saxon.parse_xml(xml_text=etree.tostring(rules, encoding="unicode")),
        )
        validator = xslt.compile_stylesheet(stylesheet_text=compiled)
        rows = {}
        negative_checked = False
        for path in sorted(corpus.glob("*/*.xml")):
            xsd.assertValid(etree.parse(str(path), xml_parser))
            report = etree.fromstring(validator.transform_to_string(source_file=str(path)).encode())
            failed = report.findall(SVRL + "failed-assert")
            if failed:
                messages = [" ".join("".join(node.itertext()).split()) for node in failed]
                raise SystemExit(f"{path}: {messages}")
            rows[path.relative_to(ROOT).as_posix()] = {
                "sha256": sha256(path.read_bytes()).hexdigest(),
                "xsd": "pass",
                "schematron": "pass",
                "schematron_fired_rules": len(report.findall(SVRL + "fired-rule")),
            }
            if path.parent.name == "unix":
                mutation = etree.parse(str(path), xml_parser)
                node = mutation.find(".//{" + BASE + "#independent}yamlpath")
                node.set("operation", "not equal")
                xsd.assertValid(mutation)
                invalid = validator.transform_to_string(xdm_node=saxon.parse_xml(
                    xml_text=etree.tostring(mutation, encoding="unicode"),
                ))
                assertions = etree.fromstring(invalid.encode()).findall(SVRL + "failed-assert")
                if not any("yamlpath" in "".join(item.itertext()) for item in assertions):
                    raise SystemExit("Schematron missed the invalid YAMLPath operation")
                negative_checked = True
        if not negative_checked:
            raise SystemExit("missing UNIX source for Schematron negative mutation")
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
