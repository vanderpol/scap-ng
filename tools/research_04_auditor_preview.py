#!/usr/bin/env python3
"""Research #235: read-only auditor preview from actual parsed Assessment YAML.

This does NOT execute Assessments, approve aliases, or infer scanner outcomes.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/assessment-simplification/english-first-04/field-presence-iteration'
OUT = BASE / 'generated-previews'
CASES = ('linux-home','windows-wmi-rights','linux-files','apache','dns')
TICK = chr(96)

def q(value):
    return TICK + str(value).replace(TICK, '') + TICK

def block(value):
    return '\n~~~yaml\n' + yaml.safe_dump(value, sort_keys=False, allow_unicode=True).rstrip() + '\n~~~\n'

class StrictLoader(yaml.SafeLoader):
    pass

def unique_mapping(loader, node):
    loader.flatten_mapping(node)
    out = {}
    for k,v in node.value:
        key = loader.construct_object(k)
        if key in out:
            raise ValueError('duplicate YAML key %r line %d' % (key,k.start_mark.line+1))
        out[key]=loader.construct_object(v)
    return out
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,unique_mapping)

def refs_check(x,sources,variables,path):
    if isinstance(x,dict):
        for key,val in x.items():
            if key=='for_each_source':
                if not isinstance(val,dict) or val.get('in') not in sources:
                    raise ValueError(path+': missing source for foreach '+repr(val))
            if key=='from' and isinstance(val,str):
                if val not in sources and not ('.' in val and val.split('.')[0] in {'user','item','record'}):
                    raise ValueError(path+': unresolved source '+repr(val))
            if key=='variable' and isinstance(val,str) and val not in variables:
                raise ValueError(path+': unresolved variable '+repr(val))
            refs_check(val,sources,variables,path+'.'+str(key))
    elif isinstance(x,list):
        for i,val in enumerate(x): refs_check(val,sources,variables,path+'['+str(i)+']')

def draw_eval(node,checks,depth=0):
    if not isinstance(node,dict) or len(node)!=1:
        raise ValueError('invalid evaluate node '+repr(node))
    key,val=next(iter(node.items()))
    pad='  '*depth
    if key=='test':
        if not isinstance(val,str) or val not in checks:
            raise ValueError('evaluate references unknown check '+repr(val))
        return [pad+'- '+q(val)+' — '+str(checks[val].get('check') or val)],[val]
    if key not in ('and','or') or not isinstance(val,list) or not val:
        raise ValueError('unsupported evaluate operator '+repr(key))
    lines=[pad+'- **'+('ALL' if key=='and' else 'ANY')+' of these child checks ('+key.upper()+')**:']
    found=[]
    for entry in val:
        part,used=draw_eval(entry,checks,depth+1)
        lines+=part
        found+=used
    return lines,found

def walk_require(node,path='require',policy=None):
    lines=[]
    if isinstance(node,list):
        for i,v in enumerate(node): lines+=walk_require(v,path+'['+str(i)+']',policy)
    elif isinstance(node,dict):
        if 'field_presence' in node:
            policy=node['field_presence']
            lines.append('- '+q(path)+': scalar-field policy '+q(policy)+' declared here; candidate lowering is not runtime proven.')
        if 'records' in node:
            lines.append('- '+q(path)+': nested record existence '+q(node['records'])+
                         ', matching '+q(node.get('matching_records','UNSPECIFIED'))+' (not root Items).')
            policy=None
        if 'presence' in node:
            lines.append('- '+q(path)+': explicit local FIELD presence '+q(node['presence'])+'.')
        for key,val in node.items():
            if key in ('and','or'):
                lines.append('- '+q(path)+': '+key.upper()+' combines whole child expressions, not value membership.')
                if not isinstance(val,list): raise ValueError('invalid '+path+'.'+key)
                lines+=walk_require(val,path+'.'+key,policy)
            elif key in ('states','fields'):
                lines+=walk_require(val,path+'.'+key,policy)
            elif key not in ('items','matching_items','field_presence','records','matching_records','presence'):
                if isinstance(val,dict):
                    if policy is not None and 'presence' not in val:
                        lines.append('- '+q(path+'.'+key)+': inherits '+q(policy)+' scalar-field policy if within its scope.')
                    lines+=walk_require(val,path+'.'+key,policy)
    return lines

def render(name,doc):
    if not isinstance(doc,dict) or set(doc)!={'metadata','sources','checks','evaluate'}:
        raise ValueError(name+': unexpected top-level structure')
    meta=doc['metadata']; checks=doc['checks']; sources=doc['sources']
    if not isinstance(checks,dict) or not checks: raise ValueError(name+': empty checks')
    vars_=meta.get('variables',{})
    refs_check({'sources':sources,'checks':checks,'variables':vars_},sources,vars_,name)
    evaluate,used=draw_eval(doc['evaluate'],checks)
    if set(checks)!=set(used):
        raise ValueError(name+': checks omitted from evaluation '+repr(set(checks)-set(used)))
    lines=['# Auditor preview — '+str(meta.get('assessment_title') or meta['id']),
           '', '**Machine-generated research explanation from complete parsed YAML.** '
           'No live result, new normative policy or scanner-equivalence proof.',
           '', '**Assessment ID:** '+q(meta['id'])+' · **Checks:** '+str(len(checks))+
           ' · **Evaluate leaves:** '+str(len(used)),
           '', '[Revised full YAML](../'+name+'.revised.research.yaml) · '
           '[Original source YAML](../../canonical-operators/'+name+'.canonical.research.yaml)',
           '', '## What is observed?', '']
    if not sources: lines+=['No separately named source; checks use their native inspectors.','']
    for src,obj in sources.items():
        lines+=['### Named source '+q(src),'', '**Inspector:** '+q(obj.get('inspect'))]
        if 'where' in obj: lines+=['**Original selector:**',block(obj['where'])]
        if 'collect' in obj: lines+=['**Collection configuration:**',block(obj['collect'])]
        for operator in ('union','intersection','difference','complement'):
            if operator in obj: lines+=['**Named Set '+operator+':**',block(obj[operator])]
    if vars_:
        lines+=['','**Variable graph:** '+str(len(vars_))+' declarations (full expressions in source YAML).']
        lines+=['- '+q(x) for x in vars_]
    lines+=['','## What must exist and match?','']
    for cid,check in checks.items():
        req=check['require']
        if 'items' not in req or 'matching_items' not in req: raise ValueError(cid+': missing Item quantifiers')
        lines+=['### '+str(check.get('check') or cid),'', '**Check ID:** '+q(cid)+
                ' · **Inspector:** '+q(check.get('inspect')),'',
                '- **Root Item existence:** '+q(req['items']),
                '- **Matching root Items:** '+q(req['matching_items'])]
        if 'from' in check: lines+=['- **Named source reference:** '+q(check['from'])]
        for key in ('where','collect','gather'):
            if key in check: lines+=['**Original '+key+' (not reconstructed):**',block(check[key])]
        lines+=['','**Explicit field, record and State scopes:**','']
        lines+=walk_require(req) or ['- No additional field-presence/record/group policy is explicitly displayed.']
        lines+=['','**Full requirement subtree (candidate wording):**',block(req)]
    counts=Counter(used)
    lines+=['','## How could the Assessment pass?','',
            'The structural AND/OR tree below is read from parsed YAML. '
            'It is not procedural IF/ELSE, and no actual outcome is calculated.','']
    lines+=evaluate
    lines+=['', '**Evaluate references:** '+str(len(used))+
            ' occurrences of '+str(len(counts))+' named checks, all accounted for.']
    repeated={k:v for k,v in counts.items() if v>1}
    if repeated: lines+=['**Repeated references retained:** '+', '.join(q(k)+' ×'+str(v) for k,v in repeated.items())]
    lines+=['','## What remains unverified?','',
            '- **No system evidence** was collected or evaluated.',
            '- Missing field, missing root Item, read error and incomplete collection are different.',
            '- Repeated field values, nested WMI records and root Items have separate quantifiers.',
            '- Field-presence and matching-label aliases are research-only; runtime equivalence remains open.',
            '- OVAL AND(False,Error) can be False, while OR(True,Error) can be True.',
            '- For command flags, dependent sources, typing and evidence rules, inspect the complete YAML.',
            '', '[Generic six-state result ledger](SEMANTIC-BOUNDARY-LEDGER.md).','']
    return '\n'.join(lines),len(checks),len(used)

def boundary_ledger():
    sys.path.insert(0,str(ROOT/'tools'))
    from oval_result_truth_tables import (TRUE,FALSE,ERROR,UNKNOWN,aggregate_operator,aggregate_check,evaluate_collected_object_test)
    examples=[
        ('OR(True,Error)',aggregate_operator('OR',[TRUE,ERROR]),'Inherited OVAL OR'),
        ('AND(False,Error)',aggregate_operator('AND',[FALSE,ERROR]),'Inherited OVAL AND'),
        ('ALL Items(False,Error)',aggregate_check('all',[FALSE,ERROR]),'Generic Item matching'),
        ('At least one Item(True,Error)',aggregate_check('at least one',[TRUE,ERROR]),'Generic Item matching'),
        ('Incomplete, known True, ALL',evaluate_collected_object_test('incomplete',existence='at_least_one_exists',check='all',exists=1,item_results=[TRUE]),'Generic collected-object helper'),
        ('Incomplete, known False, ALL',evaluate_collected_object_test('incomplete',existence='at_least_one_exists',check='all',exists=1,item_results=[FALSE]),'Generic collected-object helper'),
        ('Incomplete, known True, AT LEAST ONE',evaluate_collected_object_test('incomplete',existence='at_least_one_exists',check='at least one',exists=1,item_results=[TRUE]),'Generic collected-object helper'),
        ('Collection flag Error',evaluate_collected_object_test('error',existence='at_least_one_exists'),'Generic collected-object helper'),
        ('Collection flag Not Collected',evaluate_collected_object_test('not collected',existence='at_least_one_exists'),'Generic collected-object helper'),
    ]
    assert [v for _,v,_ in examples]==[TRUE,FALSE,FALSE,TRUE,UNKNOWN,FALSE,TRUE,ERROR,UNKNOWN]
    lines=['# Generic OVAL six-state boundary ledger — NOT Assessment execution','',
           '**Generated from the repository reference truth tables.** '
           'No scanner, real system data or candidate field-presence alias lowering was involved.','',
           '| Generic input | Model outcome | Contract |','| --- | --- | --- |']
    lines+=['| '+q(label)+' | **'+result+'** | '+scope+' |' for label,result,scope in examples]
    lines+=['','**Unverified:** absent/unreadable Apache fields; Linux/DNS inherited field-policy overrides '
            'under partial data; WMI record semantics across six statuses; repeated DNS field values.',
            '', '[Back to generated preview index](INDEX.md).','']
    return '\n'.join(lines)

def build():
    output={}
    index=['# Generated read-only auditor explanations — SCAP-NG 0.4 research','',
           '**From complete parsed candidate Assessments. Not scanner results or a new language.**','',
           '| Assessment | Checks | Evaluate leaves | Preview | Full YAML |',
           '| --- | ---: | ---: | --- | --- |']
    for name in CASES:
        doc=yaml.load((BASE/(name+'.revised.research.yaml')).read_text(),Loader=StrictLoader)
        preview,checks,leaves=render(name,doc)
        output[name+'.md']=preview
        index.append('| '+name+' | '+str(checks)+' | '+str(leaves)+' | [Read]('+name+'.md) | [YAML](../'+name+'.revised.research.yaml) |')
    index+=['','[Computed generic result boundary ledger](SEMANTIC-BOUNDARY-LEDGER.md).','']
    output['INDEX.md']='\n'.join(index)
    output['SEMANTIC-BOUNDARY-LEDGER.md']=boundary_ledger()
    return output

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    output=build()
    if args.check:
        for name,body in output.items():
            file=OUT/name
            if not file.exists() or file.read_text()!=body: raise SystemExit('stale or missing: '+str(file))
        print('PASS: '+str(len(output))+' previews match full source and generic reference tables')
        return
    OUT.mkdir(parents=True,exist_ok=True)
    for name,body in output.items():
        (OUT/name).write_text(body)
        print('GENERATED',name)

if __name__=='__main__': main()
