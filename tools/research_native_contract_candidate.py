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
  "apache.config_directives":(set(["name","raw_value","source_file"]),
                              set(["name","raw_value","source_file"]),False,set()),
  "windows.dns.zones":(set(["name","direction","directory_integration","signed",
                            "zone_signing_keys","key_signing_keys"]),
                       set(["name","direction","directory_integration","signed"]),False,set()),
  "linux.files_from_account_homes":(set(["name","mode","directory","account_id"]),
                                    set(["name","mode","directory","account_id"]),False,
                                    set(["account_filter","filename","max_depth","follow_symlinks"])),
}
OPS={"equals","contains","at_least","between","only_these_bits","matches_regex"}
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
            if alias not in scope or ref not in scope[alias]:
                fail(path+"."+field,"unbound/unknown parent field reference")
        result.append({"field":field,"operator":op,"value":expected})
    return result

def check_using(raw,allowed,path):
    if not allowed:
        if raw:fail(path,"provider has no authoring acquisition parameters")
        return {}
    if not isinstance(raw,dict) or not raw:
        fail(path,"typed provider requires explicit using parameters")
    if set(raw)!=allowed:
        fail(path,"provider using parameters must exactly match "+repr(sorted(allowed)))
    # Deep input contract deliberately not implemented; reject nested strings
    # claiming interpolated source expressions outside lexical bound captures.
    return raw

def compile_check(node,path="require",scope=None):
    scope=scope or {}
    if not isinstance(node,dict) or not node:fail(path,"requirement must be mapping")
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
            compile_check(c,path+"."+mode+"["+str(i)+"]",scope) for i,c in enumerate(items)]}
    if named:
        if set(node)-{"resource","using","must"}:
            fail(path,"named resources support only resource, using, must")
        provider=node["resource"]
        if provider not in PROVIDERS:fail(path,"unknown provider "+str(provider))
        select,fields,unique,parameters=PROVIDERS[provider]
        if not unique:fail(path,"provider does not promise singleton identity")
        using=check_using(node.get("using",{}),parameters,path+".using")
        conditions=check_predicates(node.get("must"),fields,path+".must",scope)
        return {"kind":"collection","provider":provider,"mode":"exactly_one",
                "min_count":1,"singleton":True,"using":using,
                "where":[],"predicates":conditions,"as":None}
    mode=next(iter(modes))
    if set(node)-{mode,"where","must","minimum_resources","using","as"}:
        fail(path,"unsupported population properties")
    provider=node[mode]
    if provider not in PROVIDERS:fail(path,"unknown population resource "+str(provider))
    selectable,fields,unique,parameters=PROVIDERS[provider]
    if unique:fail(path,"singleton provider requires named resource form")
    using=check_using(node.get("using",{}),parameters,path+".using")
    raw_where=node.get("where")
    selection=check_predicates(raw_where,selectable,path+".where",scope) if raw_where else []
    minimum=node.get("minimum_resources",0)
    if type(minimum)!=int or minimum<0:
        fail(path,"minimum_resources must be a nonnegative integer")
    if mode!="each" and "minimum_resources" in node:
        fail(path,"minimum_resources belongs only to each")
    if mode=="none":
        if "must" in node:fail(path,"none counts selected resources; where is the prohibited predicate")
        compare=[]
    else:
        compare=check_predicates(node.get("must"),fields,path+".must",scope)
    alias=node.get("as")
    if alias is not None:
        if mode=="none" or not isinstance(alias,str) or not NAME.fullmatch(alias) or alias in scope:
            fail(path,"invalid lexical alias")
        # In v0 we refuse nested resource queries under a field predicate.
        # The next compiler pass must test actual parent-child correlation.
        fail(path,"as is reserved; nested population lowering not yet proven")
    return {"kind":"collection","provider":provider,"mode":mode,
            "min_count":minimum,"singleton":False,"using":using,
            "where":selection,"predicates":compare,"as":None}

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
