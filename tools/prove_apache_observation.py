#!/usr/bin/env python3
"""Research proof for Apache shared Observation extraction and exact flattening."""
from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

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
    "httpd-conf-merged-included-conf-files-from-include-refernces-in-variable":"primary_and_included_configs",
    "apache-path-httpd-or-apache2-variable":"httpd_executable",
}
REVERSE_EXPORTS={v:k for k,v in EXPORTS.items()}
OBSERVATION_ID="shared.apache.httpd.discovery"
OBSERVATION_VERSION=1
OBSERVATION_PATH="../../shared/observations/apache-httpd-discovery.observation.yaml"


def export_ref(alias:str)->dict:
    return {"observation":"apache","export":alias}


def replace_external_refs(value:Any, counts:Counter)->Any:
    if isinstance(value,dict):
        return {k:replace_external_refs(v,counts) for k,v in value.items()}
    if isinstance(value,list):
        return [replace_external_refs(v,counts) for v in value]
    if isinstance(value,str) and value in set(CORE_OBJECTS+CORE_VARIABLES):
        if value not in EXPORTS:
            raise ValueError(f"private Observation node referenced by consumer: {value}")
        alias=EXPORTS[value]
        counts[alias]+=1
        return export_ref(alias)
    return value


def restore_export_refs(value:Any)->Any:
    if isinstance(value,dict):
        if set(value)=={"observation","export"}:
            if value.get("observation")!="apache":
                raise ValueError(f"unknown Observation binding: {value!r}")
            alias=value.get("export")
            if alias not in REVERSE_EXPORTS:
                raise ValueError(f"unknown Observation export: {alias!r}")
            return REVERSE_EXPORTS[alias]
        return {k:restore_export_refs(v) for k,v in value.items()}
    if isinstance(value,list):
        return [restore_export_refs(v) for v in value]
    return value


def validate_observation_document(observation_doc:dict)->None:
    obs=observation_doc.get("observation")
    if not isinstance(obs,dict):
        raise ValueError("missing observation root")
    if obs.get("id")!=OBSERVATION_ID:
        raise ValueError("Observation id mismatch")
    if obs.get("version")!=OBSERVATION_VERSION:
        raise ValueError("Observation version mismatch")
    variables=obs.get("variables") or {}
    exports=obs.get("exports") or {}
    for alias,contract in exports.items():
        if not isinstance(contract,dict):
            raise ValueError(f"invalid Observation export contract: {alias}")
        if contract.get("kind")!="values":
            raise ValueError(f"unsupported Observation export kind: {alias}")
        source=contract.get("variable")
        if source not in variables:
            raise ValueError(f"Observation export references unknown Variable: {alias}")
        if not isinstance(contract.get("datatype"),str) or not contract["datatype"]:
            raise ValueError(f"Observation export missing datatype: {alias}")
        if contract.get("cardinality") not in {
            "one","zero_or_one","one_or_more","zero_or_more"
        }:
            raise ValueError(f"Observation export has invalid cardinality: {alias}")


def validate_consumer_binding(a:dict,observation_doc:dict)->None:
    validate_observation_document(observation_doc)
    bindings=a.get("observations") or {}
    binding=bindings.get("apache")
    if not isinstance(binding,dict):
        raise ValueError("consumer missing apache Observation binding")
    obs=observation_doc["observation"]
    if binding.get("expected_id")!=obs["id"]:
        raise ValueError("Observation consumer expected_id mismatch")
    if binding.get("expected_version")!=obs["version"]:
        raise ValueError("Observation consumer expected_version mismatch")
    exports=set(obs.get("exports") or {})

    def visit(value:Any):
        if isinstance(value,dict):
            if set(value)=={"observation","export"}:
                if value.get("observation")!="apache":
                    raise ValueError("unknown Observation binding alias")
                if value.get("export") not in exports:
                    raise ValueError("unknown Observation export")
                return
            for child in value.values():
                visit(child)
        elif isinstance(value,list):
            for child in value:
                visit(child)
        elif isinstance(value,str) and value in set(CORE_OBJECTS+CORE_VARIABLES):
            raise ValueError(f"consumer retains private Observation node: {value}")
    for key,value in a.items():
        if key!="observations":
            visit(value)


def observation_document(a:dict)->dict|None:
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
            "specification":{
                "id":"scap-ng.pre-alpha.observation",
                "version":"0.3.0-research",
            },
            "objects":{name:copy.deepcopy(objects[name]) for name in CORE_OBJECTS},
            "variables":{name:copy.deepcopy(variables[name]) for name in CORE_VARIABLES},
            "exports":{
                alias:{
                    "kind":"values",
                    "variable":node,
                    "datatype":"string",
                    "cardinality":"zero_or_more",
                }
                for node,alias in EXPORTS.items()
            },
        }
    }


