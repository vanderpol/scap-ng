#!/usr/bin/env python3
"""Audit all source-backed 0.4.0 authoring docs against versioned JSON Schemas.

Diagnostic ONLY: prints failure classes and source paths, returns success to
publish blockers for review. This is deliberately not a release conformance
gate until zero failures and semantic validation are established.
"""
import argparse, collections, json, pathlib, zipfile
from jsonschema import Draft202012Validator, RefResolver
import yaml

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",type=pathlib.Path,required=True)
    ap.add_argument("--schema-dir",type=pathlib.Path,default=pathlib.Path("schema/v0.4.0"))
    ap.add_argument("--out",type=pathlib.Path,required=True)
    ap.add_argument("--limit",type=int,default=0,help="0 checks every document")
    args=ap.parse_args()
    schemas={}
    for p in args.schema_dir.rglob("*.json"):
        try:
            d=json.loads(p.read_text())
        except (UnicodeDecodeError,json.JSONDecodeError):
            continue
        if not isinstance(d,dict) or "$schema" not in d:
            continue
        schemas[p.name]=d
        if "$id" in d: schemas[d["$id"]]=d
        schemas["https://scap-ng.dev/schema/v0.4.0/"+p.relative_to(args.schema_dir).as_posix()]=d
    if "assessment.schema.json" not in schemas:
        raise ValueError("Native 0.4 Assessment schema not found")
    if "rule.schema.json" not in schemas:
        raise ValueError("Native 0.4 Rule schema not found")
    totals=collections.Counter()
    examples=collections.defaultdict(list)
    skipped=[]
    with zipfile.ZipFile(args.archive) as z:
        names=sorted(n for n in z.namelist() if n.startswith("authoring/") and n.endswith((".yaml",".json")))
        if args.limit:names=names[:args.limit]
        validators={}
        for kind in ("assessment","rule"):
            d=schemas[kind+".schema.json"]
            resolver=RefResolver.from_schema(d,store=schemas)
            validators[kind]=Draft202012Validator(d,resolver=resolver)
        for path in names:
            doc=yaml.safe_load(z.read(path)) if path.endswith(".yaml") else json.loads(z.read(path))
            kind="assessment" if "assessment" in doc else "rule" if "rule" in doc else None
            if kind is None:
                totals["non_assessment_rule"]+=1
                continue
            totals[kind+"_documents"]+=1
            try:
                errors=list(validators[kind].iter_errors(doc))
            except Exception as exc:
                key="resolver_or_validator:"+type(exc).__name__
                totals[key]+=1
                if len(examples[key])<10:examples[key].append({"path":path,"details":str(exc)[:300]})
                continue
            if not errors:
                totals[kind+"_schema_pass"]+=1
            else:
                totals[kind+"_schema_fail"]+=1
                for error in sorted(errors,key=lambda e:(len(e.path),str(e.path)))[:5]:
                    key=kind+":"+error.validator+":"+("/".join(map(str,error.absolute_path)) or "$root")
                    totals[key]+=1
                    if len(examples[key])<3:
                        examples[key].append({"path":path,"error":error.message[:240]})
    report={"status":"diagnostic_only","archive":str(args.archive),
            "checked_documents":len(names),"counts":dict(totals),
            "examples":dict(examples),"schema_release_conformant":False,
            "warning":"This audit does not prove native semantic checks, compiler support or scanner equivalence."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"checked_documents":len(names),
        "schema_passes":{k:v for k,v in totals.items() if k.endswith("_schema_pass")},
        "schema_failures":{k:v for k,v in totals.items() if k.endswith("_schema_fail")},
        "error_classes":len(examples)},indent=2))
    assert len(names)==4001 if not args.limit else len(names)<=args.limit
if __name__=="__main__":main()
