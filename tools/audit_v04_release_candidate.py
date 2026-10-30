#!/usr/bin/env python3
"""Bounded original-source CLI release gate; no scanner or full-corpus run."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from copy import deepcopy
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def run_gate(output, *, require_extracted=False):
    if require_extracted and (ROOT / '.git').exists():
        raise ValueError('clean-extract gate requires a source snapshot without .git')
    output.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / 'tests/fixtures/v04-draft-compatibility'
    pins = json.loads((fixture/'provenance.json').read_text())['sources']
    reports = []

    def command(args, log, expected=0):
        argv = [sys.executable, *map(str, args)]
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                                env=dict(os.environ, PYTHONPATH=str(ROOT/'tools'), PYTHONDONTWRITEBYTECODE='1'))
        (output/log).write_text(result.stdout+result.stderr)
        if (expected == 0 and result.returncode != 0) or (expected != 0 and result.returncode == 0):
            raise ValueError(f'CLI exit {result.returncode}; see {output/log}')
        return {'argv': argv, 'returncode': result.returncode, 'log': log}

    def convert(name, source, pin, rules, draft=False, proved=None):
        target=output/name
        args=[ROOT/'tools/v04_direct_converter.py', source, '--sha256', pin, '--output', target]
        args += ['--draft','--compile'] if draft else ['--verify']
        for rule in rules:args += ['--rule',rule]
        execution=command(args,name+'.log')
        report=json.loads((target/('package-verification.json' if draft else 'acceptance.json')).read_text())
        checked=report if draft else report.get('package_consumer')
        if proved is not None and report['outcomes'].get('PROVED',0)!=proved:
            raise ValueError('unexpected proved count: '+name)
        if checked:
            if checked['status']!='INDEPENDENT_PACKAGE_CONSUMER_PASS' or checked['scanner_evaluated']:
                raise ValueError('independent package gate failed: '+name)
        if draft:
            trace=json.loads((target/'source-trace.json').read_text())
            if not all(r.get('conversion_warnings') and not r['independent_static_proof_eligible'] for r in trace['rules']):
                raise ValueError('warning draft lost proof separation')
            execution['independent_reader']=command([ROOT/'tools/verify_v04_package_consumer.py',
                target/'CONVERTED_UNVERIFIED.scapng','--source-json',target/'authoring',
                '--source-yaml',target/'authoring','--report',target/'independent-package.json'],name+'-reader.log')
        reports.append({'name':name,'source_sha256':pin,'draft':draft,'execution':execution,
                        'outcomes':report.get('outcomes'),'package_consumer':checked})
        return report

    al=next(p for p in pins if 'Amazon_Linux' in p['file'])
    ad=next(p for p in pins if 'Active_Directory_Domain' in p['file'])
    fw=next(p for p in pins if 'Windows_Defender_Firewall' in p['file'])
    convert('linux-static',fixture/al['file'],al['sha256'],['xccdf_mil.disa.stig_rule_SV-273996r1119976_rule'],proved=1)
    server=ROOT/'tests/fixtures/v04-direct-prototype/server2025-signed.zip'
    server_pin='2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0'
    from v04_direct_scap_source import SourceModel, DS
    source=SourceModel(server,server_pin)
    rules=[next(r for r in source.rules if '_SV-'+n+'r' in r) for n in ['278139','278001','278031']]
    windows=convert('windows-static-shared',server,server_pin,rules[:2],proved=2)
    if not windows['package_consumer']['shared_objects']:
        raise ValueError('Windows example must demonstrate shared Object references')
    convert('catalog-warning',fixture/ad['file'],ad['sha256'],['xccdf_navy.navwar.niwcatlantic.scc.ms_rule_SV-243466r959010_rule'],draft=True)
    convert('all-exist-warning',fixture/al['file'],al['sha256'],['xccdf_mil.disa.stig_rule_SV-274017r1120039_rule'],draft=True)
    convert('input-binding-warning',fixture/fw['file'],fw['sha256'],['xccdf_mil.disa.fso_rule_SV-241989r922928_rule'],draft=True)
    invalid=convert('incompatible-source-negative',server,server_pin,rules[2:],proved=0)
    if invalid['outcomes'].get('BLOCKED') != 1 or invalid.get('programs'):
        raise ValueError('incompatible source produced executable candidate')

    # Deliberately modified negative fixture; never describe it as signed original.
    original=SourceModel(fixture/ad['file'],ad['sha256'],draft_compatibility=True)
    root=deepcopy(original.root)
    catalog=root.find('.//{urn:oasis:names:tc:entity:xmlns:xml:catalog}catalog')
    extension=next(n for n in catalog if n.tag=='{'+DS+'}uri')
    catalog.append(deepcopy(extension))
    negative=output/'synthetic-duplicate-catalog.zip'
    with zipfile.ZipFile(fixture/ad['file']) as before, zipfile.ZipFile(negative,'w') as after:
        for member in before.namelist():
            after.writestr(member,ET.tostring(root) if member==original.member else before.read(member))
    execution=command([ROOT/'tools/v04_direct_converter.py',negative,'--sha256',sha256(negative.read_bytes()).hexdigest(),
        '--rule','xccdf_navy.navwar.niwcatlantic.scc.ms_rule_SV-243466r959010_rule',
        '--draft','--compile','--output',output/'must-not-exist'],'ambiguous-catalog-negative.log',expected=1)
    if (output/'must-not-exist').exists():raise ValueError('ambiguous catalog emitted native output')
    reports.append({'name':'synthetic-ambiguous-catalog-negative','execution':execution})
    report={'status':'PASS','source_root':str(ROOT),'python':sys.version,'extracted':not (ROOT/'.git').exists(),
            'cases':reports,'scanner_runtime':'NOT_RUN','publisher_trust':'NOT_VERIFIED'}
    (output/'release-gate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--require-extracted',action='store_true')
    args=parser.parse_args()
    print(json.dumps(run_gate(args.output.resolve(),require_extracted=args.require_extracted),indent=2))
