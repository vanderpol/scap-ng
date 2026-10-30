"""Repackage #261 native YAML into the owner-approved 0.3-style physical tree.

No OVAL conversion, native ID rewrite, Assessment sharing or semantic
normalization. This is an explicit out-of-place deliverable operation.
"""
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
import time

import yaml

from .index import Library
from .names import benchmark_folder, native_relative, source_sv


def _read(root, relative):
    path = root/relative
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('source file escapes normalized-library boundary: '+str(relative))
    return path.read_bytes()


def _write(path, raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)
    os.utime(path,ns=(0,0))


def reflow_layout(source, output, *, full_corpus=False):
    """Make a path-only review v2 from the published normalized v1 directory."""
    started=time.perf_counter()
    source=Path(source).resolve()
    output=Path(output).resolve()
    content=source/'content'
    if not content.is_dir() or not (source/'records/streams').is_dir():
        raise ValueError('source must be a complete normalized v1 library root')
    if source.is_symlink() or output.exists() or output.is_relative_to(source):
        raise ValueError('destination must be new and outside the source tree')
    catalog=yaml.safe_load(_read(content,'catalog.yaml'))
    if catalog.get('format')!='scap-ng-library-catalog/1':
        raise ValueError('wrong source catalog format')
    entries=catalog['benchmarks']
    inventory=json.loads(_read(source/'metadata','native-files.json'))
    if full_corpus and (len(entries)!=65 or len(inventory)!=13754):
        raise ValueError('published 65-stream/native-document counts differ')

    assigned,shorts,records={},set(),{}
    native_scopes=0
    original_counts=Counter()
    for entry in entries:
        old=entry['scope']
        folder=benchmark_folder(entry['title'])
        if folder.casefold() in shorts:
            raise ValueError('duplicate human-readable Benchmark folder: '+folder)
        shorts.add(folder.casefold())
        record=json.loads(_read(source/'records/streams',old+'.json'))
        original_counts.update(r['conversion_status'] for r in record['original_ledger']['rules'])
        oldpaths={m['source_path']:m for m in record['native_path_mapping']}
        proposed={}
        if entry['native_assessments']:
            native_scopes+=1
            for kind in ('benchmark','applicability'):
                matches=[m for m in record['native_path_mapping'] if m['kind']==kind]
                if len(matches)!=1:
                    raise ValueError(folder+' requires exactly one '+kind)
                proposed[matches[0]['path']]=native_relative(folder,kind)
            for row in record['original_ledger']['rules']:
                if not row.get('assessment_path'):
                    continue
                sv=source_sv(row)
                paths=[('assessment',row['assessment_path'])]
                paths += [('rule',p) for p in row['artifacts']
                          if '/rules/' in p and p.endswith('.json')]
                if len(paths)!=2:
                    raise ValueError(folder+'/'+sv+': ambiguous imported Rule/Assessment mapping')
                for kind,path in paths:
                    source_path=(record['source_stream']+'/' +
                                 Path(path).with_suffix('.yaml').as_posix())
                    mapping=oldpaths.get(source_path)
                    if not mapping or mapping['kind']!=kind:
                        raise ValueError('missing original provenance mapping for '+source_path)
                    # The pinned #261 corpus has only automated native
                    # Assessments; manual originals are preserved records.
                    target=native_relative(folder,kind,sv)
                    if mapping['path'] in proposed and proposed[mapping['path']]!=target:
                        raise ValueError('shared source path needs explicit owner naming: '+mapping['path'])
                    proposed[mapping['path']]=target
        if len(proposed)!=len(record['native_path_mapping']):
            raise ValueError('unmapped native documents in '+folder)
        for oldpath,newpath in proposed.items():
            key=newpath.casefold()
            if key in assigned:
                raise ValueError('case-insensitive destination collision: '+newpath)
            if len(newpath)>190:
                raise ValueError('nonportable destination path: '+newpath)
            assigned[key]=oldpath
        records[old]=(folder,record,proposed)

    if full_corpus:
        expected={'CONVERTED_VERIFIED':4258,'CONVERTED_UNVERIFIED':2559,
                  'BLOCKED':422,'MANUAL_OCIL_ONLY_PRESERVED':1653}
        if native_scopes!=60 or dict(original_counts)!=expected:
            raise ValueError('published native-stream/status accounting drift')
    if len(assigned)!=len(inventory):
        raise ValueError('not every source native document has a unique destination')

    output.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.human-library-',dir=output.parent))
    lib=None
    try:
        authoring=stage/'authoring'
        updated=[]
        seen=set()
        for item in inventory:
            old=item['path']
            # Find a verified exact path, never an ID-based first match.
            lookup=[new[old] for _,_,new in records.values() if old in new]
            if len(lookup)!=1:
                raise ValueError('source inventory path ambiguous or missing: '+old)
            newpath=lookup[0]
            raw=_read(content,old)
            if sha256(raw).hexdigest()!=item['yaml_sha256']:
                raise ValueError('source YAML bytes changed: '+old)
            _write(authoring/newpath,raw)
            updated.append({**item,'path':newpath})
            seen.add(old)
        if len(seen)!=len(assigned):
            raise ValueError('unaccounted source paths')

        for old,(folder,record,mapping) in records.items():
            record['native_path_mapping']=[{**m,'path':mapping[m['path']]}
                                           for m in record['native_path_mapping']]
            record['human_readable_layout']='0.3-style-v2'
            _write(stage/'records/streams'/(folder+'.json'),
                   (json.dumps(record,indent=2,ensure_ascii=False)+'\n').encode())
            trace=source/'records/streams'/(old+'.source-trace.json')
            if trace.exists():
                _write(stage/'records/streams'/(folder+'.source-trace.json'),
                       _read(source/'records/streams',trace.name))
        new_catalog={**catalog,'benchmarks':[
            {**item,'scope':records[item['scope']][0]} for item in entries]}
        _write(stage/'metadata/catalog.yaml',
               yaml.safe_dump(new_catalog,sort_keys=False,allow_unicode=True).encode())
        _write(stage/'metadata/native-files.json',
               (json.dumps(updated,indent=2,ensure_ascii=False)+'\n').encode())
        _write(stage/'metadata/previous-export-receipt.json',
               _read(source/'metadata','export-receipt.json'))

        # The cache is disposable, so build it independently from moved YAML
        # and durable sidecars. This also recompiles every automated program.
        lib=Library(authoring,cache=stage/'metadata/library.sqlite')
        lib.refresh(full=True)
        report=lib.check()
        if report['status']!='PASS':
            raise ValueError('v2 native/reference validation failed: '+str(report['diagnostics'][:5]))
        indexed={r['path']:r for r in lib.rows()}
        preserved=Counter()
        for item in updated:
            current=indexed.get(item['path'])
            if not current or current['authoring_sha']!=item['authoring_sha256']:
                raise ValueError('native authoring graph changed: '+item['path'])
            if item['kind']=='assessment':
                if current['program_sha']!=item['program_sha256']:
                    raise ValueError('compiled Assessment hash changed: '+item['path'])
                preserved[current['status']]+=1
        if full_corpus and (preserved['CONVERTED_VERIFIED']!=4258 or
                            preserved['CONVERTED_UNVERIFIED']!=2559):
            raise ValueError('frozen 65-stream accepted proof/status floor lost')
        lib.persist()
        receipt={'format':'scap-ng-native-human-library-v2/1','status':'PASS',
                 'source_layout':'normalized-v1','streams':len(entries),
                 'native_benchmarks':native_scopes,'native_yaml':len(updated),
                 'compiled_program_hashes_unchanged':sum(preserved.values()),
                 'accepted_static_proofs_unchanged':preserved['CONVERTED_VERIFIED'],
                 'unverified_unchanged':preserved['CONVERTED_UNVERIFIED'],
                 'source_statuses':dict(original_counts),
                 'max_relative_path':max(map(lambda x:len(x['path']),updated)),
                 'automatic_shared_promotions':0,'index_check':report,
                 'seconds':time.perf_counter()-started,
                 'native_ids_and_yaml_bytes':'UNCHANGED',
                 'scanner_evaluated':False,'publisher_trust_verified':False}
        _write(stage/'metadata/reflow-receipt.json',
               (json.dumps(receipt,indent=2)+'\n').encode())
        _write(stage/'README.md',
               ("# SCAP-NG 0.4.0 human-readable authoring review v2\n\n"
                "This is a non-normative layout review, not a final release or scanner proof.\n"
                "Open authoring/ for short per-STIG folders. Each has benchmark.yaml,\n"
                "applicability.yaml, rules/SV-ID.rule.yaml and\n"
                "assessments/automated/SV-ID.automated.yaml. Manual originals remain\n"
                "in records/ until real native manual source exists. No local/ folders\n"
                "or automatic filename hashes. Shared Assessments are not fabricated.\n"
                "CLI root: authoring/; records/ and metadata/ are durable sidecars\n"
                "and disposable navigation metadata respectively. Original logical\n"
                "IDs, YAML bytes, static proof statuses and compiled programs are\n"
                "unchanged from the pinned 0.4.0 normalized v1 technical evidence.\n").encode())
        lib.close();lib=None
        if output.exists():
            raise ValueError('destination appeared during export')
        stage.rename(output)
        return receipt
    finally:
        if lib:lib.close()
        if stage.exists():
            shutil.rmtree(stage)
