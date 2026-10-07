#!/usr/bin/env python3
"""Research proof for compile-time Apache observation-module extraction."""
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
    "filepath-httpd-root-variable":"httpd_root",
    "filepath-http-conf-file-variable":"primary_config",
    "httpd-conf-merged-included-conf-files-from-include-refernces-in-variable":"primary_and_included_configs",
    "apache-path-httpd-or-apache2-variable":"httpd_executable",
}
REVERSE_EXPORTS={v:k for k,v in EXPORTS.items()}

def replace_external_refs(value:Any, counts:Counter)->Any:
    if isinstance(value,dict):
        return {k:replace_external_refs(v,counts) for k,v in value.items()}
    if isinstance(value,list):
        return [replace_external_refs(v,counts) for v in value]
    if isinstance(value,str) and value in set(CORE_OBJECTS+CORE_VARIABLES):
        if value not in EXPORTS:
            raise ValueError(f"private module node referenced by consumer: {value}")
        alias=EXPORTS[value]
        counts[alias]+=1
        return {"module_export":f"apache.{alias}"}
    return value

def restore_export_refs(value:Any)->Any:
    if isinstance(value,dict):
        if set(value)=={"module_export"}:
            ref=value["module_export"]
            prefix="apache."
            if not isinstance(ref,str) or not ref.startswith(prefix):
                raise ValueError(f"invalid module export ref: {ref!r}")
            alias=ref[len(prefix):]
            if alias not in REVERSE_EXPORTS:
                raise ValueError(f"unknown module export: {alias!r}")
            return REVERSE_EXPORTS[alias]
        return {k:restore_export_refs(v) for k,v in value.items()}
    if isinstance(value,list):
        return [restore_export_refs(v) for v in value]
    return value

def module_payload(a:dict)->dict|None:
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    if not all(name in objects for name in CORE_OBJECTS):
        return None
    if not all(name in variables for name in CORE_VARIABLES):
        return None
    return {
        "id":"scap-ng.apache.httpd.discovery",
        "version":1,
        "objects":{name:copy.deepcopy(objects[name]) for name in CORE_OBJECTS},
        "variables":{name:copy.deepcopy(variables[name]) for name in CORE_VARIABLES},
        "exports":{
            alias:{"node":node,"datatype":"string","cardinality":"zero_or_more"}
            for node,alias in EXPORTS.items()
        },
    }

def extract(doc:dict,module:dict)->tuple[dict,Counter]:
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

    # Rewrite only consumer references. Module internals were removed first.
    counts=Counter()
    rewritten=replace_external_refs(a,counts)
    a.clear()
    a.update(rewritten)
    a["imports"]={
        "apache":{
            "module":"scap-ng.apache.httpd.discovery",
            "expected_version":1,
        }
    }
    return out,counts

def flatten(extracted:dict,module:dict)->dict:
    out=copy.deepcopy(extracted)
    a=out["assessment"]
    a.pop("imports",None)
    restored=restore_export_refs(a)
    a.clear()
    a.update(restored)
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    objects.update(copy.deepcopy(module["objects"]))
    variables.update(copy.deepcopy(module["variables"]))
    a["objects"]=objects
    a["variables"]=variables
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    module=None
    eligible=[]
    export_counts=Counter()
    rejected=[]
    for path in sorted(args.root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment") or {}
        aid=str(a.get("id") or "")
        if a.get("mode")!="automated" or (".SV-" not in aid and not aid.startswith("SV-")):
            continue
        candidate=module_payload(a)
        if candidate is None:
            continue
        if module is None:
            module=candidate
        elif candidate != module:
            rejected.append({"assessment_id":aid,"reason":"core_module_payload_differs"})
            continue
        try:
            extracted,counts=extract(doc,module)
            roundtrip=flatten(extracted,module)
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

    if module is None:
        raise SystemExit("no common Apache module candidate found")

    report={
        "format":"scap-ng-apache-module-extraction-proof-0.1",
        "status":"research_only_not_accepted_design",
        "module_id":module["id"],
        "module_objects":len(CORE_OBJECTS),
        "module_variables":len(CORE_VARIABLES),
        "exports":module["exports"],
        "eligible_assessments":len(eligible),
        "eligible":eligible,
        "rejected":rejected,
        "export_reference_counts":dict(export_counts),
        "flatten_roundtrip":"passed" if eligible else "not_run",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (args.output.parent/"apache-httpd-discovery.module.json").write_text(
        json.dumps(module,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        "eligible_assessments":len(eligible),
        "rejected":rejected,
        "module_objects":len(CORE_OBJECTS),
        "module_variables":len(CORE_VARIABLES),
        "exports":list(module["exports"]),
        "export_reference_counts":dict(export_counts),
        "flatten_roundtrip":report["flatten_roundtrip"],
    },indent=2))
    if len(eligible)<10:
        raise SystemExit("unexpectedly small Apache module proof class")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
