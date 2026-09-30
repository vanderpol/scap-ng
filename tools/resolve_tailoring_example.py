#!/usr/bin/env python3
"""Resolve the worked Tailoring source fixture; not a scanner or final NG schema.

Validates documented policy boundaries using the example's proposed source
shapes. It never executes Assessment procedures or evaluates target results.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import yaml

ALLOWED={'id','version','title','purpose','description','benchmark','profile','extends','enabled_rules','disabled_rules',
         'enabled_groups','disabled_groups','parameters','check_selectors','selection_justifications',
         'parameter_justifications','provenance'}


def load(path, kind):
    doc=yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(doc,dict) or set(doc)!={kind}: raise ValueError('Expected '+kind+' document: '+str(path))
    return doc[kind]


def validate_value(parameter, value):
    kind=parameter['type']; constraints=parameter.get('constraints') or {}
    types={'integer':int,'boolean':bool,'string':str,'list':list,'record':dict}
    if kind not in types or type(value) is not types[kind]: raise ValueError('Parameter type mismatch: '+parameter['id'])
    if kind=='integer' and not constraints.get('minimum',value)<=value<=constraints.get('maximum',value):
        raise ValueError('Parameter out of range: '+parameter['id'])
    if kind=='string' and len(value)>constraints.get('max_length',len(value)): raise ValueError('Parameter too long')
    if kind=='list':
        if constraints.get('items')=='string' and any(type(item) is not str for item in value): raise ValueError('List item type mismatch')
        if 'allowed' in constraints and any(item not in constraints['allowed'] for item in value): raise ValueError('Unsupported list value')
    if kind=='record':
        fields=constraints.get('fields',{})
        if set(value)!=set(fields) or any(type(value[k]) is not types[fields[k]] for k in fields): raise ValueError('Record fields/type mismatch')


def resolve(benchmark_path, tailoring_path, input_path=None):
    benchmark_path=Path(benchmark_path).resolve();tailoring_path=Path(tailoring_path).resolve()
    benchmark=load(benchmark_path,'benchmark'); outer=load(tailoring_path,'tailoring')
    version=benchmark['version']['value'] if isinstance(benchmark['version'],dict) else benchmark['version']
    binding={'id':benchmark['id'],'version':version};profile_id=outer.get('profile')
    members=benchmark['rules']
    if len(members)!=len(set(members)): raise ValueError('Duplicate Benchmark Rule')
    selections={rid:True for rid in members}; selection_source={rid:'benchmark' for rid in members}
    rules={};rule_paths={}
    for path in (benchmark_path.parent/'rules').glob('*.rule.yaml'):
        rule=load(path,'rule')
        if rule['id'] in rules: raise ValueError('Duplicate Rule identity')
        rules[rule['id']]=rule
        rule_paths[rule['id']]=path
    if set(rules)!=set(members): raise ValueError('Rule membership mismatch')
    parameters={p['id']:p for p in benchmark.get('parameters',[])}
    values={p['id']:deepcopy(p['value']) for p in parameters.values() if p['source']=='publisher'}
    value_source={key:'benchmark' for key in values}
    selectors={rid:rules[rid]['default_assessment_choice'] for rid in members}
    selector_source={rid:'benchmark' for rid in members}
    profiles={p['id']:p for p in benchmark.get('profiles',[])}
    groups={}
    def visit(group):
        found=set(group.get('rules',[]))
        for child in group.get('groups',[]): found.update(visit(child))
        if group['id'] in groups or found-set(members): raise ValueError('Invalid Group membership')
        groups[group['id']]=found;return found
    for group in benchmark.get('groups',[]):visit(group)
    profile_stack=[]
    def apply_profile(pid):
        if pid in profile_stack or pid not in profiles: raise ValueError('Missing or cyclic Profile')
        profile_stack.append(pid);p=profiles[pid]
        if p.get('extends'): apply_profile(p['extends'])
        if 'enabled_rules' in p: raise ValueError('Publisher Profile cannot enable Rules')
        for rid in p.get('disabled_rules',[]):
            if rid not in selections: raise ValueError('Unknown Profile Rule')
            selections[rid]=False;selection_source[rid]='profile:'+pid
        for key,value in p.get('parameters',{}).items():
            if key not in parameters or parameters[key]['source']!='publisher': raise ValueError('Invalid Profile Parameter')
            validate_value(parameters[key],value);values[key]=deepcopy(value);value_source[key]='profile:'+pid
        profile_stack.pop()
    if profile_id:apply_profile(profile_id)
    publisher_selection=dict(selections);history=[];stack=[]
    def apply_layer(path):
        path=path.resolve()
        if path in stack: raise ValueError('Tailoring inheritance cycle')
        stack.append(path);t=load(path,'tailoring')
        if set(t)-ALLOWED: raise ValueError('Unsupported Tailoring mutation: '+str(sorted(set(t)-ALLOWED)))
        if t['benchmark']!=binding or t.get('profile')!=profile_id: raise ValueError('Benchmark/version/Profile binding mismatch')
        parent=t.get('extends')
        if parent:
            parent_path=(path.parent/parent['source']).resolve()
            if not parent_path.is_relative_to(tailoring_path.parent): raise ValueError('Parent Tailoring source escapes example directory')
            p=load(parent_path,'tailoring')
            if (p['id'],p['version'])!=(parent['id'],parent['version']): raise ValueError('Parent identity/version mismatch')
            apply_layer(parent_path)
        enables=set(t.get('enabled_rules',[]));disables=set(t.get('disabled_rules',[]))
        for key,target in [('enabled_groups',enables),('disabled_groups',disables)]:
            for gid in t.get(key,[]):
                if gid not in groups: raise ValueError('Unknown Tailoring Group')
                target.update(groups[gid])
        if (enables|disables)-set(members): raise ValueError('Unknown Tailoring Rule')
        if enables&disables: raise ValueError('Conflicting Group/Rule selections in one layer')
        origin='tailoring:'+t['id']
        for rid in enables: selections[rid]=True;selection_source[rid]=origin
        for rid in disables: selections[rid]=False;selection_source[rid]=origin
        for key,value in t.get('parameters',{}).items():
            if key not in parameters or not parameters[key].get('tailorable') or parameters[key]['source']!='publisher':
                raise ValueError('Unknown, non-tailorable or organization-defined Parameter: '+key)
            validate_value(parameters[key],value);values[key]=deepcopy(value);value_source[key]=origin
        for rid,selector in t.get('check_selectors',{}).items():
            if rid not in rules or selector not in rules[rid]['assessment_choices']: raise ValueError('Unknown Rule/Assessment selector')
            selectors[rid]=selector;selector_source[rid]=origin
        history.append({'id':t['id'],'version':t['version'],'purpose':t.get('purpose'),
                        'selection':dict(selections),
                        'parameter_values':deepcopy(values),'check_selectors':dict(selectors),
                        'provenance':deepcopy(t.get('provenance',{})),
                        'selection_justifications':deepcopy(t.get('selection_justifications',{})),
                        'parameter_justifications':deepcopy(t.get('parameter_justifications',{}))})
        stack.pop()
    apply_layer(tailoring_path)
    organizational_input={}
    if input_path:
        supplied=load(Path(input_path),'organizational_input')
        if supplied['benchmark']!=binding: raise ValueError('Organizational Input binding mismatch')
        for key,value in supplied['values'].items():
            if key not in parameters or parameters[key]['source']!='organization': raise ValueError('Input cannot override publisher Parameter')
            validate_value(parameters[key],value);organizational_input[key]={'value':value,'source':supplied['id'],
                                                                          'provenance':supplied.get('provenance',{})}
    methods={}
    for rid,selector in selectors.items():
        ref=rules[rid]['assessment_choices'][selector]['assessment'];owner=rule_paths[rid]
        path=(owner.parent/ref).resolve()
        if not path.is_relative_to(benchmark_path.parent): raise ValueError('Assessment source escape')
        method=load(path,'assessment');methods[rid]={'selector':selector,'assessment_id':method['id'],
                                                   'will_be_selected':selections[rid], 'selector_source':selector_source[rid]}
    return {'benchmark':binding,'profile':profile_id,'publisher_selection':publisher_selection,
            'effective_selection':selections,'selection_source':selection_source,'parameters':values,
            'parameter_source':value_source,'assessment_selections':methods,'tailoring_layers':history,
            'organizational_input':organizational_input,
            'limits':['Worked policy-source resolver only; no target execution, finalized schema or full NG conformance.',
                      'Fixture source spellings for Group operations, provenance and parent bindings are review proposals.',
                      'This resolver does not implement rebase mapping or Assessment Request execution.']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--benchmark',type=Path,required=True);p.add_argument('--tailoring',type=Path,required=True)
    p.add_argument('--organizational-input',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=resolve(a.benchmark,a.tailoring,a.organizational_input)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rules':len(result['effective_selection']),'selected':sum(result['effective_selection'].values()),
                      'tailoring_layers':len(result['tailoring_layers'])}))

if __name__=='__main__':main()
