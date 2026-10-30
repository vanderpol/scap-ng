"""Stable offline subprocess interface; JSON output for editor integrations."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import signal
import sqlite3
import sys

from . import REPORT_FORMAT
from .advisory import census
from .export import export_draft
from .reflow import reflow_layout
from .index import Library
from .transaction import apply_plan
from .records import original_records


def emit(value):
    print(json.dumps(value,ensure_ascii=False,sort_keys=True),flush=True)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',action='version',version=REPORT_FORMAT)
    sub=parser.add_subparsers(dest='mode',required=True)
    for name in ['analyze','check','apply','index','search','uses','census','compile']:
        p=sub.add_parser(name);p.add_argument('root',type=Path)
        p.add_argument('--index',type=Path,help='optional disposable generated SQLite cache')
        p.add_argument('--changed',action='append',help='complete editor notification list, relative to root')
        p.add_argument('--full',action='store_true',help='reparse all YAML; periodic census, not per-save default')
        if name in ('analyze','census'):
            p.add_argument('--near',action='store_true');p.add_argument('--max-pairs',type=int,default=100)
        if name=='apply':
            p.add_argument('--plan',type=Path,help='previously reviewed change manifest JSON')
            p.add_argument('--write',action='store_true',help='explicitly apply the printed safe presentation plan')
        if name=='search':
            p.add_argument('--query',default='');p.add_argument('--scope');p.add_argument('--limit',type=int,default=100)
            p.add_argument('--kind');p.add_argument('--status')
        if name=='uses':
            p.add_argument('--kind',default='assessment');p.add_argument('--id',required=True);p.add_argument('--scope',required=True)
        if name=='compile':
            p.add_argument('--scope',required=True);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('export-draft');p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--full-corpus-deliverable',action='store_true')
    p.add_argument('--source-archive',type=Path,help='exact published archive required for full acceptance')
    p=sub.add_parser('reflow-layout');p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--full-corpus-deliverable',action='store_true',help='require pinned 65-stream counts/proofs')
    p=sub.add_parser('records');p.add_argument('root',type=Path);p.add_argument('--scope')
    p.add_argument('--query',default='');p.add_argument('--status');p.add_argument('--limit',type=int,default=100)
    args=parser.parse_args(argv)
    old_handler=signal.getsignal(signal.SIGTERM)
    def cancelled(*_):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,cancelled)
    library=None
    try:
        if args.mode=='export-draft':
            emit(export_draft(args.source,args.output,full_corpus=args.full_corpus_deliverable,source_archive=args.source_archive));return 0
        if args.mode=='reflow-layout':
            emit(reflow_layout(args.source,args.output,full_corpus=args.full_corpus_deliverable));return 0
        if args.mode=='records':
            emit({'format':REPORT_FORMAT,'mode':'records','status':'PASS','validation_scope':'frozen_original_record_navigation',
                  'matches':original_records(args.root,scope=args.scope,query=args.query,status=args.status,limit=args.limit)});return 0
        library=Library(args.root,cache=args.index)
        if args.mode in ('search','uses') and library.loaded_cache and args.changed is None and not args.full:
            report={'format':REPORT_FORMAT,'status':'PASS','validation_scope':'cached_navigation_only',
                    'diagnostics':[],'metrics':{'parsed_documents':0}}
        else:
            library.refresh(args.changed,full=args.full)
            report=library.check(changed=args.changed)
        report['mode']=args.mode
        if args.mode=='search':report['matches']=library.search(query=args.query,scope=args.scope,
            kind=args.kind,status=args.status,limit=args.limit)
        if args.mode=='uses':
            rows=library.rows('WHERE kind=? AND id=? AND scope=?',(args.kind,args.id,args.scope))
            if len(rows)!=1:raise ValueError('uses query must select exactly one scoped identity')
            report['consumers']=library.consumers(rows[0],transitive=True)
        if args.mode in ('analyze','census'):
            if args.mode=='analyze':report['change_manifest']=library.plan(args.changed)
            report['reuse_census']=census(library,near=args.near,max_pairs=args.max_pairs)
        if args.mode=='index':
            if report['status']=='PASS':library.persist();report['generated_index']=str(library.cache)
        if args.mode=='compile' and report['status']=='PASS':
            target=args.output.resolve()
            if target.exists() or target.is_relative_to(library.root):
                raise ValueError('compiled output must be new and outside editable authoring')
            raw,manifest=library.compile_scope(args.scope)
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as output:output.write(raw)
            report.update(package=str(target),package_sha256=sha256(raw).hexdigest(),
                          compiled_programs=len(manifest['build_provenance']['compiled_programs']),
                          scanner_evaluated=False,publisher_trust_verified=False)
        if args.mode=='apply':
            plan=json.loads(args.plan.read_text()) if args.plan else library.plan(args.changed)
            emit({'event':'plan','validation':report,'change_manifest':plan})
            if report['status']!='PASS':return 1
            if args.write:emit(apply_plan(library,plan))
        else:emit(report)
        return 0 if report['status']=='PASS' else 1
    except KeyboardInterrupt:
        emit({'format':REPORT_FORMAT,'status':'CANCELLED','diagnostics':[{'code':'cancelled','severity':'info',
            'message':'operation cancelled; no implicit save or semantic promotion'}]});return 130
    except (ValueError,OSError,TypeError,sqlite3.Error) as error:
        emit({'format':REPORT_FORMAT,'status':'FAIL','diagnostics':[{'code':'tool-error','severity':'error',
            'message':str(error)}]});return 2
    finally:
        if library:library.close()
        signal.signal(signal.SIGTERM,old_handler)
