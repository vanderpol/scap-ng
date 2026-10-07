#!/usr/bin/env python3
"""Research proof for Apache shared Observation artifact extraction.

This is intentionally outside the normative 0.3 schema. It proves that a
truthless Observation artifact can own the repeated Apache discovery graph,
that consumers can reference only typed exports, and that flattening restores
the faithful converted Assessment exactly.
"""
from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

OBSERVATION_ID="shared.apache.httpd.discovery"
OBSERVATION_VERSION=1

CORE_OBJECTS=[
    "gather-unique-apache-http-installation-paths-object",
    "gather-httpd-root-files-via-apachectl-object",
    "gather-server-config-file-files-via-apachectl-object",
    "gather-include-statements-from-httpd-conf-object",
]
CORE_VARIABLES=[
    "apache-base-install-directories-unix-variable",
    "httpd-root-apachectl-v-variable",
    "filepath-httpd-root-variable",
    "server-config-file-apachectl-v-variable",
    "relative-server-config-file-variable",
    "filepath-http-conf-file-variable",
    "shell-command-check-all-include-include-optional-files-variable",
    "all-included-conf-files-from-include-refernces-in-httd-conf-variable",
    "merged-included-conf-files-from-include-refernces-in-httd-conf-variable",
    "httpd-conf-merged-included-conf-files-from-include-refernces-in-variable",
    "apache-path-httpd-or-apache2-variable",
]
EXPORTS={
    "httpd-conf-merged-included-conf-files-from-include-refernces-in-variable":
        "primary_and_included_configs",
    "apache-path-httpd-or-apache2-variable":
        "httpd_executable",
}
REVERSE_EXPORTS={alias:source for source,alias in EXPORTS.items()}
PRIVATE_NODES=set(CORE_OBJECTS+CORE_VARIABLES)


def observation_payload(a:dict)->dict|None:
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    if not all(name in objects for name in CORE_OBJECTS):
        return None
    if not all(name in variables for name in CORE_VARIABLES):
        return None
    return {
        "observation":{
            "id":OBSERVATION_ID,
            "version":OBSERVATION_VERSION,
            "objects":{
                name:copy.deepcopy(objects[name])
                for name in CORE_OBJECTS
            },
            "variables":{
                name:copy.deepcopy(variables[name])
                for name in CORE_VARIABLES
            },
            "exports":{
                alias:{
                    "source":{"variable":source},
                    "datatype":"string",
                    "cardinality":"zero_or_more",
                }
                for source,alias in EXPORTS.items()
            },
        }
    }


def export_ref(alias:str)->dict:
    return {
        "observation_export":{
            "observation":"apache",
            "export":alias,
        }
    }


def replace_external_refs(value:Any,counts:Counter)->Any:
    if isinstance(value,dict):
        return {k:replace_external_refs(v,counts) for k,v in value.items()}
    if isinstance(value,list):
        return [replace_external_refs(v,counts) for v in value]
    if isinstance(value,str) and value in PRIVATE_NODES:
        alias=EXPORTS.get(value)
        if alias is None:
            raise ValueError(f"private Observation node referenced by consumer: {value}")
        counts[alias]+=1
        return export_ref(alias)
    return value


def validate_observation(observation_doc:dict)->None:
    obs=observation_doc.get("observation")
    if not isinstance(obs,dict):
        raise ValueError("missing observation root")
    if obs.get("id")!=OBSERVATION_ID:
        raise ValueError(f"unexpected Observation id: {obs.get('id')!r}")
    if obs.get("version")!=OBSERVATION_VERSION:
        raise ValueError(f"unexpected Observation version: {obs.get('version')!r}")
    variables=obs.get("variables") or {}
    exports=obs.get("exports") or {}
    for alias,contract in exports.items():
        source=((contract or {}).get("source") or {}).get("variable")
        if source not in variables:
            raise ValueError(f"export {alias!r} references unknown Variable {source!r}")
        if contract.get("datatype")!="string":
            raise ValueError(f"export {alias!r} missing proven string datatype")
        if contract.get("cardinality")!="zero_or_more":
            raise ValueError(f"export {alias!r} missing proven cardinality")


def validate_consumer_binding(a:dict,observation_doc:dict)->None:
    imports=a.get("observations") or {}
    apache=imports.get("apache")
    if not isinstance(apache,dict):
        raise ValueError("consumer missing observations.apache binding")
    obs=observation_doc["observation"]
    if apache.get("expected_id")!=obs["id"]:
        raise ValueError("Observation id binding mismatch")
    if apache.get("expected_version")!=obs["version"]:
        raise ValueError("Observation version binding mismatch")

    exports=set(obs.get("exports") or {})

    def visit(value:Any):
        if isinstance(value,dict):
            if set(value)=={"observation_export"}:
                ref=value["observation_export"]
                if not isinstance(ref,dict):
                    raise ValueError("malformed observation_export reference")
                if ref.get("observation")!="apache":
                    raise ValueError(f"unknown Observation alias: {ref.get('observation')!r}")
                alias=ref.get("export")
                if alias not in exports:
                    raise ValueError(f"unknown Observation export: {alias!r}")
                return
            for child in value.values():
                visit(child)
        elif isinstance(value,list):
            for child in value:
                visit(child)
        elif isinstance(value,str) and value in PRIVATE_NODES:
            raise ValueError(f"consumer retains private Observation node reference: {value}")
    visit(a)


