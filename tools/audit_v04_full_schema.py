#!/usr/bin/env python3
"""Audit all source-backed 0.4.0 authoring docs against versioned JSON Schemas.

Diagnostic ONLY: prints failure classes and source paths, returns success to
publish blockers for review. This is deliberately not a release conformance
gate until zero failures and semantic validation are established.
"""
import argparse, collections, json, pathlib, zipfile
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
import yaml

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",type=pathlib.Path,required=True)
    ap.add_argument("--schema-dir",type=pathlib.Path,default=pathlib.Path("schema/v0.4.0"))
    ap.add_argument("--out",type=pathlib.Path,required=True)
    ap.add_argument("--limit",type=int,default=0,help="0 checks every document")
    ap.add_argument("--strict",action="store_true",help="Fail on any invalid Rule/Assessment source document")
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
    grouped=collections.Counter()
    group_examples=collections.defaultdict(list)
    nested_groups=collections.Counter()
    nested_examples=collections.defaultdict(list)
    failure_features=collections.Counter()
    failure_examples=collections.defaultdict(list)
    skipped=[]
    with zipfile.ZipFile(args.archive) as z:
        names=sorted(n for n in z.namelist() if n.startswith("authoring/") and n.endswith((".yaml",".json")))
        if args.limit:names=names[:args.limit]
        registry = Registry().with_resources(
            (uri, Resource.from_contents(schema))
            for uri, schema in schemas.items() if uri.startswith("https://")
        )
        validators={}
        for kind in ("assessment","rule","benchmark","applicability"):
            d=schemas[kind+".schema.json"]
            validators[kind]=Draft202012Validator(d,registry=registry)
        for path in names:
            doc=yaml.safe_load(z.read(path)) if path.endswith(".yaml") else json.loads(z.read(path))
            kind=next((k for k in ("assessment","rule","benchmark","applicability") if k in doc),None)
            if kind is None:
                totals["non_assessment_rule"]+=1
                skipped.append(path)
                print("OTHER_SOURCE",path,"top_level_keys=",list(doc) if isinstance(doc,dict) else type(doc).__name__)
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
                if kind=="assessment":
                    print("SCHEMA_FAIL",path,"assessment_id=",doc["assessment"].get("id"),"checks=",len(errors))
                    for e in errors[:2]:
                        print("  FAIL_PATH",list(e.absolute_path),"validator",e.validator)
                        for child in e.context[:5]:
                            print("    BRANCH",list(child.absolute_path),child.validator,str(child.message)[:160])
                if kind=="assessment":
                    for tid,t in (doc["assessment"].get("tests") or {}).items():
                        if not isinstance(t,dict):continue
                        req=t.get("require")
                        shape="all_items_must" if isinstance(req,dict) and "all_items_must" in req else "presence_only" if isinstance(req,dict) else "string" if isinstance(req,str) else "other"
                        features=["capability:"+str(t.get("capability","missing")),"require_form:"+shape]
                        if t.get("states"):features.append("has_legacy_states")
                        if t.get("states_match"):features.append("has_legacy_states_match")
                        if t.get("state_fields_require"):features.append("has_top_level_field_require")
                        for item in features:
                            failure_features[item]+=1
                            if len(failure_examples[item])<4:
                                failure_examples[item].append({"path":path,"test":tid})

                for error in sorted(errors,key=lambda e:(len(e.path),str(e.path)))[:5]:
                    # anyOf/oneOf wrappers hide the real rejected field path.
                    # Preserve leaf contexts separately without claiming each
                    # candidate branch is an independent validation failure.
                    frontier=[(error,0)]
                    while frontier:
                        node,depth=frontier.pop()
                        if node.context and depth<5:
                            frontier.extend((child,depth+1) for child in node.context[:60])
                        else:
                            leaf=(node.validator or "unknown")+":"+("/".join(map(str,node.absolute_path)) or "$root")
                            nested_groups[leaf]+=1
                            if len(nested_examples[leaf])<3:
                                nested_examples[leaf].append({"path":path,"message":node.message[:180]})

                    key=kind+":"+error.validator+":"+("/".join(map(str,error.absolute_path)) or "$root")
                    totals[key]+=1
                    group=kind+":"+error.validator+":"+(str(next(iter(error.absolute_path),"root")))
                    grouped[group]+=1
                    if len(group_examples[group])<4:
                        group_examples[group].append({"path":path,"message":error.message[:220]})
                    if len(examples[key])<3:
                        examples[key].append({"path":path,"error":error.message[:240]})
    report={"status":"diagnostic_only","archive":str(args.archive),
            "checked_documents":len(names),"counts":dict(totals),
            "other_source_documents":skipped,
            "examples":dict(examples),"grouped_failure_counts":dict(grouped.most_common()),
            "group_examples":dict(group_examples),
            "nested_leaf_counts":dict(nested_groups.most_common()),
            "nested_leaf_examples":dict(nested_examples),
            "failure_test_features":dict(failure_features.most_common()),
            "failure_feature_examples":dict(failure_examples),
            "schema_release_conformant":False,
            "warning":"This audit does not prove native semantic checks, compiler support or scanner equivalence."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"checked_documents":len(names),
        "schema_passes":{k:v for k,v in totals.items() if k.endswith("_schema_pass")},
        "schema_failures":{k:v for k,v in totals.items() if k.endswith("_schema_fail")},
        "validator_exceptions":{k:v for k,v in totals.items() if k.startswith("resolver_or_validator:")},
        "validator_exception_examples":{k:v for k,v in examples.items() if k.startswith("resolver_or_validator:")},
        "error_classes":len(examples),"top_failure_groups":grouped.most_common(12),
        "top_nested_leaves":nested_groups.most_common(12),
        "failure_test_features":failure_features.most_common(12)},indent=2))
    assert len(names)==4012 if not args.limit else len(names)<=args.limit
    if args.strict:
        if args.limit:raise ValueError("Strict corpus gate cannot use --limit")
        expected={"assessment_documents":2422,"assessment_schema_pass":2422,
                  "rule_documents":1567,"rule_schema_pass":1567,
                  "benchmark_documents":6,"benchmark_schema_pass":6,
                  "applicability_documents":6,"applicability_schema_pass":6}
        for k,v in expected.items():
            if totals.get(k)!=v:raise ValueError(f"Strict schema gate: {k} is {totals.get(k)} not {v}")
        failures={k:v for k,v in totals.items() if k.endswith("_schema_fail") or k.startswith("resolver_or_validator")}
        if failures:raise ValueError(f"Strict schema gate failed: {failures}")
        print("PASS strict six-STIG source authoring: 2,422 Assessments, 1,567 Rules, 6 Benchmarks, 6 Applicability documents")

if __name__=="__main__":main()
