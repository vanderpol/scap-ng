#!/usr/bin/env python3
"""Census of 0.4.0 singleton filtered-Unions created by legacy conversion.

A structural signature is evidence of *possible* synthetic wrappers, NOT
proof of the original OVAL shape for unrelated Assessments. Source-backed
Bluetooth case is separately established via pinned original SCAP XML.
Refs #229 #232.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from v04_a_authoring_graph_index import read_authoring_archive

BLUETOOTH_ID = "condition.bluetooth-installation.assessment"
BLUETOOTH_PATH = "authoring/ms_windows_11/assessments/applicability/condition.bluetooth-installation.json"

def candidate(obj):
    """Return a reversible *shape* only: single filtered union, no extra fields."""
    if not isinstance(obj, dict) or set(obj) != {"object_title", "set"}:
        return None
    expr = obj["set"]
    if not isinstance(expr, dict) or set(expr) != {"operator", "operands"} or expr["operator"] != "union":
        return None
    operands = expr["operands"]
    if not isinstance(operands, list) or len(operands) != 1:
        return None
    op = operands[0]
    if not isinstance(op, dict) or set(op) != {"object", "filters"}:
        return None
    inner = op["object"]
    if not isinstance(inner, dict) or inner.get("object_title") != obj["object_title"]:
        return None
    if "set" in inner or "filters" in inner:
        return None
    filters = op["filters"]
    if not isinstance(filters, list) or not filters or any(
        not isinstance(f, dict) or len(f) != 1 or next(iter(f)) not in {"include", "exclude"}
        for f in filters
    ):
        return None
    return {"object": inner, "filters": filters}


def inventory(documents, *, assert_bluetooth=False):
    entries = []
    by_capability = Counter()
    for path, doc in sorted(documents.items()):
        a = doc.get("assessment")
        if not isinstance(a, dict) or a.get("mode") != "automated":
            continue
        for test_id, test in (a.get("tests") or {}).items():
            obj = test.get("object")
            found = candidate(obj)
            if found is None:
                continue
            cap = test.get("capability")
            entries.append({
                "path": path, "assessment": a.get("id"), "test_id": test_id,
                "capability": cap,
                "filters": [next(iter(f)) for f in found["filters"]],
                "outer_title": obj.get("object_title"),
                "has_collect": "collect" in found["object"],
                "has_select": "select" in found["object"],
            })
            by_capability[cap] += 1
    bluetooth = [row for row in entries if row["assessment"] == BLUETOOTH_ID]
    if assert_bluetooth and (
        len(bluetooth) != 1
        or bluetooth[0]["path"] != BLUETOOTH_PATH
        or bluetooth[0]["capability"] != "independent.shellcommand"
        or bluetooth[0]["filters"] != ["include"]
        or not bluetooth[0]["has_collect"]
    ):
        raise ValueError("Windows 11 filtered-Union structural reference changed; consult source XML")
    return {
        "status": "SYNTHETIC_SHAPE_CANDIDATES_NOT_PROVEN_SOURCE_FOR_OTHERS",
        "documents": len(documents),
        "candidate_count": len(entries),
        "by_capability": dict(sorted(by_capability.items())),
        "bluetooth_original_oval_set_present": None,
        "bluetooth_case_source_proven": False,
        "source_provenance_required": True,
        "candidate_entries": entries,
        "requires_source_oval_provenance_before_bulk_rewrite": True,
        "scanner_semantics_verified": False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--assert-six",action="store_true")
    a=p.parse_args()
    docs=read_authoring_archive(a.archive,"json")
    if a.assert_six and len(docs)!=4001:
        raise ValueError("expected pinned 4,001-document 0.4 sample corpus")
    report=inventory(docs,assert_bluetooth=a.assert_six)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="candidate_entries"},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