def extract(doc:dict,observation_doc:dict)->tuple[dict,Counter]:
    out=copy.deepcopy(doc)
    a=out["assessment"]
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    for name in CORE_OBJECTS:
        objects.pop(name,None)
    for name in CORE_VARIABLES:
        variables.pop(name,None)
    if objects:
        a["objects"]=objects
    else:
        a.pop("objects",None)
    if variables:
        a["variables"]=variables
    else:
        a.pop("variables",None)

    counts=Counter()
    rewritten=replace_external_refs(a,counts)
    a.clear()
    a.update(rewritten)
    a["observations"]={
        "apache":{
            "source":"../../shared/observations/apache-httpd-discovery.observation.yaml",
            "expected_id":OBSERVATION_ID,
            "expected_version":OBSERVATION_VERSION,
        }
    }
    validate_consumer_binding(a,observation_doc)
    return out,counts


def restore_export_refs(value:Any,observation_doc:dict)->Any:
    if isinstance(value,dict):
        if set(value)=={"observation_export"}:
            ref=value["observation_export"]
            if not isinstance(ref,dict) or ref.get("observation")!="apache":
                raise ValueError(f"invalid observation export ref: {ref!r}")
            alias=ref.get("export")
            source=REVERSE_EXPORTS.get(alias)
            if source is None:
                raise ValueError(f"unknown observation export: {alias!r}")
            return source
        return {k:restore_export_refs(v,observation_doc) for k,v in value.items()}
    if isinstance(value,list):
        return [restore_export_refs(v,observation_doc) for v in value]
    return value


def flatten(extracted:dict,observation_doc:dict)->dict:
    out=copy.deepcopy(extracted)
    a=out["assessment"]
    validate_consumer_binding(a,observation_doc)
    a.pop("observations",None)
    restored=restore_export_refs(a,observation_doc)
    a.clear()
    a.update(restored)

    obs=observation_doc["observation"]
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    for name,payload in obs["objects"].items():
        if name in objects:
            raise ValueError(f"Object collision while flattening: {name}")
        objects[name]=copy.deepcopy(payload)
    for name,payload in obs["variables"].items():
        if name in variables:
            raise ValueError(f"Variable collision while flattening: {name}")
        variables[name]=copy.deepcopy(payload)
    a["objects"]=objects
    a["variables"]=variables
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--artifact-dir",type=Path,required=True)
    args=ap.parse_args()

    observation_doc=None
    eligible=[]
    rejected=[]
    export_counts=Counter()
    sample_written=False

    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment") or {}
        aid=str(a.get("id") or "")
        if a.get("mode")!="automated" or (".SV-" not in aid and not aid.startswith("SV-")):
            continue

        candidate=observation_payload(a)
        if candidate is None:
            continue
        if observation_doc is None:
            observation_doc=candidate
            validate_observation(observation_doc)
        elif candidate!=observation_doc:
            rejected.append({"assessment_id":aid,"reason":"observation_payload_differs"})
            continue

        try:
            extracted,counts=extract(doc,observation_doc)
            roundtrip=flatten(extracted,observation_doc)
        except ValueError as exc:
            rejected.append({"assessment_id":aid,"reason":str(exc)})
            continue
        if roundtrip!=doc:
            rejected.append({"assessment_id":aid,"reason":"flatten_roundtrip_mismatch"})
            continue

        export_counts.update(counts)
        eligible.append({
            "assessment_id":aid,
            "source":str(path),
            "export_references":dict(counts),
        })

        if not sample_written:
            args.artifact_dir.mkdir(parents=True,exist_ok=True)
            (args.artifact_dir/"sample-consumer.assessment.yaml").write_text(
                yaml.safe_dump(extracted,sort_keys=False,width=120),
                encoding="utf-8",
            )
            sample_written=True

    if observation_doc is None:
        raise SystemExit("no common Apache Observation candidate found")

    args.artifact_dir.mkdir(parents=True,exist_ok=True)
    observation_path=args.artifact_dir/"apache-httpd-discovery.observation.yaml"
    observation_path.write_text(
        yaml.safe_dump(observation_doc,sort_keys=False,width=120),
        encoding="utf-8",
    )

    report={
        "format":"scap-ng-apache-observation-proof-0.1",
        "status":"research_only_not_accepted_design",
        "observation_id":OBSERVATION_ID,
        "observation_version":OBSERVATION_VERSION,
        "objects":len(CORE_OBJECTS),
        "variables":len(CORE_VARIABLES),
        "exports":observation_doc["observation"]["exports"],
        "eligible_assessments":len(eligible),
        "eligible":eligible,
        "rejected":rejected,
        "export_reference_counts":dict(export_counts),
        "flatten_roundtrip":"passed" if eligible else "not_run",
        "consumer_private_scope":"passed" if eligible else "not_run",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "eligible_assessments":len(eligible),
        "rejected":len(rejected),
        "objects":len(CORE_OBJECTS),
        "variables":len(CORE_VARIABLES),
        "exports":list(observation_doc["observation"]["exports"]),
        "export_reference_counts":dict(export_counts),
        "flatten_roundtrip":report["flatten_roundtrip"],
    },indent=2,sort_keys=True))
    if len(eligible)<10:
        raise SystemExit("unexpectedly small Apache Observation proof class")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
