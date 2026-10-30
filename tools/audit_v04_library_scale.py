#!/usr/bin/env python3
"""Explicit synthetic index budget audit; not a corpus conversion or CI default."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import resource
import time

from scap_ng_library.documents import canonical_yaml
from scap_ng_library.index import Library

ROOT=Path(__file__).resolve().parents[1]


def audit(output,streams=100,rules_per_stream=50):
    if output.exists():raise ValueError('scale audit needs a new output directory')
    if not 1<=streams<=100 or not 1<=rules_per_stream<=100:raise ValueError('bounded synthetic audit dimensions required')
    output.mkdir(parents=True);content=output/'content';content.mkdir()
    fixture=ROOT/'tests/fixtures/v04-native-library/focused-draft/linux-static/authoring/direct-slice'
    benchmark=json.loads((fixture/'benchmark.json').read_text())['benchmark']
    rule=json.loads(next((fixture/'rules').glob('*.json')).read_text())['rule']
    assessment=json.loads(next((fixture/'assessments').glob('*.json')).read_text())['assessment']
    lib=Library(content);started=time.perf_counter();changed=None
    try:
        def put(path,doc):
            raw=canonical_yaml(doc);target=content/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            # Seeds are native-fixture copies; generation here measures index,
            # not independent validation/proof of synthetic compliance content.
            lib.update(path,raw,check_schema=False)
        for stream in range(streams):
            scope=f'scale-{stream:03}';members=[]
            for n in range(rules_per_stream):
                a=deepcopy(assessment);a['id']=f'collection-scale-{n:03}-assessment'
                r=deepcopy(rule);r['id']=f'policy-scale-{n:03}-rule';r['assessment_choices']={'automated':{'assessment':a['id']}};r['default_assessment_choice']='automated';r['applicability']=[]
                path=f'assessments/local/{scope}/{a["id"]}.yaml';put(path,{'assessment':a})
                if changed is None:changed=(path,deepcopy(a))
                put(f'rules/{scope}/{r["id"]}.yaml',{'rule':r});members.append(r['id'])
            b=deepcopy(benchmark);b['id']='scale-benchmark';b['rules']=members;b['profiles']=[];b['groups']=[];b['applicability_catalog']=None
            put(f'benchmarks/{scope}.yaml',{'benchmark':b})
        initial=lib.check()
        if initial['status']!='PASS':raise ValueError(str(initial['diagnostics'][:3]))
        lib.persist();setup_seconds=time.perf_counter()-started
    finally:lib.close()
    started=time.perf_counter();lazy=Library(content)
    try:matches=lazy.search(scope='scale-000',query='collection',limit=20)
    finally:lazy.close()
    search_seconds=time.perf_counter()-started
    path,a=changed;a['assessment_title']+=' (synthetic edit)';(content/path).write_bytes(canonical_yaml({'assessment':a}))
    started=time.perf_counter();incremental=Library(content)
    try:
        incremental.refresh([path]);checked=incremental.check(changed=[path])
    finally:incremental.close()
    seconds=time.perf_counter()-started
    expected=streams*(rules_per_stream*2+1)
    if checked['status']!='PASS' or checked['metrics']['indexed_documents']!=expected or checked['metrics']['parsed_documents']!=1:
        raise ValueError('incremental synthetic index acceptance failed')
    report={'status':'PASS','synthetic':True,'streams':streams,'native_index_documents':expected,
        'setup_seconds':setup_seconds,'lazy_scope_search_seconds':search_seconds,'lazy_matches':len(matches),
        'incremental_check_seconds':seconds,'incremental':checked,
        'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'limitations':['Index/reference performance only; not scanner/runtime/source-proof evidence',
                       'Initial native-fixture copies seeded without per-document schema replay; edited Assessment validated normally']}
    (output/'scale-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--streams',type=int,default=100);parser.add_argument('--rules-per-stream',type=int,default=50)
    args=parser.parse_args();print(json.dumps(audit(args.output,args.streams,args.rules_per_stream),indent=2))
