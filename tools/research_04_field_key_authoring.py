#!/usr/bin/env python3
"""Research-only 0.4 state-field-key compact syntax, with exact 0.3 lowering.

Transforms exactly one canonical field predicate per list entry:
    - field: owner_uid
      value: 0
      operation: equals
      existence: one_or_more
      match: all
into:
    - owner_uid:
        value: 0
        operation: equals
        existence: one_or_more
        match: all
and reverses it. No existence/match defaults or predicate logic changes.

State composition remains list-shaped and ordered. Logical branches are traversed
only through known operators. Unknown structures remain canonical unchanged.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import argparse
import json
import zipfile

import yaml

LOGICAL={"all","any","one","odd"}
RESERVED={"field","value","operation","existence","match","datatype",
          "value_match","input","variable","states","state","state_title",
          "redact_result","reported_elements","capability",*LOGICAL}
# A list entry deliberately has only one mapping field; the key inside the
# mapping is field-specific. Explicit composite branches keep their own keys.
PREDICATE_KEYS={"value","operation","datatype","existence","match","value_match",
                "variable","input","nil","redact_result","var_check",
                "state_title","check_existence","entity_check","mask","record"}

def fold_node(entry,counts:Counter):
    """Canonical State predicate or logical branch -> compact field-key node."""
    if not isinstance(entry,dict):
        counts["non_mapping_entries_unchanged"]+=1
        return deepcopy(entry)
    if "field" in entry:
        field=entry["field"]
        counts["canonical_field_nodes"]+=1
        if not isinstance(field,str) or not field.strip():
            counts["non_literal_or_empty_fields_unmodified"]+=1
            return deepcopy(entry)
        # In a separate field-key grammar, a field called "value", "field",
        # or "all" is valid. Disambiguate by the shape of its payload:
        # a mapping is a field, while logical all/any/one/odd require lists.
        # This eliminates a troublesome real Windows Registry exception.
        payload={k:deepcopy(v) for k,v in entry.items() if k!="field"}
        # A non-empty payload retains all comparison metadata. Do not let
        # this macro invent a field predicate without explicit data.
        if not payload:
            counts["empty_predicate_unmodified"]+=1
            return deepcopy(entry)
        counts["field_key_compacted"]+=1
        counts[f"field_name:{field}"]+=1
        return {field:payload}
    if len(entry)==1:
        operator=next(iter(entry))
        if operator in LOGICAL and isinstance(entry[operator],list):
            counts[f"logic_branch:{operator}"]+=1
            return {operator:[fold_node(x,counts) for x in entry[operator]]}
    counts["other_state_structures_unchanged"]+=1
    return deepcopy(entry)


def unfold_node(entry):
    if not isinstance(entry,dict):
        return deepcopy(entry)
    # Canonical longhand has a string-valued field property. A compact
    # field named "field" is distinguishable because its payload is a map.
    if "field" in entry and (len(entry)!=1 or not isinstance(entry["field"],dict)):
        return deepcopy(entry)
    if len(entry)!=1:
        raise ValueError("A compact State entry must have one field key")
    key=next(iter(entry))
    payload=entry[key]
    if key in LOGICAL and isinstance(payload,list):
        return {key:[unfold_node(x) for x in payload]}
    if not isinstance(key,str) or not key.strip():
        raise ValueError("A compact field key must be a nonempty string")
    if not isinstance(payload,dict) or not payload:
        raise ValueError("A compact field predicate requires a nonempty mapping payload")
    if "field" in payload:
        raise ValueError("Compact field-key conflicts with an explicit field property")
    return {"field":key,**deepcopy(payload)}


def fold_document(document):
    result=deepcopy(document)
    a=result.get("assessment") or {}
    counts=Counter()
    for tid,test in (a.get("tests") or {}).items():
        if not isinstance(test,dict):
            continue
        states=test.get("states")
        if isinstance(states,list):
            counts["state_lists"]+=1
            test["states"]=[fold_node(s,counts) for s in states]
        else:
            if "states" in test:
                counts["nonlist_states_unmodified"]+=1
    return result,counts


def unfold_document(document):
    result=deepcopy(document)
    a=result.get("assessment") or {}
    for test in (a.get("tests") or {}).values():
        if not isinstance(test,dict):
            continue
        if isinstance(test.get("states"),list):
            test["states"]=[unfold_node(entry) for entry in test["states"]]
    return result


def audit(archive):
    counts=Counter()
    by_benchmark=defaultdict(Counter)
    examples=[]
    exceptions=[]
    with zipfile.ZipFile(archive) as source:
        if source.testzip() is not None:
            raise ValueError("Corrupt six-STIG source zip")
        for name in sorted(source.namelist()):
            if not name.startswith("authoring/") or not name.endswith(".automated.yaml"):
                continue
            original=yaml.safe_load(source.read(name))
            if not isinstance(original,dict) or (original.get("assessment") or {}).get("mode")!="automated":
                continue
            shorter,stats=fold_document(original)
            reconstructed=unfold_document(shorter)
            if reconstructed!=original:
                raise ValueError(f"Source round-trip mismatch: {name}")
            counts["assessments_exact_roundtrip"]+=1
            counts.update(stats)
            package=name.split("/")[1]
            by_benchmark[package]["assessments_exact_roundtrip"]+=1
            by_benchmark[package].update(stats)
            if stats["field_key_compacted"]>0 and len(examples)<15:
                for test_id,test in original["assessment"].get("tests",{}).items():
                    if not isinstance(test,dict):
                        continue
                    for predicate in (test.get("states") or []):
                        if isinstance(predicate,dict) and "field" in predicate:
                            compact=fold_node(predicate,Counter())
                            examples.append({"file":name,"test":test_id,
                                             "before":predicate,"after":compact})
                            break
                    if len(examples)>=15:
                        break
            if any(key.startswith("reserved_field_name:") for key in stats):
                exceptions.append({"file":name,
                                   "reserved_field_names":{
                                       k:v for k,v in stats.items() if k.startswith("reserved_field_name:")}})
    return {
        "source":archive.name,
        "status":"exact_parsed_0_3_roundtrip_only",
        "counts":dict(counts),
        "by_benchmark":{k:dict(v) for k,v in sorted(by_benchmark.items())},
        "examples":examples[:15],
        "reserved_name_cases":exceptions[:30],
        "limitations":[
            "The six-STIG snapshot only; primary full-corpus OVAL source field-entity counts are a separate measure.",
            "Dynamic field keys are only accepted within a strictly versioned compact source schema, not canonical NG.",
            "Names colliding with comparison or logical keywords, e.g. Windows Registry value, remain valid compact field keys because map versus list/string payload shapes are disjoint.",
            "The compiler still needs capability-specific field enumeration, schema validation and complete semantic conformance.",
            "This counts one predicate per source list entry, preserving duplicate field entries and ordering.",
        ],
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.authoring_zip)
    output=json.dumps(result,indent=2,sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output+"\n")
    print("COUNTS",json.dumps(result["counts"]))
    print("RESERVED",json.dumps(result["reserved_name_cases"][:5]))
    print("EXAMPLES",json.dumps(result["examples"][:3]))
