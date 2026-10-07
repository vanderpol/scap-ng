#!/usr/bin/env python3
"""Research proof for a shared RHEL dconf Observation with mixed exports.

The proving case is the source-shared dconf discovery graph used by RHEL 9
SV-258013, SV-258020, and SV-258026.  The Observation owns one meaningful
textfilecontent Object plus its derived lock-directory Variable.  It exports:
- gathered dconf database Items; and
- derived lock-directory string values.

Consumer Tests/Objects/evaluate logic remain local.  Flattening must restore the
faithful converted Assessment exactly.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

OBSERVATION_ID="shared.rhel.dconf-user-databases"
OBSERVATION_VERSION=1
OBSERVATION_PATH="../../shared/observations/rhel-dconf-user-databases.observation.yaml"
BINDING_ALIAS="dconf"

ITEM_EXPORT="databases"
VALUE_EXPORT="lock_directories"

EXPECTED_OBJECT_TITLE="dconf user databases"
EXPECTED_OBJECT_CAPABILITY="independent.textfilecontent54"
EXPECTED_VARIABLE_TITLE="dconf user database locks directories"


def _contains_scalar(value:Any,target:str)->bool:
    if isinstance(value,dict):
        return any(_contains_scalar(v,target) for v in value.values())
    if isinstance(value,list):
        return any(_contains_scalar(v,target) for v in value)
    return value==target


def candidate_nodes(a:dict)->tuple[str,dict,str,dict]|None:
    object_matches=[]
    for name,payload in (a.get("objects") or {}).items():
        if not isinstance(payload,dict):
            continue
        if payload.get("object_title")!=EXPECTED_OBJECT_TITLE:
            continue
        if payload.get("capability") not in (None,EXPECTED_OBJECT_CAPABILITY):
            continue
        if not _contains_scalar(payload,"/etc/dconf/profile/user"):
            continue
        if not _contains_scalar(payload,r"^system-db:(\S+)\s*$"):
            continue
        object_matches.append((name,payload))

    variable_matches=[]
    for name,payload in (a.get("variables") or {}).items():
        if not isinstance(payload,dict):
            continue
        if payload.get("title")!=EXPECTED_VARIABLE_TITLE:
            continue
        if payload.get("kind")!="local" or payload.get("datatype")!="string":
            continue
        variable_matches.append((name,payload))

    if not object_matches and not variable_matches:
        return None
    if len(object_matches)!=1 or len(variable_matches)!=1:
        raise ValueError(
            "expected one dconf source Object and one lock-directory Variable; "
            f"objects={[x[0] for x in object_matches]} variables={[x[0] for x in variable_matches]}"
        )

    object_name,object_payload=object_matches[0]
    variable_name,variable_payload=variable_matches[0]
    if not _contains_scalar(variable_payload,object_name):
        raise ValueError("dconf lock-directory Variable does not consume the candidate Object")
    return object_name,object_payload,variable_name,variable_payload


def observation_document(a:dict)->dict|None:
    candidate=candidate_nodes(a)
    if candidate is None:
        return None
    object_name,object_payload,variable_name,variable_payload=candidate
    capability=object_payload.get("capability") or EXPECTED_OBJECT_CAPABILITY
    return {
        "observation":{
            "id":OBSERVATION_ID,
            "version":OBSERVATION_VERSION,
            "specification":{
                "id":"scap-ng.pre-alpha.observation",
                "version":"0.3.0-research",
            },
            "objects":{
                object_name:copy.deepcopy(object_payload),
            },
            "variables":{
                variable_name:copy.deepcopy(variable_payload),
            },
            "exports":{
                ITEM_EXPORT:{
                    "kind":"items",
                    "object":object_name,
                    "capability":capability,
                },
                VALUE_EXPORT:{
                    "kind":"values",
                    "variable":variable_name,
                    "datatype":"string",
                    "cardinality":"zero_or_more",
                },
            },
        }
    }


def export_ref(alias:str)->dict:
    return {"observation":BINDING_ALIAS,"export":alias}


def replace_external_refs(value:Any,object_name:str,variable_name:str,counts:Counter)->Any:
    if isinstance(value,dict):
        return {
            k:replace_external_refs(v,object_name,variable_name,counts)
            for k,v in value.items()
        }
    if isinstance(value,list):
        return [replace_external_refs(v,object_name,variable_name,counts) for v in value]
    if value==object_name:
        counts[ITEM_EXPORT]+=1
        return export_ref(ITEM_EXPORT)
    if value==variable_name:
        counts[VALUE_EXPORT]+=1
        return export_ref(VALUE_EXPORT)
    return value


def restore_export_refs(value:Any,object_name:str,variable_name:str)->Any:
    if isinstance(value,dict):
        if set(value)=={"observation","export"}:
            if value.get("observation")!=BINDING_ALIAS:
                raise ValueError("unknown Observation binding alias")
            alias=value.get("export")
            if alias==ITEM_EXPORT:
                return object_name
            if alias==VALUE_EXPORT:
                return variable_name
            raise ValueError("unknown Observation export")
        return {k:restore_export_refs(v,object_name,variable_name) for k,v in value.items()}
    if isinstance(value,list):
        return [restore_export_refs(v,object_name,variable_name) for v in value]
    return value


def validate_consumer_binding(a:dict,observation_doc:dict)->None:
    obs=observation_doc.get("observation") or {}
    binding=(a.get("observations") or {}).get(BINDING_ALIAS)
    if not isinstance(binding,dict):
        raise ValueError("consumer missing dconf Observation binding")
    if binding.get("expected_id")!=obs.get("id"):
        raise ValueError("Observation consumer expected_id mismatch")
    if binding.get("expected_version")!=obs.get("version"):
        raise ValueError("Observation consumer expected_version mismatch")
    exports=set(obs.get("exports") or {})

    def visit(value:Any):
        if isinstance(value,dict):
            if set(value)=={"observation","export"}:
                if value.get("observation")!=BINDING_ALIAS:
                    raise ValueError("unknown Observation binding alias")
                if value.get("export") not in exports:
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


def extract(doc:dict,observation_doc:dict)->tuple[dict,str,str,Counter]:
    out=copy.deepcopy(doc)
    a=out["assessment"]
    candidate=candidate_nodes(a)
    if candidate is None:
        raise ValueError("Assessment has no dconf Observation candidate")
    object_name,_,variable_name,_=candidate
    if observation_document(a)!=observation_doc:
        raise ValueError("shared dconf Observation payload differs")

    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    objects.pop(object_name)
    variables.pop(variable_name)
    if objects:
        a["objects"]=objects
    else:
        a.pop("objects",None)
    if variables:
        a["variables"]=variables
    else:
        a.pop("variables",None)

    counts=Counter()
    rewritten=replace_external_refs(a,object_name,variable_name,counts)
    a.clear()
    a.update(rewritten)
    if counts[ITEM_EXPORT]==0 or counts[VALUE_EXPORT]==0:
        raise ValueError(
            "dconf mixed-export proof requires both Item and value consumers: "
            f"{dict(counts)}"
        )
    a["observations"]={
        BINDING_ALIAS:{
            "source":OBSERVATION_PATH,
            "expected_id":OBSERVATION_ID,
            "expected_version":OBSERVATION_VERSION,
        }
    }
    validate_consumer_binding(a,observation_doc)
    return out,object_name,variable_name,counts


def flatten(extracted:dict,observation_doc:dict,object_name:str,variable_name:str)->dict:
    out=copy.deepcopy(extracted)
    a=out["assessment"]
    validate_consumer_binding(a,observation_doc)
    a.pop("observations",None)
    restored=restore_export_refs(a,object_name,variable_name)
    a.clear()
    a.update(restored)

    obs=observation_doc["observation"]
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    if object_name in objects or variable_name in variables:
        raise ValueError("name collision while flattening dconf Observation")
    objects[object_name]=copy.deepcopy(obs["objects"][object_name])
    variables[variable_name]=copy.deepcopy(obs["variables"][variable_name])
    a["objects"]=objects
    a["variables"]=variables
    return out


def observation_digest(observation_doc:dict)->str:
    raw=json.dumps(observation_doc,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def result_shape(observation_doc:dict)->dict:
    obs=observation_doc["observation"]
    digest=observation_digest(observation_doc)
    completeness={
        "logical_complete":True,
        "population_complete":True,
        "evidence_complete":True,
        "stop_reason":None,
    }
    return {
        "observation_result":{
            "execution_id":"<execution-id>",
            "observation_id":obs["id"],
            "observation_version":obs["version"],
            "observation_digest_sha256":digest,
            "target_ref":"<target-id>",
            "binding_identity":"<effective-input-binding-id>",
            "status":"complete",
            "completeness":copy.deepcopy(completeness),
            "diagnostics":[],
            "exports":{
                ITEM_EXPORT:{
                    "kind":"items",
                    "status":"complete",
                    "completeness":copy.deepcopy(completeness),
                    "item_refs":["<item-ref>"],
                    "provenance":{
                        "observation_execution_id":"<execution-id>",
                        "source_object":obs["exports"][ITEM_EXPORT]["object"],
                        "observation_digest_sha256":digest,
                    },
                },
                VALUE_EXPORT:{
                    "kind":"values",
                    "datatype":"string",
                    "status":"complete",
                    "runtime_cardinality":"many",
                    "values":["<derived-lock-directory>"],
                    "item_refs":["<source-item-ref>"],
                    "provenance":{
                        "observation_execution_id":"<execution-id>",
                        "source_variable":obs["exports"][VALUE_EXPORT]["variable"],
                        "observation_digest_sha256":digest,
                    },
                },
            },
        }
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--artifact-dir",type=Path,required=True)
    ap.add_argument("--sample-count",type=int,default=3)
    args=ap.parse_args()

    observation=None
    eligible=[]
    rejected=[]
    samples=[]
    totals=Counter()

    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment") or {}
        aid=str(a.get("id") or "")
        if a.get("mode")!="automated":
            continue
        try:
            candidate=observation_document(a)
        except ValueError as exc:
            rejected.append({"assessment_id":aid,"reason":str(exc)})
            continue
        if candidate is None:
            continue
        if observation is None:
            observation=candidate
        elif candidate!=observation:
            rejected.append({"assessment_id":aid,"reason":"shared dconf Observation payload differs"})
            continue
        try:
            extracted,object_name,variable_name,counts=extract(doc,observation)
            restored=flatten(extracted,observation,object_name,variable_name)
        except ValueError as exc:
            rejected.append({"assessment_id":aid,"reason":str(exc)})
            continue
        if restored!=doc:
            rejected.append({"assessment_id":aid,"reason":"flatten_roundtrip_mismatch"})
            continue
        totals.update(counts)
        eligible.append({
            "assessment_id":aid,
            "source":str(path),
            "original_object_name":object_name,
            "original_variable_name":variable_name,
            "export_references":dict(counts),
        })
        if len(samples)<args.sample_count:
            samples.append((aid,extracted))

    if observation is None:
        raise SystemExit("no shared dconf Observation candidate found")

    args.artifact_dir.mkdir(parents=True,exist_ok=True)
    obsdir=args.artifact_dir/"shared"/"observations"
    obsdir.mkdir(parents=True,exist_ok=True)
    (obsdir/"rhel-dconf-user-databases.observation.yaml").write_text(
        yaml.safe_dump(observation,sort_keys=False,width=120),encoding="utf-8"
    )
    (obsdir/"rhel-dconf-user-databases.observation-result.example.yaml").write_text(
        yaml.safe_dump(result_shape(observation),sort_keys=False,width=120),encoding="utf-8"
    )
    sampledir=args.artifact_dir/"consumer-samples"
    sampledir.mkdir(parents=True,exist_ok=True)
    for i,(aid,sample) in enumerate(samples,1):
        safe="".join(c if c.isalnum() or c in "._-" else "_" for c in aid)
        (sampledir/f"{i:02d}-{safe}.assessment.yaml").write_text(
            yaml.safe_dump(sample,sort_keys=False,width=120),encoding="utf-8"
        )

    report={
        "format":"scap-ng-rhel-dconf-observation-proof-0.1",
        "status":"research_only_not_accepted_design",
        "observation_id":OBSERVATION_ID,
        "observation_version":OBSERVATION_VERSION,
        "observation_digest_sha256":observation_digest(observation),
        "exports":observation["observation"]["exports"],
        "eligible_assessments":len(eligible),
        "eligible":eligible,
        "rejected":rejected,
        "export_reference_counts":dict(totals),
        "flatten_roundtrip":"passed" if eligible else "not_run",
        "semantic_claim":"source_shared_mixed_item_value_export_and_exact_flattening_only",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "eligible_assessments":len(eligible),
        "rejected":len(rejected),
        "export_reference_counts":dict(totals),
        "flatten_roundtrip":report["flatten_roundtrip"],
    },indent=2,sort_keys=True))
    if len(eligible)!=3:
        raise SystemExit(f"expected exactly three source-shared dconf consumers, found {len(eligible)}")
    if rejected:
        raise SystemExit(f"unexpected rejected dconf candidates: {rejected}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
