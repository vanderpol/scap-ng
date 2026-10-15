#!/usr/bin/env python3
"""Source-backed OVAL 5.12.3 var_check audit for constant Windows user-right selectors.

Only inspects immutable NIWC-distributed SCAP 1.4 XML and reviewed NG enums.
No scanner execution and no assumed default OVAL attribute values.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def inspect_zip(path: Path, reviewed_enum: list[str]) -> dict:
    expected=set(reviewed_enum)
    findings=[]
    scanned=0
    possible=[]
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.lower().endswith(".xml"):
                continue
            scanned+=1
            root=ET.fromstring(archive.read(name))
            variables={}
            for node in root.iter():
                if local(node.tag)!="constant_variable" or not node.get("id"):
                    continue
                values=[
                    (v.text or "").strip()
                    for v in node
                    if local(v.tag)=="value"
                ]
                variables[node.attrib["id"]]={
                    "values":values,
                    "datatype":node.get("datatype"),
                    "title":node.get("comment"),
                }
            for obj in root.iter():
                if local(obj.tag)!="userright_object":
                    continue
                for entity in obj:
                    if local(entity.tag)!="userright" or not entity.get("var_ref"):
                        continue
                    variable=variables.get(entity.attrib["var_ref"])
                    record={
                        "xml":name,
                        "object_id":obj.get("id"),
                        "variable_ref":entity.get("var_ref"),
                        "object_entity_attributes":dict(entity.attrib),
                        "variable_found":variable is not None,
                    }
                    possible.append(record)
                    if variable is None:
                        continue
                    values=variable["values"]
                    if (len(values)==len(reviewed_enum) and
                        len(set(values))==len(values) and set(values)==expected):
                        findings.append({
                            **record,
                            "literal_count":len(values),
                            "literal_unique":True,
                            "exactly_matches_reviewed_enum":True,
                            "source_var_check":entity.get("var_check"),
                            "source_operation":entity.get("operation"),
                            "source_datatype":entity.get("datatype"),
                            "variable_datatype":variable.get("datatype"),
                        })
    return {
        "artifact":path.name,
        "xml_members_scanned":scanned,
        "candidate_variable_selectors":len(possible),
        "full_constant_enum_matches":len(findings),
        "matches":findings,
        "other_selector_samples":possible[:7] if not findings else [],
    }


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--mapping",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("archives",nargs="+",type=Path)
    args=parser.parse_args()
    mapping=json.loads(args.mapping.read_text(encoding="utf-8"))
    assert mapping["specification_version"]=="0.4.0"
    enum=mapping["native"]["selector_value_enums"]["userright"]
    assert len(enum)==len(set(enum)) and len(enum)>1
    rows=[inspect_zip(p,enum) for p in args.archives]
    report={
        "status":"source evidence only; no scanner runtime claim",
        "mapping":mapping["capability"],
        "expected_enum_members":len(enum),
        "archives":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("OVAL_USERRIGHT_SOURCE_PROOF",json.dumps(report,sort_keys=True),flush=True)
    if any(not row["matches"] for row in rows):
        raise SystemExit("Cannot prove reviewed constant enum source in every archive")
    # Original var_check is the authority: do not translate omitted values or
    # 'all' to 'one'. Distinguish one/at-least-one from all and missing values.
    for row in rows:
        for match in row["matches"]:
            if match["source_var_check"] not in {"only one","at least one"}:
                raise SystemExit(
                    f"Need explicit OVAL var_check review: {row['artifact']}: "
                    f"{match['source_var_check']!r}"
                )


if __name__=="__main__":
    main()
