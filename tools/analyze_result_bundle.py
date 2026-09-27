#!/usr/bin/env python3
"""Summarize the structure and size of a SCAP/SCC result ZIP.

The tool is intentionally read-only. It avoids recording file contents and
is suitable for producing sanitized size/structure evidence for research.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def xml_summary(data: bytes) -> dict:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        return {"parse_error": str(exc)}

    counts: dict[str, int] = {}
    for node in root.iter():
        name = local_name(node.tag)
        counts[name] = counts.get(name, 0) + 1

    interesting = {
        key: counts[key]
        for key in (
            "rule-result",
            "message",
            "definition",
            "test",
            "tested_item",
            "system_data",
            "questionnaire",
            "questionnaire_result",
            "test_action_result",
        )
        if key in counts
    }

    return {
        "root": local_name(root.tag),
        "element_count": sum(counts.values()),
        "interesting_counts": interesting,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_file", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    result = {
        "archive": args.zip_file.name,
        "compressed_file_size": args.zip_file.stat().st_size,
        "members": [],
    }

    with zipfile.ZipFile(args.zip_file) as archive:
        for info in archive.infolist():
            entry = {
                "name": Path(info.filename).name,
                "uncompressed_size": info.file_size,
                "compressed_size": info.compress_size,
            }
            if info.filename.lower().endswith(".xml"):
                entry["xml"] = xml_summary(archive.read(info))
            result["members"].append(entry)

    result["total_uncompressed_size"] = sum(
        item["uncompressed_size"] for item in result["members"]
    )

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
