#!/usr/bin/env python3
"""#235 — one cardinality vocabulary and structural State/field groups.

Research-only *presentation* of the source-exact flat-require experiment.
`scope: states|fields` -> `states: {and|or: ...}` / `fields: {and|or: ...}`;
`match: some` -> `match: at_least_one` at Item and record levels;
`all_fields_must_exist: true` -> group-local `presence: all`.
No SCAP 0.4 normative, collection, OVAL six-state or evidence changes.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile
import yaml
from jsonschema import Draft202012Validator
from research_04_fixed_require_editor import PINNED, SAMPLES, to_fixed, from_fixed
from research_04_flat_require import flat_doc, source_doc, schema_for_flat

GROUPS = frozenset({'states', 'fields'})
OPERATORS = frozenset({'and', 'or'})
QUANTIFIERS = frozenset({'all', 'at_least_one', 'exactly_one', 'none'})
RESERVED_TOP = frozenset({'items','match','states','fields'})


def _operator(node):
    found = set(node) & OPERATORS
    if len(found)!=1:
        raise ValueError('logical group requires exactly one and/or')
    return next(iter(found))


def modernize(node, counts=None):
    """Convert scoped groups and matching quantifiers without modifying field literals."""
    if isinstance(node,list):
        return [modernize(v,counts) for v in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    if isinstance(node.get('scope'),str) and node['scope'] in GROUPS:
        scope=node['scope']; op=_operator(node)
        allowed={'scope',op}
        if scope=='fields' and node.get('all_fields_must_exist') is True:
            allowed.add('all_fields_must_exist')
        if set(node)!=allowed:
            raise ValueError('unsupported or ambiguous scoped group')
        children=node[op]
        if not isinstance(children,list) or len(children)<(2 if scope=='states' else 1):
            raise ValueError('invalid group operands')
        result={op:[modernize(v,counts) for v in children]}
        if 'all_fields_must_exist' in node:
            result['presence']='all'
            if counts is not None: counts['field_true_replaced']+=1
        if counts is not None: counts['scope_replaced_'+scope]+=1
        return {scope:result}
    if 'scope' in node and isinstance(node['scope'],str):
        raise ValueError('unexpected scope enum outside group')
    out={}
    for key,value in node.items():
        if key=='match' and value=='some' and (('items' in node) or ('records' in node)):
            out[key]='at_least_one'
            if counts is not None: counts['some_replaced']+=1
        else:
            out[key]=modernize(value,counts)
    return out


def demodernize(node):
    if isinstance(node,list):
        return [demodernize(v) for v in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    groupkeys=set(node)&GROUPS
    if groupkeys:
        if len(groupkeys)!=1 or len(node)!=1:
            raise ValueError('ambiguous states/fields grouping')
        kind=next(iter(groupkeys)); body=node[kind]
        if not isinstance(body,dict):
            raise ValueError('group must be mapping')
        op=_operator(body)
        expected={op}
        if kind=='fields' and body.get('presence')=='all':
            expected.add('presence')
        if set(body)!=expected:
            raise ValueError('group has unsupported or misplaced controls')
        children=body[op]
        if not isinstance(children,list) or len(children)<(2 if kind=='states' else 1):
            raise ValueError('group operands empty or invalid')
        out={'scope':kind,op:[demodernize(v) for v in children]}
        if 'presence' in body:
            out['all_fields_must_exist']=True
        return out
    if 'scope' in node and isinstance(node.get('scope'),str):
        raise ValueError('old scope keyword is not legal in authoring')
    if 'all_fields_must_exist' in node:
        raise ValueError('old Boolean field presence marker is not legal in authoring')
    out={}
    for key,value in node.items():
        if key=='match' and (('items' in node) or ('records' in node)):
            if not isinstance(value,str) or value not in QUANTIFIERS:
                raise ValueError('match must use one of four consistent cardinalities')
            out[key]='some' if value=='at_least_one' else value
        else:
            out[key]=demodernize(value)
    return out


def to_consistent(require, counts=None):
    if not isinstance(require,dict) or 'items' not in require:
        raise ValueError('missing Item requirement')
    if 'condition' in require:
        raise ValueError('removed condition wrapper')
    if set(require)=={'items'}:
        return deepcopy(require)
    if 'match' not in require:
        raise ValueError('requirement has no match')
    predicate={k:v for k,v in require.items() if k not in ('items','match')}
    if len(predicate)!=1 and 'scope' not in predicate:
        raise ValueError('one field or one grouped clause is required')
    normalized=modernize(predicate,counts)
    if set(normalized)&{'items','match'}:
        raise ValueError('reserved Item keys used as predicates')
    if 'scope' in normalized or 'all_fields_must_exist' in normalized:
        raise ValueError('legacy grouping vocabulary survived normalization')
    return {'items':require['items'], 'match':('at_least_one' if require['match']=='some' else require['match']), **normalized}


def from_consistent(require):
    if not isinstance(require,dict) or 'items' not in require:
        raise ValueError('missing Item requirement')
    if 'condition' in require:
        raise ValueError('removed condition wrapper')
    if set(require)=={'items'}:
        return deepcopy(require)
    if 'match' not in require or require['match'] not in QUANTIFIERS:
        raise ValueError('unknown or missing matching quantifier')
    predicate={k:v for k,v in require.items() if k not in ('items','match')}
    if len(predicate)!=1:
        raise ValueError('one native field or one named scope group only')
    if 'states' in predicate or 'fields' in predicate:
        restored=demodernize(predicate)
    elif 'scope' in predicate or 'all_fields_must_exist' in predicate:
        raise ValueError('legacy group controls rejected')
    else:
        restored=demodernize(predicate)
    return {'items':require['items'], 'match':('some' if require['match']=='at_least_one' else require['match']),**restored}


def document_to_consistent(flat, counts=None):
    out=deepcopy(flat)
    for ck in out['checks'].values():
        old=ck['require']
        ck['require']=to_consistent(old,counts)
        if old.get('match')=='some' and counts is not None:
            counts['some_replaced']+=1
    return out


def document_to_flat(doc):
    out=deepcopy(doc)
    for ck in out['checks'].values():
        ck['require']=from_consistent(ck['require'])
    return out


def schema_for_consistent(base):
    s=schema_for_flat(base)
    s['$id']='https://scap-ng.dev/research/english-first-04/consistent-quantifiers.schema.json'
    s['title']='RESEARCH: consistent cardinality and states/fields groups, no condition/scope/true flags'
    s['$defs']['modernState']={'oneOf':[
        {'type':'object','minProperties':1,'maxProperties':1,
         'patternProperties':{'^(?!(?:states|fields)$).+$':{'type':'object','minProperties':1}},
         'additionalProperties':False},
        {'type':'object','required':['states'],'properties':{'states':{'$ref':'#/$defs/modernStatesGroup'}},'additionalProperties':False},
        {'type':'object','required':['fields'],'properties':{'fields':{'$ref':'#/$defs/modernFieldsGroup'}},'additionalProperties':False},
    ]}
    for kind in GROUPS:
        clauses=[]
        for op in ('and','or'):
            prop={op:{'type':'array','minItems':2 if kind=='states' else 1,
                      'items':{'$ref':'#/$defs/modernState'}}}
            if kind=='fields':prop['presence']={'const':'all'}
            clauses.append({'type':'object','required':[op], 'properties':prop,'additionalProperties':False})
        s['$defs']['modern'+kind.title()+'Group']={'oneOf':clauses}
    presence=s['$defs']['requirement']['oneOf'][0]
    entries=[deepcopy(presence)]
    modes=set()
    for entry in s['$defs']['requirement']['oneOf'][1:]:
        properties=entry.get('properties',{})
        if 'items' in properties and 'match' in properties:
            key=(properties['items'].get('const'),properties['match'].get('const'))
            if key[0] is not None and key[1] is not None:modes.add(key)
    for items, match in sorted(modes):
        match='at_least_one' if match=='some' else match
        basics={'items':{'const':items},'match':{'const':match}}
        entries.append({'type':'object','required':['items','match'],
            'minProperties':3,'maxProperties':3,'properties':basics,
            'patternProperties':{'^(?!(?:items|match|scope|states|fields|condition|all_fields_must_exist)$).+$':{'type':'object','minProperties':1}},
            'additionalProperties':False})
        for kind in ('states','fields'):
            entries.append({'type':'object','required':['items','match',kind],
                'properties':{**basics,kind:{'$ref':'#/$defs/modern'+kind.title()+'Group'}},
                'additionalProperties':False})
    s['$defs']['requirement']={'oneOf':entries}
    Draft202012Validator.check_schema(s)
    return s


def proof(archive, base_schema, output):
    digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest!=PINNED:raise ValueError('unexpected pinned source archive hash')
    base=json.loads(Path(base_schema).read_text())
    contract=schema_for_consistent(base)
    validator=Draft202012Validator(contract)
    counts=Counter(); failures=[]; samples={}; collisions=[]
    with zipfile.ZipFile(archive) as z:
        for path in sorted(z.namelist()):
            if not(path.startswith('authoring/') and '/assessments/' in path and path.endswith('.yaml')):
                continue
            source=(yaml.safe_load(z.read(path)) or {}).get('assessment') or {}
            if source.get('mode')!='automated' or not isinstance(source.get('tests'),dict) or not source['tests']:
                continue
            counts['assessments']+=1; counts['tests']+=len(source['tests'])
            try:
                fixed=to_fixed(source)
                flat=flat_doc(fixed)
                candidate=document_to_consistent(flat,counts)
                schema_err=next(validator.iter_errors(candidate),None)
                if schema_err:raise ValueError('schema: '+schema_err.message[:250])
                recovered=document_to_flat(candidate)
                if recovered!=flat or from_fixed(source_doc(recovered))!=source:
                    raise ValueError('complete Assessment source mismatch')
                counts['exact_assessments']+=1; counts['exact_tests']+=len(source['tests'])
                if path in SAMPLES.values():
                    samples[next(n for n,p in SAMPLES.items() if p==path)]=candidate
                bad=deepcopy(candidate)
                first=next(iter(bad['checks'].values()))['require']
                first['condition']={'unexpected':{'is':True}}
                if validator.is_valid(bad):raise ValueError('schema accepted removed condition wrapper')
                try:document_to_flat(bad)
                except (ValueError,TypeError,KeyError):pass
                else:raise ValueError('parser accepted removed condition wrapper')
                counts['negative_guards']+=1
            except (ValueError,AssertionError,TypeError,KeyError) as e:
                failures.append({'path':path,'error':str(e)[:320]})
                if 'reserved' in str(e) or 'collid' in str(e):collisions.append(path)
    if (counts['assessments'],counts['tests'])!=(872,1375):
        raise AssertionError('pinned source corpus drift')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    (output/'consistent-quantifiers.editor.schema.json').write_text(json.dumps(contract,indent=2)+'\n')
    for name,doc in samples.items():
        (output/(name+'.consistent.research.yaml')).write_text('# RESEARCH ONLY — not normative 0.4 or scanner validated\n'+yaml.safe_dump(doc,sort_keys=False,allow_unicode=True,width=110))
    report={'source_sha256':digest,'counts':dict(counts),'failures':failures,'collisions':collisions,
         'samples':sorted(samples),'proof_scope':'Complete native Assessment structure, not execution/evidence parity'}
    (output/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (output/'report.md').write_text(markdown_report(report))
    return report


def markdown_report(r):
    c=r['counts'];lines=[
      '# Consistent cardinalities and structural groups — six-STIG proof','',
      '**Research only: not approved 0.4 grammar or scanner/OVAL execution parity.**','',
      f"- **{c['exact_assessments']}/{c['assessments']}** complete Assessments, **{c['exact_tests']}/{c['tests']}** Tests exactly reconstructed.",
      f"- `some` → `at_least_one`: **{c['some_replaced']}** matching quantifiers (Item and record).",
      f"- `scope: states|fields` → explicit structural groups: **{c['scope_replaced_states']}** whole-State groups, **{c['scope_replaced_fields']}** field groups.",
      f"- `all_fields_must_exist: true` → `fields.presence: all`: **{c['field_true_replaced']}** scoped field groups.",
      f"- Inadmissible wrapper mutations rejected: **{c['negative_guards']}**.",
      f"- Reserved/ambiguous name collision Assessments: **{len(r['collisions'])}**.", '',
      '## Real Windows 11 WMI DomainRole requirement', '',
      '```yaml', 'require:', '  items: at_least_one', '  match: all', '  states:', '    or:',
      '      - result:', '          records: at_least_one','          match: all','          domainrole: {is: "1"}',
      '      - result:', '          records: at_least_one','          match: all','          domainrole: {is: "3"}', '```', '',
      '`states.or` combines full alternative State evaluations; it does not mean per-record `domainrole` membership.', '',
      '## Source boundary and unsupported shortcuts', '',
      '- The example is a transformation of the original **Windows 11 SV-253495** WMI check; the complete 7-Test Assessment and its `evaluate.or` graph remain intact.',
      '- Every record branch still requires at least one record and all observed records to satisfy its own role condition.',
      '- Converting both branches to `domainrole: {in: [1,3]}` **would change results** for mixed records.',
      '- Literal Boolean field tests (`is: true` or `is: false`) are intentionally preserved. No legacy Test `all_exist` semantics are normalized.',
      '- Parser/schema coverage and source structure do not establish independent scanner/OVAL evidence parity.', '',
      '## Source exceptions', ''
    ]
    lines += ['- `'+e['path']+'` — '+e['error'] for e in r['failures']]
    lines += ['', '## Complete source-backed sample Assessments', '',
        'Complete six-STIG derived RHEL, Windows, DNS and Apache examples are adjacent to this report as `*.consistent.research.yaml`.','']
    return '\n'.join(lines)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--archive',required=True)
    ap.add_argument('--base-schema',required=True)
    ap.add_argument('--out',required=True)
    opts=ap.parse_args()
    print(json.dumps(proof(opts.archive,opts.base_schema,opts.out),indent=2)[:5000])