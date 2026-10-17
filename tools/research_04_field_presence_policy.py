#!/usr/bin/env python3
"""Issue #235: test-level field presence vs broad `scope: items_and_fields`.

This research-only presentation moves the inherited State-field policy into the
one contiguous `require` block. Group-local and record-local meaning is retained.
Only exact source dictionary inversion is asserted, not scanner/OVAL parity.
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
from research_04_flat_require import flat_doc, source_doc
from research_04_consistent_quantifiers import document_to_consistent, document_to_flat
from research_04_canonical_operators import (
    to_canonical_document, from_canonical_document, schema_for_canonical,
)

SOURCE_TO_POLICY={
    'all_state_fields_exist':'all',
    'all_state_fields_when_present':'if_present',
}
POLICY_TO_SOURCE={value:key for key,value in SOURCE_TO_POLICY.items()}
assert len(POLICY_TO_SOURCE)==len(SOURCE_TO_POLICY)


def to_policy(doc,counts=None):
    out=deepcopy(doc)
    for check in out['checks'].values():
        inherited=set(check)&set(SOURCE_TO_POLICY)
        if len(inherited)>1:
            raise ValueError('conflicting inherited State-field policies')
        require=check['require']
        if 'field_presence' in require:
            raise ValueError('inherited State-field policy conflict')
        if inherited:
            source=next(iter(inherited))
            if check[source] is not True or set(require)=={'items'}:
                raise ValueError('inapplicable source State-field policy')
            # Insert immediately after the Item `match`, before States/predicates.
            new={}
            for k,v in require.items():
                new[k]=v
                if k=='match':new['field_presence']=SOURCE_TO_POLICY[source]
            check['require']=new
            del check[source]
            if counts is not None:counts['inherited_'+SOURCE_TO_POLICY[source]]+=1
        if counts is not None:
            for node in walk(require):
                if isinstance(node,dict) and set(node)=={'fields'}:
                    if node['fields'].get('presence')=='all':
                        counts['local_field_group_presence_all']+=1
    return out


def walk(node):
    yield node
    if isinstance(node,dict):
        for val in node.values():yield from walk(val)
    elif isinstance(node,list):
        for val in node:yield from walk(val)


def from_policy(doc):
    out=deepcopy(doc)
    for check in out['checks'].values():
        if set(check)&set(SOURCE_TO_POLICY):
            raise ValueError('old Test-level :true field-presence flags are forbidden')
        req=check['require']
        # This policy has a precise root level; it cannot cascade to records.
        for k,v in req.items():
            if k!='field_presence':
                for child in walk(v):
                    if isinstance(child,dict) and 'field_presence' in child:
                        raise ValueError('field_presence nested outside requirement root')
        if 'field_presence' in req:
            value=req['field_presence']
            if value not in POLICY_TO_SOURCE or set(req)=={'items','field_presence'}:
                raise ValueError('unsupported top-level State-field policy')
            check[POLICY_TO_SOURCE[value]]=True
            del req['field_presence']
    return out


def schema_policy(base):
    s=schema_for_canonical(base)
    s['$id']='https://scap-ng.dev/research/english-first-04/field-presence-policy.schema.json'
    s['title']='RESEARCH ONLY: State-field policy scoped to one requirement'
    check=s['$defs']['check']
    for old in SOURCE_TO_POLICY:
        check['properties'].pop(old,None)
    entries=s['$defs']['requirement']['allOf'][0]['oneOf']
    for entry in entries[1:]:
        entry['properties']['field_presence']={'enum':['all','if_present'],
            'description':'Apply this presence requirement to State fields of every State in this Check, not to Item counts or nested record subfields.'}
        if 'maxProperties' in entry:entry['maxProperties']+=1
        for old_pattern, item_contract in list(entry.get('patternProperties',{}).items()):
            if old_pattern.startswith('^(?!(?:'):
                del entry['patternProperties'][old_pattern]
                entry['patternProperties']['^(?!(?:field_presence|'+old_pattern[len('^(?!(?:'):]]=item_contract
    # Prevent accidental insertion of field_presence in nested field/map clauses.
    s['$defs']['noNestedFieldPresence']={
        'if':{'type':'object'},
        'then':{'propertyNames':{'not':{'const':'field_presence'}},
                'additionalProperties':{'$ref':'#/$defs/noNestedFieldPresence'}},
        'else':{'if':{'type':'array'},'then':{'items':{'$ref':'#/$defs/noNestedFieldPresence'}}},
    }
    # Validating nested policy precision requires separate root-level rules;
    # the source inversion decoder additionally rejects nested keys.
    Draft202012Validator.check_schema(s)
    return s


def proof(archive,base_schema,output):
    digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest!=PINNED:raise ValueError('pinned six-STIG source changed')
    base=json.loads(Path(base_schema).read_text())
    schema=schema_policy(base)
    validator=Draft202012Validator(schema)
    counts=Counter(); errors=[]; samples={}
    with zipfile.ZipFile(archive) as z:
        for path in sorted(z.namelist()):
            if not(path.startswith('authoring/') and '/assessments/' in path and path.endswith('.yaml')):continue
            original=(yaml.safe_load(z.read(path)) or {}).get('assessment') or {}
            if original.get('mode')!='automated' or not isinstance(original.get('tests'),dict) or not original['tests']:continue
            counts['assessments']+=1;counts['tests']+=len(original['tests'])
            try:
                fixed=to_fixed(original)
                flat=flat_doc(fixed)
                consistent=document_to_consistent(flat)
                canonical=to_canonical_document(consistent)
                candidate=to_policy(canonical,counts)
                err=next(validator.iter_errors(candidate),None)
                if err:raise ValueError('schema: '+err.message[:180])
                inverted=from_policy(candidate)
                if (inverted!=canonical or from_canonical_document(inverted)!=consistent
                    or document_to_flat(consistent)!=flat
                    or from_fixed(source_doc(flat))!=original):
                    raise ValueError('complete Assessment source mismatch')
                counts['exact_assessments']+=1;counts['exact_tests']+=len(original['tests'])
                if path in SAMPLES.values():
                    samples[next(k for k,v in SAMPLES.items() if v==path)]=candidate
                bad=deepcopy(candidate)
                ck=next(iter(bad['checks'].values()))
                ck['all_state_fields_exist']=True
                if validator.is_valid(bad):raise ValueError('schema accepted obsolete boolean flag')
                try:from_policy(bad)
                except ValueError:pass
                else:raise ValueError('inverse accepted obsolete boolean flag')
                counts['invalid_bool_rejected']+=1
            except (ValueError,AssertionError,KeyError,TypeError) as e:
                errors.append({'path':path,'error':str(e)[:260]})
    if (counts['assessments'],counts['tests'])!=(872,1375):raise ValueError('corpus drift')
    dest=Path(output);dest.mkdir(parents=True,exist_ok=True)
    (dest/'field-presence-policy.editor.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
    for label,doc in samples.items():
        (dest/(label+'.field-policy.research.yaml')).write_text('# Research only: source-structural inversion, not scanner parity\n'+yaml.safe_dump(doc,sort_keys=False,width=108,allow_unicode=True))
    result={'source_sha256':digest,'counts':dict(counts),'errors':errors,'samples':sorted(samples)}
    (dest/'report.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (dest/'report.md').write_text(report(result))
    return result


def report(r):
    c=r['counts']
    lines=['# State-wide field presence versus a combined Item/field scope — six-STIG research','',
       '**Research only; structural inversion, not independent OVAL six-state/evidence parity or an approved v0.4 grammar.**','',
       f"- Source corpus: {c['assessments']} Assessments / {c['tests']} named Tests.",
       f"- Exact source reconstruction: **{c['exact_assessments']}/{c['assessments']}** complete Assessments / **{c['exact_tests']}/{c['tests']}** Tests.",
       f"- Test-inherited State-field policies lifted inside `require`: **{c['inherited_all']+c['inherited_if_present']}** (required={c['inherited_all']}, optional={c['inherited_if_present']}).",
       f"- Local State `fields.presence: all` groups retained: **{c['local_field_group_presence_all']}** (counts per admitted Check).",
       f"- Old Boolean flag mutations rejected: **{c['invalid_bool_rejected']}**.",'',
       '## Three independent real patterns','',
       '**DNS — Items required, State-wide field presence required; separate complete States preserved:**','',
       '```yaml','require:','  items: at_least_one','  match: all','  field_presence: all','  states:','    and:',
       '      - stdout_line: {greater_than_or_equal: 48}',
       '      - stdout_line: {less_than_or_equal: 168}','```','',
       '**Linux user initialization files — Items optional; all eight specified fields required on any Item that exists:**','',
       '```yaml','require:','  items: if_present','  match: all','  fields:','    and:',
       '      - setuid: {equals: false}','      - setgid: {equals: false}',
       '    presence: all','```','',
       '**Apache optional configuration field — Item required, field may be absent:**','',
       '```yaml','require:','  items: at_least_one','  match: all',
       '  stdout_line: {when_present_matches_regex: "KeepAlive On"}','```','',
       '## Does `scope: items|items_and_fields` solve these cases?','',
       '| Source class | Item existence | Field presence | Why a combined scope is insufficient |',
       '| --- | --- | --- | --- |',
       '| DNS validity | at_least_one | all fields required | One broad `items_and_fields` label could abbreviate this case only |',
       '| Linux user files | if_present | all fields required *when an Item exists* | Optional Items do not imply optional fields |',
       '| Apache config | at_least_one | optional field | Required Items do not imply required fields |',
       '| Windows WMI record | at_least_one | record-local fields and two whole State branches | A Check-level scope must not silently alter record cardinality or State `or` |','',
       '`scope` is useful to disambiguate what a boolean `and`/`or` combines only when structure does not already identify that scope. Here, `states.and/or` and `fields.and/or` already identify grouping. The unresolved axis is field **presence policy**, not the object being scoped.','',
       '**Experimental preference:** use a single `field_presence: all|if_present` at the owning requirement for an inherited State policy, and `fields.presence: all` for group-local constraints. Do not apply it implicitly to nested records; local overrides remain explicit. No invented defaults.','',
       '## Remaining boundaries','',
       '- This is a reversible renaming of original Test-wide `all_state_fields_exist: true` and `all_state_fields_when_present: true`, not new runtime semantics.',
       '- Leaf comparisons may still carry required/optional/absent value semantics; the `no_values_exist` and `when_present_*` family needs separate study.',
       '- An explicit group-local `fields.presence` is not necessarily equivalent to a Test-wide inherited `field_presence`; no global hoist across States without proof.',
       '- Independent scanner/evidence parity, missing/error/incomplete statuses, and the known contradictory bootloader case remain open.','',
       '## Rejected source','']
    lines.extend('- `'+a['path']+'` — '+a['error'] for a in r['errors'])
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--base-schema',required=True);p.add_argument('--out',required=True)
    args=p.parse_args()
    print(json.dumps(proof(args.archive,args.base_schema,args.out),indent=2)[:5000])