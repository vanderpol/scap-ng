#!/usr/bin/env python3
"""#235: Remove the syntactic condition wrapper and redundant record-exists:true.

Research-only source-exact presentation experiment. The existing six-STIG
converter remains unchanged. Never normalize legacy all_exist or change OVAL
Item/record/status semantics to improve a coverage number.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import yaml
from jsonschema import Draft202012Validator
from research_04_fixed_require_editor import to_fixed, from_fixed, PINNED, SAMPLES
from research_04_require_presentation_comparison import encode, decode, PRESENCE, COMPARISONS

RECORD_MATCH = {
    'every_record': 'all',
    'some_record': 'some',
    'exactly_one_matching_record': 'exactly_one',
    'no_matching_record': 'none',
}
RECORD_REVERSE = {value:key for key,value in RECORD_MATCH.items()}
RESERVED = frozenset({'items','match'})


def records_to_flat(node, counts=None):
    """Replace only proven record-exists:true + matching-mode pairs."""
    if isinstance(node,list):
        return [records_to_flat(v,counts) for v in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    if 'at_least_one_record_exists' in node:
        modes=set(node)&set(RECORD_MATCH)
        if (node['at_least_one_record_exists'] is not True or len(modes)!=1
                or set(node)!=modes|{'at_least_one_record_exists'}):
            raise ValueError('ambiguous source record existence or match semantics')
        mode=next(iter(modes))
        fields=node[mode]
        if not isinstance(fields,dict) or not fields or set(fields)&{'records','match'}:
            raise ValueError('record contains conflicting reserved fields')
        if counts is not None: counts['redundant_record_true_removed']+=1
        return {'records':'at_least_one', 'match':RECORD_MATCH[mode],
                **{k:records_to_flat(v,counts) for k,v in fields.items()}}
    return {k:records_to_flat(v,counts) for k,v in node.items()}


def records_to_source(node):
    if isinstance(node,list):
        return [records_to_source(v) for v in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    if 'records' in node and isinstance(node['records'],str):
        if node['records']!='at_least_one' or node.get('match') not in RECORD_REVERSE:
            raise ValueError('unsupported or incomplete record requirements')
        fields={k:v for k,v in node.items() if k not in ('records','match')}
        if not fields or 'at_least_one_record_exists' in fields:
            raise ValueError('record requires fields and cannot carry old true flag')
        return {'at_least_one_record_exists':True,
                RECORD_REVERSE[node['match']]:{k:records_to_source(v) for k,v in fields.items()}}
    if 'at_least_one_record_exists' in node:
        raise ValueError('legacy record bool is not legal authoring syntax')
    return {k:records_to_source(v) for k,v in node.items()}


def flatten(require,counts=None):
    """One require block: items, match, then native predicates; no condition."""
    paired=encode(require,'split')
    if set(paired)=={'items'}:
        return paired
    fields=records_to_flat(paired['condition'],counts)
    collision=set(fields)&RESERVED
    if collision:
        raise ValueError('predicate collides with reserved require keys: '+repr(sorted(collision)))
    _validate_flat_predicate(fields)
    return {'items':paired['items'], 'match':paired['match'],**fields}


def _validate_flat_predicate(predicate):
    """Fail closed on ambiguous extra clauses or malformed group scopes."""
    if not predicate:
        raise ValueError('matched requirement needs direct predicate')
    if 'scope' in predicate and isinstance(predicate['scope'],str):
        scope=predicate['scope']
        if scope not in ('fields','states'):
            raise ValueError('invalid predicate grouping scope')
        ops=set(predicate)&{'and','or'}
        allowed={'scope',*ops}
        if scope=='fields':allowed.add('all_fields_must_exist')
        if len(ops)!=1 or set(predicate)!=allowed and set(predicate)!=allowed-{'all_fields_must_exist'}:
            raise ValueError('ambiguous predicate grouping')
        if 'all_fields_must_exist' in predicate and predicate['all_fields_must_exist'] is not True:
            raise ValueError('field presence requirement must be true')
        terms=predicate[next(iter(ops))]
        if not isinstance(terms,list) or len(terms)<(2 if scope=='states' else 1):
            raise ValueError('invalid logical group operands')
    elif len(predicate)!=1 or not isinstance(next(iter(predicate.values())),dict):
        raise ValueError('direct predicate must contain one named field or one explicit group')


def unflatten(require):
    if not isinstance(require,dict) or 'items' not in require:
        raise ValueError('require must contain items')
    if set(require)=={'items'}:
        return decode(require,'split')
    if 'match' not in require or not isinstance(require['match'],str):
        raise ValueError('matched requirement must name match cardinality')
    predicate={k:v for k,v in require.items() if k not in RESERVED}
    _validate_flat_predicate(predicate)
    return decode({'items':require['items'], 'match':require['match'],
                   'condition':records_to_source(predicate)},'split')


def flat_doc(doc,counts=None):
    out=deepcopy(doc)
    for ck in out['checks'].values():
        ck['require']=flatten(ck['require'],counts)
    return out


def source_doc(doc):
    out=deepcopy(doc)
    for ck in out['checks'].values():
        ck['require']=unflatten(ck['require'])
    return out


def schema_for_flat(base):
    """Strict Item/match modes with an inlined named field or explicit group.

    Leaves are constrained to one named field. Grouped fields/states have an
    explicit scope and operator. Capability-specific field/operator completion
    remains a separate contract as in the prior research schema.
    """
    schema=deepcopy(base)
    schema['$id']='https://scap-ng.dev/research/english-first-04/flat-require.editor.schema.json'
    schema['title']='RESEARCH ONLY: flat require without condition or record true'
    entries=[{'type':'object','required':['items'],'additionalProperties':False,
              'properties':{'items':{'enum':[v[0] for v in PRESENCE.values()]}}}]
    for items,match,_ in COMPARISONS.values():
        basic={'items':{'const':items},'match':{'const':match}}
        # One inline predicate, field name is not hardcoded into the language.
        # 'and'/'or' as literal observed fields remain legal in single-field form.
        leaf={'type':'object','required':['items','match'],
              'minProperties':3,'maxProperties':3,
              'properties':basic,
              'patternProperties':{'^(?!(?:items|match)$).+$':{'type':'object','minProperties':1}},
              'additionalProperties':False}
        entries.append(leaf)
        for scope in ('states','fields'):
            for op in ('and','or'):
                props={**basic,'scope':{'const':scope},op:{'type':'array',
                        'minItems':2 if scope=='states' else 1,
                        'items':{'$ref':'#/$defs/stateNode'}}}
                if scope=='fields':
                    props['all_fields_must_exist']={'const':True}
                entries.append({'type':'object','required':['items','match','scope',op],
                                'properties':props,'additionalProperties':False})
    schema['$defs']['requirement']={'oneOf':entries}
    Draft202012Validator.check_schema(schema)
    return schema


def census(archive,base_schema,out_dir):
    digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest!=PINNED:
        raise ValueError('pinned corpus SHA256 mismatch')
    base=json.loads(Path(base_schema).read_text())
    flat_schema=schema_for_flat(base)
    validator=Draft202012Validator(flat_schema)
    counts=Counter(); modes=Counter(); failures=[]; samples={}; collisions=[]
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for path in sorted(z.namelist()):
            if not(path.startswith('authoring/') and '/assessments/' in path and path.endswith('.yaml')):
                continue
            src=(yaml.safe_load(z.read(path)) or {}).get('assessment') or {}
            if src.get('mode')!='automated' or not isinstance(src.get('tests'),dict) or not src['tests']:
                continue
            counts['assessments']+=1; counts['tests']+=len(src['tests'])
            try:
                fixed=to_fixed(src)
                candidate=flat_doc(fixed,counts)
                error=next(validator.iter_errors(candidate),None)
                if error is not None:
                    raise ValueError('flat editor schema: '+str(error.message)[:160])
                if source_doc(candidate)!=fixed or from_fixed(source_doc(candidate))!=src:
                    raise ValueError('full source dictionary mismatch')
                counts['exact_assessments']+=1
                counts['exact_tests']+=len(src['tests'])
                for ck in fixed['checks'].values():
                    modes[ck['require']['items']]+=1
                if path in SAMPLES.values():
                    label=next(k for k,v in SAMPLES.items() if v==path)
                    samples[label]=candidate
                # Invalid-input guard: an inserted `condition` wrapper MUST fail.
                invalid=deepcopy(candidate)
                next(iter(invalid['checks'].values()))['require']['condition']={'value':{'is':'bad'}}
                if validator.is_valid(invalid):
                    raise ValueError('schema accepted old condition wrapper')
                try:source_doc(invalid)
                except (ValueError,TypeError,KeyError):pass
                else:raise ValueError('decoder accepted old condition wrapper')
                counts['negative_guards']+=1
            except (ValueError,TypeError,KeyError,AssertionError) as e:
                failures.append({'path':path,'error':str(e)[:350]})
                if 'collides with reserved' in str(e):collisions.append(path)
    if (counts['assessments'],counts['tests'])!=(872,1375):
        raise AssertionError('corpus drift')
    (out/'flat-require.editor.schema.json').write_text(json.dumps(flat_schema,indent=2)+'\n')
    for label,doc in samples.items():
        (out/(label+'.flat.research.yaml')).write_text('# RESEARCH ONLY; not normative or scanner validated\n'
          +yaml.safe_dump(doc,sort_keys=False,allow_unicode=True,width=110))
    result={'source_sha256':digest,'counts':dict(counts),'modes':dict(modes),
            'failures':failures,'collisions':collisions,
            'samples':sorted(samples),
            'limits':['Structural source-dictionary inversion only, not independent scanner parity.',
            '201 legacy all_exist Test uses preserved rather than semantically normalized.',
            'Existing grouped-State and nested field semantics unchanged.',
            'Capability-specific editors still need full typed mappings.']}
    (out/'report.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (out/'report.md').write_text(markdown_report(result))
    return result


def markdown_report(r):
    c=r['counts']; lines=[
      '# Removing `condition` and record `: true` — six-STIG research proof','',
      '**Experimental authoring only; not an adopted 0.4 schema or independent scanner proof.**','',
      f"- Corpus **{c['assessments']} automated Assessments / {c['tests']} Tests**.",
      f"- Flat direct-field requirement: **{c['exact_assessments']}/{c['assessments']} Assessments**, **{c['exact_tests']}/{c['tests']} Tests** reconstructed exactly.",
      f"- Redundant `at_least_one_record_exists: true` flags replaced: **{c['redundant_record_true_removed']}**.",
      f"- Fail-closed malformed `condition` wrapper probes: **{c['negative_guards']}**.",
      f"- Reserved Item/match predicate name collisions: **{len(r['collisions'])}** Assessments.",'',
      '## Real RHEL nosuid check (same original source meaning)','',
      '```yaml','require:','  items: at_least_one','  match: all',
      '  mount_options: {at_least_one_value_is: nosuid}','```','',
      '## Windows WMI record-group example (whole States must stay separate)','',
      '```yaml','require:','  items: at_least_one','  match: all','  scope: states','  or:',
      '    - result:','        records: at_least_one','        match: all','        domainrole: {is: "1"}',
      '    - result:','        records: at_least_one','        match: all','        domainrole: {is: "3"}',
      '```','',
      'This is **not** equivalent to flattening entire States into `domainrole: {in: [1, 3]}`.','',
      '## Requirements and boundaries','',
      'The source structure, Item/cardinality requirements and all nested record semantics are source-exact for admitted Assessments. Missing/error/incomplete results have **not** been independently executed.',
      'Literal field-level Boolean checks (`is: true`, `is: false`) are untouched: these are **meaningful data comparisons**, not meaningless marker flags.',
      'Other Boolean control fields (such as inherited field-presence rules) need separately verified elimination if they affect semantics.','',
      '## Failures','']
    lines += ['- `'+e['path']+'` — '+e['error'] for e in r['failures']]
    lines += ['','## Complete examples','',
      'The adjacent five `*.flat.research.yaml` files contain complete authoring research Assessments. Each was reconstructed against the pinned source when admitted.','']
    return '\n'.join(lines)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--archive',required=True)
    ap.add_argument('--base-schema',required=True)
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    print(json.dumps(census(a.archive,a.base_schema,a.out),indent=2)[:4800])