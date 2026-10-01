#!/usr/bin/env python3
"""Census source-explicit OVAL mask attribute usage in XML files and ZIP archives.

This is evidence tooling, not a converter. It intentionally counts only mask
attributes present in source XML; XSD-inherited/default mask=false is excluded.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


OVAL_DEF = "http://oval.mitre.org/XMLSchema/oval-definitions-5"


def split_qname(name: str) -> tuple[str, str]:
    if name.startswith("{") and "}" in name:
        uri, local = name[1:].split("}", 1)
        return uri, local
    return "", name


def capability_from_uri(uri: str) -> str:
    if uri == OVAL_DEF:
        return "oval-definitions"
    if uri.startswith(OVAL_DEF + "#"):
        return uri.split("#", 1)[1]
    return uri or "unqualified"


@dataclass(frozen=True)
class MaskOccurrence:
    source: str
    member: str | None
    value: str
    capability: str
    namespace: str
    element: str
    section: str
    owner_id: str | None
    context: str


def normalized_mask(value: str) -> str:
    v = value.strip().lower()
    if v in {"true", "1"}:
        return "true"
    if v in {"false", "0"}:
        return "false"
    return "invalid:" + value


def walk(root: ET.Element, source: str, member: str | None) -> list[MaskOccurrence]:
    out: list[MaskOccurrence] = []

    def visit(node: ET.Element, section: str = "other", owner_id: str | None = None):
        uri, local = split_qname(node.tag)
        next_section = section
        if uri == OVAL_DEF and local in {"objects", "states", "variables", "tests"}:
            next_section = local

        next_owner = owner_id
        if node.get("id"):
            next_owner = node.get("id")

        if "mask" in node.attrib:
            context = "record_field" if local == "field" else f"{next_section}_entity"
            out.append(
                MaskOccurrence(
                    source=source,
                    member=member,
                    value=normalized_mask(node.attrib["mask"]),
                    capability=capability_from_uri(uri),
                    namespace=uri,
                    element=local,
                    section=next_section,
                    owner_id=next_owner,
                    context=context,
                )
            )

        for child in list(node):
            visit(child, next_section, next_owner)

    visit(root)
    return out


def scan_xml_bytes(data: bytes, source: str, member: str | None = None) -> list[MaskOccurrence]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f"XML parse failure in {source}{'!' + member if member else ''}: {exc}") from exc
    return walk(root, source, member)


def scan_path(path: Path) -> list[MaskOccurrence]:
    if zipfile.is_zipfile(path):
        rows: list[MaskOccurrence] = []
        with zipfile.ZipFile(path) as zf:
            for info in sorted(zf.infolist(), key=lambda x: x.filename):
                if info.is_dir() or not info.filename.lower().endswith((".xml", ".oval")):
                    continue
                rows.extend(scan_xml_bytes(zf.read(info), str(path), info.filename))
        return rows
    if path.suffix.lower() in {".xml", ".oval"}:
        return scan_xml_bytes(path.read_bytes(), str(path))
    return []


def build_summary(rows: list[MaskOccurrence], inputs: list[str]) -> dict:
    by_value = Counter(r.value for r in rows)
    by_capability = Counter((r.capability, r.value) for r in rows)
    by_context = Counter((r.context, r.value) for r in rows)
    by_element = Counter((r.capability, r.element, r.section, r.value) for r in rows)

    return {
        "scope": {
            "inputs": inputs,
            "source_explicit_only": True,
            "xsd_default_false_excluded": True,
        },
        "occurrences": len(rows),
        "by_value": dict(sorted(by_value.items())),
        "by_capability": [
            {"capability": k[0], "value": k[1], "count": n}
            for k, n in sorted(by_capability.items())
        ],
        "by_context": [
            {"context": k[0], "value": k[1], "count": n}
            for k, n in sorted(by_context.items())
        ],
        "by_element": [
            {
                "capability": k[0],
                "element": k[1],
                "section": k[2],
                "value": k[3],
                "count": n,
            }
            for k, n in sorted(by_element.items())
        ],
        "rows": [asdict(r) for r in rows],
    }


def discover(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            paths.extend(
                q for q in sorted(p.rglob("*"))
                if q.is_file() and (zipfile.is_zipfile(q) or q.suffix.lower() in {".xml", ".oval"})
            )
        elif p.is_file():
            paths.append(p)
        else:
            raise FileNotFoundError(raw)
    return paths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="XML/OVAL files, ZIP files, or directories")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    paths = discover(args.inputs)
    rows: list[MaskOccurrence] = []
    failures = []
    for path in paths:
        try:
            rows.extend(scan_path(path))
        except (ValueError, OSError, zipfile.BadZipFile) as exc:
            failures.append({"source": str(path), "error": str(exc)})

    report = build_summary(rows, args.inputs)
    report["files_scanned"] = len(paths)
    report["failures"] = failures
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "files_scanned": len(paths),
        "occurrences": len(rows),
        "by_value": report["by_value"],
        "failures": len(failures),
    }, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