def extract(doc:dict,observation_doc:dict)->tuple[dict,Counter]:
    out=copy.deepcopy(doc)
    a=out["assessment"]
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    for name in CORE_OBJECTS:
        objects.pop(name)
    for name in CORE_VARIABLES:
        variables.pop(name)
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
            "source":OBSERVATION_PATH,
            "expected_id":OBSERVATION_ID,
            "expected_version":OBSERVATION_VERSION,
        }
    }
    validate_consumer_binding(a,observation_doc)
    return out,counts


def flatten(extracted:dict,observation_doc:dict)->dict:
    out=copy.deepcopy(extracted)
    a=out["assessment"]
    validate_consumer_binding(a,observation_doc)
    a.pop("observations",None)
    restored=restore_export_refs(a)
    a.clear()
    a.update(restored)

    obs=observation_doc["observation"]
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    objects.update(copy.deepcopy(obs["objects"]))
    variables.update(copy.deepcopy(obs["variables"]))
    a["objects"]=objects
    a["variables"]=variables
    return out


def result_shape(observation_doc:dict)->dict:
    """Illustrative result contract; values/items intentionally omitted."""
    obs=observation_doc["observation"]
    return {
        "observation_result":{
            "observation_id":obs["id"],
            "observation_version":obs["version"],
            "target":{
                "id":"<target-id>",
            },
            "status":"complete",
            "exports":{
                alias:{
                    "kind":contract["kind"],
                    "datatype":contract["datatype"],
                    "cardinality":contract["cardinality"],
                    "status":"complete",
                    "values":"<materialized-or-referenced-values>",
                    "provenance":"<source-object-variable-item-lineage>",
                }
                for alias,contract in obs["exports"].items()
            },
        }
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--artifact-dir",type=Path)
    ap.add_argument("--sample-count",type=int,default=3)
    args=ap.parse_args()

    observation=None
    eligible=[]
    export_counts=Counter()
    rejected=[]
    samples=[]
    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment") or {}
        aid=str(a.get("id") or "")
        if a.get("mode")!="automated" or (".SV-" not in aid and not aid.startswith("SV-")):
            continue
        candidate=observation_document(a)
        if candidate is None:
            continue
        if observation is None:
            observation=candidate
        elif candidate != observation:
            rejected.append({"assessment_id":aid,"reason":"core_observation_payload_differs"})
            continue
        try:
            extracted,counts=extract(doc,observation)
            roundtrip=flatten(extracted,observation)
        except ValueError as exc:
            rejected.append({"assessment_id":aid,"reason":str(exc)})
            continue
        if roundtrip != doc:
            rejected.append({"assessment_id":aid,"reason":"flatten_roundtrip_mismatch"})
            continue
        export_counts.update(counts)
        eligible.append({
            "assessment_id":aid,
            "source":str(path),
            "export_references":dict(counts),
        })
        if len(samples)<args.sample_count:
            samples.append((aid,extracted))

    if observation is None:
        raise SystemExit("no common Apache Observation candidate found")

    report={
        "format":"scap-ng-apache-observation-extraction-proof-0.1",
        "status":"research_only_not_accepted_design",
        "observation_id":OBSERVATION_ID,
        "observation_version":OBSERVATION_VERSION,
        "observation_objects":len(CORE_OBJECTS),
        "observation_variables":len(CORE_VARIABLES),
        "exports":observation["observation"]["exports"],
        "eligible_assessments":len(eligible),
        "eligible":eligible,
        "rejected":rejected,
        "export_reference_counts":dict(export_counts),
        "flatten_roundtrip":"passed" if eligible else "not_run",
        "semantic_claim":"source_graph_extraction_and_exact_flattening_only",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    artifact_dir=args.artifact_dir or args.output.parent
    obs_dir=artifact_dir/"shared"/"observations"
    obs_dir.mkdir(parents=True,exist_ok=True)
    (obs_dir/"apache-httpd-discovery.observation.yaml").write_text(
        yaml.safe_dump(observation,sort_keys=False),
        encoding="utf-8",
    )
    (obs_dir/"apache-httpd-discovery.observation-result.example.yaml").write_text(
        yaml.safe_dump(result_shape(observation),sort_keys=False),
        encoding="utf-8",
    )
    sample_dir=artifact_dir/"consumer-samples"
    sample_dir.mkdir(parents=True,exist_ok=True)
    for ordinal,(aid,sample) in enumerate(samples,1):
        safe="".join(c if c.isalnum() or c in "._-" else "_" for c in aid)
        (sample_dir/f"{ordinal:02d}-{safe}.assessment.yaml").write_text(
            yaml.safe_dump(sample,sort_keys=False),
            encoding="utf-8",
        )

    print(json.dumps({
        "eligible_assessments":len(eligible),
        "rejected":rejected,
        "observation_objects":len(CORE_OBJECTS),
        "observation_variables":len(CORE_VARIABLES),
        "exports":list(observation["observation"]["exports"]),
        "export_reference_counts":dict(export_counts),
        "flatten_roundtrip":report["flatten_roundtrip"],
        "artifact_dir":str(artifact_dir),
    },indent=2))
    if len(eligible)<10:
        raise SystemExit("unexpectedly small Apache Observation proof class")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
