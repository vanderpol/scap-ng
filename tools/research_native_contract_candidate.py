#!/usr/bin/env python3
"""#235 research: one typed AST for new SCAP-NG auditor-written assertions.

Validates unambiguous authoring structure and lowers it into a small internal
semantic form shared by named-resource and population syntax. This is NOT the
normative v0.4 schema, scanner, typed collector, full six-state runtime or a
lossless SCAP 1.4 converter. The provider catalog is research-only; a real
editor would obtain a versioned, validated schema from each provider.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import yaml

ROOT=Path(__file__).resolve().parents[1]
EXAMPLES=ROOT/"research/requirements-first-language/contract-candidate/examples"
# catalog entry: selectable fields, comparable fields, identity guarantee,
# authoring acquisition parameter names, fixture-backed only unless noted.
PROVIDERS={
  "linux.mounts":(set(["mount_point","filesystem","mount_options"]),
                  set(["mount_point","filesystem","mount_options"]),False,set()),
  "windows.accounts":(set(["category","username","enabled"]),
                      set(["category","username","enabled"]),False,set()),
  "windows.registry_value":(set(["name","value"]),
                           set(["name","value"]),True,set(["hive","key","name","view"])),
  "windows.computer_role":(set(["role"]),
                           set(["role"]),True,set()),
  "windows.user_rights":(set(["right","principal"]),
                         set(["right","principal"]),False,set(["right"])),
  "apache.config_directives":(set(["name","raw_value","integer_value","source_file"]),
                              set(["name","raw_value","integer_value","source_file"]),False,set()),
  "windows.dns.zones":(set(["name","direction","directory_integration","signed",
                            "zone_signing_keys","key_signing_keys"]),
                       set(["name","direction","directory_integration","signed"]),False,set()),
  "linux.files_from_account_homes":(set(["name","mode","directory","account_id"]),
                                    set(["name","mode","directory","account_id"]),False,
                                    set(["account_filter","filename","max_depth","follow_symlinks"])),
}
OPS={"equals","not_equals","contains","at_least","between","only_these_bits","matches_regex"}
# Strict, known parent-child links: no invisible join, no implicit completeness.
RELATIONS={
  "windows.dns.zones":{
    "zone_signing_keys":{"owner":"zone_id",
                         "fields":{"zone_id","validity_hours","kind"}},
    "key_signing_keys":{"owner":"zone_id",
                        "fields":{"zone_id","validity_hours","kind"}},
  }
}
QUANTIFIERS={"each","some","none","exactly_one"}
GROUPS={"all","any"}
REGEX=re.compile(r"^\$([a-z][a-z0-9_]*)\.([a-z_][a-z0-9_]*)$")
NAME=re.compile(r"^[a-z][a-z0-9_]*$")
OCTAL=re.compile(r"^[0-7]{4}$")
class StrictLoader(yaml.SafeLoader):pass

def mapping(loader,node):
    output={}
    for k,v in node.value:
        key=loader.construct_object(k)
        if key in output:raise ValueError("duplicate YAML key "+str(key))
        output[key]=loader.construct_object(v)
    return output
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)

def fail(path,reason):
    raise ValueError(path+": "+reason)

def check_predicates(raw,known,path,scope):
    if not isinstance(raw,dict) or not raw:fail(path,"require nonempty field predicates")
    result=[]
    for field,test in raw.items():
        if field not in known:fail(path,"provider does not expose field "+str(field))
        if not isinstance(test,dict) or len(test)!=1:
            fail(path+"."+field,"exactly one predicate operation required")
        op,expected=next(iter(test.items()))
        if op not in OPS:fail(path+"."+field,"unregistered operation "+str(op))
        if op=="only_these_bits" and (not isinstance(expected,str) or not OCTAL.fullmatch(expected)):
            fail(path+"."+field,"only_these_bits requires four-digit octal string")
        if op=="between" and (not isinstance(expected,list) or len(expected)!=2 or
             not all(type(x) in (int,float) for x in expected)):
            fail(path+"."+field,"between requires two typed numeric bounds")
        if op=="at_least" and type(expected) not in (int,float):
            fail(path+"."+field,"at_least requires typed numeric threshold")
        if op=="matches_regex":
            if not isinstance(expected,str):fail(path+"."+field,"regex must be string")
            try:re.compile(expected)
            except re.error:fail(path+"."+field,"invalid regular expression")
        if isinstance(expected,str) and expected.startswith("$"):
            found=REGEX.fullmatch(expected)
            if not found:fail(path+"."+field,"references must be whole lexical path")
            alias,ref=found.groups()
            if alias not in scope or ref not in scope[alias]["fields"]:
                fail(path+"."+field,"unbound/unknown parent field reference")
        result.append({"field":field,"operator":op,"value":expected})
    return result

def check_using(raw,allowed,path,provider,scope):
    if not allowed:
        if raw:fail(path,"provider has no authoring acquisition parameters")
        return {}
    if not isinstance(raw,dict) or not raw:
        fail(path,"typed provider requires explicit using parameters")
    if set(raw)!=allowed:
        fail(path,"provider using parameters must exactly match "+repr(sorted(allowed)))
    # Fail closed for the small explicitly supported research provider inputs.
    # The previous prototype only checked top-level parameter names; that
    # would accept Gemini's incorrect home_directory selector in a typed
    # account_filter and could change the collection silently.
    if provider=="linux.files_from_account_homes":
        account=raw["account_filter"]
        if not isinstance(account,dict) or not account:
            fail(path+".account_filter","must provide nonempty account predicates")
        permitted={"uid","username","home_dir"}
        if set(account)-permitted:
            fail(path+".account_filter","unrecognized account field "+
                 repr(sorted(set(account)-permitted)))
        check_predicates(account,permitted,path+".account_filter",scope)
        regex=raw["filename"]
        if not isinstance(regex,str) or not regex:
            fail(path+".filename","must be a filename regular expression string")
        try:re.compile(regex)
        except re.error:
            fail(path+".filename","invalid filename regular expression")
        if type(raw["max_depth"]) is not int or raw["max_depth"]!=1:
            fail(path+".max_depth","only depth 1 has fixture-tested provider support")
        if type(raw["follow_symlinks"]) is not bool:
            fail(path+".follow_symlinks","must be a Boolean")
    elif provider=="windows.registry_value":
        for name in ("hive","key","name","view"):
            if not isinstance(raw[name],str) or not raw[name]:
                fail(path+"."+name,"must be a nonempty string")
        if raw["view"] not in {"32bit","64bit"}:
            fail(path+".view","registry view must be 32bit or 64bit")
    elif provider=="windows.user_rights":
        if not isinstance(raw["right"],str) or not raw["right"]:
            fail(path+".right","Windows privilege name must be nonempty")
    else:
        fail(path,"unregistered typed acquisition parameter contract for "+provider)
    return raw

def compile_check(node,path="require",scope=None,current_fields=None):
    scope=scope or {}
    if not isinstance(node,dict) or not node:fail(path,"requirement must be mapping")
    # Field assertions inside an Item-scope composite are not separate
    # Objects or States; they use the current typed resource fields.
    if set(node)=={"fields"}:
        if current_fields is None:fail(path,"fields requires current selected Item scope")
        return {"kind":"fields","predicates":check_predicates(
            node["fields"],current_fields,path+".fields",scope)}
    groups=set(node)&GROUPS
    modes=set(node)&QUANTIFIERS
    named="resource" in node
    if len(groups)+len(modes)+int(named)!=1:
        fail(path,"exactly one named resource, population or Boolean group")
    if groups:
        mode=next(iter(groups))
        if set(node)!={mode}:fail(path,"Boolean group cannot mix fields and child requirements")
        items=node[mode]
        if not isinstance(items,list) or len(items)<2:
            fail(path,"Boolean group requires at least two requirements")
        return {"kind":"logic","operator":mode,"children":[
            compile_check(c,path+"."+mode+"["+str(i)+"]",scope,current_fields) for i,c in enumerate(items)]}
    if named:
        if set(node)-{"resource","using","must"}:
            fail(path,"named resources support only resource, using, must")
        provider=node["resource"]
        if provider not in PROVIDERS:fail(path,"unknown provider "+str(provider))
        select,fields,unique,parameters=PROVIDERS[provider]
        if not unique:fail(path,"provider does not promise singleton identity")
        using=check_using(node.get("using",{}),parameters,path+".using",provider,scope)
        conditions=check_predicates(node.get("must"),fields,path+".must",scope)
        return {"kind":"collection","provider":provider,"mode":"exactly_one",
                "min_count":1,"singleton":True,"using":using,
                "where":[],"predicates":conditions,"as":None}
    mode=next(iter(modes))
    if set(node)-{mode,"where","must","minimum_resources","using","as"}:
        fail(path,"unsupported population properties")
    provider=node[mode]
    parent_ref=None
    owner_field=None
    if isinstance(provider,str) and provider.startswith("$"):
        found=REGEX.fullmatch(provider)
        if not found:fail(path,"nested resource must be whole lexical parent.field reference")
        alias,relation=found.groups()
        if alias not in scope:fail(path,"unbound parent alias "+alias)
        parent_provider=scope[alias]["provider"]
        contract=RELATIONS.get(parent_provider,{}).get(relation)
        if contract is None:fail(path,"undeclared typed child relation "+provider)
        selectable=contract["fields"]
        fields=selectable
        unique=False
        parameters=set()
        parent_ref={"alias":alias,"relation":relation}
        owner_field=contract["owner"]
    else:
        if provider not in PROVIDERS:fail(path,"unknown population resource "+str(provider))
        selectable,fields,unique,parameters=PROVIDERS[provider]
        if unique:fail(path,"singleton provider requires named resource form")
    using=check_using(node.get("using",{}),parameters,path+".using",provider,scope)
    raw_where=node.get("where")
    selection=check_predicates(raw_where,selectable,path+".where",scope) if raw_where else []
    minimum=node.get("minimum_resources",0)
    if type(minimum)!=int or minimum<0:
        fail(path,"minimum_resources must be a nonnegative integer")
    if mode!="each" and "minimum_resources" in node:
        fail(path,"minimum_resources belongs only to each")
    alias=node.get("as")
    if alias is not None and (mode=="none" or not isinstance(alias,str) or
                            not NAME.fullmatch(alias) or alias in scope):
        fail(path,"invalid lexical alias")
    local_scope=dict(scope)
    if alias is not None:
        if parent_ref is not None:
            fail(path,"a child Item alias requires a declared provider relation contract")
        local_scope[alias]={"provider":provider,"fields":fields}
    nested=None
    if mode=="none":
        if "must" in node:fail(path,"none counts selected resources; where is the prohibited predicate")
        compare=[]
    else:
        raw_must=node.get("must")
        if isinstance(raw_must,dict) and (
           set(raw_must)&(GROUPS|QUANTIFIERS|{"resource","fields"})):
            nested=compile_check(raw_must,path+".must",local_scope,fields)
            compare=[]
        else:
            compare=check_predicates(raw_must,fields,path+".must",local_scope)
    return {"kind":"collection","provider":provider,"mode":mode,
            "min_count":minimum,"singleton":False,"using":using,
            "where":selection,"predicates":compare,"as":alias,
            "nested":nested,"parent_ref":parent_ref,"owner_field":owner_field}

def compile_doc(doc):
    if not isinstance(doc,dict) or set(doc)!={"id","title","require"}:
        fail("root","exactly id, title, require")
    if not all(isinstance(doc[k],str) and doc[k] for k in ("id","title")):
        fail("root","id and title must be nonempty strings")
    return {"id":doc["id"],"title":doc["title"],
            "ast":compile_check(doc["require"])}

def read(path):
    return compile_doc(yaml.load(Path(path).read_text(),Loader=StrictLoader))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("files",nargs="*")
    args=parser.parse_args()
    paths=[Path(x) for x in args.files] if args.files else sorted(EXAMPLES.glob("*.yaml"))
    if not paths:raise SystemExit("no examples")
    for p in paths:
        ast=read(p)
        print("PASS native candidate",p.name,ast["ast"]["kind"])
    print("Compiled",len(paths),"native policy examples. Fixture-only provider catalog; no scan parity.")

if __name__=="__main__":main()
