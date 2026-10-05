#!/usr/bin/env python3
"""Unsigned draft result ZIP: exact-byte integrity and execution-reference checks.

Policy scoring/class-specific Rule interpretation and signer trust are separate.
No archive member is extracted to the filesystem during verification.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import stat
import zipfile
from assessment_results_v02 import validate_schema,validate_result_set,index,check_refs,item_validator
from item_materialization_v02 import _unique_object,_finite_float,validate_materialization
from reported_elements import _check_redaction


def decode(data):
    return json.loads(data.decode('utf-8'),object_pairs_hook=_unique_object,parse_float=_finite_float,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON number')))

def encode(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')

def safe_path(name):
    if not name or '\\' in name or ':' in name or '\x00' in name or name.startswith('/') or any(p in ('','.','..') for p in name.split('/')):
        raise ValueError('Unsafe/ambiguous result-package member path')
    return name

def unique(rows,key,label):
    result={}
    for row in rows:
        if row[key] in result: raise ValueError(f'Duplicate {label}')
        result[row[key]]=row
    return result

def validate_local_result(row):
    items=index(row['items'],'Item');tests=index(row['tests'],'Test');objects=index(row['objects'],'Object');variables=index(row['variables'],'Variable')
    if set(row['expression_execution']['executed_tests'])!=set(tests):raise ValueError('Expression/Test registry mismatch')
    for item in items.values():
        item_validator(item['capability']).validate(item)
        from collected_item_contract_v02 import context_errors
        if context_errors(item) or item['provenance'].get('target_ref')!=row['target_ref']:raise ValueError('Invalid local Item context/target')
    for obj in objects.values():check_refs(obj['item_refs'],items,'Object/Item')
    for variable in variables.values():check_refs(variable['item_refs'],items,'Variable/Item')
    for test in tests.values():
        check_refs(test['object_refs'],objects,'Test/Object');check_refs(test['item_refs'],items,'Test/Item')
        if test['object_refs'] and not set(test['item_refs'])<=set().union(*(set(objects[ref]['item_refs']) for ref in test['object_refs'])):raise ValueError('Test Items outside Object result')
        for per in test['per_item_results']:
            if per['item_ref'] not in test['item_refs']:raise ValueError('Per-Item reference outside Test')
            for state in per['state_results']:
                if state['state_ref'] not in test['state_refs']:raise ValueError('State result outside Test')
                for entity in state['entity_results']:check_refs(entity.get('variable_refs',[]),variables,'Entity/Variable')
    for use in row['field_uses']:
        if use['test_ref'] not in tests or use['item_ref'] not in items:raise ValueError('Dangling field-use reference')
    for trace in row['expression_execution']['trace']:
        if trace['owner_invocation_ref']!=row['execution_id']:raise ValueError('Trace owner mismatch')
        if trace['kind']=='test' and (trace['assessment']!=row['assessment']['id'] or trace['test'] not in tests or trace['outcome']!=tests[trace['test']]['outcome']):raise ValueError('Trace/Test identity/outcome mismatch')
    recorded=[(t['alias'],t['invocation_ref'],t['outcome'],t['reused']) for t in row['expression_execution']['trace'] if t['kind']=='dependency']
    linked=[(d['alias'],d['execution_id'],d['outcome'],d['reused']) for d in row['dependent_assessments']]
    if recorded!=linked:raise ValueError('Dependency trace/reference mismatch')
    report=row.get('item_report')
    if report is not None:
        if report['source_execution_ref']!=row['execution_id'] or report['source_completeness']!={k:row[k] for k in ('logical_complete','population_complete','evidence_complete')}:raise ValueError('Report execution/completeness mismatch')
        projected=index([entry['item'] for entry in report['items']],'projected Item')
        if set(projected)!=set(items):raise ValueError('Canonical/report Item registry mismatch')
        for identity,item in projected.items():
            original=items[identity]
            if any(field not in original['fields'] or value!=original['fields'][field] for field,value in item['fields'].items()):raise ValueError('Report changed canonical values')
            if any(item.get(k)!=original.get(k) for k in ('capability','status','imported','provenance')):raise ValueError('Report changed canonical identity/provenance')


def check_evidence_refs(value,members):
    if isinstance(value,dict):
        if 'evidence_refs' in value:
            if not isinstance(value['evidence_refs'],list) or any(ref not in members for ref in value['evidence_refs']):raise ValueError('Unbound evidence reference (auxiliary evidence members are not supported in this draft)')
        for child in value.values():check_evidence_refs(child,members)
    elif isinstance(value,list):
        for child in value:check_evidence_refs(child,members)


def validate_graph(manifest,documents,assessments=None):
    validate_schema('result-package-manifest.schema.json',manifest)
    entries=unique(manifest['members'],'id','logical member identity')
    paths=unique(manifest['members'],'path','member path')
    if len({p.casefold() for p in paths})!=len(paths): raise ValueError('Case-colliding member paths')
    if set(documents)!=set(entries): raise ValueError('Missing/extra logical result documents')
    for entry in entries.values():
        safe_path(entry['path']);kind=entry['kind'];doc=documents[entry['id']]
        if entry['path']=='manifest.json':raise ValueError('Reserved manifest member path')
        check_evidence_refs(doc,entries)
        validate_schema(kind.replace('_','-')+'.schema.json',doc);_check_redaction(doc)
    scans=[documents[e['id']]['scan_result'] for e in entries.values() if e['kind']=='scan_result']
    if len(scans)!=1 or entries.get(manifest['scan_result_ref'],{}).get('kind')!='scan_result':
        raise ValueError('Exactly one authoritative Scan Result required')
    scan=scans[0]
    if scan['run_id']!=manifest['run_id'] or scan.get('signature_status')!='unsigned': raise ValueError('Run/signature status mismatch')
    targets=unique(scan['targets'],'id','target identity')
    benchmarks={e['id']:documents[e['id']]['benchmark_result'] for e in entries.values() if e['kind']=='benchmark_result'}
    results={e['id']:documents[e['id']]['assessment_result'] for e in entries.values() if e['kind']=='assessment_result'}
    references=unique(scan['benchmark_results'],'benchmark_result_ref','Scan/Benchmark reference')
    if set(references)!=set(benchmarks): raise ValueError('Scan/Benchmark result registry mismatch')
    assessment_refs=scan.get('assessment_result_refs',[])
    if len(assessment_refs)!=len(set(assessment_refs)) or set(assessment_refs)!=set(results): raise ValueError('Scan/Assessment result registry mismatch')
    for identity,row in results.items():
        if identity!=row['execution_id'] or row['target_ref'] not in targets: raise ValueError('Assessment execution/target mismatch')
        expr=row['expression_execution']
        if expr['invocation_ref']!=identity or expr['assessment']!=row['assessment']['id'] or expr['outcome']!=row['outcome']:
            raise ValueError('Assessment/expression result mismatch')
        validate_materialization(row)
        validate_local_result(row)
    grouped=set()
    for group in manifest['evaluation_groups']:
        ids=set(group['execution_ids'])
        if ids & grouped or not ids<=results.keys() or group['entry_execution_id'] not in ids or group['target_ref'] not in targets:
            raise ValueError('Invalid/overlapping evaluation group')
        grouped.update(ids);active=set();reached=set()
        def visit(identity):
            if identity in active: raise ValueError('Result dependency cycle')
            if identity in reached:return
            active.add(identity);row=results[identity]
            if row['target_ref']!=group['target_ref']:raise ValueError('Cross-target dependency group')
            if row.get('binding_set_id')!=results[group['entry_execution_id']].get('binding_set_id'):
                raise ValueError('Cross-binding dependency group')
            for dep in row.get('dependent_assessments',[]):
                child=results.get(dep['execution_id'])
                if child is None or dep['execution_id'] not in ids: raise ValueError('Dependency outside invocation group')
                if dep['assessment']!=child['assessment'] or dep['outcome']!=child['outcome'] or dep.get('purpose')!=child['purpose']:
                    raise ValueError('Dependency identity/outcome mismatch')
                visit(dep['execution_id'])
            active.remove(identity);reached.add(identity)
        visit(group['entry_execution_id'])
        if reached!=ids:raise ValueError('Unreachable result artifact in evaluation group')
        if assessments is not None:
            validate_result_set({'entry_execution_id':group['entry_execution_id'],'target_ref':group['target_ref'],
                'assessment_results':[documents[i] for i in group['execution_ids']]},assessments)
    if grouped!=set(results):raise ValueError('Ungrouped Assessment executions')
    for identity,benchmark in benchmarks.items():
        reference=references[identity];policy=benchmark['effective_policy']
        if benchmark['run_id']!=scan['run_id'] or benchmark['target_ref'] not in targets or reference['target_ref']!=benchmark['target_ref']:
            raise ValueError('Benchmark run/target mismatch')
        if reference['benchmark_id']!=benchmark['benchmark']['id'] or reference.get('benchmark_version')!=benchmark['benchmark']['version']:
            raise ValueError('Benchmark identity/version mismatch')
        if reference.get('profile_id')!=policy['profile']:raise ValueError('Scan/Benchmark Profile mismatch')
        if 'summary' in reference and reference['summary']!=benchmark['summary']:raise ValueError('Scan/Benchmark summary mismatch')
        rules=unique(benchmark['rule_results'],'rule_id','Rule result identity')
        if set(policy['selected_rules'])!=set(rules) or set(policy['selected_rules']) & set(policy['disabled_rules']):
            raise ValueError('Effective selected/disabled Rule registry mismatch')
        counts=Counter(rule['outcome'] for rule in rules.values())
        if benchmark['summary']['total']!=len(rules) or any(benchmark['summary'][key]!=counts[key] for key in ('pass','fail','error','unknown','not_evaluated','not_applicable')):
            raise ValueError('Benchmark outcome summary mismatch')
        for rule in rules.values():
            unique(rule['instances'],'id','Rule instance identity')
            for instance in rule['instances']:
                ref=instance['assessment_result_ref'];invocation=instance.get('assessment_invocation_id')
                if ref is None:
                    if invocation is not None or instance['outcome'] not in ('not_evaluated','not_applicable','unknown','error'):
                        raise ValueError('Completed Rule instance lacks Assessment execution')
                    continue
                result=results.get(ref)
                if result is None or invocation!=ref or result['target_ref']!=benchmark['target_ref'] or result['purpose']!='assessment':
                    raise ValueError('Rule/Assessment execution binding mismatch')
                selected=rule['assessment']
                if selected is None or selected['id']!=result['assessment']['id'] or selected['version']!=result['assessment']['version'] or selected.get('mode')!=result['mode']:
                    raise ValueError('Rule selected Assessment identity/version/mode mismatch')
            for condition in (rule.get('applicability') or {}).get('conditions',[]):
                ref=condition.get('assessment_result_ref')
                if ref is None:continue
                result=results.get(ref)
                if result is None or result['purpose']!='applicability' or result['target_ref']!=benchmark['target_ref'] or condition.get('assessment_invocation_id')!=ref:
                    raise ValueError('Applicability execution binding mismatch')
    return {'run_id':scan['run_id'],'benchmark_results':len(benchmarks),'assessment_results':len(results),
            'integrity':'verified','signature_status':'unsigned','semantic_validation':'references_and_expression_scheduling' if assessments is not None else 'references'}


def write_result_package(path,scan,benchmarks,result_sets,*,assessments=None):
    documents={};kinds={};groups=[]
    def add(identity,kind,document):
        if identity in documents: raise ValueError('Duplicate logical result member')
        documents[identity]=document;kinds[identity]=kind
    scan_ref='scan:'+scan['scan_result']['run_id'];add(scan_ref,'scan_result',scan)
    for identity,document in benchmarks.items():add(identity,'benchmark_result',document)
    for result_set in result_sets:
        ids=[]
        for document in result_set['assessment_results']:
            identity=document['assessment_result']['execution_id'];add(identity,'assessment_result',document);ids.append(identity)
        groups.append({'entry_execution_id':result_set['entry_execution_id'],'target_ref':result_set['target_ref'],'execution_ids':sorted(ids)})
    manifest={'format_version':'scap-ng.result-package.draft-1','result_schema_version':'0.2.0','digest_algorithm':'sha256',
              'signature_status':'unsigned','run_id':scan['scan_result']['run_id'],'scan_result_ref':scan_ref,'members':[],
              'evaluation_groups':sorted(groups,key=lambda row:row['entry_execution_id'])}
    payloads={}
    for n,identity in enumerate(sorted(documents)):
        kind=kinds[identity];doc=documents[identity];raw=encode(doc)
        label=doc.get('assessment_result',{}).get('assessment',{}).get('id',identity)
        slug=re.sub(r'[^A-Za-z0-9._-]+','-',label)[:60].strip('.-') or 'result'
        folder={'scan_result':'scan-results','benchmark_result':'benchmark-results','assessment_result':'assessment-results'}[kind]
        member=f'{folder}/{n+1:04d}--{slug}.json';payloads[member]=raw
        manifest['members'].append({'id':identity,'kind':kind,'path':member,'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'schema_version':'0.2.0'})
    validate_graph(manifest,documents,assessments)
    payloads['manifest.json']=encode(manifest)
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for member,raw in sorted(payloads.items()):
            info=zipfile.ZipInfo(member,(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,raw,compresslevel=9)
    return manifest


def verify_result_package(path,*,assessments=None,max_members=10000,max_uncompressed_bytes=64*1024*1024):
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist()
        if len(infos)>max_members or sum(i.file_size for i in infos)>max_uncompressed_bytes:raise ValueError('Result-package resource limit')
        names=[i.filename for i in infos]
        if len(names)!=len(set(names)) or len(names)!=len({name.casefold() for name in names}):raise ValueError('Duplicate/case-colliding ZIP member')
        for info in infos:
            safe_path(info.filename)
            if info.is_dir() or stat.S_ISLNK(info.external_attr>>16) or info.flag_bits&1 or info.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED):
                raise ValueError('Unsupported/symlink/encrypted result member')
        if 'manifest.json' not in names:raise ValueError('Missing result manifest')
        manifest=decode(archive.read('manifest.json'));validate_schema('result-package-manifest.schema.json',manifest)
        expected={row['path'] for row in manifest['members']}|{'manifest.json'}
        if expected!=set(names):raise ValueError('Unbound/missing ZIP member')
        documents={}
        for row in manifest['members']:
            raw=archive.read(row['path'])
            if len(raw)!=row['size'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Result member digest/size mismatch')
            if row['id'] in documents:raise ValueError('Duplicate logical result member')
            documents[row['id']]=decode(raw)
    return validate_graph(manifest,documents,assessments)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('package',type=Path);parser.add_argument('--assessments',type=Path);parser.add_argument('--build-input',type=Path,help='JSON object containing scan, benchmarks and result_sets')
    args=parser.parse_args();sources=None
    if args.assessments:
        from assessment_expression import load_assessments
        sources=load_assessments(args.assessments)
    if args.build_input:
        inputs=decode(args.build_input.read_bytes())
        if set(inputs)!={'scan','benchmarks','result_sets'}:raise ValueError('Invalid build input members')
        write_result_package(args.package,inputs['scan'],inputs['benchmarks'],inputs['result_sets'],assessments=sources)
    print(json.dumps(verify_result_package(args.package,assessments=sources),indent=2))

if __name__=='__main__':main()
