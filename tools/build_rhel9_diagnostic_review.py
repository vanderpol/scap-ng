#!/usr/bin/env python3
"""Inventory existing output for owner diagnosis; never regenerate or normalize NG."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import yaml

ROOT=Path('research/iterations/003/source/split-rule-assessment/rhel9-full')
OUT=Path('research/iterations/003/review/rhel9-diagnostic-review')
SNAPSHOT='64d3c32231a0713fdf210bc9a2fff67387072373'
BASE=f'https://github.com/vanderpol/scap-ng/blob/{SNAPSHOT}/'
FUNCTIONS={'concat','split','count','unique','substring','begin','end','arithmetic','time_difference','escape_regex','regex_capture','glob_to_regex','merge'}

def load(p): return yaml.safe_load(p.read_text())
def link(p,label): return f'[{label}]({BASE}{p.as_posix()})'
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)

def features(a,rule):
    nodes=list(walk(a)); keys=set(k for n in nodes for k in n)
    checks=a.get('tests',a.get('checks',{})); result=set()
    if a.get('mode')=='manual': result.add('manual-only')
    if a.get('variables'): result.add('variables')
    if len(a.get('variables',{}))>1: result.add('multiple-variables')
    if any('object_values' in n for n in nodes): result.add('collection-field-extraction')
    if any('variable' in n for v in a.get('variables',{}).values() for n in walk(v.get('expression',{}))): result.add('variable-chain')
    if 'set' in keys: result.add('sets')
    if any(n.get('filters') for n in nodes): result.add('filters')
    if any(len(n.get('states',[]))>1 for n in nodes): result.add('multiple-states')
    if len(checks)>1: result.add('multiple-tests')
    if any('assert' in t and t['assert'].get('state') is None and not t['assert'].get('states') for t in checks.values()): result.add('existence-without-state')
    if any(len(n.get('all',n.get('any',[])))>1 for n in nodes if isinstance(n.get('all',n.get('any',[])),list)): result.add('boolean-composition')
    if 'not' in keys: result.add('negation')
    if any(n.get('behaviors') for n in nodes): result.add('collection-behaviors')
    if rule.get('applicability'): result.add('rule-applicability')
    for f in FUNCTIONS & keys: result.add('function:'+f)
    for t in checks.values():
        if t.get('capability'): result.add('capability:'+t['capability'])
    return sorted(result)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    paths=list((ROOT/'assessments').rglob('*.yaml'))
    assessment_index={}
    for p in paths:
        a=load(p)['assessment']
        if a['id'] in assessment_index: raise ValueError('Duplicate Assessment identity')
        assessment_index[a['id']]=(p,a)
    rows=[]; total=Counter(); flags=Counter()
    for rp in sorted((ROOT/'rules').glob('*.yaml')):
        r=load(rp)['rule']; choices=r.get('checks',{})
        if not choices or r.get('default_check') not in choices: raise ValueError('Unresolved default selector')
        target=choices[r['default_check']]
        ap,a=assessment_index[target]
        for aid in choices.values():
            if aid not in assessment_index: raise ValueError('Unresolved Assessment selection')
        fs=features(a,r)
        gaps=['Rule selection uses opaque Assessment IDs instead of relative YAML paths']
        if 'checks' in a: gaps.append('Assessment still uses checks instead of tests')
        if 'deprecated' in a: gaps.append('Assessment contains removed deprecated attribute')
        if any('collect' in n or 'object_title' in n or 'object_values' in n for n in walk(a)):
            gaps.append('Collection vocabulary migration incomplete')
        if 'collection-field-extraction' in fs:
            gaps.append('Variable embeds acquisition payload without named Collection identity')
        if a.get('variables'):
            gaps.append('Variable names lack the agreed variable marker' if any('variable' not in name for name in a['variables']) else 'Variable naming present; graph preservation unverified')
        total.update(fs); flags.update(gaps)
        rows.append({'id':r['id'],'title':r.get('title'),'mode':a.get('mode'),
                     'rule_path':rp.as_posix(),'assessment_path':ap.as_posix(),
                     'selectors':choices,'default_selector':r['default_check'],
                     'features':fs,'known_gaps':gaps,
                     'rule_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),
                     'assessment_sha256':hashlib.sha256(ap.read_bytes()).hexdigest()})
    if len(rows)!=445: raise ValueError('Expected 445 Rules')
    # Cover each observed feature, then broaden the sample with complex Rules.
    observed=set(total); remaining=set(observed); selected=[]
    anchors=['SV-257777','SV-257781','SV-258013']
    for rid in anchors:
        row=next(r for r in rows if r['id']==rid); selected.append(row); remaining-=set(row['features'])
    while remaining:
        candidates=[r for r in rows if r not in selected]
        best=max(candidates,key=lambda r:(len(set(r['features'])&remaining),len(r['features']),r['id']))
        if not (set(best['features'])&remaining): raise ValueError('Uncovered features')
        selected.append(best); remaining-=set(best['features'])
    for row in sorted(rows,key=lambda r:(-len(r['features']),r['id'])):
        if len(selected)>=24: break
        if row not in selected: selected.append(row)
    manual=next(r for r in rows if r['mode']=='manual')
    if manual not in selected: selected.append(manual)
    if set(f for r in selected for f in r['features'])!=observed: raise ValueError('Coverage mismatch')
    app=load(ROOT/'applicability.yaml')['applicability']
    for item in app:
        if not (ROOT/item['assessment']).is_file(): raise ValueError('Unresolved applicability Assessment')
    summary={'status':'diagnostic_existing_output_not_current_design_compliant',
             'snapshot_commit':SNAPSHOT,'rules':len(rows),'sample_rules':len(selected),
             'assessment_files':len(paths),'profiles':len(load(ROOT/'benchmark.yaml')['benchmark'].get('profiles',[])),
             'applicability_assessments':len(app),'default_assessment_modes':dict(Counter(r['mode'] for r in rows)),
             'observed_feature_rule_counts':dict(sorted(total.items())),
             'known_gap_rule_counts':dict(sorted(flags.items())),
             'selected_rules':[r['id'] for r in selected],
             'missing_design_coverage':['Variable reference to existing named Collection','Preserved named Collection sharing','Embedded Collection expressed in current native vocabulary'],
             'limits':['Feature detection inventories serialized keys, not source semantic fidelity.',
                       'No source regenerated or normalized. No runtime or full round-trip validation performed.',
                       'Pinned originals/IR must establish Collection identity; this inventory cannot reconstruct it.']}
    (OUT/'inventory.json').write_text(json.dumps({'summary':summary,'rules':rows},indent=2)+'\n')
    intro=['# Larger RHEL 9 diagnostic sample','',
           '**Status: DIAGNOSTIC REVIEW — existing generated output has known design gaps.**',
           '',f'This review covers all **445 Rules**, with **{len(selected)} selected Rules** spanning every feature/capability category detected in the default Assessment serialization. It is a navigation/audit view, not a fresh conversion or repaired NG benchmark.',
           '',f'All source links are pinned to commit `{SNAPSHOT}`. The generated source is unchanged; hashes and every Rule\'s selectors/gaps are in [inventory.json](inventory.json).',
           '', 'Start with these examples; the following table explains why each was selected:',
           '', '| Rule | What to inspect | Assessment |', '| --- | --- | --- |']
    for r in selected:
        intro.append(f"| {link(Path(r['rule_path']),r['id'])} | {', '.join(r['features']) or 'basic evaluation'} | {link(Path(r['assessment_path']),'Open YAML')} |")
    intro+=['','## Full benchmark and supporting structure','',
            f"- {link(ROOT/'benchmark.yaml','Full Benchmark: groups, all Rule membership, 11 Profiles and parameters')}",
            f"- {link(ROOT/'applicability.yaml','Applicability registry')} ({len(app)} bindings)",
            '- [All 445 Rules with assessment links and known gaps](all-rules.md)',
            '- [Current accepted design and unresolved syntax](../../design/CURRENT-DESIGN.md)',
            '', '## Known gaps to keep visible','',
            '| Finding | Rules affected in their default Assessment/selection |','| --- | --- |']
    for gap,n in sorted(flags.items()): intro.append(f'| {gap} | {n} |')
    intro+=['','## Coverage that this existing output cannot demonstrate','',
            'Named Collection references and preserved Collection sharing are not implemented here. Embedded Variable acquisitions exist in the older `object_values.collect` syntax, but that does not establish correct sharing or the accepted final grammar. These missing forms require source-driven examples and tests; this sample does not pretend to provide them.',
            '', '## Suggested review order','',
            '1. Inspect the Benchmark structure and the three opening Rules (release version, symlink, and dconf Variable/Collection extraction).',
            '2. Inspect the complex cases in the table: variable chains, sets, filters and multiple States.',
            '3. Inspect manual selection and applicability below; then use the all-Rule inventory for broader review.',
            '', '## Applicability Assessments','', '| Applicability ID | Assessment |','| --- | --- |']
    for item in app: intro.append(f"| {item['id']} | {link(ROOT/item['assessment'],'Open YAML')} |")
    intro+=['','## Evidence and limits','',
            f"Validated inventory: 445 distinct Rule files; {len(paths)} unique Assessment identities; all Rule selector targets/defaults and {len(app)} applicability file references resolve. Every detected feature category is represented in the selected Rules. This is structural inventory evidence, not current-design acceptance or runtime equivalence.",
            '', 'Reproduce: `python tools/build_rhel9_diagnostic_review.py`. No authoring generator is invoked.',
            '', 'Provenance category: **Evidence/Audit** for feature classification and gaps; **Inherited** for the linked source. The underlying SCAP source pin remains recorded in the full source-package evidence. No policy/source defects were silently repaired.']
    (OUT/'README.md').write_text('\n'.join(intro)+'\n')
    allrows=['# All 445 RHEL 9 Rules — diagnostic inventory','',
             'Existing generated output; known gaps are listed, not waived. See [sample and limitations](README.md).','',
             '| Rule | Title | Default Assessment | Observed features | Known gaps |','| --- | --- | --- | --- | --- |']
    for r in rows:
        title=(r['title'] or '').replace('|','\\|').replace('\n',' ')
        allrows.append(f"| {link(Path(r['rule_path']),r['id'])} | {title} | {link(Path(r['assessment_path']),r['mode'])} | {', '.join(r['features'])} | {'; '.join(r['known_gaps'])} |")
    (OUT/'all-rules.md').write_text('\n'.join(allrows)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
