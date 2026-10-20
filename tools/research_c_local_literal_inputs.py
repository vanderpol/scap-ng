#!/usr/bin/env python3
"""Refs #245: source-conserving fixed literal Object-input authoring research.

OVAL local Variables whose entire expression is one typed literal are not
runtime-derived computations, but a reference in an Object selector is not an
ordinary State expectation. This adapter exposes a single-use literal as an
editable collection input while preserving original Object selectors, typed
OVAL Variable and reference identity in a REQUIRED source provenance sidecar.
This is not a native full-C assessment compiler or scanner evaluation proof.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import re
from research_c_source_identity_contract import source_digest

STAGE = 'C_RESEARCH_TYPED_LITERAL_COLLECTION_INPUTS'
SENTINEL = 'c_collection_input'
ALIAS = re.compile(r'input_[a-z][a-z0-9_]{0,75}\Z')
SUPPORTED = {
    'string':str, 'version':str, 'rpm_evr':str, 'debian_evr':str,
    'fileset_revision':str, 'ios_version':str, 'binary':str,
    'ipv4':str, 'ipv6':str, 'integer':int, 'boolean':bool, 'float':float,
}


def _valid_literal(datatype,value):
    ty = SUPPORTED.get(datatype)
    return (ty is not None and type(value) is ty and
            (not isinstance(value,str) or len(value)<=4096) and
            (not isinstance(value,float) or math.isfinite(value)))


def _refs(value,variable_id,path=()):
    if isinstance(value,dict):
        if value == {'variable':variable_id}:
            yield path
        for name,member in value.items():
            yield from _refs(member,variable_id,path+(name,))
    elif isinstance(value,list):
        for i,member in enumerate(value):
            yield from _refs(member,variable_id,path+(i,))


def _at(value,path):
    node=value
    for part in path: node=node[part]
    return node


def _selector_for_path(path):
    if (not isinstance(path,(list,tuple)) or len(path)<5 or
        path[0]!='objects' or path[-1]!='value' or
        path[2]!='select' or type(path[3]) is not str or not path[3]):
        return None
    return path[3]


def _alias(selector,path,used):
    tail=[]
    # A record selector must show which member of a positional record is bound.
    for pos in path[4:-1]:
        if type(pos) is int: tail.append(str(pos))
    raw='_'.join([selector]+tail)
    base='input_'+re.sub(r'[^a-z0-9_]+','_',raw.lower()).strip('_')
    if not ALIAS.fullmatch(base):
        return None
    alias=base; idx=2
    while alias in used:
        alias=f'{base[:68]}_{idx}'
        idx+=1
        if not ALIAS.fullmatch(alias):
            raise ValueError('ambiguous collection input naming')
    return alias


def present_literal_collection_inputs(original):
    if not isinstance(original,dict) or original.get('mode')!='automated':
        raise ValueError('automated typed source Assessment required')
    vars_=original.get('variables')
    if not isinstance(vars_,dict) or not vars_:
        raise ValueError('source local Variables are required')
    graph=deepcopy(original)
    author={'stage':STAGE,'collection_inputs':{}}
    bindings={}
    used=set()
    outside={k:v for k,v in original.items() if k!='variables'}
    for vid,variable in sorted(vars_.items()):
        if (type(vid) is not str or not isinstance(variable,dict) or
            set(variable)!={'kind','datatype','expression','title'} or
            variable['kind']!='local' or not isinstance(variable['expression'],dict) or
            set(variable['expression'])!={'literal'}):
            continue
        literal=variable['expression']['literal']
        if (not isinstance(literal,dict) or set(literal)!={'datatype','value'} or
            literal['datatype']!=variable['datatype'] or
            not _valid_literal(literal['datatype'],literal['value']) or
            type(variable['title']) is not str or not variable['title']):
            continue
        refs=list(_refs(outside,vid))
        # Dynamic DAG / shared Object references remain in original typed graph.
        if len(refs)!=1 or list(_refs(vars_,vid)):
            continue
        path=refs[0]
        selector=_selector_for_path(path)
        if selector is None:
            continue
        alias=_alias(selector,path,used)
        if alias is None:continue
        used.add(alias)
        author['collection_inputs'][alias]={
            'selector':selector,
            'description':variable['title'],
            'datatype':literal['datatype'],
            'value':deepcopy(literal['value']),
        }
        bindings[alias]={
            'source_variable_id':vid, 'source_variable':deepcopy(variable),
            'source_path':list(path), 'source_selector':selector,
        }
        container=_at(graph,path[:-1])
        if not isinstance(container,dict) or container.get('value')!={'variable':vid}:
            raise ValueError('source Object selector is not an exact Variable binding')
        container['value']={SENTINEL:alias}
        graph['variables'].pop(vid)
    if not bindings:
        raise ValueError('no source-proven single-use literal Object inputs')
    return author, {
        'stage':STAGE,'original_source_sha256':source_digest(original),
        'source_graph_without_literal_bindings':graph,
        'bindings':bindings,
    }


def compile_literal_collection_inputs(author,sidecar):
    if (not isinstance(author,dict) or set(author)!={'stage','collection_inputs'} or
        author['stage']!=STAGE or not isinstance(sidecar,dict) or
        set(sidecar)!={'stage','original_source_sha256',
                        'source_graph_without_literal_bindings','bindings'} or
        sidecar['stage']!=STAGE):
        raise ValueError('unrecognized C collection input source contract')
    values=author['collection_inputs'];bindings=sidecar['bindings']
    if (not isinstance(values,dict) or not isinstance(bindings,dict) or
        not 1<=len(values)<=256 or set(values)!=set(bindings)):
        raise ValueError('incomplete C collection input identity bindings')
    result=deepcopy(sidecar['source_graph_without_literal_bindings'])
    variables=result.get('variables')
    if not isinstance(variables,dict):
        raise ValueError('missing typed source Variable collection')
    seen=set(variables);seen_paths=set()
    for alias,entry in values.items():
        binding=bindings[alias]
        if (type(alias) is not str or not ALIAS.fullmatch(alias) or
            not isinstance(entry,dict) or
            set(entry)!={'selector','description','datatype','value'} or
            not isinstance(binding,dict) or
            set(binding)!={'source_variable_id','source_variable',
                           'source_path','source_selector'}):
            raise ValueError('unrecognized collection input or source binding')
        vid=binding['source_variable_id'];original_var=binding['source_variable']
        path=binding['source_path'];selector=_selector_for_path(path)
        if (type(vid) is not str or not vid or vid in seen or
            selector is None or selector!=binding['source_selector'] or
            tuple(path) in seen_paths):
            raise ValueError('unbound or duplicate source input identity')
        seen.add(vid);seen_paths.add(tuple(path))
        if (not isinstance(original_var,dict) or
            set(original_var)!={'kind','datatype','expression','title'} or
            original_var['kind']!='local' or
            not isinstance(original_var['expression'],dict) or
            set(original_var['expression'])!={'literal'} or
            not isinstance(original_var['expression']['literal'],dict) or
            set(original_var['expression']['literal'])!={'datatype','value'}):
            raise ValueError('original typed local Variable shape was changed')
        datatype=original_var['datatype']
        if (datatype!=original_var['expression']['literal']['datatype'] or
            not _valid_literal(datatype,entry['value']) or
            entry['datatype']!=datatype or
            entry['selector']!=selector or
            entry['description']!=original_var['title']):
            raise ValueError('source datatype, purpose, selector or literal changed')
        try:parent=_at(result,path[:-1])
        except (KeyError,IndexError,TypeError) as exc:
            raise ValueError('source Object binding path missing') from exc
        if (not isinstance(parent,dict) or parent.get('value')!={SENTINEL:alias} or
            list(_refs(result,vid))):
            raise ValueError('source Object Variable reference changed or reused')
        var=deepcopy(original_var)
        var['expression']['literal']['value']=deepcopy(entry['value'])
        variables[vid]=var
        parent['value']={'variable':vid}
    return result


def prove_literal_collection_inputs(original,author,sidecar):
    rebuilt=compile_literal_collection_inputs(author,sidecar)
    if rebuilt!=original or source_digest(rebuilt)!=sidecar['original_source_sha256']:
        raise ValueError('authored C collection input does not reproduce original source graph')
    return {'original_typed_graph_recreated':True,
            'inline_local_variables':len(author['collection_inputs']),
            'native_C_conversion_proven':False,
            'scanner_execution_proven':False}


def census(review_dir,manifest,*,examples_dir=None):
    if manifest.get('stage')!='SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY':
        raise ValueError('untrusted source-compatible native manifest')
    target={(x['file'],x['definition_id']) for x in manifest['unsupported']
            if x['reason'].startswith('VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY')}
    seen={};proof=[]
    if examples_dir is not None:
        examples_dir=Path(examples_dir);examples_dir.mkdir(parents=True,exist_ok=True)
    for file in sorted(Path(review_dir).glob('*.review.json')):
        r=json.loads(file.read_text(encoding='utf-8'))
        key=(r.get('source',{}).get('file'),r.get('source',{}).get('definition_id'))
        if key not in target:continue
        if key in seen:raise ValueError('duplicate original OVAL source Definition')
        source=r['A_source_compatibility_fallback'];seen[key]=True
        try:author,sidecar=present_literal_collection_inputs(source)
        except ValueError as exc:
            if str(exc)=='no source-proven single-use literal Object inputs':continue
            raise
        proof_result=prove_literal_collection_inputs(source,author,sidecar)
        row={'source_file':key[0],'definition_id':key[1],
             'inlined_local_literals':proof_result['inline_local_variables']}
        if examples_dir is not None:
            import yaml
            stem=sha256((key[0]+'|'+key[1]).encode()).hexdigest()[:24]
            name=stem+'.collection-inputs.research.yaml'
            companion=stem+'.source-provenance.research.json'
            (examples_dir/name).write_text(
                '# C research only; collection bindings kept in typed source IR.\n'
                +'# Original OVAL: '+key[0]+'\n'
                +'# Definition: '+key[1]+'\n'
                +yaml.safe_dump(author,sort_keys=False,allow_unicode=True),
                encoding='utf-8')
            (examples_dir/companion).write_text(
                json.dumps(sidecar,indent=2,sort_keys=True)+'\n',encoding='utf-8')
            aa=yaml.safe_load((examples_dir/name).read_text(encoding='utf-8'))
            bb=json.loads((examples_dir/companion).read_text(encoding='utf-8'))
            if compile_literal_collection_inputs(aa,bb)!=source:
                raise ValueError('serialization changed original source IR')
            row.update({'author_file':name,'source_sidecar_file':companion})
        proof.append(row)
    if set(seen)!=target:
        raise ValueError('missing Variable-blocked original OVAL Definitions')
    return {'stage':STAGE,'variable_blocked_definitions':len(target),
            'original_definitions_with_inline_local_literals':len(proof),
            'inlined_local_literal_variables':sum(r['inlined_local_literals'] for r in proof),
            'still_native_C_converted_definitions':manifest['native_C_Definitions'],
            'native_C_conversion_proven':False,'scanner_execution_proven':False,
            'proof_examples':proof}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--review',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--examples-dir',type=Path)
    a=p.parse_args()
    report=census(a.review,json.loads(a.manifest.read_text(encoding='utf-8')),
                  examples_dir=a.examples_dir)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='proof_examples'},sort_keys=True))


if __name__=='__main__':main()
