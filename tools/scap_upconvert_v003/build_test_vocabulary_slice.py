#!/usr/bin/env python3
"""Reproduce two real RHEL9 rules for Test vocabulary/path authoring review."""
import json
from pathlib import Path
from assessment_test_syntax import assessment_test_syntax, verify_assessment_test_syntax
from build_rhel9_split_policy_review import load, dump, resolve_source_ref

def main():
    source=Path('research/iterations/003/source/split-rule-assessment/rhel9-full')
    output=Path('research/iterations/003/review/test-vocabulary-slice')
    # Remove the obsolete Policy layer from an earlier slice generation.
    import shutil
    if (output/'policies').exists(): shutil.rmtree(output/'policies')
    comparisons=paths=0
    for rid in ('SV-257777','SV-257781'):
        rule=load(source/'rules'/(rid+'.rule.yaml'))
        p=rule['rule']
        targets=p.pop('checks')
        p['assessment_choices']={}
        for selector, target in targets.items():
            mode='manual' if target.endswith('.manual') else 'automated'
            p['assessment_choices'][selector]={'assessment': f'../assessments/{mode}/{target}.assessment.yaml'}
        p['default_assessment_choice']=p.pop('default_check')
        if p['default_assessment_choice'] not in p['assessment_choices']:
            raise ValueError('Unresolved default Assessment choice')
        rule_file=output/'rules'/(rid+'.rule.yaml')
        for ref in p['assessment_choices'].values():
            relative=(source/'rules'/ref['assessment']).resolve().relative_to(source.resolve())
            original=load(source/relative)
            converted=assessment_test_syntax(original)
            dump(output/relative, converted)
            verify_assessment_test_syntax(original, load(output/relative))
            comparisons+=1
        dump(rule_file,rule)
        if 'policy' in p:
            raise ValueError('Separate Policy linkage is superseded')
        for ref in p['assessment_choices'].values():
            assessment_file=(rule_file.parent/ref['assessment']).resolve()
            aid=load(assessment_file)['assessment']['id']
            resolve_source_ref(output,rule_file,ref['assessment'],'assessment',aid)
            paths+=1
    report={'status':'authoring_review_slice_not_runtime_equivalence',
            'rules':2,'policies':0,'distinct_assessments':4,
            'assessment_comparisons_including_selector_aliases':comparisons,
            'explicit_paths_validated':paths,
            'allowed_changes':['Rule assessment_choices/default_assessment_choice with relative Assessment paths',
                               'assessment tests/test- IDs/evaluate.test',
                               'assert.item_quantifier',
                               'remove stale deprecated: false metadata'],
            'baseline':'split-rule-assessment/rhel9-full at 54f8764c',
            'limits':['No scanner execution or full round trip performed.',
                      'All other assessment fields and values preserved.',
                      'Complete benchmark regeneration deferred until owner review.']}
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
