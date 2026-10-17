#!/usr/bin/env python3
"""#235 source of truth for research authoring provider fields/relations.

This catalog covers a limited candidate authoring surface. Its presence is
NOT proof that an actual provider exists or matches SCAP 1.4 source behavior.
No network or host collection is performed by loading the catalog.
"""
from __future__ import annotations
from pathlib import Path
import yaml

CATALOG_PATH=(Path(__file__).resolve().parents[1]/
              "research/requirements-first-language/contract-candidate/provider-catalog.v0.1.yaml")
ALLOWED_TYPES={"string","list_string","integer","boolean","posix_mode"}
ALLOWED_USING={"string","boolean","registry_view","account_predicates","regex_string","one"}

def load_catalog(path=CATALOG_PATH):
    doc=yaml.safe_load(Path(path).read_text())
    if not isinstance(doc,dict) or set(doc)!={"catalog_version","evidence_contract","providers"}:
        raise ValueError("unrecognized research provider catalog envelope")
    if doc["catalog_version"]!="0.1.0":
        raise ValueError("unsupported research catalog version")
    if not isinstance(doc["providers"],dict) or not doc["providers"]:
        raise ValueError("provider catalog is empty")
    expected={"identity","coverage","implementation","using","fields","relations"}
    for name,spec in doc["providers"].items():
        if not isinstance(name,str) or not name or not isinstance(spec,dict):
            raise ValueError("invalid provider")
        if set(spec)-expected-{"singleton"} or expected-set(spec):
            raise ValueError("unknown or missing provider contract fields for "+name)
        for field in ("identity","coverage","implementation"):
            if not isinstance(spec[field],str) or not spec[field]:
                raise ValueError("provider metadata missing for "+name)
        if "singleton" in spec and spec["singleton"] is not True:
            raise ValueError("singleton must be true or omitted")
        for key,types,allowed in (("using",spec["using"],ALLOWED_USING),
                                   ("fields",spec["fields"],ALLOWED_TYPES)):
            if not isinstance(types,dict):
                raise ValueError(name+" "+key+" must be a field mapping")
            for fld,typ in types.items():
                if not isinstance(fld,str) or not fld or typ not in allowed:
                    raise ValueError(name+" has invalid "+key+" field "+str(fld))
        if not spec["fields"]:
            raise ValueError(name+" needs at least one comparable field")
        if not isinstance(spec["relations"],dict):
            raise ValueError(name+" relations must be mapping")
        for rel,data in spec["relations"].items():
            if not isinstance(data,dict) or set(data)!={"owner_field","fields"}:
                raise ValueError(name+" relation contract invalid "+str(rel))
            if data["owner_field"] not in data["fields"]:
                raise ValueError(name+" relation owner field not declared")
            if not data["fields"] or any(t not in ALLOWED_TYPES for t in data["fields"].values()):
                raise ValueError(name+" relation field type unknown "+str(rel))
    return doc

CATALOG=load_catalog()
PROVIDERS={}
FIELD_TYPES={}
RELATIONS={}
RELATION_TYPES={}
for name,spec in CATALOG["providers"].items():
    own=set(spec["fields"])
    params=set(spec["using"])
    PROVIDERS[name]=(own,own,spec.get("singleton",False),params)
    FIELD_TYPES[name]=dict(spec["fields"])
    RELATIONS[name]={}
    RELATION_TYPES[name]={}
    for rel,data in spec["relations"].items():
        RELATIONS[name][rel]={"owner":data["owner_field"],
                              "fields":set(data["fields"])}
        RELATION_TYPES[name][rel]=dict(data["fields"])

def operator_accepts(field_type,operation,expected):
    """Refuse type/operation combinations absent from the provider dictionary.

    This is compile-time shape validation, not runtime evidence acquisition.
    bool must not be treated as a Python integer.
    """
    if operation in {"equals","not_equals"}:
        if field_type=="string":return type(expected)==str
        if field_type=="boolean":return type(expected)==bool
        if field_type in {"integer","posix_mode"}:return type(expected)==int
        return False
    if operation=="contains":
        return field_type=="list_string" and type(expected)==str
    if operation in {"at_least","between"}:
        if field_type!="integer":return False
        if operation=="at_least":return type(expected)==int
        return (isinstance(expected,list) and len(expected)==2
                and all(type(x)==int for x in expected)
                and expected[0]<=expected[1])
    if operation=="only_these_bits":
        return field_type=="posix_mode" and type(expected)==str
    if operation=="matches_regex":
        return field_type=="string" and type(expected)==str
    return False
