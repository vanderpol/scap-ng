#!/usr/bin/env python3
"""Research #235: compare holistic vs explicit Item/State requirement authoring.

Both are reversible presentations of the already source-exact fixed-require pilot.
They are research candidates, NOT approved syntax; OVAL execution not tested.
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

# The existing independently exercised 871/872 authoring lowerer is our baseline.
from research_04_fixed_require_editor import to_fixed, from_fixed, PINNED, SAMPLES

# Each pair remains distinct for SOURCE inversion, even if future native semantics
# prove redundant (e.g., exactly_one + all vs exactly_one + exactly_one).
PRESENCE = {
    'at_least_one': ('at_least_one', 'at_least_one_exists'),
    'exactly_one': ('exactly_one', 'exactly_one_exists'),
    'none': ('none', 'none_exist'),
    'if_present': ('if_present', 'if_present'),
    'all_exist': ('legacy_all_exist', 'legacy_all_exist'),
}
COMPARISONS = {
    'at_least_one_all_match': ('at_least_one', 'all', 'at_least_one_exists_and_all_match'),
    'at_least_one_some_match': ('at_least_one', 'some', 'at_least_one_exists_and_some_match'),
    'at_least_one_one_match': ('at_least_one', 'exactly_one', 'at_least_one_exists_and_exactly_one_matches'),
    'if_present_all_match': ('if_present', 'all', 'if_present_all_match'),
    'if_present_some_match': ('if_present', 'some', 'if_present_some_match'),
    'if_present_none_match': ('if_present', 'none', 'if_present_none_match'),
    'exactly_one_all_match': ('exactly_one', 'all', 'exactly_one_exists_and_all_match'),
    'exactly_one_one_match': ('exactly_one', 'exactly_one', 'exactly_one_exists_and_exactly_one_matches'),
    'all_exist_all_match': ('legacy_all_exist', 'all', 'legacy_all_exist_and_all_match'),
    'all_exist_none_match': ('legacy_all_exist', 'none', 'legacy_all_exist_and_none_match'),
}
MERGED_TO_SOURCE = {name: src for src, (_, name) in PRESENCE.items()}
MERGED_TO_SOURCE.update({data[2]: src for src, data in COMPARISONS.items()})
SPLIT_TO_SOURCE = {(items, match): src for src, (items, match, _) in COMPARISONS.items()}
assert len(MERGED_TO_SOURCE) == len(PRESENCE) + len(COMPARISONS) == 15
assert len(SPLIT_TO_SOURCE) == len(COMPARISONS)


def encode(require, style):
    """No hidden defaults: every source mode has exactly one reversible encoding."""
    if not isinstance(require, dict) or set(require) not in ({'items'}, {'items','condition'}):
        raise ValueError('unexpected source requirement shape')
    source = require['items']
    if set(require) == {'items'} and source in PRESENCE:
        items, name = PRESENCE[source]
        return {'items': items} if style == 'split' else {name: True} if style == 'merged' else _bad()
    if set(require) == {'items','condition'} and source in COMPARISONS:
        items, match, name = COMPARISONS[source]
        cond = deepcopy(require['condition'])
        if not isinstance(cond,dict) or not cond:
            raise ValueError('condition must be nonempty')
        if style == 'split':
            return {'items': items, 'match': match, 'condition': cond}
        if style == 'merged':
            return {name: cond}
    raise ValueError('unsupported item/match combination or presentation')


def _bad():
    raise ValueError('unknown presentation')


def decode(require, style):
    if not isinstance(require,dict):
        raise ValueError('require must be mapping')
    if style == 'split':
        if set(require) == {'items'}:
            lookup = {val[0]: src for src, val in PRESENCE.items()}
            mode = lookup.get(require['items'])
            if mode is None:
                raise ValueError('unlisted presence mode')
            return {'items': mode}
        if set(require) != {'items','match','condition'}:
            raise ValueError('split require needs items, match and condition')
        mode = SPLIT_TO_SOURCE.get((require['items'], require['match']))
        if mode is None:
            raise ValueError('unsupported items + match combination')
        condition = require['condition']
    elif style == 'merged':
        if len(require)!=1:
            raise ValueError('merged requirement must have one named clause')
        key, condition = next(iter(require.items()))
        mode = MERGED_TO_SOURCE.get(key)
        if mode is None:
            raise ValueError('unknown merged phrase')
        if mode in PRESENCE:
            if condition is not True:
                raise ValueError('presence-only requirement must be true')
            return {'items':mode}
    else:
        return _bad()
    if not isinstance(condition,dict) or not condition:
        raise ValueError('State-bearing condition must be nonempty')
    return {'items':mode,'condition':deepcopy(condition)}


def schema_for(base,style):
    schema=deepcopy(base)
    schema['$id']='https://scap-ng.dev/research/english-first-04/require-'+style+'.schema.json'
    schema['title']='RESEARCH: '+style+' requirement presentation; not normative'
    entries=[]
    if style=='split':
        entries.append({
            'type':'object','required':['items'],'additionalProperties':False,
            'properties': {'items': {'type':'string','enum':[v[0] for v in PRESENCE.values()]}}
        })
        for items,match,_ in COMPARISONS.values():
            entries.append({
                'type':'object','required':['items','match','condition'],
                'additionalProperties':False,
                'properties':{'items':{'const':items},'match':{'const':match},
                              'condition':{'$ref':'#/$defs/condition'}}
            })
    elif style=='merged':
        for src,(_,name) in PRESENCE.items():
            entries.append({'type':'object','required':[name],'additionalProperties':False,
                            'properties':{name:{'const':True}}})
        for src,(_,_,name) in COMPARISONS.items():
            entries.append({'type':'object','required':[name],'additionalProperties':False,
                            'properties':{name:{'$ref':'#/$defs/condition'}}})
    else:
        _bad()
    schema['$defs']['requirement']={'oneOf':entries}
    Draft202012Validator.check_schema(schema)
    return schema


def transformed(doc,style):
    result=deepcopy(doc)
    for check in result['checks'].values():
        check['require']=encode(check['require'],style)
    return result


def reverted(doc,style):
    result=deepcopy(doc)
    for check in result['checks'].values():
        check['require']=decode(check['require'],style)
    return result


def proof(archive,base_schema,output,samples):
    digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest!=PINNED:
        raise ValueError('six-STIG archive SHA256 differs from pinned baseline')
    base=json.loads(Path(base_schema).read_text())
    schemas={s:schema_for(base,s) for s in ('split','merged')}
    validators={s:Draft202012Validator(v) for s,v in schemas.items()}
    counts=Counter()
    modes=Counter()
    failures=[]
    sums={s:Counter() for s in ('split','merged')}
    chosen={}
    with zipfile.ZipFile(archive) as z:
        for path in sorted(z.namelist()):
            if not (path.startswith('authoring/') and '/assessments/' in path and path.endswith('.yaml')):
                continue
            orig=(yaml.safe_load(z.read(path)) or {}).get('assessment') or {}
            if orig.get('mode')!='automated' or not isinstance(orig.get('tests'),dict) or not orig['tests']:
                continue
            counts['assessments']+=1
            counts['tests']+=len(orig['tests'])
            try:
                fixed=to_fixed(orig)
                if not Draft202012Validator(base).is_valid(fixed):
                    raise ValueError('existing editor schema did not accept original')
                converted={style:transformed(fixed,style) for style in validators}
                for style,candidate in converted.items():
                    err=next(validators[style].iter_errors(candidate),None)
                    if err is not None:
                        raise ValueError(style+' schema: '+str(err.message)[:180])
                    recovered=reverted(candidate,style)
                    if recovered!=fixed or from_fixed(recovered)!=orig:
                        raise ValueError(style+' failed complete dictionary reconstruction')
                    counts[style+'_exact_assessments']+=1
                    counts[style+'_exact_tests']+=len(orig['tests'])
                    # Negative guards per admitted Assessment; both decoder and schema must reject.
                    altered=deepcopy(candidate)
                    req=next(iter(altered['checks'].values()))['require']
                    req['invented_key']=1
                    if validators[style].is_valid(altered):
                        raise ValueError(style+' schema incorrectly accepted unexpected key')
                    try:
                        reverted(altered,style)
                    except ValueError:
                        pass
                    else:
                        raise ValueError(style+' decoder incorrectly accepted unexpected key')
                    counts['negative_schema_decoder_guards']+=1
                    for check in candidate['checks'].values():
                        r=check['require']
                        # Compare only the requirement expression, not unchanged data graph.
                        emitted=yaml.safe_dump({'require':r},sort_keys=False,allow_unicode=True)
                        sums[style]['yaml_chars']+=len(emitted)
                        sums[style]['yaml_lines']+=len(emitted.splitlines())
                        sums[style]['max_line_length']=max(sums[style]['max_line_length'],
                                                          max(map(len,emitted.splitlines())))
                for check in fixed['checks'].values():
                    modes[check['require']['items']]+=1
                    counts['checks']+=1
                if path in SAMPLES.values():
                    chosen[path]={style:converted[style] for style in converted}
            except (ValueError,TypeError,AssertionError,KeyError) as e:
                failures.append({'path':path,'error':str(e)[:230]})
    if counts['assessments']!=872 or counts['tests']!=1375:
        raise RuntimeError('expected 872 Assessments, 1375 Tests, got '+str(dict(counts)))
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    for style, schema in schemas.items():
        (out/('require-'+style+'.schema.json')).write_text(json.dumps(schema,indent=2)+'\n')
    for path,both in chosen.items():
        label=next(k for k,v in SAMPLES.items() if v==path)
        for style,content in both.items():
            (out/(label+'.'+style+'.research.yaml')).write_text(
                '# RESEARCH ONLY: source structural equality, NOT scanner parity\n'
                + yaml.safe_dump(content,sort_keys=False,allow_unicode=True,width=96))
    result={'source_sha256':digest,'counts':dict(counts),'mode_distribution':dict(modes),
            'presentation_size':{s:dict(v) for s,v in sums.items()},'failures':failures,
            'legacy_all_exist_tests':sum(v for m,v in modes.items() if m.startswith('all_exist')),
            'samples':sorted(next(k for k,v in SAMPLES.items() if v==p) for p in chosen),
            'proof_scope':'complete structural source dictionary inversion; no scanner or human usability evidence'}
    (out/'report.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (out/'report.md').write_text(markdown_report(result))
    return result


def markdown_report(r):
    c=r['counts']; m=r['mode_distribution']; sizes=r['presentation_size']
    lines=["# Merged versus split requirements — six-STIG experimental proof", "",
       "**Research only. Neither grammar is approved; not scanner/OVAL execution parity or an auditor usability study.**", "",
       f"- Corpus: **{c['assessments']} automated Assessments**, **{c['tests']} named Tests**.",
       f"- Split: **{c['split_exact_assessments']}/{c['assessments']} full Assessments**, **{c['split_exact_tests']}/{c['tests']} Tests** exactly reconstructed.",
       f"- Merged: **{c['merged_exact_assessments']}/{c['assessments']} full Assessments**, **{c['merged_exact_tests']}/{c['tests']} Tests** exactly reconstructed.",
       f"- Both: {c['negative_schema_decoder_guards']} invalid-input mutations rejected by schema AND decoder.",
       f"- Source-legacy all_exist Tests retained explicitly: **{r['legacy_all_exist_tests']}**. These are **not** proof they can be changed to at-least-one on incomplete observations.",
       "", "## One simple real RHEL nosuid requirement", "",
       "Split (author can see how many Items exist versus how many must match):", "",
       '```yaml', 'require:', '  items: at_least_one', '  match: all',
       '  condition:', '    mount_options: {at_least_one_value_is: nosuid}', '```', '',
       "Merged (the Item existence/match rule is named as one thought):", '',
       '```yaml', 'require:', '  at_least_one_exists_and_all_match:',
       '    mount_options: {at_least_one_value_is: nosuid}', '```', '',
       "## Measured encoding size (requirements only; not cognitive readability)", "",
       "| Presentation | YAML characters | YAML lines | Longest generated line |",
       "| --- | ---: | ---: | ---: |"]
    for style in ('split','merged'):
        t=sizes[style]
        lines.append(f"| {style} | {t['yaml_chars']} | {t['yaml_lines']} | {t['max_line_length']} |")
    lines += ["", "## Six-STIG requirement modes (source exact)", "",
              "| Source mode | Tests | Split existence / match | Merged name |",
              "| --- | ---: | --- | --- |"]
    for name,count in sorted(m.items(),key=lambda kv:(-kv[1],kv[0])):
        if name in PRESENCE:
            a,b=PRESENCE[name]; split=f'`{a}` / *(none)*'; merged=b
        else:
            a,b,merged=COMPARISONS[name];split=f'`{a}` / `{b}`'
        lines.append(f'| `{name}` | {count} | {split} | `{merged}` |')
    lines.extend(["", "## Interpreting the result", "",
      "- These two forms preserve precisely the same typed condition tree and source/collector graph; only the `require` presentation differs.",
      "- `items: none` is not `match: none`; presence and matching remain different concepts.",
      "- `items: exactly_one` detects duplicates and is not equivalent to `match: exactly_one`.",
      "- Complete Windows whole-State OR groups preserve `scope: states`; not flattened into field/record membership.",
      "- One known invalid source Assessment (`none_exist` Test with State) is expected to remain rejected.",
      "- 201 inherited `all_exist` uses remain **importer-only legacy distinctions** pending a native six-state/evidence contract. This test does not remove them.",
      "- Size reduction cannot choose the winning author syntax: blind auditor review of both versions, and independent runtime differential tests remain required.",
      "", "## Full real research examples", "",
      "Each example has both complete representations, including all original named sources and `evaluate` logic. See the adjacent `*.split.research.yaml` and `*.merged.research.yaml` files.",""])
    if r['failures']:
        lines += ['## Rejected original Assessment', '']
        for e in r['failures']:lines.append('- `'+e['path']+'` — '+e['error'])
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True)
    p.add_argument('--base-schema',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    print(json.dumps(proof(a.archive,a.base_schema,a.out,None),indent=2)[:4000])