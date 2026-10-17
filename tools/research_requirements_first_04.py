#!/usr/bin/env python3
"""Research prototype grammar validator for SCAP-NG requirements-first YAML.

This is NOT a scanner, runtime evaluator, adopted schema, approved typed
provider catalog, or proof that legacy SCAP 1.4 converts losslessly.
It deliberately fails closed on invalid authored structure and undefined
scoped references, while keeping provider execution semantics out of scope.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import yaml

ROOT=Path(__file__).resolve().parents[1]
SAMPLES=ROOT/'research/requirements-first-language/examples'
QUANTIFIERS={'every','some','none','exactly_one','one_matching'}
GROUPS={'all','any'}
OPS={'equals','not_equals','equals_ignore_case','matches_regex',
     'contains','one_of','not_in','at_least','at_most','between','has_none_of'}
RESOURCES={'linux.mounts','linux.accounts','linux.files',
           'windows.registry_values','windows.computer',
           'windows.user_right_assignments','apache.loaded_directives',
           'windows.dns.zones','windows.time_source'}
FIELDS={'where','must','using','as','if_empty'}
SPECIAL={'if','manual'}
PROHIBITED={'object','state','test','evaluate','datatype','matching_items',
            'matching_records','state_fields_presence','all_state_fields_exist'}
REFERENCE=re.compile(r'\$([a-z][a-z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_.]*)')
IDENTIFIER=re.compile(r'^[a-z][a-z0-9_]*$')

class Loader(yaml.SafeLoader): pass

def no_duplicate(loader,node):
    loader.flatten_mapping(node)
    out={}
    for k,v in node.value:
        key=loader.construct_object(k)
        if key in out: raise ValueError(f'YAML duplicate key {key!r}, line {k.start_mark.line+1}')
        out[key]=loader.construct_object(v)
    return out
Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,no_duplicate)

def fail(path,msg): raise ValueError(f'{path}: {msg}')

def links(value,scope,inputs,path):
    if isinstance(value,dict):
        for key,v in value.items(): links(v,scope,inputs,path+'.'+str(key))
    elif isinstance(value,list):
        for i,v in enumerate(value):links(v,scope,inputs,path+'['+str(i)+']')
    elif isinstance(value,str):
        for m in REFERENCE.finditer(value):
            source=m.group(1)
            if source=='site':
                allowed=inputs.get('site',{})
                if m.group(2).split('.')[0] not in allowed:
                    fail(path,'undeclared site input '+m.group(0))
            elif source not in scope:
                fail(path,'unbound lexical variable '+m.group(0))

def predicates(value,path,scope,inputs):
    if not isinstance(value,dict) or not value:fail(path,'predicate must be a nonempty mapping')
    for field,condition in value.items():
        if field in PROHIBITED: fail(path,'deprecated OVAL-shaped field '+field)
        if not isinstance(field,str) or not field:fail(path,'bad field name')
        if not isinstance(condition,dict) or len(condition)!=1:
            fail(path+'.'+str(field),'exactly one operator required')
        op,param=next(iter(condition.items()))
        if op not in OPS:fail(path+'.'+str(field),'unknown operation '+str(op))
        if op=='between' and (not isinstance(param,list) or len(param)!=2):
            fail(path+'.'+str(field),'between expects exactly two bounds')
        if op in {'one_of','not_in','has_none_of'} and (not isinstance(param,list) or not param):
            fail(path+'.'+str(field),op+' requires a nonempty list')
        if op in {'matches_regex'} and not isinstance(param,str):
            fail(path+'.'+str(field),'regex must be string')
        links(param,scope,inputs,path+'.'+str(field))

def assertion(value,path,scope,inputs):
    if not isinstance(value,dict) or not value:fail(path,'must be nonempty mapping')
    logical=set(value)&(GROUPS|QUANTIFIERS|SPECIAL)
    if logical:
        require(value,path,scope,inputs)
    elif set(value)=={'fields'}:
        predicates(value['fields'],path+'.fields',scope,inputs)
    else:
        predicates(value,path,scope,inputs)

def require(node,path='require',scope=frozenset(),inputs=None):
    inputs=inputs or {}
    if not isinstance(node,dict) or not node:fail(path,'require mapping cannot be empty')
    for k in node:
        if k in PROHIBITED: fail(path,'OVAL-like operation not permitted: '+k)
    # When a collection item must satisfy a mixture of scalar field predicates
    # and nested resource requirements, a fields leaf is one sibling in all/any.
    # It is NOT an OVAL State or a second evaluation engine.
    if set(node)=={'fields'}:
        predicates(node['fields'],path+'.fields',scope,inputs)
        return
    modes=set(node)&(QUANTIFIERS|GROUPS|SPECIAL)
    if len(modes)!=1:fail(path,'exactly one requirement operator required; found '+repr(sorted(modes)))
    mode=next(iter(modes))
    if mode in GROUPS:
        if set(node)!={mode}:fail(path,'all/any cannot include sibling properties')
        branches=node[mode]
        if not isinstance(branches,list) or len(branches)<2: fail(path,'all/any requires >=2 branches')
        for i,v in enumerate(branches):require(v,path+'.'+mode+'['+str(i)+']',scope,inputs)
        return
    if mode=='manual':
        if set(node)!={'manual'}:fail(path,'manual has unexpected siblings')
        item=node['manual']
        if not isinstance(item,dict) or not {'question','answers','pass_when','evidence_required','record'}<=set(item):
            fail(path,'manual check lacks explicit response/provenance contract')
        if item['pass_when'] not in item['answers']:fail(path,'manual passing value not in answers')
        if not {'assessor','assessed_at','point_of_contact'}<=set(item['record']):
            fail(path,'manual assessment requires who/when/POC')
        return
    if mode=='if':
        if set(node)!={'if'}: fail(path,'if has unexpected siblings')
        item=node['if']
        if not isinstance(item,dict) or set(item)!={'fact','equals','then','otherwise','on_unknown'}:
            fail(path+'.if','if requires fact/equals/then/otherwise/on_unknown')
        if item['on_unknown'] not in {'unknown','error','not_applicable'}:
            fail(path+'.if','must explicitly declare non-Boolean condition outcome')
        if item['fact']!='windows.computer.is_domain_controller':
            fail(path+'.if','no unregistered fact provider accepted')
        require(item['then'],path+'.if.then',scope,inputs)
        require(item['otherwise'],path+'.if.otherwise',scope,inputs)
        return
    if set(node)-({mode}|FIELDS):
        fail(path,'unsupported quantifier properties '+repr(set(node)-({mode}|FIELDS)))
    collection=node[mode]
    if not isinstance(collection,str) or not collection:fail(path,'quantified provider must be a string')
    if collection.startswith('$'):
        links(collection,scope,inputs,path+'.'+mode)
    elif collection not in RESOURCES:
        fail(path,'unregistered typed evidence provider '+collection)
    if 'as' in node:
        alias=node['as']
        if not isinstance(alias,str) or not IDENTIFIER.fullmatch(alias) or alias=='site' or alias in scope:
            fail(path,'invalid/shadowing lexical alias '+repr(alias))
        inner_scope=scope|{alias}
    else:inner_scope=scope
    if 'if_empty' in node:
        if mode!='every':fail(path,'if_empty only valid for every; other operators define empty directly')
        if node['if_empty'] not in {'pass','fail','unknown'}:
            fail(path,'if_empty needs explicit pass, fail or unknown')
    if mode=='every' and 'if_empty' not in node:
        fail(path,'every MUST explicitly declare if_empty')
    if 'where' in node:predicates(node['where'],path+'.where',scope,inputs)
    if 'using' in node:
        if not isinstance(node['using'],dict) or not node['using']:
            fail(path,'using requires explicit provider input mapping')
        links(node['using'],scope,inputs,path+'.using')
    if mode=='none' and 'must' in node:
        fail(path,'none means zero resources selected after where; express prohibited properties in where, not must')
    if 'must' in node:
        assertion(node['must'],path+'.must',inner_scope,inputs)
    elif mode in {'every','some','exactly_one','one_matching'}:
        fail(path,'this quantifier requires a must assertion')

def validate(doc,path='<Assessment>'):
    if not isinstance(doc,dict):fail(path,'expected mapping')
    if set(doc)-{'id','title','require','inputs'} or not {'id','title','require'}<=set(doc):
        fail(path,'root must have id, title, require; optional inputs only')
    if not isinstance(doc['id'],str) or not isinstance(doc['title'],str):
        fail(path,'id/title must be strings')
    inputs=doc.get('inputs',{})
    if not isinstance(inputs,dict):fail(path,'inputs mapping required')
    for ns,group in inputs.items():
        if ns!='site' or not isinstance(group,dict):
            fail(path,'prototype only admits explicit site input namespace')
        for key,contract in group.items():
            if not isinstance(contract,dict) or contract.get('provenance')!='required':
                fail(path,'site input missing provenance: '+key)
    require(doc['require'],inputs=inputs)
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('files',nargs='*')
    args=parser.parse_args()
    paths=[Path(x) for x in args.files] if args.files else sorted(SAMPLES.glob('*.yaml'))
    if not paths:raise SystemExit('no samples')
    for path in paths:
        doc=yaml.load(path.read_text(),Loader=Loader)
        validate(doc,str(path))
        print('PASS requirements-first structural authoring:',path.name)
    print(f'Validated {len(paths)} research examples; no scanner/provider/compiler parity inferred.')

if __name__=='__main__':main()
