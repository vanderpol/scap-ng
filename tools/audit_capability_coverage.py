#!/usr/bin/env python3
"""Evidence/Audit: conservative current mapping/test-content inventory.

Static test mentions and dated migration mentions are candidates, not proven
positive/negative coverage or target execution. No vendor coverage is inferred
from generated schema meta-validation alone.
"""
import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from generate_capability_schema import generate
from collected_item_contract_v02 import capability_schema

ROOT=Path(__file__).resolve().parents[1]
CENSUS='research/iterations/003/evidence/full-current-native-normalize-compile/native-schema-census.json'

def capabilities(value):
    found=set()
    if isinstance(value,dict):
        if isinstance(value.get('capability'),str):found.add(value['capability'])
        for child in value.values():found.update(capabilities(child))
    elif isinstance(value,list):
        for child in value:found.update(capabilities(child))
    return found

def audit(root=ROOT):
    workflow=yaml.safe_load((root/'.github/workflows/scap-ng-current-regression.yml').read_text())
    maintained=set()
    for step in workflow['jobs']['contracts']['steps']:
        for line in step.get('run','').splitlines():
            words=line.split()
            if len(words)>1 and words[0]=='python' and words[1].endswith('.py') and Path(words[1]).name.startswith('test_'):maintained.add(words[1])
    constants={}
    for path in sorted(maintained):
        nodes=ast.walk(ast.parse((root/path).read_text(encoding='utf-8')))
        constants[path]={node.value for node in nodes if isinstance(node,ast.Constant) and isinstance(node.value,str)}
    content={};items={}
    for path in sorted((root/'tests').rglob('*')):
        if path.suffix not in ('.yaml','.yml','.json'):continue
        data=yaml.safe_load(path.read_text(encoding='utf-8')) if path.suffix!='.json' else json.loads(path.read_text(encoding='utf-8'))
        rel=path.relative_to(root).as_posix()
        if isinstance(data,dict) and isinstance(data.get('assessment'),dict):
            for cap in capabilities(data['assessment']):content.setdefault(cap,[]).append(rel)
        if isinstance(data,list):
            for case in data:
                if isinstance(case,dict) and isinstance(case.get('expected_valid'),bool) and isinstance(case.get('item'),dict):
                    cap=case['item'].get('capability')
                    if cap:items.setdefault(cap,[]).append({'file':rel,'case':case['id'],'expected_valid':case['expected_valid']})
    census=json.loads((root/CENSUS).read_text())
    mentioned={v for field in census['fields'] if field['path'].endswith('.capability') for v in field.get('examples',[]) if isinstance(v,str)}
    rows=[]
    for path in sorted((root/'schema/v0.1.0/capability-mappings').glob('*.json')):
        mapping=json.loads(path.read_text())
        if 'capability' not in mapping:continue
        cap=mapping['capability'];Draft202012Validator.check_schema(generate(mapping,root))
        item=capability_schema(mapping)
        if item is not None:Draft202012Validator.check_schema(item)
        source=mapping.get('source',{});family=Path(source.get('definitions_schema','')).name.removesuffix('-definitions-schema.xsd')
        source_cap=family+'.'+source.get('test','').removesuffix('_test')
        candidates=[test for test,values in constants.items() if any(v==cap or v.endswith('/'+path.name) or v==path.name for v in values)]
        authored=content.get(cap,[])
        rows.append({'capability':cap,'mapping':path.relative_to(root).as_posix(),
            'generated_schema_meta_validation':'passed_0.1_authoring_and_0.2_item' if item is not None else 'passed_0.1_authoring_no_item_contract',
            'focused_test_reference_candidates':sorted(candidates),
            'positive_negative_authoring_coverage':'requires_method_level_review',
            'standalone_assessment_content':authored,
            'standalone_expected_result_coverage':'partial_feature_oracle_only' if authored else 'missing',
            'collected_item_contract_cases':items.get(cap,[]),
            'migration_evidence':{'status':'dated_census_mention_only' if cap in mentioned or source_cap in mentioned else 'not_attributed',
                                  'source':CENSUS,'matching_mentions':sorted({cap,source_cap}&mentioned)},
            'target_execution':'not_demonstrated',
            'platform_prerequisites':family+' target/resource access; no scanner/target conformance established',
            'disposition':'partial_standalone_feature_evidence' if authored else 'needs_standalone_assessment_and_expected_results'})
    summary={'mapped_capabilities':len(rows),'generated_meta_validated':len(rows),
        'capabilities_with_standalone_content':sum(bool(r['standalone_assessment_content']) for r in rows),
        'capabilities_without_standalone_content':sum(not r['standalone_assessment_content'] for r in rows),
        'capabilities_with_item_cases':sum(bool(r['collected_item_contract_cases']) for r in rows),
        'capabilities_with_static_test_candidates':sum(bool(r['focused_test_reference_candidates']) for r in rows),
        'target_execution_demonstrated':0}
    return {'format':'scap-ng.capability-coverage-audit.1','scope':'Current reviewed mappings and maintained test/content paths. Static mentions do not prove fixtures execute, assertions cover semantics or collectors run. Dated census mentions do not prove per-capability round-trip equivalence. Full positive/negative method-level and vendor feature coverage remain open.',
            'summary':summary,'capabilities':rows}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'docs/audit/capability-coverage-2026-10-03/current-mappings.json')
    args=p.parse_args();result=audit();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result['summary'],indent=2))
if __name__=='__main__':main()
