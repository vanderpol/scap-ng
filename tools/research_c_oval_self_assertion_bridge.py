#!/usr/bin/env python3
"""#245 Reproducible read-only 0.4-C review bridge over v003 OVAL roundtrips.

A successful v003 semantic roundtrip is the compatibility floor, NOT a native
C authoring conversion. Generate original test comments/definition titles,
meaningful C display labels, full original typed A execution fallback, and
per-Definition disposition, with no invented scanner-parity claims.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"
REPO="OVAL-Community/SCAP-Self-Assertion"
STAGE="C_READ_ONLY_SOURCE_REVIEW_A_COMPATIBILITY_FALLBACK"
SUFFIX=".review.json"


def local(tag):
    return tag.rsplit("}",1)[-1]


def child(node,tag):
    return next((c for c in node if local(c.tag)==tag),None) if node is not None else None


def text_of(node,tag):
    entry=child(node,tag)
    return "".join(entry.itertext()).strip() if entry is not None else None


def slug(text):
    words=re.sub(r"[^a-z0-9]+","-",(text or "").lower()).strip("-")
    return (words[:75].rstrip("-") or "unnamed")


def original_source(path):
    raw=path.read_bytes()
    root=ET.fromstring(raw)
    defs={}
    tests={}
    for section,kind,dest in (("definitions","definition",defs),
                              ("tests","test",tests)):
        container=child(root,section)
        if container is None: continue
        for node in container:
            ident=node.get("id")
            if local(node.tag)!=kind and not (kind=="test" and local(node.tag).endswith("_test")):
                raise ValueError(f"unexpected OVAL element in {section}: {node.tag}")
            if not ident or ident in dest:
                raise ValueError("duplicate/empty source identifier")
            dest[ident]=node
    return {"sha256":sha256(raw).hexdigest(),"definitions":defs,"tests":tests}


def original_test_refs(definitions,definition_id):
    seen=set()
    visiting=set()
    tests=set()
    def visit(did):
        if did in visiting:
            raise ValueError("cyclic extended Definition")
        if did in seen:
            return
        if did not in definitions:
            raise ValueError("unresolved extended Definition")
        visiting.add(did)
        definition=definitions[did]
        # Walk original Definition criteria only: source Metadata has no check.
        criteria=child(definition,"criteria")
        if criteria is not None:
            for node in criteria.iter():
                if local(node.tag)=="criterion":
                    ref=node.get("test_ref")
                    if not ref:
                        raise ValueError("criterion without Test identity")
                    tests.add(ref)
                elif local(node.tag)=="extend_definition":
                    ref=node.get("definition_ref")
                    if not ref:
                        raise ValueError("extended Definition without identity")
                    visit(ref)
        visiting.remove(did)
        seen.add(did)
    visit(definition_id)
    return sorted(tests)


def safe_native_path(row,artifacts):
    if not isinstance(row.get("native"),str):
        raise ValueError("successful roundtrip missing native output")
    path=Path(row["native"]).resolve()
    root=artifacts.resolve()
    if root not in path.parents:
        raise ValueError("native output path escapes roundtrip directory")
    return path


def review_native(row,source,artifacts):
    if row.get("equal") is not True or row.get("stage")!="equal":
        raise ValueError("native source parity not established")
    did=row["definition_id"]
    definition=source["definitions"][did]
    raw=json.loads(safe_native_path(row,artifacts).read_text(encoding="utf-8"))
    assessment=raw.get("assessment")
    if not isinstance(assessment,dict) or not isinstance(assessment.get("tests"),dict):
        raise ValueError("source-compatible A Tests unavailable")
    native_tests=assessment["tests"]
    if not native_tests:
        raise ValueError("roundtrip Assessment has no Tests")
    test_refs=original_test_refs(source["definitions"],did)
    if any(k not in source["tests"] for k in test_refs):
        raise ValueError("missing referenced OVAL Test")
    metadata=child(definition,"metadata")
    title=text_of(metadata,"title")
    description=text_of(metadata,"description")
    original_tests=[]
    for tid in test_refs:
        test=source["tests"][tid]
        original_tests.append({"id":tid,"kind":local(test.tag),
                               "comment":test.get("comment"),
                               "check":test.get("check"),
                               "check_existence":test.get("check_existence"),
                               "state_operator":test.get("state_operator")})
    display={}
    used=set()
    for internal,test in sorted(native_tests.items()):
        value=test.get("test_title")
        label=value.strip() if type(value) is str and value.strip() else None
        # Do not synthesize policy meaning from an opaque OVAL Test identifier.
        name=slug(label or "undocumented-source-test")
        base=name
        i=2
        while name in used:
            name=base+"-"+str(i)
            i+=1
        used.add(name)
        display[name]={"description":label,"native_test_id":internal,
                       "description_missing":label is None}
    # OVAL comments and exact roundtrip Tests remain explicit: a count match
    # alone cannot determine each original ID's generated internal Test ID.
    return {
        "status":STAGE,
        "source":{"repository":REPO,"revision":PIN,
                  "file":row["file"],"source_file_sha256":source["sha256"],
                  "definition_id":did,"definition_title":title,
                  "definition_description":description,
                  "original_test_documentation":original_tests},
        "C_read_only_view":{
            "assessment_title":title,"checks":display,
            "original_test_count":len(original_tests),
            "native_test_count":len(display),
            "original_criteria_preserved_in_A":True,
            "C_source_independent_compilation_proven":False,
            "OVAL_scanner_runtime_parity_proven":False,
        },
        "A_source_compatibility_fallback":assessment,
    }


def export(source_root,roundtrip_report,native_root,out):
    source_root=Path(source_root)
    native_root=Path(native_root)
    out=Path(out)
    report=json.loads(Path(roundtrip_report).read_text(encoding="utf-8"))
    if not isinstance(report.get("results"),list):
        raise ValueError("per-Definition v003 semantic roundtrip rows required")
    if report.get("parse_failures"):
        raise ValueError("cannot publish while original OVAL source parsing failed")
    sources={}
    identities=set()
    counts=Counter()
    tests=set()
    for file in sorted(source_root.rglob("*.xml")):
        rel=file.relative_to(source_root).as_posix()
        source=original_source(file)
        sources[rel]=source
        for did in source["definitions"]:
            identities.add((rel,did))
        for tid in source["tests"]:
            tests.add((rel,tid))
    by_rows={(r.get("file"),r.get("definition_id")):r
             for r in report["results"]}
    if len(by_rows)!=len(report["results"]) or set(by_rows)!=identities:
        raise ValueError("roundtrip output does not account for every source Definition")
    out.mkdir(parents=True,exist_ok=True)
    exported=[]
    blocked=[]
    for key in sorted(identities):
        file,did=key
        row=by_rows[key]
        if row.get("equal") is not True:
            reason={"file":file,"definition_id":did,"stage":row.get("stage"),
                    "unsupported_features":row.get("unsupported_features"),
                    "error":row.get("error")}
            blocked.append(reason)
            counts["blocked"]+=1
            continue
        view=review_native(row,sources[file],native_root)
        filename=sha256((file+"\0"+did).encode("utf-8")).hexdigest()[:24]+SUFFIX
        (out/filename).write_text(json.dumps(view,indent=2,ensure_ascii=False,
                                             sort_keys=True)+"\n",encoding="utf-8")
        exported.append({"file":file,"definition_id":did,"review_file":filename,
                         "original_tests":len(view["source"]["original_test_documentation"]),
                         "native_tests":view["C_read_only_view"]["native_test_count"]})
        counts["source_parity_A_review_only"]+=1
    result={"source_repository":REPO,"source_revision":PIN,"status":STAGE,
            "source_file_count":len(sources),
            "source_definition_count":len(identities),
            "source_test_count":len(tests),
            "A_source_parity_review_definitions":len(exported),
            "failed_A_roundtrip_or_unsupported_definitions":len(blocked),
            "native_0_4_C_converted_definitions":0,
            "scanner_execution_parity_proven":False,
            "blocked_definitions":blocked,"exported_views":exported}
    (out/"manifest.json").write_text(json.dumps(result,indent=2,
                                   sort_keys=True)+"\n",encoding="utf-8")
    return result


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--native-out",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args(argv)
    data=export(args.corpus,args.report,args.native_out,args.output)
    print(json.dumps({k:v for k,v in data.items()
                      if k not in ("blocked_definitions","exported_views")},
                     indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
