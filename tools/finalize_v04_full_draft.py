"""Finalize DRAFT reporting and audit preservation without rerunning conversion."""
from collections import Counter
import csv
from hashlib import sha256
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from v04_direct_scap_source import DS, XCCDF, OCIL, digest, ensure, xml_identity
from v04_direct_inventory import summarize

def finalize_source(target,pin,baseline,known=None):
    target=Path(target)
    known={} if known is None else known
    retained=set()
    ledger=json.loads((target/'ledger.json').read_text())
    rows=ledger['rules']
    original=target/'source-preservation'/pin['file']
    ensure(original.stat().st_size==pin['bytes'] and sha256(original.read_bytes()).hexdigest()==pin['sha256'],
           'preserved original ZIP mismatch')
    programs={p['assessment']:p['program_sha256'] for p in json.loads((target/'compilation.json').read_text())}
    expected_native=set()
    review=(target/'review.html').read_text()
    for row in rows:
        key=pin['file']+'!'+row['source_rule']
        if key in baseline:
            ensure(baseline[key].get('source_zip_sha256')==pin['sha256'],'published proof original ZIP pin drift')
        node=ET.parse(target/row['preserved_original_rule']).getroot()
        ensure(digest(xml_identity(node))==row['source_rule_sha256'],'preserved Rule XML mismatch: '+key)
        row['has_manual_source']=any(c['system']==OCIL for c in row['checks'])
        if key in known and row['conversion_attempted']:
            ensure(row['draft_status']=='BLOCKED_EXPLICIT','known-invalid original emitted as a candidate')
            old=row.get('primary_blocker')
            issue={'category':'source-exclusion','message':known[key],'source_id':row['source_rule']}
            row['primary_blocker']=issue
            row['blockers']=[issue]+[b for b in row.get('blockers',[]) if b!=issue]
            if old:
                review=review.replace(html.escape(json.dumps(old,indent=2)),html.escape(json.dumps(issue,indent=2)))
        if row['draft_status']=='BLOCKED_EXPLICIT':
            ensure(row.get('primary_blocker',{}).get('message'),'blocked Rule lacks diagnostic')
            ensure(not row.get('assessment_path'),'blocked Rule has native Assessment')
            row.update(status='blocked',proof_level='none',artifacts=[],compile_status='NOT_RUN_BLOCKED')
            if row['primary_blocker']['category']=='source-exclusion':
                row['original_source_validation']=('UNSUPPORTED_PACKAGE_EXTENSION' if 'sqlext' in row['primary_blocker']['message']
                                                   else 'KNOWN_INVALID_OR_DEPRECATED')
        elif row['draft_status']=='MANUAL_OCIL_ONLY_PRESERVED':
            ensure(not row.get('assessment_path'),'manual preservation fabricated an Assessment')
            row.update(proof_level='none',artifacts=[],compile_status='NOT_APPLICABLE_MANUAL')
        else:
            path=target/row['assessment_path']
            expected_native.add(path.name)
            assessment=json.loads(path.read_text())['assessment']
            ensure(path.with_suffix('.yaml').is_file(),'missing candidate YAML')
            ensure(digest(assessment)==row['authoring_sha256'],'candidate authoring digest drift')
            if row['compile_status']=='COMPILED_OPERANDS_CHECKED':
                ensure(programs.get(assessment['id'])==row['program_sha256'],'compiled program digest drift')
            else:
                ensure(assessment['id'] not in programs,'uncompiled candidate packaged as executable')
            if key in baseline:
                ensure(not row.get('conversion_warnings'),'warning-admitted content cannot inherit verified proof')
                ensure(all(row[k]==baseline[key][k] for k in ['source_rule_sha256','authoring_sha256','program_sha256']),
                       'retained baseline drift')
                ensure(row['draft_status']=='RETAINED_PUBLISHED_STATIC_PRIMARY_PROOF','lost proof label')
                row.update(proof_level='source_proved',original_source_validation='RETAINED_PUBLISHED_EXACT_INPUT_HASH_EVIDENCE')
                retained.add(key)
        row['conversion_status'] = (
            'CONVERTED_VERIFIED' if key in retained else
            'CONVERTED_UNVERIFIED' if row.get('assessment_path') else
            'BLOCKED' if row['conversion_attempted'] else 'MANUAL_OCIL_ONLY_PRESERVED')
    actual_native={p.name for p in (target/'authoring/direct-slice/assessments').glob('*.json')}
    ensure(expected_native==actual_native,'unaccounted or fabricated native Assessment')
    ledger['initial_conversion_summary']=ledger.get('initial_conversion_summary',ledger['summary'])
    ledger['summary']=summarize(rows)
    (target/'review.html').write_text(review)
    (target/'ledger.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
    s=json.loads((target/'summary.json').read_text())
    s['statuses']=dict(Counter(r['draft_status'] for r in rows))
    s['conversion_statuses']=dict(Counter(r['conversion_status'] for r in rows))
    (target/'summary.json').write_text(json.dumps(s,indent=2)+'\n')
    return rows,s,retained


def finalize(output, source_pins, baseline, known=None):
    output=Path(output)
    summaries=[]
    compact=[]
    retained=set()
    pins=source_pins['sources']
    known={} if known is None else known
    columns=['benchmark','source_rule','draft_status','conversion_attempted','original_source_validation',
             'independent_source_proof','compile_status','has_manual_source','primary_blocker','blockers',
             'preserved_original_rule','assessment_path','conversion_status','conversion_warnings']
    ensure(len(pins)==65,'exact 65-source pins required')
    for pin in pins:
        target=output/pin['file'].removesuffix('.zip')
        rows,source_summary,source_retained=finalize_source(target,pin,baseline,known)
        # Independent complete original accounting, separate from converter discovery.
        with zipfile.ZipFile(target/'source-preservation'/pin['file']) as z:
            members=[n for n in z.namelist() if n.endswith('.xml')]
            ensure(len(members)==1,'original SCAP member count drift')
            original=ET.fromstring(z.read(members[0]))
        components={n.get('id'):n[0] for n in original.findall('{'+DS+'}component')}
        checklists=original.findall('{'+DS+'}data-stream/{'+DS+'}checklists/{'+DS+'}component-ref')
        ensure(len(checklists)==1,'original checklist count drift')
        href=checklists[0].get('{http://www.w3.org/1999/xlink}href')
        ensure(href and href.startswith('#'),'original checklist binding unsupported')
        benchmark=components[href[1:]]
        ids={n.get('id') for n in benchmark.iter('{'+XCCDF+'}Rule')}
        ensure(ids=={r['source_rule'] for r in rows},'original Rule omitted or fabricated')
        preserved=json.loads((target/'source-preservation/components.json').read_text())
        ensure(set(preserved)==set(components),'original component omitted or fabricated')
        for key,node in components.items():
            copied=ET.parse(target/preserved[key]['path']).getroot()
            ensure(digest(xml_identity(copied))==digest(xml_identity(node)),'original component/manual content drift')
        summaries.append(source_summary)
        retained.update(source_retained)
        compact.extend({k:row.get(k) for k in columns} for row in rows)
    ensure(len(compact)==8892 and len({(r['benchmark'],r['source_rule']) for r in compact})==8892,'Rule accounting drift')
    ensure(retained==set(baseline),'published proof floor lost')
    ensure(sum(r['conversion_attempted'] for r in compact)==7239,'automated attempt accounting drift')
    (output/'ledger.json').write_text(json.dumps({'rules':compact},indent=2,ensure_ascii=False)+'\n')
    with (output/'ledger.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
        for row in compact:w.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    summary={'benchmarks':65,'rules':8892,'automated_conversion_attempts':7239,
             'retained_published_proofs':len(retained),'statuses':dict(Counter(r['draft_status'] for r in compact)),
             'sources':summaries,'checks':['All 65 original ZIP byte counts and SHA-256 retained',
                 'Every original Rule XML identity retained','No fabricated blocked/manual Assessment',
                 'Every native candidate has JSON/YAML and an exact authoring hash',
                 'Compiled program hashes agree with actual diagnostic packages',
                 'All published proof authoring/program/source-Rule hashes retained'],
             'limitations':['DRAFT, not verified for execution','Native primary subset; complete original policy/manual content preserved separately',
                 'Unverified candidates require original validity and independent proof in stage two',
                 'No schema/#255/source-repair/runtime acceptance inferred']}
    blocked=Counter()
    for row in compact:
        if row['draft_status']!='BLOCKED_EXPLICIT':continue
        issue=row['primary_blocker'] or {}
        message=issue.get('message','')
        category=('sqlext_package' if 'sqlext' in message else
                  'effective_deprecated_original' if message.startswith('Effectively deprecated original') else
                  'known_invalid_or_deprecated_original' if issue.get('category')=='source-exclusion' else
                  'catalog_binding' if message.startswith('unresolved checklist catalog href:') else
                  'blocked_contract_255' if message in ['unsupported Test existence: all_exist',
                      'OVAL check imports/exports unsupported','multiple aggregation components need an approved collection expression',
                      'unsupported acquisition parameter comparison/type'] or message.startswith('unsupported function:') else
                  'other_converter_or_source_investigation')
        blocked[category]+=1
    summary['blocked_primary_dispositions']=dict(blocked)
    summary['conversion_statuses']=dict(Counter(r['conversion_status'] for r in compact))
    summary['overlapping_warning_rules']=dict(Counter(code for row in compact
        for code in {w['code'] for w in row.get('conversion_warnings') or []}))
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
