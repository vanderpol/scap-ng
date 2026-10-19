#!/usr/bin/env python3
"""Refs #245: immutable cross-Rule observation references (C research only).

Resolve version-AND-digest-pinned acquisition contracts into the unified C
frontend. This is NOT a signed catalog, runtime cache, OS collector or source
OVAL equivalence guarantee.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
import re

REF=re.compile(r"shared/(?:[a-z][a-z0-9_-]*/)*[a-z][a-z0-9_-]*@[0-9a-z][0-9a-z._-]*\Z")
DIGEST=re.compile(r"[0-9a-f]{64}\Z")

def catalog_digest(entry):
    if not isinstance(entry,dict) or set(entry) not in ({"from"},{"from","source_object"}):
        raise ValueError("catalog entry must contain one from and optional source identity")
    frm=entry["from"]
    if not isinstance(frm,dict) or len(frm)!=1:
        raise ValueError("catalog from requires exactly one collection capability")
    capability,arguments=next(iter(frm.items()))
    if type(capability) is not str or not capability or not isinstance(arguments,dict):
        raise ValueError("catalog acquisition arguments must be an explicit mapping")
    if "source_object" in entry and (
        type(entry["source_object"]) is not str or not entry["source_object"]
    ):
        raise ValueError("source Object identity must be explicit")
    try:
        payload=json.dumps(entry,sort_keys=True,separators=(",",":"),
                           ensure_ascii=False,allow_nan=False)
    except (TypeError,ValueError) as exc:
        raise ValueError("noncanonical or unserializable catalog acquisition") from exc
    return sha256(payload.encode("utf-8")).hexdigest()

def resolve_external_observations(document,catalog):
    if not isinstance(document,dict) or not isinstance(document.get("observations"),dict):
        raise ValueError("C document must declare named observations")
    if not isinstance(catalog,dict):
        raise ValueError("explicit available catalog required")
    out=deepcopy(document)
    dependencies=[]
    for alias,entry in out["observations"].items():
        if not isinstance(entry,dict):
            raise ValueError("observation entry must be a mapping")
        if "use" not in entry:
            if set(entry) not in ({"from"},{"from","source_object"}):
                raise ValueError("invalid local observation declaration")
            continue
        if set(entry)!={"use","sha256"}:
            raise ValueError("catalog observation requires use and immutable digest only")
        ref,expected=entry["use"],entry["sha256"]
        if type(ref) is not str or len(ref)>255 or not REF.fullmatch(ref):
            raise ValueError("only version-pinned, namespaced shared references supported")
        if type(expected) is not str or not DIGEST.fullmatch(expected):
            raise ValueError("full lowercase SHA-256 must be explicitly pinned")
        source=catalog.get(ref)
        if source is None:
            raise ValueError("unresolved pinned shared observation")
        actual=catalog_digest(source)
        if actual!=expected:
            raise ValueError("shared observation contract digest mismatch")
        out["observations"][alias]=deepcopy(source)
        dependencies.append({"observation_alias":alias,"ref":ref,"sha256":actual})
    return {
        "stage":"C_RESEARCH_SHARED_CATALOG_RESOLVER_NO_SCANNER",
        "resolved_C_ast":out,"pinned_catalog_dependencies":dependencies,
        "source_content_hashes_verified":True,
        "catalog_signature_verified":False,
        "cross_rule_runtime_collection_sharing_verified":False,
        "source_oval_parity_verified":False,
    }

def compile_c_pinned_catalog(document,catalog,*,source_documents=None):
    """Compile resolved C through the established single native-A frontend."""
    resolved=resolve_external_observations(document,catalog)
    from research_c_unified_compiler import compile_c_unified
    compiled=compile_c_unified(resolved["resolved_C_ast"],
                               source_documents=source_documents)
    return {
        "stage":"C_RESEARCH_CATALOG_TO_UNIFIED_A_NO_SCANNER",
        "compiled":compiled,
        "catalog_dependencies":resolved["pinned_catalog_dependencies"],
        "catalog_signature_verified":False,
        "cross_rule_runtime_collection_sharing_verified":False,
        "source_oval_parity_verified":False,
    }
