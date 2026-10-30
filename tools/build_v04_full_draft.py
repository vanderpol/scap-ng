"""Explicit all-corpus DRAFT deliverable; never verified-package admission.

Attempts native authoring through all existing approved supported mappings.
Preserves complete originals/manual content and every Rule outcome. Independent
proof is optional evidence, never a prerequisite for this diagnostic draft.
The strict verify_v04_direct_scope path is unchanged.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import csv
from hashlib import sha256, sha1
import html
import json
from pathlib import Path
import shutil
import time
import xml.etree.ElementTree as ET

from v04_direct_scap_source import SourceModel, OVAL, OCIL, XCCDF, digest, ensure
from v04_direct_converter import ROOT, assemble_subset, convert_benchmark
from v04_direct_yaml import authoring_yaml
from v04_native_bundle_compiler import build_bundle, compile_assessment_program
from audit_v04_eight_assessment_pilot import verify_program
from audit_v04_direct_benchmark import verify_compiled

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def diagnostic_mappings():
    """Existing supported contracts only; no production activation or schema edit."""
    mappings = [json.loads(p.read_text()) for p in sorted(
        (ROOT/'schema/v0.4.0/capability-mappings/supported').glob('*.json'))]
    ensure(all(m['specification_version']=='0.4.0' for m in mappings), 'mapping version drift')
    # Ambiguous catalogs must not make previously supported Rules regress.
    for kind in ['test', 'object', 'state']:
        keys = [(m['source']['namespace'], m['source'][kind]) for m in mappings if m['source'].get(kind)]
        ensure(len(keys)==len(set(keys)), 'ambiguous diagnostic '+kind+' mapping')
    return mappings

def deprecated_tests():
    x = '{http://www.w3.org/2001/XMLSchema}'
    result = set()
    for path in (ROOT/'third_party/scap-1.4-schemas/oval_5.12.3').glob('*-definitions-schema.xsd'):
        root = ET.parse(path).getroot()
        for n in root.findall(x+'element'):
            if n.get('name','').endswith('_test') and any(v.tag.endswith('}deprecated_info') for v in n.iter()):
                result.add('{'+root.get('targetNamespace')+'}'+n.get('name'))
    for row in json.loads((ROOT/'specification/migration/oval-test-support-overrides.json').read_text())['overrides']:
        if row['effective_status']=='supported_reinstated':
            ns, _, name = row['qualified_name'].rpartition('#')
            result.discard('{'+ns+'}'+name)
    return result

def preserve_source(source, source_path, target):
    """Keep original bytes plus inspectable XML; never synthesize a manual method."""
    folder = target/'source-preservation'
    folder.mkdir()
    shutil.copy2(source_path, folder/source_path.name)
    components = {}
    for identifier, node in source.components.items():
        name = 'components/'+digest(identifier)[:20]+'.xml'
        path = folder/name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(ET.tostring(node, encoding='utf-8', xml_declaration=True))
        components[identifier] = {'path':'source-preservation/'+name,'root_tag':node.tag,
                                 'xml_identity_sha256':digest(__import__('v04_direct_scap_source').xml_identity(node))}
    write_json(folder/'components.json', components)
    return components

def apply_source_exclusions(source, coverage, documents, trace, known, deprecated, package_exception):
    """No known-invalid/deprecated candidate enters emitted native authoring."""
    remove = set()
    for row in coverage['rules']:
        key = source.archive_name+'!'+row['source_rule']
        reason = known.get(key)
        for dep in row['dependencies']:
            if dep['kind']=='test':
                node = source.node(dep['component'],dep['id'],'test')
                if node.tag in deprecated or node.get('deprecated','false') in ('true','1'):
                    reason = 'Effectively deprecated original OVAL Test: '+dep['id']
                    break
        automated = any(c['system']==OVAL for c in row['checks'])
        if automated and package_exception:
            reason = 'Nonstandard independent.sqlext source package remains fail-closed'
        if automated and reason:
            remove.add(row['source_rule'])
            issue = {'category':'source-exclusion','message':reason,'source_id':row['source_rule']}
            row.update(status='blocked',primary_blocker=issue,blockers=[issue]+row.get('blockers',[]))
            row.pop('artifacts',None)
    bindings = [b for b in trace['rules'] if b['source_rule'] not in remove]
    retained = {p:d for p,d in documents.items() if any(p in r.get('artifacts',[]) for r in coverage['rules'] if r['status']=='converted')}
    return assemble_subset(source,retained,bindings,diagnostic_mappings())

def render_review(source, target, rows, components):
    escape = html.escape
    chunks = ['<!doctype html><meta charset="utf-8"><title>DRAFT source review</title>',
        '<h1>DRAFT — NOT VERIFIED FOR EXECUTION</h1><p>All original Rules and manual content are preserved. '
        'Native authoring is a partial automated conversion; source proof, policy/CPE/manual migration and runtime parity are separate.</p>',
        '<p><a href="ledger.json">Rule ledger</a> · <a href="source-preservation/'+escape(source.archive_name)+'">Exact original ZIP</a></p>']
    for row in rows:
        original = source.rules[row['source_rule']]
        relative = 'source-preservation/rules/'+digest(row['source_rule'])[:20]+'.xml'
        path = target/relative
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(ET.tostring(original,encoding='utf-8',xml_declaration=True))
        row['preserved_original_rule'] = relative
        title = original.findtext('{'+XCCDF+'}title','')
        chunks += ['<details><summary>'+escape(row['source_rule']+' — '+row['draft_status']+' — '+title)+'</summary>',
            '<p><a href="'+relative+'">Original Rule XML (all metadata and checks)</a></p>',
            '<pre>'+escape(ET.tostring(original,encoding='unicode'))+'</pre>']
        if row.get('assessment_path'):
            chunks += ['<p>Native candidate: <a href="'+escape(row['assessment_path'])+'">JSON</a> · '
                       '<a href="'+escape(str(Path(row['assessment_path']).with_suffix('.yaml')))+'">YAML</a></p>']
        if row.get('primary_blocker'):
            chunks += ['<pre>'+escape(json.dumps(row['primary_blocker'],indent=2))+'</pre>']
        if row.get('conversion_warnings'):
            chunks += ['<p>CONVERTED_UNVERIFIED compatibility warnings:</p><pre>'+
                       escape(json.dumps(row['conversion_warnings'],indent=2))+'</pre>']
        chunks += ['</details>']
    chunks += ['<h2>Preserved source components, including OCIL/manual content</h2><ul>']
    chunks += ['<li><a href="'+escape(v['path'])+'">'+escape(k+' '+v['root_tag'])+'</a></li>' for k,v in components.items()]
    chunks += ['</ul>']
    (target/'review.html').write_text('\n'.join(chunks))

def build_one(job):
    pin, inputs, output, baseline, known = job
    started = time.perf_counter()
    source_path = Path(inputs)/pin['file']
    raw = source_path.read_bytes()
    ensure(len(raw)==pin['bytes'] and sha256(raw).hexdigest()==pin['sha256'], 'source ZIP digest/size drift')
    ensure(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob_sha'], 'source Git blob drift')
    target = Path(output)/pin['file'].removesuffix('.zip')
    target.mkdir()
    source = SourceModel(source_path,pin['sha256'],inventory_broken_references=True,draft_compatibility=True)
    source.archive_name = pin['file']
    components = preserve_source(source,source_path,target)
    mappings = diagnostic_mappings()
    docs, trace, coverage = convert_benchmark(source,mappings=mappings)
    package_exception = any('}sqlext_' in n.tag for c in source.components.values() for n in c.iter())
    docs, trace = apply_source_exclusions(source,coverage,docs,trace,known,deprecated_tests(),package_exception)
    bindings = {b['source_rule']:b for b in trace['rules']}
    programs = []
    compiled_rules = set()
    for row in coverage['rules']:
        automated = any(c['system']==OVAL for c in row['checks'])
        row.update(benchmark=target.name,conversion_attempted=automated,original_source_validation='NOT_RUN_EXCEPT_RECORDED_EXCLUSIONS',
                   independent_source_proof='NOT_RUN',scanner_evaluated=False,manual_content='PRESERVED_ORIGINAL_NOT_NATIVE_EXECUTION')
        if not automated:
            row['draft_status']='MANUAL_OCIL_ONLY_PRESERVED'
        elif row['status']!='converted':
            row['draft_status']='BLOCKED_EXPLICIT'
        else:
            binding = bindings[row['source_rule']]
            path = next(p for p in row['artifacts'] if '/assessments/' in p and p.endswith('.json'))
            assessment = docs[path]['assessment']
            row.update(draft_status='CONVERTED_SCHEMA_VALID_UNVERIFIED',assessment_path=path,
                       authoring_sha256=digest(assessment),compile_status='NOT_RUN')
            try:
                program = compile_assessment_program(assessment)
                verify_program(assessment,program)
            except ValueError as error:
                row.update(compile_status='BLOCKED',compile_diagnostic=str(error))
            else:
                row.update(compile_status='COMPILED_OPERANDS_CHECKED',program_sha256=digest(program))
                compiled_rules.add(row['source_rule'])
            previous = baseline.get(pin['file']+'!'+row['source_rule'])
            if previous:
                ensure(not row.get('conversion_warnings'), 'unverified warning cannot inherit a published proof')
                ensure(all(row.get(k)==previous[k] for k in ['source_rule_sha256','authoring_sha256','program_sha256']),
                       'published proof/hash baseline drift: '+row['source_rule'])
                row.update(draft_status='RETAINED_PUBLISHED_STATIC_PRIMARY_PROOF',independent_source_proof='RETAINED_EXACT_HASH_EVIDENCE')
        row['conversion_status'] = (
            'CONVERTED_VERIFIED' if row['draft_status']=='RETAINED_PUBLISHED_STATIC_PRIMARY_PROOF' else
            'CONVERTED_UNVERIFIED' if row['draft_status']=='CONVERTED_SCHEMA_VALID_UNVERIFIED' else
            'BLOCKED' if automated else 'MANUAL_OCIL_ONLY_PRESERVED')
    # Diagnostic executable packages contain only actually compiled candidates.
    compiled_docs = {p:d for p,d in docs.items() if any(p in r.get('artifacts',[]) for r in coverage['rules'] if r['source_rule'] in compiled_rules)}
    compiled_docs, _ = assemble_subset(source,compiled_docs,[b for b in trace['rules'] if b['source_rule'] in compiled_rules],mappings)
    if compiled_docs:
        bundle, _ = build_bundle(compiled_docs)
        programs = verify_compiled(compiled_docs,bundle)
        (target/'UNVERIFIED-diagnostic-candidates.scapng').write_bytes(bundle)
    for relative, document in docs.items():
        path = target/relative
        write_json(path,document)
        path.with_suffix('.yaml').write_text(authoring_yaml(document))
    render_review(source,target,coverage['rules'],components)
    coverage.update(draft_only=True,proof_required_for_draft=False,
                    mapping_scope='DIAGNOSTIC_ALL_EXISTING_APPROVED_SUPPORTED_MAPPINGS',
                    original_zip=pin,scope='Complete original preservation and Rule accounting; native primary automated subset only')
    write_json(target/'ledger.json',coverage)
    write_json(target/'source-trace.json',trace)
    write_json(target/'compilation.json',programs)
    summary={'benchmark':target.name,'source_pin':pin,'rules':len(coverage['rules']),
             'statuses':dict(Counter(r['draft_status'] for r in coverage['rules'])),
             'automated_attempts':sum(r['conversion_attempted'] for r in coverage['rules']),
             'compiled_programs':len(programs),'elapsed_seconds':time.perf_counter()-started}
    write_json(target/'summary.json',summary)
    print(json.dumps(summary),flush=True)
    return summary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-pins',type=Path,required=True)
    parser.add_argument('--inputs',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--known-invalid',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--acknowledge-full-corpus-deliverable',action='store_true',required=True)
    args=parser.parse_args()
    ensure(args.workers in range(1,5),'bounded worker count required')
    pins=json.loads(args.source_pins.read_text())
    ensure(len(pins['sources'])==65 and len({p['file'] for p in pins['sources']})==65,'exact 65-source pins required')
    baseline=json.loads(args.baseline.read_text())['records']
    known={r['file']+'!'+r['rule']:r['reason'] for r in json.loads(args.known_invalid.read_text())}
    args.output.mkdir(exist_ok=False)
    jobs=[(p,args.inputs,args.output,baseline,known) for p in pins['sources']]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        summaries=list(pool.map(build_one,jobs))
    rows=[]
    for s in summaries:
        for row in json.loads((args.output/s['benchmark']/'ledger.json').read_text())['rules']:
            columns=['benchmark','source_rule','draft_status','conversion_attempted','original_source_validation',
                     'independent_source_proof','compile_status','primary_blocker','blockers','preserved_original_rule','assessment_path']
            rows.append({k:row.get(k) for k in columns})
    ensure(len(rows)==8892 and len({(r['benchmark'],r['source_rule']) for r in rows})==8892,'Rule accounting drift')
    ensure(sum(r['draft_status']=='RETAINED_PUBLISHED_STATIC_PRIMARY_PROOF' for r in rows)==len(baseline),'proof baseline lost')
    write_json(args.output/'source-pins.json',pins)
    write_json(args.output/'ledger.json',{'rules':rows})
    with (args.output/'ledger.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
        for row in rows:writer.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in row.items()})
    write_json(args.output/'summary.json',{'benchmarks':65,'rules':len(rows),
        'statuses':dict(Counter(r['draft_status'] for r in rows)),'sources':summaries,
        'limitations':['DRAFT, not final verified release','Native output covers primary automated subset; complete original Rules/manual content preserved separately','No source repair, unsupported-case bypass or runtime claim']})
    (args.output/'index.html').write_text('<!doctype html><meta charset="utf-8"><h1>All-65 DRAFT — NOT VERIFIED FOR EXECUTION</h1>'
        '<p>All original Rules/manual content retained. <a href="ledger.csv">Rule ledger CSV</a> · <a href="ledger.json">JSON</a></p><ul>'+
        ''.join('<li><a href="'+html.escape(s['benchmark'])+'/review.html">'+html.escape(s['benchmark'])+'</a> — '+str(s['rules'])+' Rules</li>' for s in summaries)+'</ul>')
    from finalize_v04_full_draft import finalize
    finalize(args.output,pins,baseline,known)

if __name__=='__main__':main()
