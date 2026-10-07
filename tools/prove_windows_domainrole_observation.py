#!/usr/bin/env python3
"""Research proof for a Windows shared Observation Item export.

Targets the repeated DomainRole WMI acquisition in converted Windows Server 2025
content. The Observation owns only the acquisition Object; Rule-specific States,
Tests, and evaluate logic remain local. Flattening must restore the faithful
converted Assessment exactly.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import yaml

OBSERVATION_ID="shared.windows.computer-system-role"
OBSERVATION_VERSION=1
OBSERVATION_PATH="../../shared/observations/windows-computer-system-role.observation.yaml"
BINDING_ALIAS="system_role"
EXPORT_NAME="computer_system"
CANONICAL_OBJECT_NAME="computer-system-role"

EXPECTED_CAPABILITY="windows.wmi.query"
EXPECTED_COLLECT={
    "namespace":"root\\cimv2",
    "query":"SELECT DomainRole FROM win32_computersystem",
}


def candidate_object(a:dict)->tuple[str,dict]|None:
    matches=[]
    for name,payload in (a.get("objects") or {}).items():
        if (
            isinstance(payload,dict)
            and payload.get("capability")==EXPECTED_CAPABILITY
            and payload.get("collect")==EXPECTED_COLLECT
        ):
            matches.append((name,payload))
    if not matches:
        return None
    if len(matches)!=1:
        raise ValueError(f"multiple DomainRole WMI Objects in one Assessment: {[x[0] for x in matches]}")
    return matches[0]


def observation_document(payload:dict)->dict:
    return {
        "observation":{
            "id":OBSERVATION_ID,
            "version":OBSERVATION_VERSION,
            "specification":{
                "id":"scap-ng.pre-alpha.observation",
                "version":"0.3.0-research",
            },
            "objects":{
                CANONICAL_OBJECT_NAME:copy.deepcopy(payload),
            },
            "exports":{
                EXPORT_NAME:{
                    "kind":"items",
                    "object":CANONICAL_OBJECT_NAME,
                    "capability":EXPECTED_CAPABILITY,
                }
            },
        }
    }


def export_ref()->dict:
    return {"observation":BINDING_ALIAS,"export":EXPORT_NAME}


def scalar_ref_count(value:Any,target:str)->int:
    if isinstance(value,dict):
        return sum(scalar_ref_count(v,target) for v in value.values())
    if isinstance(value,list):
        return sum(scalar_ref_count(v,target) for v in value)
    return int(value==target) if isinstance(value,str) else 0


def validate_consumer(a:dict,observation_doc:dict)->None:
    binding=(a.get("observations") or {}).get(BINDING_ALIAS)
    if not isinstance(binding,dict):
        raise ValueError("consumer missing system_role Observation binding")
    obs=observation_doc["observation"]
    if binding.get("expected_id")!=obs["id"]:
        raise ValueError("Observation consumer expected_id mismatch")
    if binding.get("expected_version")!=obs["version"]:
        raise ValueError("Observation consumer expected_version mismatch")

    def visit(value:Any):
        if isinstance(value,dict):
            if set(value)=={"observation","export"}:
                if value.get("observation")!=BINDING_ALIAS:
                    raise ValueError("unknown Observation binding alias")
                if value.get("export")!=EXPORT_NAME:
                    raise ValueError("unknown Observation export")
                return
            for child in value.values():
                visit(child)
        elif isinstance(value,list):
            for child in value:
                visit(child)
    for key,value in a.items():
        if key!="observations":
            visit(value)


def extract(doc:dict,observation_doc:dict)->tuple[dict,str,int]:
    out=copy.deepcopy(doc)
    a=out["assessment"]
    candidate=candidate_object(a)
    if candidate is None:
        raise ValueError("Assessment has no DomainRole WMI Object")
    object_name,payload=candidate
    if observation_document(payload)!=observation_doc:
        raise ValueError("DomainRole Observation payload differs")

    total_refs=scalar_ref_count(a,object_name)
    rewritten_refs=0
    for test in (a.get("tests") or {}).values():
        if isinstance(test,dict) and test.get("object")==object_name:
            test["object"]=export_ref()
            rewritten_refs+=1
    if rewritten_refs==0:
        raise ValueError("DomainRole Object has no Test consumer")
    if total_refs!=rewritten_refs:
        raise ValueError(
            f"DomainRole Object has non-Test consumers: total={total_refs} tests={rewritten_refs}"
        )

    a["objects"].pop(object_name)
    if not a["objects"]:
        a.pop("objects",None)
    a["observations"]={
        BINDING_ALIAS:{
            "source":OBSERVATION_PATH,
            "expected_id":OBSERVATION_ID,
            "expected_version":OBSERVATION_VERSION,
        }
    }
    validate_consumer(a,observation_doc)
    return out,object_name,rewritten_refs


def flatten(extracted:dict,observation_doc:dict,object_name:str)->dict:
    out=copy.deepcopy(extracted)
    a=out["assessment"]
    validate_consumer(a,observation_doc)
    a.pop("observations",None)
    restored=0
    for test in (a.get("tests") or {}).values():
        if isinstance(test,dict) and test.get("object")==export_ref():
            test["object"]=object_name
            restored+=1
    if not restored:
        raise ValueError("no Observation Item export references to flatten")
    objects=a.get("objects") or {}
    if object_name in objects:
        raise ValueError(f"Object collision while flattening: {object_name}")
    payload=observation_doc["observation"]["objects"][CANONICAL_OBJECT_NAME]
    objects[object_name]=copy.deepcopy(payload)
    a["objects"]=objects
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--artifact-dir",type=Path,required=True)
    ap.add_argument("--sample-count",type=int,default=4)
    args=ap.parse_args()

    observation=None
    eligible=[]
    rejected=[]
    samples=[]

    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment") or {}
        aid=str(a.get("id") or "")
        if a.get("mode")!="automated" or not a.get("tests"):
            continue
        try:
            candidate=candidate_object(a)
        except ValueError as exc:
            rejected.append({"assessment_id":aid,"reason":str(exc)})
            continue
        if candidate is None:
            continue
        object_name,payload=candidate
        candidate_obs=observation_document(payload)
        if observation is None:
            observation=candidate_obs
        elif candidate_obs!=observation:
            rejected.append({"assessment_id":aid,"reason":"shared DomainRole Object payload differs"})
            continue
        try:
            extracted,original_name,refs=extract(doc,observation)
            restored=flatten(extracted,observation,original_name)
        except ValueError as exc:
            rejected.append({"assessment_id":aid,"reason":str(exc)})
            continue
        if restored!=doc:
            rejected.append({"assessment_id":aid,"reason":"flatten_roundtrip_mismatch"})
            continue
        eligible.append({
            "assessment_id":aid,
            "source":str(path),
            "original_object_name":original_name,
            "test_consumers":refs,
        })
        if len(samples)<args.sample_count:
            samples.append((aid,extracted))

    if observation is None:
        raise SystemExit("no DomainRole WMI Observation candidate found")

    args.artifact_dir.mkdir(parents=True,exist_ok=True)
    obsdir=args.artifact_dir/"shared"/"observations"
    obsdir.mkdir(parents=True,exist_ok=True)
    (obsdir/"windows-computer-system-role.observation.yaml").write_text(
        yaml.safe_dump(observation,sort_keys=False),
        encoding="utf-8",
    )
    sampledir=args.artifact_dir/"consumer-samples"
    sampledir.mkdir(parents=True,exist_ok=True)
    for i,(aid,sample) in enumerate(samples,1):
        safe="".join(c if c.isalnum() or c in "._-" else "_" for c in aid)
        (sampledir/f"{i:02d}-{safe}.assessment.yaml").write_text(
            yaml.safe_dump(sample,sort_keys=False,width=120),
            encoding="utf-8",
        )

    report={
        "format":"scap-ng-windows-domainrole-observation-proof-0.1",
        "status":"research_only_not_accepted_design",
        "observation_id":OBSERVATION_ID,
        "observation_version":OBSERVATION_VERSION,
        "export":{
            "name":EXPORT_NAME,
            **observation["observation"]["exports"][EXPORT_NAME],
        },
        "eligible_assessments":len(eligible),
        "eligible":eligible,
        "rejected":rejected,
        "flatten_roundtrip":"passed" if eligible else "not_run",
        "semantic_claim":"source_graph_item_export_and_exact_flattening_only",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "eligible_assessments":len(eligible),
        "rejected":len(rejected),
        "export_kind":"items",
        "test_consumers":sum(x["test_consumers"] for x in eligible),
        "flatten_roundtrip":report["flatten_roundtrip"],
    },indent=2,sort_keys=True))
    if len(eligible)<4:
        raise SystemExit("expected at least four DomainRole Observation consumers")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
