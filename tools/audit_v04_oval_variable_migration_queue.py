#!/usr/bin/env python3
"""Source-pinned OVAL Variable migration queue for canonical SCAP-NG 0.4.0.

Preserves original 0.3-compatible Variable graphs and dependencies from
OVAL Self-Assertion source review. This is NOT current 0.4 conversion
or scanner parity. Refs #248 #229 #232.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"
FIRST="VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY"

def fingerprint(value):
    return sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
                             separators=(",",":")).encode()).hexdigest()

def references(value,path=()):
    """Walk source Variable refs, including annotated typed/cardinality uses.

    Native authored operands may carry `datatype` and `value_match`
    beside `variable`. Those are still one Variable reference, not an
    opaque mapping. Never interpret a non-string or unknown compound
    structure as a Variable reference merely because it has that key.
    """
    if isinstance(value,dict):
        ref_fields={"variable","datatype","value_match"}
        if (type(value.get("variable")) is str
                and set(value)<=ref_fields):
            yield (path,value["variable"])
        else:
            for key,child in value.items():
                yield from references(child,path+(key,))
    elif isinstance(value,list):
        for i,child in enumerate(value):
            yield from references(child,path+(i,))

def variable_dependencies(variables):
    edges={name:sorted({ref for _,ref in references(row["expression"])
                        if ref in variables}) for name,row in variables.items()}
    pending,visited,ordered=set(),set(),[]
    def visit(name):
        if name in pending:raise ValueError("Cyclic source Variable: "+name)
        if name in visited:return
        pending.add(name)
        for target in edges[name]:visit(target)
        pending.remove(name)
        visited.add(name)
        ordered.append(name)
    for name in sorted(edges):visit(name)
    return edges,ordered

def inspect(row,document):
    src=document.get("source") or {}
    a=document.get("A_source_compatibility_fallback") or {}
    if (src.get("file")!=row["file"] or
        src.get("definition_id")!=row["definition_id"] or
        len(src.get("source_file_sha256") or "")!=64):
        raise ValueError("Pinned OVAL Definition/sha mismatch")
    variables=a.get("variables") or {}
    if a.get("mode")!="automated" or not isinstance(variables,dict) or not variables:
        raise ValueError("Automated source Variables not found")
    kinds=Counter();ops=Counter()
    for name,var in variables.items():
        # The historical lossless OVAL import preserves collision-resolved
        # IDs such as '...-variable-2'. They must be inventoried as source,
        # not silently renamed to satisfy a new authored-0.4 naming policy.
        if not isinstance(name,str) or not name or not isinstance(var,dict):
            raise ValueError("Malformed named source Variable")
        if var.get("kind") not in {"local","constant","external"}:
            raise ValueError("Unrecognized OVAL Variable origin")
        kinds[var["kind"]]+=1
        expression=var.get("expression")
        if not isinstance(expression,dict) or len(expression)!=1:
            raise ValueError("Unsupported original Variable expression shape")
        ops.update(expression.keys())
    deps,order=variable_dependencies(variables)
    consumers={}
    for section in ("objects","shared_objects","tests","states","variables"):
        for path,name in references(a.get(section,{}),(section,)):
            if name not in variables:
                raise ValueError("Dangling original Variable: "+name)
            consumers.setdefault(name,[]).append(list(path))
    if set(consumers)!=set(variables):
        raise ValueError("Orphan declared source Variables: "+
                         str(sorted(set(variables)-set(consumers))))
    capabilities=sorted({test["capability"] for test in a.get("tests",{}).values()})
    return {
        "test_capabilities":capabilities,
        "test_count":len(a.get("tests",{})),
        "state_count":len(a.get("states",{})),
        "source_file":row["file"],"source_definition_id":row["definition_id"],
        "source_xml_sha256":src["source_file_sha256"],"assessment_id":a["id"],
        "variable_count":len(variables),"origins":dict(sorted(kinds.items())),
        "operators":dict(sorted(ops.items())),"source_variable_names":sorted(variables),
        "expression_dependency_edges":deps,"dependency_first_order":order,
        "variable_consumer_paths":consumers,
        "source_variables_sha256":fingerprint(variables),
        "migration_group":("constant_only" if set(kinds)=={"constant"}
                           else "locally_derived_or_mixed"),
        "original_source_graph_closure":"PASS",
        "current_040_schema":"NOT_TESTED",
        "independent_oval_xml_roundtrip":"NOT_TESTED",
        "scanner_result_parity":"NOT_PROVEN",
    }

def audit(base):
    base=Path(base)
    review=json.loads((base/"c-review/manifest.json").read_text())
    old=json.loads((base/"c-native/conversion-manifest.json").read_text())
    if (review.get("source_revision")!=PIN or
        review.get("source_definition_count")!=167 or
        review.get("A_source_parity_review_definitions")!=162 or
        old.get("source_compatible_not_yet_native_C")!=126):
        raise ValueError("Pinned Self-Assertion OVAL evidence changed")
    index={(v["file"],v["definition_id"]):v
           for v in review["exported_views"]}
    if len(index)!=162:raise ValueError("Duplicate historical OVAL Definition")
    blockers=[v for v in old["unsupported"]
              if v.get("reason","").startswith(FIRST)]
    if len(blockers)!=68:raise ValueError("Expected 68 original Variable blockers")
    records=[];seen=set()
    for row in sorted(blockers,key=lambda r:(r["file"],r["definition_id"])):
        key=row["file"],row["definition_id"]
        if key in seen or key not in index:
            raise ValueError("Source Variable Definition duplicate/missing")
        seen.add(key)
        file=(base/"c-review"/index[key]["review_file"]).resolve()
        if not file.is_relative_to((base/"c-review").resolve()):
            raise ValueError("Review file escapes pinned evidence")
        records.append(inspect(row,json.loads(file.read_text())))
    catalog_dir=Path(__file__).resolve().parents[1]/"schema/v0.4.0/capability-mappings/supported"
    available={p.stem for p in catalog_dir.glob("*.json")}
    if len(available)!=100:raise ValueError("Unsupported current 0.4 capability catalog census")
    counts=Counter();operations=Counter()
    for row in records:
        missing=sorted(set(row["test_capabilities"])-available)
        row["unsupported_current_040_capabilities"]=missing
        row["native_mapping_status"]=(
            "UNSUPPORTED_NATIVE_CAPABILITY" if missing
            else "MAPPED_NOT_SOURCE_OR_SEMANTICALLY_VALIDATED")
        counts["definitions"]+=1
        counts["variables"]+=row["variable_count"]
        counts["constant_variables"]+=row["origins"].get("constant",0)
        counts["local_variables"]+=row["origins"].get("local",0)
        counts["one_variable_definitions"]+=row["variable_count"]==1
        counts[row["migration_group"]+"_definitions"]+=1
        if row["migration_group"]=="constant_only":
            counts["constant_only_missing_native_mapping_definitions"]+=bool(missing)
            counts["constant_only_supported_capability_definitions"]+=not bool(missing)
        operations.update(row["operators"])
    if not (counts["definitions"]==68 and counts["variables"]==245 and
            counts["constant_only_definitions"]==42 and
            counts["locally_derived_or_mixed_definitions"]==26 and
            counts["constant_only_missing_native_mapping_definitions"]==29 and
            counts["constant_only_supported_capability_definitions"]==13):
        missing_caps=Counter(cap for row in records
                             if row["migration_group"]=="constant_only"
                             for cap in row["unsupported_current_040_capabilities"])
        raise ValueError("Source Variable graph corpus count changed: "+
                         json.dumps(dict(sorted(counts.items())),sort_keys=True)+
                         "; absent native capabilities="+
                         json.dumps(dict(sorted(missing_caps.items())),sort_keys=True))
    return {
        "status":"SOURCE_VARIABLE_GRAPHS_CLOSED_040_CONVERSION_NOT_PROVEN",
        "pinned_source_revision":PIN,"definitions":68,
        "counts":dict(sorted(counts.items())),
        "source_variable_expression_operators":dict(sorted(operations.items())),
        "current_040_validated_conversions_from_this_audit":0,
        "scanner_execution_parity":False,"records":records,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-review",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    result=audit(args.source_review)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))

if __name__=="__main__":main()
