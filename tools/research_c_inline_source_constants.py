#!/usr/bin/env python3
"""Refs #245: source-conserving inline C literal-array authoring research.

Original OVAL constant Variable is not a separate authored C Variable.
A narrow standalone C field predicate compiles back to one typed, named
A-compatible constant Variable and equivalent explicit value quantifier.
It is not a full C assessment compiler, scanner nor six-state result proof.
The source binder retains old ID only in migration/compiler provenance.

Guardrails: strings only, equality only, finite nonempty arrays, explicit
value_match and identical source consumer scope. Anything else fails closed.
"""
from __future__ import annotations

from copy import deepcopy
import re

VALID_MATCH={"one":"only one","one_or_more":"at least one",
             "all":"all","none":"none satisfy"}
MAX_LENGTH=4096
MAX_ITEMS=256
IDENT=re.compile(r"oval:[A-Za-z0-9_.-]+:var:[A-Za-z0-9_.-]+\Z")


def lower_inline_expected_values(authoring, *, compiler_variable_identity):
    """Lower hand-authored C values WITHOUT consulting source OVAL XML."""
    if not isinstance(authoring,dict) or set(authoring)!={"field","equals","value_match"}:
        raise ValueError("one C inline predicate with explicit value_match required")
    field=authoring["field"]
    items=authoring["equals"]
    mode=authoring["value_match"]
    if type(field) is not str or not field or type(items) is not list or (
        not 1<=len(items)<=MAX_ITEMS) or (
        any(type(v) is not str or len(v)>MAX_LENGTH for v in items)) or (
        mode not in VALID_MATCH):
        raise ValueError("unsupported typed inline literal list or value matcher")
    if type(compiler_variable_identity) is not str or not IDENT.fullmatch(compiler_variable_identity):
        raise ValueError("source provenance identity must be explicitly supplied")
    native_var={"kind":"constant","datatype":"string",
                "value":deepcopy(items)}
    return {"stage":"C_RESEARCH_INLINE_STRINGS_TO_EXACT_TYPED_A_CONSTANT",
            "authoring_variable_declarations":0,
            "compiler_only_variable_count":1,
            "compiled_variables":{compiler_variable_identity:native_var},
            "compiled_comparison":{
                "field":field,"datatype":"string","operation":"equals",
                "value":{"variable":compiler_variable_identity},
                "value_match":mode},
            "source_oval_var_check":VALID_MATCH[mode],
            "source_oval_variable_id":compiler_variable_identity,
            "scanner_execution_parity_proven":False,
            "native_full_C_assessment_compilation_proven":False}


def project_source_constant_consumer(root,variable_id):
    """Research-only original-source oracle for exact one-state consumer.

    Separate from the source-independent compiler above. Never guess
    semantics for more than one consumer or a source datatype/cast not proven.
    """
    all_vars=[n for n in root.iter() if (
        n.attrib.get("id")==variable_id and
        n.tag.rsplit("}",1)[-1]=="constant_variable")]
    if len(all_vars)!=1:
        raise ValueError("one original OVAL constant Variable required")
    source=all_vars[0]
    if source.get("datatype","string")!="string":
        raise ValueError("non-string source Variable not yet proven")
    values=[n.text or "" for n in source
            if n.tag.rsplit("}",1)[-1]=="value"]
    references=[n for n in root.iter()
                if n.attrib.get("var_ref")==variable_id]
    if len(references)!=1:
        raise ValueError("shared/missing source references require separate conversion")
    entity=references[0]
    if entity.attrib.get("operation","equals")!="equals":
        raise ValueError("non-equality source use needs independent proof")
    source_mode=entity.get("var_check","all")
    reverse={v:k for k,v in VALID_MATCH.items()}
    if source_mode not in reverse:
        raise ValueError("unproven source var_check")
    authored={"field":entity.tag.rsplit("}",1)[-1],
             "equals":values,"value_match":reverse[source_mode]}
    compiled=lower_inline_expected_values(
        authored,compiler_variable_identity=variable_id)
    if (compiled["compiled_variables"][variable_id]["value"]!=values
        or compiled["source_oval_var_check"]!=source_mode):
        raise ValueError("C literal-array projection does not preserve source contract")
    return {"source_original_oval_variable_id":variable_id,
            "source_variable_comment":source.get("comment"),
            "source_entity_field":authored["field"],
            "source_var_check":source_mode,
            "C_authoring_predicate":authored,
            "A_compiled_compatibility":compiled,
            "source_runtime_semantics_proven":False}
