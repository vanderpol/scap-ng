#!/usr/bin/env python3
"""Compare source Rule check selectors, defaults and metadata to a full native review."""
import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scap_upconvert_v003.convert_collection_review import source_benchmark
from scap_upconvert_v003.build_rhel9_review_slice import NS, local
from scap_upconvert_v003.audit_profile_selection import native_rule_id


def audit(package, output):
    xr=source_benchmark(package)
    evidence=json.loads((output/'evidence.json').read_text(encoding='utf-8'))
    bindings={r['rule_id']:r for r in evidence['rules']}
    issues=[]; comparisons=[]
    source_rules=xr.findall('.//x:Rule',NS)
    paths=list((output/'rules').glob('*.rule.yaml'))
    if len(paths)!=len(source_rules): issues.append('Rule file count differs')
    benchmark=yaml.safe_load((output/'benchmark.yaml').read_text(encoding='utf-8'))['benchmark']
    if set(benchmark['rules'])!={native_rule_id(r.get('id')) for r in source_rules}:
        issues.append('Benchmark membership differs')
    for element in source_rules:
        rid=native_rule_id(element.get('id'))
        native=yaml.safe_load((output/'rules'/f'{rid}.rule.yaml').read_text(encoding='utf-8'))['rule']
        choices=native['assessment_choices'];expected={}; checks=element.findall('x:check',NS)
        for check in checks:
            selector=(check.get('selector') or '').strip() or 'default'
            if selector in expected: issues.append(rid+': duplicate source selector')
            expected[selector]=check
        fallbacks={row['selector']:row for row in bindings[rid].get('manual_fallbacks',[])}
        expected_native=set(expected)-{selector for selector in fallbacks if selector!='default'}
        if set(choices)!=expected_native: issues.append(rid+': selector set differs')
        if 'default' not in expected or native['default_assessment_choice']!='default':
            issues.append(rid+': source default selection is not preserved')
        assessment_definitions={a['path']:a['source_graph_bindings']['source_definition']
                                for a in bindings[rid]['assessments']
                                if a.get('path') and a.get('source_graph_bindings')}
        for selector,check in expected.items():
            if selector in fallbacks and selector!='default':
                if selector in choices: issues.append(rid+': deprecated automated selector was not skipped: '+selector)
                continue
            ref=choices[selector]['assessment']; target=(output/'rules'/ref).resolve()
            if not target.is_relative_to(output.resolve()): raise ValueError('Package escape')
            method=yaml.safe_load(target.read_text(encoding='utf-8'))['assessment']
            manual=check.get('system')=='http://scap.nist.gov/schema/ocil/2'
            expected_mode='manual' if manual or selector in fallbacks else 'automated'
            if method['mode']!=expected_mode: issues.append(rid+': mode differs for '+selector)
            if selector in fallbacks:
                # Intentional NG migration rule: deprecated automated OVAL is
                # not converted. The source default may point to the verified
                # source manual Assessment instead.
                continue
            if not manual:
                original=check.find('x:check-content-ref',NS)
                path=target.relative_to(output.resolve()).as_posix()
                if assessment_definitions.get(path)!=original.get('name'):
                    issues.append(rid+': source definition binding differs for '+selector)
            else:
                content=check.find('x:check-content',NS)
                procedure=' '.join(''.join(content.itertext()).split()) if content is not None else None
                if not procedure:
                    source_ref=check.find('x:check-content-ref',NS)
                    alternatives=[c for c in checks if c is not check and c.get('system')==check.get('system')
                                  and c.find('x:check-content-ref',NS) is not None
                                  and c.find('x:check-content-ref',NS).attrib==source_ref.attrib]
                    values={' '.join(''.join(c.find('x:check-content',NS).itertext()).split())
                            for c in alternatives if c.find('x:check-content',NS) is not None}
                    if len(values)!=1: issues.append(rid+': unresolved shared manual procedure')
                    procedure=next(iter(values),None)
                if method['procedure']!=procedure: issues.append(rid+': manual procedure differs')
        for key,default in (('severity',None),('role','full')):
            if native[key]!=(element.get(key) or default): issues.append(rid+': '+key+' differs')
        if native['weight']!=float(element.get('weight') or '1'): issues.append(rid+': weight differs')
        source_title=' '.join(''.join(element.find('x:title',NS).itertext()).split())
        if native['title']!=source_title: issues.append(rid+': title differs')
        comparisons.append({'rule':rid,'selectors':list(expected),'native_selectors':list(choices),
                            'manual_fallbacks':list(fallbacks),'default':'default',
                            'matched':not any(x.startswith(rid+':') for x in issues)})
    return {'source_rules':len(source_rules),'native_rules':len(paths),'rule_comparisons':comparisons,
            'issues':issues,'limits':['Compares source bindings, manual inline procedures and selected Rule metadata; does not prove runtime equivalence or complete metadata conformance.']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();report=audit(a.input,a.output)
    (a.output/'rule-source-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rules':report['source_rules'],'issues':report['issues']},indent=2))
    return int(bool(report['issues']))

if __name__=='__main__':raise SystemExit(main())
