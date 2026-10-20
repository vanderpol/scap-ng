#!/usr/bin/env python3
"""Pinned original OVAL triage of *all* remaining 0.4.0 singleton Sets.

This is a READ-ONLY inventory. A matching OVAL Object comment is only an
identity hint, never sufficient authority to rewrite an Object/Set. Compare
exact source IDs, filters, variables, collector semantics and evaluation
before any change. Refs #248.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from audit_v04_filtered_union_oval_provenance import PINS, source_objects, git_blob_digest, local
from v04_a_authoring_graph_index import read_authoring_archive


def local_set_sites(documents):
    rows=[]
    def walk(value,route, info):
        if isinstance(value,list):
            for i,child in enumerate(value):
                walk(child,route+[i],info)
        elif isinstance(value,dict):
            s=value.get("set")
            if isinstance(s,dict) and isinstance(s.get("operands"),list) and len(s["operands"])==1:
                operand=s["operands"][0]
                filters=operand.get("filters") if isinstance(operand,dict) else None
                if (isinstance(operand,dict) and isinstance(operand.get("object"),dict)):
                    leaf=operand["object"]
                else:
                    leaf={}
                rows.append({
                    **info, "site":route+["set"],
                    "operator":s.get("operator"),
                    "outer_title":value.get("object_title"),
                    "leaf_title":leaf.get("object_title"),
                    "leaf_capability":leaf.get("capability"),
                    "filter_actions":([next(iter(f)) if isinstance(f,dict) and len(f)==1 else "MALFORMED"
                                       for f in filters] if isinstance(filters,list) else None),
                    "operand_keys":sorted(operand) if isinstance(operand,dict) else None,
                })
            for key,child in value.items():
                walk(child,route+[key],info)
    for path,document in sorted(documents.items()):
        assessment=document.get("assessment") if isinstance(document,dict) else None
        if not isinstance(assessment,dict) or assessment.get("mode")!="automated":
            continue
        base={"path":path,"assessment":assessment.get("id"),"test":None,
              "test_capability":None, "test_title":None}
        for ident,test in sorted((assessment.get("tests") or {}).items()):
            walk(test,["assessment","tests",ident],
                 {**base,"test":ident,"test_capability":test.get("capability"),
                  "test_title":test.get("test_title")})
        for kind in ("variables","objects","shared_objects"):
            walk(assessment.get(kind) or {},["assessment",kind],base)
    return rows


def source_tests(xml):
    root=ET.fromstring(xml)
    return [t for t in root.iter()
            if local(t).endswith("_test") and t.get("id")]


def normalized_xml_structure(element):
    """Namespace/prefix independent exact element+attribute+text structure."""
    return {
        "tag":local(element),
        "attributes":sorted((local_name(key),value) for key,value in element.attrib.items()),
        "text":(element.text or "").strip(),
        "children":[normalized_xml_structure(child) for child in element],
    }


def local_name(name):
    return name.rsplit("}",1)[-1]


def originals(source_dir):
    sources={}
    checksums={}
    for benchmark,(filename,expected_git_blob) in PINS.items():
        contents=(source_dir/filename).read_bytes()
        if git_blob_digest(contents)!=expected_git_blob:
            raise ValueError("original OVAL archive changed: "+filename)
        with zipfile.ZipFile(source_dir/filename) as z:
            xml=[name for name in z.namelist() if name.endswith(".xml")]
            if len(xml)!=1:
                raise ValueError("ambiguous OVAL source "+filename)
            xml_data=z.read(xml[0])
            sources[benchmark]={
                "objects":source_objects(xml_data),
                "tests":source_tests(xml_data),
            }
        checksums[benchmark]=hashlib.sha256(contents).hexdigest()
    return sources,checksums


def audit(ng_docs, sources,checksums,*,assert_six=False):
    singletons=local_set_sites(ng_docs)
    records=[]
    for item in singletons:
        parts=item["path"].split("/")
        benchmark=parts[1] if len(parts)>1 else None
        if benchmark=="shared":
            original_collections=list(sources.values())
        elif benchmark in sources:
            original_collections=[sources[benchmark]]
        else:
            raise ValueError("No pinned OVAL source for "+item["path"])
        # Fixtures may pass only source Object arrays. Production supplies
        # original Tests too, for an independent Test-comment -> object_ref
        # check when the converter did not retain an Object title.
        source_candidates=[obj for source in original_collections
                           for obj in (source["objects"] if isinstance(source,dict) else source)]
        original_tests=[test for source in original_collections
                        for test in (source["tests"] if isinstance(source,dict) else [])]
        title=item["outer_title"] or item["leaf_title"]
        matches=[obj for obj in source_candidates if title is not None and obj.get("comment")==title]
        linked=[]
        if item.get("test_title"):
            for original_test in original_tests:
                if original_test.get("comment")==item["test_title"]:
                    refs=sorted({child.get("object_ref")
                                 for child in original_test.iter()
                                 if child.get("object_ref")})
                    linked.append({"test_id":original_test.get("id"),
                                   "object_refs":refs})
        unique_linked_refs=sorted({ref for t in linked for ref in t["object_refs"]})
        linkage=( "UNIQUE_OVAL_TEST_OBJECT_REF" if len(unique_linked_refs)==1 else
                  "MULTIPLE_OVAL_TEST_OBJECT_REFS" if unique_linked_refs else
                  "NO_MATCHED_OVAL_TEST_COMMENT")
        graph=[]
        for obj in matches:
            direct_filters=[node for node in obj if local(node)=="filter"]
            sets=[node for node in obj if local(node)=="set"]
            actions=[e.get("action","exclude") for e in direct_filters]
            graph.append({
                "source_id":obj.get("id"),
                "source_type":local(obj),
                "source_structure_sha256":hashlib.sha256(
                    json.dumps(normalized_xml_structure(obj),sort_keys=True,
                               separators=(",",":")).encode()).hexdigest(),
                "direct_filters":actions,
                "source_sets":[{"operator":s.get("set_operator","UNION"),
                                "references":[(c.text or "").strip()
                                              for c in s.iter()
                                              if local(c)=="object_reference"]}
                               for s in sets],
            })
        classifications=[]
        if not title:
            classifications=["NO_SOURCE_TITLE"]
        elif not graph:
            classifications=["NO_SOURCE_COMMENT_MATCH"]
        elif len(graph)>1:
            # Shared NG Assessments may originate from both Linux package
            # archives. Same exact OVAL Object ID/structure in both is a
            # repeated source copy, not competing identity.
            source_shapes={(m["source_id"],m["source_structure_sha256"])
                           for m in graph}
            identities={m["source_id"] for m in graph}
            if len(source_shapes)==1:
                classifications=["REPEATED_IDENTICAL_SOURCE_OBJECT"]
            elif len(identities)==1:
                classifications=["SAME_ID_DIVERGENT_SOURCE_XML"]
            else:
                classifications=["MULTIPLE_DISTINCT_SOURCE_OBJECTS"]
        elif graph[0]["source_sets"]:
            classifications=["SOURCE_CONTAINS_SET"]
        elif graph[0]["direct_filters"]==item["filter_actions"]:
            classifications=["UNIQUE_SOURCE_DIRECT_FILTER_NO_SET"]
        else:
            classifications=["SOURCE_FILTER_MISMATCH"]
        records.append({**item, "source_title_checked":title,
                        "source_matches":graph, "classification":classifications[0],
                        "source_test_linkage":linkage,
                        "source_test_object_refs":unique_linked_refs,
                        "source_test_candidates":linked})
    counts=Counter(r["classification"] for r in records)
    links=Counter(r["source_test_linkage"] for r in records)
    missing_title_links=Counter(r["source_test_linkage"]
                                for r in records if r["classification"]=="NO_SOURCE_TITLE")
    if assert_six and (len(ng_docs)!=4001 or len(singletons)!=50):
        raise ValueError("Pinned 0.4.0 singleton-Set baseline changed")
    return {
        "status":"SOURCE_COMMENT_TRIAGE_NOT_SOURCE_IDENTITY_OR_SCANNER_PARITY",
        "documents":len(ng_docs),
        "singleton_set_occurrences":len(singletons),
        "classifications":dict(sorted(counts.items())),
        "test_linkage":dict(sorted(links.items())),
        "missing_title_test_linkage":dict(sorted(missing_title_links.items())),
        "by_parent_area":dict(Counter(
            ("test" if r["test"] else r["site"][1])
            for r in records)),
        "original_oval_source_zip_sha256":checksums,
        "items":records,
        "rewrites_authorized":False,
        "scanner_semantics_verified":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--assert-six",action="store_true")
    args=p.parse_args()
    documents=read_authoring_archive(args.archive,"json")
    sources,checksums=originals(args.source_dir)
    report=audit(documents,sources,checksums,assert_six=args.assert_six)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":report["status"],
        "singleton_set_occurrences":report["singleton_set_occurrences"],
        "classifications":report["classifications"],
        "test_linkage":report["test_linkage"],
        "missing_title_test_linkage":report["missing_title_test_linkage"],
        "by_parent_area":report["by_parent_area"],
        "sample_needing_review": [
            {"path":r["path"], "test":r["test"],
             "classification":r["classification"],
             "matched_sources":[x["source_id"] for x in r["source_matches"]]}
            for r in report["items"] if r["classification"] not in (
                "UNIQUE_SOURCE_DIRECT_FILTER_NO_SET", "SOURCE_CONTAINS_SET")
        ][:12],
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
