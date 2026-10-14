#!/usr/bin/env python3
"""Research-only build-time import of a repeated Apache Object/Variable graph.

Imports are AUTHORING SOURCE sugar. The compiler expands imports into EXACTLY
the same existing SCAP-NG 0.3 Assessment definitions. No scanner scheduling,
cross-Assessment value sharing, caching, or new evaluation semantics are implied.

Fail closed on divergent definitions, ambiguous references, private leakage,
identity/version/hash mismatch, name collisions, or missing exports.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

import yaml

from prove_apache_observation import CORE_OBJECTS, CORE_VARIABLES, EXPORTS

MODULE_ID = "research.apache.httpd.discovery.source"
MODULE_VERSION = 1
MODULE_FILE = "shared/source-modules/apache-httpd-discovery.module.yaml"


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",",":"),
                                     ensure_ascii=False).encode()).hexdigest()


def extract_refs(value, kind):
    """Reference scanner, not arbitrary string replacement."""
    found = []
    def walk(node, path=()):
        if isinstance(node, list):
            for i,x in enumerate(node): walk(x,path+(i,))
        elif isinstance(node, dict):
            for k,v in node.items():
                if kind == "variables" and k == "variable" and isinstance(v,str):
                    found.append((v,path+(k,)))
                if kind == "objects" and k == "object" and isinstance(v,str):
                    found.append((v,path+(k,)))
                if (kind == "objects" and k == "in" and isinstance(v,str)
                        and isinstance(node.get("item"),str)):
                    found.append((v,path+(k,)))
                walk(v,path+(k,))
    walk(value)
    return found


def module_from_assessment(doc):
    a=doc["assessment"]
    objects=a.get("objects") or {}
    variables=a.get("variables") or {}
    if not all(n in objects for n in CORE_OBJECTS):
        raise ValueError("Missing complete Apache source Object graph")
    if not all(n in variables for n in CORE_VARIABLES):
        raise ValueError("Missing complete Apache source Variable graph")
    selected_objects={n:deepcopy(objects[n]) for n in CORE_OBJECTS}
    selected_variables={n:deepcopy(variables[n]) for n in CORE_VARIABLES}
    for n,payload in selected_objects.items():
        for ref,loc in extract_refs(payload,"objects"):
            if ref in objects and ref not in selected_objects:
                raise ValueError(f"Graph not source-closed: Object {n} -> {ref}")
        for ref,loc in extract_refs(payload,"variables"):
            if ref in variables and ref not in selected_variables:
                raise ValueError(f"Graph not source-closed: Object {n} -> {ref}")
    for n,payload in selected_variables.items():
        for ref,loc in extract_refs(payload,"variables"):
            if ref in variables and ref not in selected_variables:
                raise ValueError(f"Graph not source-closed: Variable {n} -> {ref}")
        for ref,loc in extract_refs(payload,"objects"):
            if ref in objects and ref not in selected_objects:
                raise ValueError(f"Graph not source-closed: Variable {n} -> {ref}")
    exports={}
    for source,alias in EXPORTS.items():
        v=selected_variables[source]
        exports[alias]={"type":"variable","name":source, "datatype":v.get("datatype")}
        if exports[alias]["datatype"] is None:
            raise ValueError("Cannot infer exported datatype: "+alias)
    return {"source_module":{
        "id":MODULE_ID, "version":MODULE_VERSION,
        "objects":selected_objects,
        "variables":selected_variables,
        "exports":exports,
    }}


def validated_module(module):
    if not isinstance(module,dict) or set(module)!={"source_module"}:
        raise ValueError("Invalid source module root")
    source=module["source_module"]
    if not isinstance(source,dict) or set(source)!={"id","version","objects","variables","exports"}:
        raise ValueError("Unexpected source module fields")
    if source["id"]!=MODULE_ID or source["version"]!=MODULE_VERSION:
        raise ValueError("Source module identity/version mismatch")
    objs=source["objects"]; vars=source["variables"]
    if not isinstance(objs,dict) or not isinstance(vars,dict):
        raise ValueError("Invalid source registries")
    exports=source["exports"]
    if not isinstance(exports,dict) or not exports:
        raise ValueError("Source module requires exports")
    for alias,entry in exports.items():
        if not isinstance(entry,dict) or set(entry)!={"type","name","datatype"}:
            raise ValueError("Invalid source export contract: "+str(alias))
        kind=entry["type"];name=entry["name"]
        target={"variable":vars,"object":objs}.get(kind)
        if target is None or name not in target:
            raise ValueError("Export references missing declaration: "+str(alias))
        if kind=="variable" and entry["datatype"]!=target[name].get("datatype"):
            raise ValueError("Export datatype mismatch: "+str(alias))
    return source


def external_references(doc, selected_names):
    """Only look outside the selected declarations. Never rewrite unrelated YAML."""
    a=doc["assessment"]
    outside={k:v for k,v in a.items() if k not in {"objects","variables","imports"}}
    for section in ("objects","variables"):
        outside[section]={k:v for k,v in (a.get(section) or {}).items() if k not in selected_names[section]}
    hits=[]
    for kind in ("objects","variables"):
        for name,path in extract_refs(outside,kind):
            if name in selected_names[kind]:
                hits.append((kind,name,path))
    return hits


def source_authoring(doc,module):
    """Extract module definitions, retaining output refs by original names."""
    source=validated_module(module)
    a=deepcopy(doc["assessment"])
    if "imports" in a:
        raise ValueError("Assessment already has imports")
    regs={"objects":source["objects"],"variables":source["variables"]}
    for section,expected in regs.items():
        active=a.get(section) or {}
        for name,definition in expected.items():
            if name not in active or active[name]!=definition:
                raise ValueError("Source differs or missing: "+section+"."+name)
    selected={section:set(defs) for section,defs in regs.items()}
    exported={entry["name"] for entry in source["exports"].values()}
    hits=external_references({"assessment":a},selected)
    private=[(kind,name,path) for kind,name,path in hits if name not in exported]
    if private:
        raise ValueError("Consumer accesses source-private component: "+repr(private[:3]))
    if not hits:
        raise ValueError("Unused source graph cannot improve authoring")
    for section,names in selected.items():
        for name in names:
            del a[section][name]
        if not a[section]:
            del a[section]
    a["imports"]={
        "apache_discovery":{
            "source":MODULE_FILE,
            "id":source["id"],
            "version":source["version"],
            "sha256":sha(module),
            "exports":sorted(source["exports"]),
        },
    }
    result=deepcopy(doc)
    result["assessment"]=a
    if lower_source(result,module)!=doc:
        raise ValueError("Source import compiler did not preserve 0.3 Assessment")
    return result, hits


def lower_source(authoring,module):
    """Independently expand source-only imported module, no runtime references."""
    source=validated_module(module)
    out=deepcopy(authoring)
    a=out["assessment"]
    imports=a.get("imports")
    if not isinstance(imports,dict) or set(imports)!={"apache_discovery"}:
        raise ValueError("Missing/extra source imports")
    binding=imports["apache_discovery"]
    if not isinstance(binding,dict) or set(binding)!={"source","id","version","sha256","exports"}:
        raise ValueError("Import contract not exact")
    required={"source":MODULE_FILE,"id":source["id"],"version":source["version"],
              "sha256":sha(module),"exports":sorted(source["exports"])}
    if binding!=required:
        raise ValueError("Import source identity/digest/export contract mismatch")
    del a["imports"]
    selected={section:set(source[section]) for section in ("objects","variables")}
    hits=external_references({"assessment":a},selected)
    declared_exports={item["name"] for item in source["exports"].values()}
    if any(name not in declared_exports for _,name,_ in hits):
        raise ValueError("Consumer references non-exported private source")
    if not hits:
        raise ValueError("Source import unused by consumer")
    for section in ("objects","variables"):
        registry=a.setdefault(section,{})
        if set(registry)&selected[section]:
            raise ValueError("Compiler namespace collision in "+section)
        registry.update(deepcopy(source[section]))
    return out


def collect(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        documents={}
        for path in z.namelist():
            if not path.startswith("authoring/apache_server_2-4_unix_server/") or not path.endswith(".yaml"):
                continue
            doc=yaml.safe_load(z.read(path))
            if isinstance(doc,dict) and isinstance(doc.get("assessment"),dict) and doc["assessment"].get("mode")=="automated":
                documents[path.removeprefix("authoring/")]=doc
        return documents


def run(zip_path, study):
    docs=collect(zip_path)
    candidates=[]
    for path,doc in docs.items():
        try:
            module=module_from_assessment(doc)
        except ValueError:
            continue
        candidates.append((path,doc,module))
    if not candidates:
        raise ValueError("No full legacy Apache 4-Object+11-Variable source graphs in immutable 0.3 authoring; do not claim compatibility")
    groups={}
    for path,doc,module in candidates:
        groups.setdefault(sha(module),[]).append((path,doc,module))
    chosen=max(groups.values(), key=len)
    module=chosen[0][2]
    extracted=[]
    refused=[]
    originals={}
    for path,doc,graph in chosen:
        try:
            candidate,refs=source_authoring(doc,module)
            extracted.append((path,doc,candidate,refs))
            originals[path]=doc
        except ValueError as ex:
            refused.append({"path":path,"reason":str(ex)})
    if not extracted:
        raise ValueError("No safe consumers of repeat Apache source module")
    target=study/"BUILD-TIME-IMPORT"
    source_file=target/MODULE_FILE
    source_file.parent.mkdir(parents=True,exist_ok=True)
    source_file.write_text(yaml.safe_dump(module,sort_keys=False),encoding="utf-8")
    consumers=target/"consumer-samples"
    consumers.mkdir(parents=True,exist_ok=True)
    for path,original,candidate,refs in extracted[:3]:
        stem=Path(path).stem
        (consumers/(stem+".import.RESEARCH.yaml")).write_text(
            "# Experimental authoring-only source import; compiler expands before scanning.\n"
            +yaml.safe_dump(candidate,sort_keys=False),encoding="utf-8")
        (consumers/(stem+".expanded-0.3.yaml")).write_text(
            yaml.safe_dump(lower_source(candidate,module),sort_keys=False),encoding="utf-8")
    report={
        "research_only":True,
        "runtime_semantics_modified":False,
        "source_bundle_sha256":sha(module),
        "module_objects":len(module["source_module"]["objects"]),
        "module_variables":len(module["source_module"]["variables"]),
        "public_exports":module["source_module"]["exports"],
        "identical_graph_candidates":len(chosen),
        "safe_exact_roundtrip_consumers":len(extracted),
        "refusals":refused,
        "export_consumer_references":sum(len(hits) for _,_,_,hits in extracted),
        "original_named_definitions_across_consumers":len(extracted)*(
             len(module["source_module"]["objects"])+len(module["source_module"]["variables"])),
        "authoring_definitions_with_import_module":len(module["source_module"]["objects"])+len(module["source_module"]["variables"]),
        "consumer_source_references_included":sorted(p for p,_,_,_ in extracted),
        "note":"Exact parsed 0.3 authoring expansion. No scanner runtime work-sharing or OVAL execution claim.",
    }
    (target/"RESULTS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (target/"README.md").write_text(
        "# Apache build-time source graph import — research only\n\n"
        "The shared module is **source-only**, not an Assessment, Observation or Result. "
        "The compiler expands it into each standalone Assessment before packaging.\n\n"
        f"Exactly matching consumers: **{len(extracted)}**; imported graph: "
        f"**{len(module['source_module']['objects'])} Objects** and "
        f"**{len(module['source_module']['variables'])} Variables**.\n\n"
        "Each eligible consumer independently reconstructs exactly the same parsed released 0.3 Assessment. "
        "No runtime caching, scanner scheduling, shared status or source evidence is introduced.\n\n"
        "Inspect shared/source-modules/, consumer-samples/, and RESULTS.json.\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--study",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(run(a.authoring_zip,a.study),indent=2,sort_keys=True))

if __name__=="__main__":
    main()
