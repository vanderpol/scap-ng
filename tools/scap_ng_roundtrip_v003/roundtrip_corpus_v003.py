#!/usr/bin/env python3
"""Round-trip every OVAL Definition in a corpus through native SCAP-NG v003.

Pipeline per definition:
  source OVAL -> native v003 assessment -> regenerated OVAL -> semantic compare.

The comparison is intentionally root-definition scoped and ID-independent.
Generated IDs, comments, and provenance serialization are not compared.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from scap_upconvert_v003.build_rhel9_review_slice import (
    local,
    lower_definition,
    semantic_id,
    unsupported_definition_features,
)
from check_current_authoring_contract import violations
from scap_upconvert_v003.cleanliness import assert_native_clean
from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary
from scap_ng_roundtrip_v003.native_assessment_to_oval import build as reverse_build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare

def definition_nodes(root):
    return [
        node for node in root.iter()
        if local(node.tag) == "definition" and node.get("id")
    ]

def safe_name(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)

def dependency_depth(root, definition_id):
    by_id = {
        node.get("id"): node
        for node in root.iter()
        if node.get("id")
    }
    ids = set(by_id)

    def refs(node):
        out=set()
        for item in node.iter():
            for value in item.attrib.values():
                if value in ids:
                    out.add(value)
            text=(item.text or "").strip()
            if text in ids:
                out.add(text)
        return out

    graph={
        node_id: refs(node)-{node_id}
        for node_id,node in by_id.items()
    }
    memo={}
    visiting=set()

    def walk(node_id):
        if node_id in memo:
            return memo[node_id]
        if node_id in visiting:
            return (0,[node_id,"<cycle>"])
        visiting.add(node_id)
        best=(0,[node_id])
        for target in sorted(graph.get(node_id,())):
            depth,path=walk(target)
            cand=(1+depth,[node_id]+path)
            if cand[0] > best[0]:
                best=cand
        visiting.remove(node_id)
        memo[node_id]=best
        return best

    return walk(definition_id)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--inventory-only",action="store_true")
    ap.add_argument("--layout", choices=("current", "historical"), default="current",
                    help="Current OVAL-aligned Test/Object/State/Variable graph, or explicit historical baseline.")
    ap.add_argument(
        "--include",
        default="*.xml",
        help="Filename glob applied recursively (default: *.xml).",
    )
    args=ap.parse_args()

    args.out.mkdir(parents=True,exist_ok=True)
    rows=[]
    parse_failures=[]
    total=0
    equal=0

    sources=sorted(args.corpus.rglob(args.include))
    for source in sources:
        rel=source.relative_to(args.corpus).as_posix()
        try:
            root=ET.parse(source).getroot()
        except Exception as exc:
            parse_failures.append({"file":rel,"error":str(exc)})
            continue

        for definition in definition_nodes(root):
            total+=1
            did=definition.get("id")
            depth,path=dependency_depth(root,did)
            row={
                "file":rel,
                "definition_id":did,
                "dependency_depth":depth,
                "dependency_path":path,
            }
            unsupported=unsupported_definition_features(root,did)
            if unsupported:
                row["stage"]="lower"
                row["unsupported_features"]=unsupported
                rows.append(row)
                continue

            native,error=lower_definition(
                root,did,"roundtrip."+semantic_id(did,"definition"),
                collection_graph=args.layout == "current",
            )
            if native is None:
                row["stage"]="lower"
                row["error"]=error
                rows.append(row)
                continue

            if args.layout == "current":
                native = align_assessment_vocabulary(native)
                # Native 0.2.0 requires reporting behavior to be authored
                # explicitly. SCAP 1.4/OVAL conversion preserves the complete
                # evidence surface by selecting all reported elements.
                for test in native.get("assessment", {}).get("tests", {}).values():
                    test["reported_elements"] = "all"

            try:
                assert_native_clean(native)
                if args.layout == "current":
                    errors = violations(native)
                    if errors:
                        raise ValueError("Current authoring contract: " + str(errors))
            except Exception as exc:
                row["stage"]="cleanliness"
                row["error"]=str(exc)
                rows.append(row)
                continue

            stem=safe_name(Path(rel).with_suffix("").as_posix()+"__"+did)
            native_path=args.out/(stem+".native.json")
            regen_path=args.out/(stem+".oval.xml")
            native_path.write_text(json.dumps(native,indent=2)+"\n",encoding="utf-8")

            try:
                tree,regen_id=reverse_build(native)
                ET.indent(tree,space="  ")
                tree.write(regen_path,encoding="utf-8",xml_declaration=True)
            except Exception as exc:
                row["stage"]="reverse"
                row["error"]=str(exc)
                row["native"]=native_path.as_posix()
                rows.append(row)
                continue

            try:
                result=compare(
                    source,regen_path,
                    source_root=did,
                    regenerated_root=regen_id,
                    root_only=True,
                )
            except Exception as exc:
                row["stage"]="compare"
                row["error"]=str(exc)
                row["native"]=native_path.as_posix()
                row["regenerated"]=regen_path.as_posix()
                rows.append(row)
                continue

            row["stage"]="equal" if result["equal"] else "semantic-diff"
            row["equal"]=bool(result["equal"])
            row["native"]=native_path.as_posix()
            row["regenerated"]=regen_path.as_posix()
            if not result["equal"]:
                row["source_definition"]=result.get("source_definition")
                row["regenerated_definition"]=result.get("regenerated_definition")
            else:
                equal+=1
            rows.append(row)

    failures=[r for r in rows if not r.get("equal")]
    by_stage={}
    for row in failures:
        by_stage[row.get("stage","unknown")]=by_stage.get(row.get("stage","unknown"),0)+1

    deepest=max(rows,key=lambda r:r.get("dependency_depth",0),default=None)
    report={
        "native_layout":args.layout,
        "files":len(sources),
        "definitions":total,
        "semantic_equal":equal,
        "max_dependency_depth":deepest.get("dependency_depth",0) if deepest else 0,
        "deepest_dependency_file":deepest.get("file") if deepest else None,
        "deepest_dependency_definition":deepest.get("definition_id") if deepest else None,
        "deepest_dependency_path":deepest.get("dependency_path",[]) if deepest else [],
        "failures":len(failures),
        "failures_by_stage":dict(sorted(by_stage.items())),
        "parse_failures":parse_failures,
        "results":rows,
    }
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    summary={k:v for k,v in report.items() if k!="results"}
    if failures:
        summary["failure_details"]=[
            {
                "file":row.get("file"),
                "definition_id":row.get("definition_id"),
                "stage":row.get("stage"),
                "dependency_depth":row.get("dependency_depth"),
                "error":row.get("error"),
                "source_definition":row.get("source_definition"),
                "regenerated_definition":row.get("regenerated_definition"),
            }
            for row in failures
        ]
    print(json.dumps(summary,indent=2,sort_keys=True))

    if args.inventory_only:
        return 0
    return 1 if parse_failures or failures else 0

if __name__=="__main__":
    raise SystemExit(main())
