#!/usr/bin/env python3
"""Census explicit XML attribute values in XML files and ZIP archives.

Used as evidence tooling for deciding whether legacy OVAL behavior attributes
and enum values deserve native SCAP-NG authoring surface. Only attributes
physically present in source XML are counted; XSD defaults are not materialized.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def split_qname(name: str) -> tuple[str, str]:
    if name.startswith("{") and "}" in name:
        uri, local = name[1:].split("}", 1)
        return uri, local
    return "", name


def scan_xml_bytes(data: bytes, *, source: str, member: str | None,
                   namespace: str, element: str, attributes: set[str]):
    try:
        root=ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(
            f"XML parse failure in {source}{'!' + member if member else ''}: {exc}"
        ) from exc

    rows=[]
    for node in root.iter():
        uri, local=split_qname(node.tag)
        if uri != namespace or local != element:
            continue
        for attr in sorted(attributes):
            if attr in node.attrib:
                rows.append({
                    "source":source,
                    "member":member,
                    "namespace":uri,
                    "element":local,
                    "attribute":attr,
                    "value":node.attrib[attr],
                })
    return rows


def scan_path(path: Path, **kwargs):
    rows=[]
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            for info in sorted(zf.infolist(), key=lambda x:x.filename):
                if info.is_dir() or not info.filename.lower().endswith((".xml",".oval")):
                    continue
                rows.extend(scan_xml_bytes(
                    zf.read(info), source=str(path), member=info.filename, **kwargs
                ))
        return rows
    if path.suffix.lower() in {".xml",".oval"}:
        return scan_xml_bytes(
            path.read_bytes(), source=str(path), member=None, **kwargs
        )
    return rows


def discover(inputs):
    paths=[]
    for raw in inputs:
        p=Path(raw)
        if p.is_dir():
            paths.extend(
                q for q in sorted(p.rglob("*"))
                if q.is_file() and (
                    q.suffix.lower() in {".xml",".oval"} or zipfile.is_zipfile(q)
                )
            )
        elif p.is_file():
            paths.append(p)
        else:
            raise FileNotFoundError(raw)
    return paths


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--namespace", required=True)
    ap.add_argument("--element", required=True)
    ap.add_argument("--attribute", action="append", required=True)
    ap.add_argument("--output", required=True)
    args=ap.parse_args()

    paths=discover(args.inputs)
    rows=[]
    failures=[]
    for path in paths:
        try:
            rows.extend(scan_path(
                path,
                namespace=args.namespace,
                element=args.element,
                attributes=set(args.attribute),
            ))
        except (ValueError,OSError,zipfile.BadZipFile) as exc:
            failures.append({"source":str(path),"error":str(exc)})

    counts=Counter((r["attribute"],r["value"]) for r in rows)
    report={
        "scope":{
            "inputs":args.inputs,
            "namespace":args.namespace,
            "element":args.element,
            "attributes":sorted(set(args.attribute)),
            "source_explicit_only":True,
            "xsd_defaults_excluded":True,
        },
        "files_scanned":len(paths),
        "occurrences":len(rows),
        "counts":[
            {"attribute":k[0],"value":k[1],"count":n}
            for k,n in sorted(counts.items())
        ],
        "rows":rows,
        "failures":failures,
    }
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "files_scanned":len(paths),
        "occurrences":len(rows),
        "counts":report["counts"],
        "failures":len(failures),
    },indent=2,sort_keys=True))
    return 1 if failures else 0


if __name__=="__main__":
    raise SystemExit(main())
