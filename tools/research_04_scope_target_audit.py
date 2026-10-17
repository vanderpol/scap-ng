#!/usr/bin/env python3
"""#235: six-STIG source census testing proposed items+fields combined scopes.

Source-structure evidence only. Do not infer scanner/evidence six-state parity
or adopt merged cardinality settings as native semantics.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile
import yaml
from research_04_fixed_require_editor import PINNED


def collect_field_modes(states, inherited=None):
    """Return effective ordinary scalar field modes and distinct record count.

    Record requirements are deliberately separate: a Test/group scalar field
    policy MUST NOT silently cascade into record members.
    """
    modes=[]; records=0; missing=[]; scopes=Counter()
    def rec(node, policy):
        nonlocal records
        if isinstance(node,list):
            for entry in node: rec(entry,policy)
            return
        if not isinstance(node,dict):
            raise ValueError('invalid State node')
        groups=[key for key in ('and','or') if key in node and isinstance(node[key],list)]
        if groups:
            if len(groups)!=1 or set(node)-set(groups)-{'state_fields_require'}:
                raise ValueError('ambiguous state group')
            new_policy=node.get('state_fields_require',policy)
            if 'state_fields_require' in node: scopes['group']+=1
            rec(node[groups[0]],new_policy)
            return
        if len(node)!=1:
            raise ValueError('state leaf has multiple fields')
        name,field=next(iter(node.items()))
        if not isinstance(field,dict):
            raise ValueError('state field is not a mapping')
        if 'record' in field:
            records+=1
            return
        effective=field.get('require',policy)
        if effective is None:missing.append(name)
        else:modes.append((name,effective))
    rec(states,inherited)
    return modes,records,missing,scopes


def census(path):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=PINNED:
        raise ValueError('unexpected six-STIG archive SHA256')
    counts=Counter(); source_examples={}; distributions=Counter(); failures=[]
    examples_by_kind={}
    with zipfile.ZipFile(path) as z:
        for file in sorted(z.namelist()):
            if not(file.startswith('authoring/') and '/assessments/' in file and file.endswith('.yaml')): continue
            a=(yaml.safe_load(z.read(file)) or {}).get('assessment') or {}
            if a.get('mode')!='automated' or not isinstance(a.get('tests'),dict) or not a['tests']:
                continue
            counts['assessments']+=1
            for name,test in a['tests'].items():
                counts['tests']+=1
                if not isinstance(test.get('states'),list) or not test['states']:
                    counts['tests_no_states']+=1
                    continue
                counts['tests_with_states']+=1
                try:
                    fields,record_count,missing,group_scopes=collect_field_modes(test['states'],test.get('state_fields_require'))
                except (TypeError,ValueError) as e:
                    failures.append(dict(file=file,test=name,error=str(e)))
                    continue
                counts['ordinary_field_leaves']+=len(fields)
                counts['record_leaf_wrappers']+=record_count
                counts['missing_ordinary_field_policy']+=len(missing)
                counts['group_field_policies']+=group_scopes['group']
                if test.get('state_fields_require') is not None:counts['tests_with_shared_scalar_policy']+=1
                if record_count:counts['tests_containing_record']+=1
                if not fields:
                    counts['tests_with_only_records_or_no_fields']+=1
                    continue
                counts['tests_with_scalar_fields']+=1
                item_mode=test.get('collected_items_require')
                field_modes=[mode for name,mode in fields]
                unique=set(field_modes)
                classifications={}
                if len(unique)==1:
                    counts['same_policy_all_scalar_fields']+=1
                    classifications['same_scalar_policy']=True
                    if len(fields)>=2:counts['same_policy_multiple_fields']+=1
                else:counts['mixed_field_policies']+=1
                if unique=={item_mode}:
                    counts['item_policy_equals_all_scalar_policies']+=1
                    classifications['same_as_items']=True
                    if record_count==0:
                        counts['possible_combined_item_field_alias_no_records']+=1
                        classifications['candidate_both']=True
                    else:counts['possible_combined_but_record_isolation_required']+=1
                else:
                    counts['item_policy_differs_from_some_fields']+=1
                    classifications['differs']=True
                if any(m.startswith('none_') or m=='none_exist' for m in unique):
                    counts['tests_with_absent_field_policy']+=1
                if any(m.startswith('may_be_absent') for m in unique):
                    counts['tests_with_optional_field_policy']+=1
                if any(m.startswith('only_one') or m.startswith('at_least_one_exists_and_only_one') for m in unique):
                    counts['tests_with_exactly_one_field_policy']+=1
                distributions[('item:'+str(item_mode),'mixed' if len(unique)>1 else next(iter(unique)))]+=1
                for kind in classifications:
                    if kind not in examples_by_kind:
                        examples_by_kind[kind]={
                            'source':file,'test':name,'item_mode':item_mode,
                            'scalar_fields':fields[:12], 'record_count':record_count,
                            'shared_test_field_policy':test.get('state_fields_require')}
    if counts['assessments']!=872 or counts['tests']!=1375:
        raise AssertionError('unexpected source corpus: '+repr(counts))
    return {'counts':dict(counts),'examples':examples_by_kind,
            'mode_pairs':[{'item_and_field_mode':k[0]+' / '+k[1],'tests':v} for k,v in distributions.most_common(16)],
            'parse_exceptions':failures,
            'limits':[
             'Raw Test/field source-requirement equality only, NOT proof that Items and scalar field Values share a six-state evaluation domain.',
             'Record fields are independently quantified and never implicitly inherit ordinary State-field policy.',
             'A combined-scope shorthand needs its own exact AST lowering and negative six-state tests before it could be admitted.',
             'The six STIG source has one known original invalid none_exist+State Test; this descriptive census does not accept that Test as valid grammar.'
            ]}


def markdown(r):
    c=r['counts']; lines=['# Combined Item/field scope — real six-STIG feasibility audit','',
      '**Research only; no proposed `scope: items_and_fields` form is approved or source-evaluator verified.**','',
      'The question is whether one cardinality declaration can apply to both **collected Items** and **ordinary State field values**. They are different populations, and Windows record members form another separate population. Equal source enum names do not imply identical data or scanner result behavior.','',
      f"- Corpus: **{c['assessments']} unique automated Assessments / {c['tests']} named Tests**.",
      f"- With States: **{c['tests_with_states']}**; with ordinary scalar field leaves: **{c['tests_with_scalar_fields']}**.",
      f"- Ordinary scalar field requirements with one common mode: **{c['same_policy_all_scalar_fields']} Tests**, including **{c.get('same_policy_multiple_fields',0)}** with multiple scalar fields.",
      f"- Field requirements differ from their Item Test requirement in at least one scalar field: **{c['item_policy_differs_from_some_fields']} Tests**.",
      f"- Entire scalar field set uses the *same named requirement mode* as the Item Test: **{c['item_policy_equals_all_scalar_policies']} Tests**; no record wrapper: **{c['possible_combined_item_field_alias_no_records']} Tests**.",
      f"- Tests containing records: **{c['tests_containing_record']}**; record wrappers found: **{c['record_leaf_wrappers']}**.",
      f"- Shared Test-level scalar field policies: **{c.get('tests_with_shared_scalar_policy',0)} Tests**; grouped ones: **{c.get('group_field_policies',0)}**.",
      f"- Missing effective scalar field requirements: **{c.get('missing_ordinary_field_policy',0)}** (expected 0).",
      '', '## Key comparisons', '',
      '| Approach | Reader sees | Risk |', '| --- | --- | --- |',
      '| Separate Item and shared field rule | `items` and `match`; group-level `fields` policy | Slight duplication, but each population is explicit |',
      '| New `scope: items_and_fields` shorthand | One policy targets two populations | Wrong or misleading for differing cardinalities; additional branch in editor grammar |',
      '| Structural `fields` grouping, no `scope` key | Item rules stay at `require`; any field policy applies only within its `fields` structure | Can avoid repeated field clauses without pretending Item and field matching are the same |',
      '', '## Counterexamples from actual source intent', '',
      '- RHEL `/home` nosuid: all selected *Items* pass if each partition has **at least one** `nosuid` option; not all mount-option values need equal `nosuid`. A shared Item+field `match: all` is incorrect for `rw,nosuid`.',
      '- Apache optional `stdout_line`: the collected shellcommand Item must exist while a State field can be absent; one shared Item/field presence policy would change this.',
      '- Windows user-right membership: at least one collected Item *matches*, while its `trustee_name` field has its own value-presence/matching rule; do not conflate count of matching Items with count of member values.',
      '- WMI `result.record` and its `domainrole` field are independent nested populations and must not inherit a scalar State-field policy by accident.',
      '', '## Recommendation for next design iteration', '',
      'Prefer a **shared field policy at the nearest existing `fields` group or Test scope, with explicit leaf overrides**; reserve combined Item+field shorthand unless its corpus benefit and lossless AST expansion justify a new `scope` keyword. A missing policy at every ancestor must be rejected, not silently defaulted. Keep no `condition` wrapper. The prior independently verified scoped prototype saved **1,106 / 2,550** requirement declarations (43.4%) across six benchmark appearances; that is not a new unique-Test count from this report.',
      '', '## Real source examples for why the scope matters', '']
    for kind,example in r['examples'].items():
        lines.append(f"- **{kind}:** `{example['source']}` / `{example['test']}`; Item mode `{example['item_mode']}`; scalar field modes `{sorted(set(mode for _,mode in example['scalar_fields']))}`; record wrappers {example['record_count']}.")
    if r['parse_exceptions']:
        lines+=['','## Unparsed source structure (do not infer grammar support)','']
        for x in r['parse_exceptions'][:20]: lines.append('- `'+x['source'] if 'source' in x else '- `'+x['file']+'` / `'+x['test']+'`: '+x['error'])
    lines+=['','## Evidence boundary','']+['- '+v for v in r['limits']]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True)
    p.add_argument('--output',required=True)
    opts=p.parse_args();report=census(opts.archive)
    folder=Path(opts.output);folder.mkdir(parents=True,exist_ok=True)
    (folder/'scope-target-audit.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (folder/'scope-target-audit.md').write_text(markdown(report))
    print(json.dumps(report['counts'],indent=2,sort_keys=True))