#!/usr/bin/env python3
"""Draft 0.4 generator sweep for every supported reviewed OVAL capability.

No 0.3 runtime fallback is allowed: metadata extraction may reuse the source
converter implementation, but all output URLs and authored native shapes must
be strictly version-local 0.4.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from generate_capability_schema_v04 import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPINGS=ROOT/"schema"/"v0.4.0"/"capability-mappings"/"supported"


def recursive_refs(node):
    if isinstance(node,dict):
        for k,v in node.items():
            if k=="$ref":
                yield v
            else:
                yield from recursive_refs(v)
    elif isinstance(node,list):
        for x in node:
            yield from recursive_refs(x)


def audit_all():
    mappings=sorted(MAPPINGS.glob("*.json"))
    if len(mappings)!=100:
        raise AssertionError(f"Expected 100 native supported mappings; found {len(mappings)}")
    metrics=Counter()
    errors=[]
    individual=[]
    for path in mappings:
        label=path.stem
        try:
            mapping=json.loads(path.read_text(encoding="utf-8"))
            if mapping.get("specification_version")!="0.4.0":
                raise ValueError("Mapping is not versioned 0.4.0")
            schema=generate(mapping,ROOT)
            Draft202012Validator.check_schema(schema)
            if schema["$id"] != (
                "https://scap-ng.dev/schema/v0.4.0/generated/capabilities/"
                + mapping["capability"]+".schema.json"
            ):
                raise ValueError("Generated schema ID is not the native 0.4 version")
            for ref in recursive_refs(schema):
                if "/v0.3.0/" in ref or "/v0.2.0/" in ref or "/v0.1.0/" in ref:
                    raise ValueError(f"Foreign SCAP-NG schema version: {ref}")
                if ref.startswith("https://scap-ng.dev/") and not ref.startswith(
                    "https://scap-ng.dev/schema/v0.4.0/"
                ):
                    raise ValueError(f"External/unknown versioned schema URL: {ref}")
            defs=schema["$defs"]
            if "require" not in defs["test"]["required"]:
                raise ValueError("No required native Test requirement")
            for legacy in ("existence","match"):
                if legacy in defs["test"]["required"] or legacy in defs["test"]["properties"]:
                    raise ValueError(f"Legacy Test cardinality still accepted: {legacy}")
            if "state" in defs:
                raise ValueError("Legacy named State wrapper exposed by draft")
            select=defs.get("object",{}).get("properties",{}).get("select",{}).get("properties",{})
            source_selected=set(mapping.get("native",{}).get("selector_map",{}).values())
            if not set(select)<=source_selected:
                raise ValueError("Generated Object selector not in reviewed native map")
            metrics["generated"]+=1
            metrics["selectors"]+=len(select)
            state=defs.get("state_predicate",{})
            if isinstance(state,dict):
                metrics["named_state_predicates"]+=len(state.get("oneOf",[]))
            if mapping.get("native",{}).get("record_state_fields"):
                metrics["capabilities_with_records"]+=1
            individual.append({
                "capability":mapping["capability"],
                "selector_fields":sorted(select),
                "state_field_count":len(state.get("oneOf",[])) if isinstance(state,dict) else 0,
            })
        except Exception as exc:
            metrics["failed"]+=1
            errors.append({"capability":label,"error":str(exc)})
    return {
        "status":"pre-alpha structural generator sweep only",
        "counts":dict(metrics),
        "failures":errors,
        "supported_capabilities_seen":len(mappings),
        "successful_capabilities":individual,
        "limitations":[
            "This checks generation and schema syntax for all 100 supported 0.4 mappings, not 100 live-target native Test executions.",
            "Capability selector/type narrowing is partial; semantic value enums, collector WMI/cmdlet selection and complex Objects need additional gate coverage.",
            "Full 0.4 Assessment source migration/deep-validation is a separate gate.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=audit_all()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("CAPABILITY_04_GENERATOR_AUDIT",json.dumps({
        "seen":result["supported_capabilities_seen"],
        "counts":result["counts"],
        "failures":result["failures"][:30],
    },sort_keys=True),flush=True)
    if result["failures"]:
        raise SystemExit(f"{len(result['failures'])} supported v0.4 mappings failed generation")


if __name__=="__main__":
    main()
