#!/usr/bin/env python3
"""Research #235: strict A/B adapter for Gemini's explicit DNS child relations.

This is an ALTERNATIVE PRESENTATION only. It must compile to EXACTLY the same
existing native requirement AST as a fully equivalent lexical parent scope.
Not normative; intentionally supports just the tested DNS zone/keys surface.
"""
from __future__ import annotations
from pathlib import Path
import yaml
from research_native_contract_candidate import compile_doc,RELATIONS,StrictLoader

def compile_relation_document(doc):
    if not isinstance(doc,dict) or set(doc)!={"id","title","target","filter","constraints","sub_resources"}:
        raise ValueError("explicit relation file requires six exact top-level fields")
    provider=doc["target"]
    if provider!="windows.dns.zones":
        raise ValueError("research adapter supports only typed Windows DNS zone relations")
    cons=doc["constraints"]
    if not isinstance(cons,dict) or set(cons)!={"min_count","fields"}:
        raise ValueError("zone constraints require min_count and fields")
    sub=doc["sub_resources"]
    if not isinstance(sub,list) or len(sub)<1:
        raise ValueError("sub_resources requires one or more child collections")
    nested=[{"fields":cons["fields"]}]
    seen=set()
    for child in sub:
        if not isinstance(child,dict) or set(child)!={"target","relationship","constraints"}:
            raise ValueError("child requires target, relationship and constraints")
        target=child["target"]
        rel=RELATIONS.get(provider,{}).get(target)
        if rel is None:
            raise ValueError("unknown typed parent-child relationship "+str(target))
        if child["relationship"]!=rel["owner"]:
            raise ValueError("relationship join must match trusted provider catalog")
        if target in seen:
            raise ValueError("duplicate child relation "+target)
        seen.add(target)
        rules=child["constraints"]
        if not isinstance(rules,dict) or set(rules)!={"min_count","all"}:
            raise ValueError("child constraints require min_count and all field predicates")
        nested.append({"each":"$zone."+target,
                       "minimum_resources":rules["min_count"],
                       "must":rules["all"]})
    native={"id":doc["id"],"title":doc["title"],
            "require":{"each":provider,"as":"zone","where":doc["filter"],
                      "minimum_resources":cons["min_count"],
                      "must":{"all":nested}}}
    return compile_doc(native)

def read(path):
    return compile_relation_document(yaml.load(Path(path).read_text(),Loader=StrictLoader))
