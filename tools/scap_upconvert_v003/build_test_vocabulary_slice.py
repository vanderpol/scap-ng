#!/usr/bin/env python3
"""Reproduce two real RHEL9 rules for Test vocabulary/path authoring review."""
import json
from pathlib import Path
from assessment_test_syntax import assessment_test_syntax, verify_assessment_test_syntax
from build_rhel9_split_policy_review import load, dump, resolve_source_ref

def main():
    source=Path('research/iterations/003/source/split-policy-assessment/rhel9-full')
    output=Path('research/iterations/003/review/test-vocabulary-slice')
    comparisons=paths=0
    for rid in ('SV-257777','SV-257781'):
        rule=load(source/'rules'/(rid+'.rule.yaml'))
        policy=load(source/'policies'/(rid+'.policy.yaml'))
        p=policy['policy']
        p['assessment_choices']=p.pop('checks')
        p['default_assessment_choice']=p.pop('default_check')
        if p['default_assessment_choice'] not in p['assessment_choices']:
            raise ValueError('Unresolved default Assessment choice')
        rule_file=output/'rules'/(rid+'.rule.yaml')
        policy_file=output/'policies'/(rid+'.policy.yaml')
        for ref in p['assessment_choices'].values():
            relative=(source/'policies'/ref['assessment']).resolve().relative_to(source.resolve())
            original=load(source/relative)
            converted=assessment_test_syntax(original)
            dump(output/relative, converted)
            verify_assessment_test_syntax(original, load(output/relative))
            comparisons+=1
        dump(rule_file,rule)
        dump(policy_file,policy)
        resolve_source_ref(output,rule_file,rule['rule']['policy'],'policy',p['id'])
        paths+=1
        for ref in p['assessment_choices'].values():
            assessment_file=(policy_file.parent/ref['assessment']).resolve()
            aid=load(assessment_file)['assessment']['id']
            resolve_source_ref(output,policy_file,ref['assessment'],'assessment',aid)
            paths+=1
    report={'status':'authoring_review_slice_not_runtime_equivalence',
            'rules':2,'policies':2,'distinct_assessments':4,
            'assessment_comparisons_including_selector_aliases':comparisons,
            'explicit_paths_validated':paths,
            'allowed_changes':['policy assessment_choices/default_assessment_choice',
                               'assessment tests/test- IDs/evaluate.test',
                               'assert.item_quantifier'],
            'baseline':'split-policy-assessment/rhel9-full at 54f8764c',
            'limits':['No scanner execution or full round trip performed.',
                      'All other assessment fields and values preserved.',
                      'Complete benchmark regeneration deferred until owner review.']}
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
