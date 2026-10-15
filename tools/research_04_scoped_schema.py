#!/usr/bin/env python3
"""Research-only 0.4 scoped-State requirement validator (not accepted normative schema).

Use the existing full v0.4 schema with a version-local *in-memory* research
Assessment-language variant, then expand explicit scopes and validate the
unchanged canonical full document and every native capability Test. This does
not silently alter the accepted 0.3 or proposed 0.4 JSON Schema snapshots.
"""
from copy import deepcopy
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from research_04_native_deep_content_census import (
    SHARED, ROOT_ASSESSMENT_SCHEMA, ROOT_ASSESSMENT_VALIDATOR,
    validator_for,
)
from research_04_scoped_state_require import expand

LANG_URI="https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json"

def candidate_language():
    lang=deepcopy(SHARED[LANG_URI])
    defs=lang["$defs"]
    opt=deepcopy(defs["scalar_field_predicate"])
    if opt.get("required")!=["require"]:
        raise ValueError("Unexpected v0.4 scalar State schema baseline")
    opt["required"]=[]
    defs["scoped_scalar_field_predicate"]=opt

    old=defs["state_entry"]["oneOf"]
    scalar=deepcopy(old[0])
    scalar["additionalProperties"]["oneOf"]=[
        {"$ref":"#/$defs/scoped_scalar_field_predicate"},
        {"$ref":"#/$defs/record_wrapper_predicate"},
    ]
    entries=[scalar]
    for verb in ("and","or","one","odd"):
        entries.append({
            "type":"object",
            "required":[verb],
            "properties":{
                verb:{
                    "type":"array","minItems":1,
                    "items":{"$ref":"#/$defs/state_entry"},
                },
                "state_fields_require":{"$ref":"#/$defs/paired_requirement"},
            },
            "additionalProperties":False,
        })
    defs["state_entry"]={"oneOf":entries}
    defs["test"]["properties"]["state_fields_require"]={
        "$ref":"#/$defs/paired_requirement",
    }
    defs["test"].setdefault("allOf",[]).append({
        "if":{"required":["state_fields_require"]},
        "then":{"required":["states"]},
    })
    lang["title"]="SCAP-NG 0.4 scoped State requirement research candidate"
    lang["description"]="Research overlay for Joval preview; explicit Test/group/field inheritance; not normative."
    Draft202012Validator.check_schema(lang)
    return lang

CANDIDATE_LANGUAGE=candidate_language()
REGISTRY=Registry().with_resources([
    (uri,Resource.from_contents(CANDIDATE_LANGUAGE if uri==LANG_URI else schema))
    for uri,schema in SHARED.items()
])
CANDIDATE_VALIDATOR=Draft202012Validator(
    ROOT_ASSESSMENT_SCHEMA,registry=REGISTRY
)

def fail(errors,which):
    first=next(iter(errors),None)
    if first is not None:
        raise ValueError(f"{which}: path={list(first.path)}: {first.message[:350]}")

def validate(document,cache=None):
    """Return fully-expanded native valid Assessment; never accept hidden fields."""
    if cache is None:cache={}
    fail(CANDIDATE_VALIDATOR.iter_errors(document),"scoped candidate syntax")
    explicit=expand(document)
    fail(ROOT_ASSESSMENT_VALIDATOR.iter_errors(explicit),"expanded base 0.4 schema")
    for tid,test in (explicit.get("assessment",{}).get("tests") or {}).items():
        capability=test.get("capability")
        if not capability:
            raise ValueError(f"Missing capability for native Test {tid}")
        fail(validator_for(capability,cache).iter_errors(test),
             f"native capability {capability} Test {tid}")
    return explicit
