#!/usr/bin/env python3
"""Refs #245: bounded, non-runtime observation reuse by exact acquisition scope.

No IO/OS collector, cache, XML semantics, or changing policy. This enforces
identity when handing already-collected evidence to multiple independent checks.
"""
from copy import deepcopy
from hashlib import sha256
import json

SCOPES=frozenset({"host","snapshot","execution_identity","environment",
                  "provider_version","input_fingerprint","parent_identity"})
STATUSES=frozenset({"complete","incomplete","error","not_collected",
                    "not_applicable"})

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      allow_nan=False,ensure_ascii=False)

def identity(request, scope):
    if not isinstance(request,dict) or not request or (
        not isinstance(scope,dict) or set(scope)!=SCOPES
    ):
        raise ValueError("full collection contract and bounded execution scope required")
    if any(type(v) is not str or not v for v in scope.values()):
        raise ValueError("no implicit snapshot/identity/scope defaults")
    try:
        return sha256(canonical({"request":request,"scope":scope}).encode()).hexdigest()
    except (TypeError,ValueError) as exc:
        raise ValueError("unsupported acquisition/identity payload") from exc

def freeze_observation(request, scope, evidence):
    key=identity(request,scope)
    if not isinstance(evidence,dict) or set(evidence)!={"status","items","provenance"}:
        raise ValueError("raw Items, collection status and provenance required")
    if evidence["status"] not in STATUSES or not isinstance(evidence["items"],list) or (
        not isinstance(evidence["provenance"],dict)
    ):
        raise ValueError("invalid collection envelope")
    ids=[]
    for item in evidence["items"]:
        if not isinstance(item,dict) or type(item.get("id")) is not str or not item["id"]:
            raise ValueError("Items need distinct stable source identities")
        ids.append(item["id"])
    if len(set(ids))!=len(ids):
        raise ValueError("duplicate source Item identities")
    return {"kind":"C_RESEARCH_FROZEN_OBSERVATION", "identity":key,
            "request":deepcopy(request),"scope":deepcopy(scope),
            "evidence":deepcopy(evidence),
            "evidence_sha256":sha256(canonical(evidence).encode()).hexdigest(),
            "runtime_collector_executed":False,
            "source_oval_parity_verified":False}

def read_observation(frozen, request, scope):
    if not isinstance(frozen,dict) or frozen.get("kind")!="C_RESEARCH_FROZEN_OBSERVATION" or (
        frozen.get("runtime_collector_executed") is not False or
        frozen.get("source_oval_parity_verified") is not False or
        frozen.get("identity")!=identity(request,scope) or
        frozen.get("evidence_sha256")!=sha256(canonical(frozen.get("evidence")).encode()).hexdigest() or
        frozen.get("request")!=request or frozen.get("scope")!=scope
    ):
        raise ValueError("observation cannot cross request/snapshot/provenance boundary")
    return deepcopy(frozen["evidence"])
