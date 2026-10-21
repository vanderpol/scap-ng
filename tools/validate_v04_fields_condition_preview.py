#!/usr/bin/env python3
"""Validate proposal-only SCAP-NG 0.4 condition fields+require vocabulary.

Human-facing proposal: `fields` is one original OVAL State-sized complete
condition, with ordinary field AND defined by the grammar, and a preceding
local `require` (or explicitly declared enclosing Test field requirement).
The official versioned schema is NEVER modified by this script.

Fail closed if a field lacks a local, explicit source-inherited, or own
existence+match rule. Record predicates/Variables and repeated-name OVAL
entities are not expanded into this narrow simple-fields subset.
Refs #248 #239.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

from v04_canonical_source_ir import _schema_validators,validate_docs,compile_pair
from v04_a_authoring_graph_index import read_authoring_archive


LOGICAL=frozenset(("and","or","one","xor","all","any","odd"))


def candidate_schema(path):
    """Create a self-contained temporary copy; require active old grammar."""
    root=Path(__file__).resolve().parents[1]/"schema/v0.4.0"
    shutil.copytree(root,path)
    dest=path/"assessment-language.schema.json"
    d=json.loads(dest.read_text())
    # A Test with a shared State-field requirement uses scoped_state_entry;
    # a Test whose individual conditions/fields explicitly supply their own
    # requirement uses state_entry. The proposed group must work under BOTH
    # branches or it would reject valid source-backed converted Assessments.
    for shape,predicate in (("scoped_state_entry","inherited_field_predicate"),
                            ("state_entry","inherited_field_predicate")):
        entries=d["$defs"][shape]["oneOf"]
        if any(choice.get("required")==["fields"] for choice in entries):
            raise ValueError("Proposed generic fields scope already in normative "+shape)
        branch={
          "type":"object",
          "required":["fields"],
          "properties":{
            "require":{"$ref":"#/$defs/paired_requirement",
                       "description":"Explicit local field existence/matching rule; overrides declared Test scope."},
            "fields":{"type":"object","minProperties":2,
                      "propertyNames":{"type":"string","minLength":1},
                      "additionalProperties":{"$ref":"#/$defs/"+predicate},
                      "description":"One complete expected condition, AND of ordinary field predicates."},
          },
          "additionalProperties":False,
          "title":"Proposed complete expected condition (NOT accepted schema)"
        }
        entries.append(branch)
    d["x-last-modified"]="2026-10-21"
    dest.write_text(json.dumps(d,indent=2)+"\n")
    return path


def field_scopes(test):
    """Inspect only candidate condition grammar, not nested record `fields`."""
    if not isinstance(test,dict):
        raise ValueError("Not an authored Test")
    requirement=test.get("require")
    if not isinstance(requirement,dict) or not isinstance(requirement.get("all_items_must"),list):
        return []
    result=[]
    test_scope=test.get("state_fields_require")
    def visit(node,inherited,path):
        if not isinstance(node,dict) or not node:
            raise ValueError("Empty/malformed State condition at "+str(path))
        if "fields" in node:
            if set(node)-{"fields","require"}:
                raise ValueError("Ambiguous fields condition containing logical siblings")
            fields=node["fields"]
            if not isinstance(fields,dict) or len(fields)<2:
                raise ValueError("Only two-or-more scalar fields in this narrow preview")
            if any(not isinstance(name,str) or not isinstance(field,dict)
                   or not field for name,field in fields.items()):
                raise ValueError("Invalid field map in condition")
            if any("record" in field for field in fields.values()):
                raise ValueError("Record cardinality must not inherit ordinary scalar scope")
            local=node.get("require")
            if local is not None and not isinstance(local,str):
                raise ValueError("Local field requirement must be explicit scalar token")
            effective=local if local is not None else inherited
            if effective is None and not all(
                 isinstance(field.get("require"),str) for field in fields.values()):
                raise ValueError("Field missing explicit or inherited existence+matching")
            scope=("local" if local is not None else
                   "inherited" if effective is not None else "each_field")
            result.append({"path":list(path),"scope":scope,"fields":list(fields)})
            return
        logical=[name for name in LOGICAL if name in node and isinstance(node[name],list)]
        if logical:
            if len(logical)!=1 or set(node)-{logical[0],"state_fields_require"}:
                raise ValueError("Ambiguous nested State operators")
            op=logical[0]
            child_scope=node.get("state_fields_require",inherited)
            if not node[op]:
                raise ValueError("Empty logical State aggregation")
            for i,child in enumerate(node[op]):
                visit(child,child_scope,path+(op,i))
            return
        # Ordinary single-field leaf: leaf-level `require` is validated by
        # the versioned scalar predicate schema; do not descend into record
        # wrapper `fields`, which have independent requirements.
    for i,clause in enumerate(requirement["all_items_must"]):
        visit(clause,test_scope,("require","all_items_must",i))
    return result


def audit(jsonzip,yamlzip):
    json_docs=read_authoring_archive(jsonzip,"json")
    yaml_docs=read_authoring_archive(yamlzip,"yaml")
    if len(json_docs)!=4001 or len(yaml_docs)!=4001:
        raise ValueError("Six-STIG candidate corpus must contain all 4,001 files per format")
    if {x.removesuffix(".json") for x in json_docs}!={x.removesuffix(".yaml") for x in yaml_docs}:
        raise ValueError("JSON/YAML file identity mismatch")
    counts=Counter()
    examples=[]
    for path,data in sorted(json_docs.items()):
        a=data.get("assessment")
        if not isinstance(a,dict) or a.get("mode")!="automated":
            continue
        for name,test in (a.get("tests") or {}).items():
            for site in field_scopes(test):
                counts["groups"]+=1
                counts[site["scope"]]+=1
                if len(examples)<10:
                    examples.append({"document":path,"test":name,**site})
    # The source-reversible field preview introduced exactly these 231
    # groups. Do not count pre-existing record.fields as scalar conditions.
    expected={"groups":231,"local":184,"inherited":44,"each_field":3}
    if {k:counts[k] for k in expected}!=expected:
        raise ValueError("Proposed field-scope source census drift: "+
                         repr(dict(counts)))
    with TemporaryDirectory(prefix="v04-fields-condition-") as td:
        validators=_schema_validators(candidate_schema(Path(td)/"v0.4.0"))
        validate_docs(json_docs,validators)
        validate_docs(yaml_docs,validators)
    # A source-IR compiler pass does not imply executable evaluation. It
    # checks references and exact source graph reconstruction independently.
    _,ir=compile_pair(jsonzip,yamlzip,validate_schema=False)
    if (ir.get("source_reconstruction")!="PASS"
        or ir.get("yaml_json_byte_parity")!="PASS"
        or ir.get("documents")!=4001 or ir.get("tests")!=1375):
        raise ValueError("Field proposal failed current typed source IR")
    return {
        "status":"PROPOSED_FIELDS_SCOPE_SCHEMA_AND_SOURCE_IR_PASS_NOT_NORMATIVE",
        "documents":4001,"automated_tests":1375,
        "new_condition_scopes":dict(sorted(counts.items())),
        "samples":examples,
        "candidate_json_yaml_parity":"PASS",
        "proposal_only_schema":"PASS",
        "maintained_source_ir_source_reconstruction":"PASS",
        "accepted_040_schema_changed":False,
        "original_oval_xml_export":"NOT_RUN",
        "scanner_six_state_parity":"NOT_RUN"
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-zip",type=Path,required=True)
    p.add_argument("--yaml-zip",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    result=audit(args.json_zip,args.yaml_zip)
    args.report.parent.mkdir(exist_ok=True,parents=True)
    args.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="samples"},
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
