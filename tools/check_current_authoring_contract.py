#!/usr/bin/env python3
"""Authoring-readiness guard; not a complete schema or semantic evaluator."""
import argparse
import json
from pathlib import Path
import yaml

OLD_KEYS={'collect','object_title','object_values','state_capability'}
ASSESSMENT_SECTION_ORDER=('collections','variables','tests','evaluate')

def violations(document):
    errors=[]
    def visit(value,path):
        if isinstance(value,list):
            for i,item in enumerate(value): visit(item,f'{path}[{i}]')
        elif isinstance(value,dict):
            for key,item in value.items():
                here=f'{path}.{key}'
                if key in OLD_KEYS: errors.append(f'{here}: stale Object/collection or capability syntax')
                visit(item,here)
    if 'policy' in document: errors.append('policy: superseded document type')
    rule=document.get('rule',{})
    if 'policy' in rule: errors.append('rule.policy: superseded Policy linkage')
    a=document.get('assessment',{})
    for profile in document.get('benchmark',{}).get('profiles',[]):
        if 'enabled_rules' in profile:
            errors.append('benchmark.profiles: publisher Profiles are subtractive; enabled_rules belongs to Tailoring')
        if 'disabled_rules' not in profile:
            errors.append('benchmark.profiles: show disabled_rules explicitly, including an empty list')
        if '<ProfileDescription' in (profile.get('description') or ''):
            errors.append('benchmark.profiles: remove source XML description wrapper')
    sections=[key for key in a if key in ASSESSMENT_SECTION_ORDER]
    expected=[key for key in ASSESSMENT_SECTION_ORDER if key in a]
    if sections != expected:
        errors.append('assessment: presentation order must be collections, variables, tests, evaluate (omit absent sections)')
    if 'deprecated' in a: errors.append('assessment.deprecated: forbidden native attribute')
    if 'checks' in a: errors.append('assessment.checks: use Tests')
    for name in a.get('tests',{}):
        if not name.startswith('test-'): errors.append(f'assessment.tests.{name}: missing test- prefix')
    visit(document,'document')
    return errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument('source',type=Path)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    problems=[]
    files=list(args.source.rglob('*.yaml'))
    if not files: problems.append({'file':str(args.source),'errors':['No YAML review source found']})
    if (args.source/'policies').exists(): problems.append({'file':'policies/','errors':['Superseded Policy directory']})
    for f in sorted(files):
        doc=yaml.safe_load(f.read_text())
        errors=violations(doc) if isinstance(doc,dict) else ['Expected document mapping']
        if errors: problems.append({'file':str(f.relative_to(args.source)),'errors':errors})
    report={'status':'blocked' if problems else 'vocabulary_guard_passed_not_semantic_equivalence',
            'yaml_files':len(files),'violations':problems,
            'limits':['Does not verify full grammar, graph closure, preserved sharing or runtime results.']}
    if args.report: args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 1 if problems else 0

if __name__=='__main__': raise SystemExit(main())
