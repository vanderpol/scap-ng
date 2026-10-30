"""Out-of-place layout export of existing native drafts; never OVAL conversion."""
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
import zipfile
import xml.etree.ElementTree as ET

import yaml

from .documents import canonical_yaml, digest, filename, parse, slug, title
from .index import Library

DRAFT_SHA = 'a09ee9a13cdfeeb1b8599eab61308e935a19b99eb62eadafd32002d13d90f8bd'
DRAFT_LOCATOR = 'https://github.com/vanderpol/scap-ng-evidence/tree/v04-revised-all65-draft-files-20261030-a08c9beb9/runs/v04-converter/2026-10-30-all-65-revised-draft-download'


def original_stream_title(stream, ledger, checked_bytes):
    """Read presentation metadata from the one preserved source Benchmark."""
    components=stream/'source-preservation/components.json'
    if not components.is_file():return 'Original-only source records'
    entries=json.loads(checked_bytes(components))
    selected=entries.get(ledger.get('source_benchmark_component'))
    if not selected:raise ValueError('preserved Benchmark metadata binding is missing')
    node=ET.fromstring(checked_bytes(stream/selected['path']))
    namespace='{http://checklists.nist.gov/xccdf/1.2}'
    if node.tag!=namespace+'Benchmark':raise ValueError('preserved title target is not the selected Benchmark')
    label=node.find(namespace+'title')
    return ''.join(label.itertext()) if label is not None else 'Original-only source records'


def export_draft(source, output, *, full_corpus=False, validate_schema=True, source_archive=None):
    """Retain complete native payloads and proof hashes under shorter paths.

    Input must be the already-generated DRAFT directory, never original ZIPs.
    Full-corpus accounting is an explicit deliverable gate, not ordinary CI.
    """
    started = time.perf_counter()
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.exists() or output.is_relative_to(source):
        raise ValueError('export requires a new destination outside the input tree')
    if source.is_symlink():raise ValueError('source symlink is not eligible')
    streams = sorted(p.parent for p in source.glob('*/ledger.json'))
    if not streams:raise ValueError('no completed DRAFT stream ledgers')
    if full_corpus and len(streams)!=65:raise ValueError('expected exactly 65 published streams')
    pinned_files = None
    if full_corpus:
        if not source_archive or sha256(Path(source_archive).read_bytes()).hexdigest()!=DRAFT_SHA:
            raise ValueError('full acceptance requires the exact published DRAFT archive SHA256')
        with zipfile.ZipFile(source_archive) as archive:
            pinned_files = {r['path']:r for r in json.loads(archive.read('all-65-revised-draft/artifact-files.json'))}
        expected_streams = {Path(p).parent.as_posix() for p in pinned_files if p.count('/')==1 and p.endswith('/ledger.json')}
        if {p.relative_to(source).as_posix() for p in streams}!=expected_streams:
            raise ValueError('source stream identities differ from pinned archive')
    def checked_bytes(path):
        if path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError('DRAFT source reference escapes input boundary')
        raw=path.read_bytes()
        if pinned_files is not None:
            item=pinned_files.get(path.relative_to(source).as_posix())
            if not item or len(raw)!=item['bytes'] or sha256(raw).hexdigest()!=item['sha256']:
                raise ValueError('source file differs from pinned published DRAFT: '+str(path))
        return raw
    output.parent.mkdir(parents=True,exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.native-library-',dir=output.parent))
    content = stage/'content';content.mkdir()
    index = Library(content,cache=stage/'metadata/library.sqlite')
    counts, retained, compiled, paths, catalogs = Counter(), 0, 0, set(), []
    inventory = []
    try:
        used_scopes = set()
        for stream in streams:
            ledger = json.loads(checked_bytes(stream/'ledger.json'))
            rows = ledger['rules']
            native = sorted((stream/'authoring').rglob('*.yaml'))
            # Native kind dispatch, not original ZIP basename or numeric Rule ID.
            documents = [(p,parse(checked_bytes(p))) for p in native]
            benchmarks = [doc['benchmark'] for _,doc in documents if 'benchmark' in doc]
            if len(benchmarks)>1:raise ValueError('ambiguous Benchmark stream')
            if benchmarks:
                benchmark = benchmarks[0]
                label = title(benchmark)
                label = label.replace('[AUTOMATED PROTOTYPE SUBSET]','').strip()
                # Generic imported IDs (e.g. direct-slice) need an explicit,
                # deterministic navigation namespace, independent of file order.
                scope = slug(label,48)+'-'+digest({'id':benchmark['id'],'title':benchmark.get('title')})[:8]
                if scope in used_scopes:raise ValueError('indistinguishable Benchmark namespace; explicit ownership needed')
                used_scopes.add(scope)
            else:
                # A wholly manual/blocked stream has no fabricated native tree.
                # Its immutable source identity stays in records, not editable IDs.
                scope = 'preserved-original-'+digest(ledger.get('original_zip',stream.name))[:12]
                label = original_stream_title(stream,ledger,checked_bytes)
            by_rule = {r['source_rule']:r for r in rows}
            if len(by_rule)!=len(rows):raise ValueError('duplicate original Rule identity')
            by_assessment = {}
            by_native_rule = {}
            for row in rows:
                status = row.get('conversion_status') or (
                    'CONVERTED_VERIFIED' if row['draft_status']=='RETAINED_PUBLISHED_STATIC_PRIMARY_PROOF' else
                    'CONVERTED_UNVERIFIED' if row.get('assessment_path') else
                    'BLOCKED' if row['conversion_attempted'] else 'MANUAL_OCIL_ONLY_PRESERVED')
                counts[status] += 1
                if row.get('assessment_path'):
                    path = stream/row['assessment_path']
                    body = json.loads(checked_bytes(path))['assessment']
                    if digest(body)!=row['authoring_sha256']:raise ValueError('original Assessment authoring hash drift')
                    by_assessment[body['id']] = {**row,'conversion_status':status}
                    rule_paths = [a for a in row['artifacts'] if '/rules/' in a and a.endswith('.json')]
                    for rp in rule_paths:
                        rule = json.loads(checked_bytes(stream/rp))['rule']
                        by_native_rule[rule['id']] = {**row,'conversion_status':status}
                elif status.startswith('CONVERTED_'):
                    raise ValueError('native count cannot be supplied by a placeholder')
            mapping = []
            for original,doc in documents:
                kind,body = next(iter(doc.items()))
                pair = original.with_suffix('.json')
                if not pair.exists() or json.loads(checked_bytes(pair))!=doc:
                    raise ValueError('published JSON/YAML authoring differs')
                if kind=='benchmark':relative='benchmarks/'+scope+'.yaml'
                elif kind=='applicability':relative='applicability/'+scope+'.yaml'
                elif kind=='rule':relative='rules/'+scope+'/'+filename(kind,body)
                else:relative='assessments/local/'+scope+'/'+filename(kind,body)
                if len(relative)>190 or relative.casefold() in paths:
                    raise ValueError('nonportable/colliding normalized authoring path: '+relative)
                paths.add(relative.casefold())
                target = content/relative;target.parent.mkdir(parents=True,exist_ok=True)
                raw = canonical_yaml(doc);target.write_bytes(raw);os.utime(target,ns=(0,0))
                proof = (by_assessment if kind=='assessment' else by_native_rule).get(body['id'],{})
                index.update(relative,raw,provenance=proof,check_schema=validate_schema)
                indexed = index.rows('WHERE path=?',(relative,))[0]
                if kind=='assessment' and body.get('mode')=='automated':
                    if not proof:raise ValueError('unaccounted native Assessment')
                    if indexed['program_sha']!=proof['program_sha256']:
                        raise ValueError('layout export changed compiled Assessment/operands')
                    compiled += 1
                    if proof['conversion_status']=='CONVERTED_VERIFIED':
                        if indexed['status']!='CONVERTED_VERIFIED':raise ValueError('accepted proof/hash pair lost')
                        retained += 1
                item = {'source_path':original.relative_to(source).as_posix(),'path':relative,
                        'kind':kind,'id':body['id'],'document_sha256':digest(doc),
                        'authoring_sha256':digest(body),'yaml_sha256':sha256(raw).hexdigest(),
                        'program_sha256':indexed['program_sha']}
                mapping.append(item);inventory.append(item)
            record = stage/'records/streams'/ (scope+'.json');record.parent.mkdir(parents=True,exist_ok=True)
            record.write_text(json.dumps({'source_stream':stream.name,'original_ledger':ledger,
                'native_path_mapping':mapping,'source_artifact':DRAFT_LOCATOR,
                'source_archive_sha256':DRAFT_SHA,'scope_is_navigation_namespace_not_applicability':True},
                indent=2,ensure_ascii=False)+'\n')
            trace = stream/'source-trace.json'
            if trace.exists():
                record.with_name(scope+'.source-trace.json').write_bytes(checked_bytes(trace))
            catalogs.append({'scope':scope,'native_benchmark_id':benchmarks[0]['id'] if benchmarks else None,
                'title':label,'original_rules':len(rows),'native_assessments':len(by_assessment),
                'conversion_statuses':dict(Counter(r['conversion_status'] for r in rows))})
        report = index.check()
        if report['status']!='PASS':raise ValueError('export reference validation failed: '+str(report['diagnostics'][:5]))
        if full_corpus:
            expected={'CONVERTED_VERIFIED':4258,'CONVERTED_UNVERIFIED':2559,'BLOCKED':422,'MANUAL_OCIL_ONLY_PRESERVED':1653}
            if dict(counts)!=expected or compiled!=6817 or retained!=4258:
                raise ValueError('published 65-stream accounting/proof floor drift')
        index.persist()
        catalog={'format':'scap-ng-library-catalog/1','generated':True,
            'authoring_source_of_truth':'YAML; this is a disposable navigation index',
            'benchmarks':sorted(catalogs,key=lambda c:c['scope'])}
        (content/'catalog.yaml').write_text(yaml.safe_dump(catalog,sort_keys=False,allow_unicode=True))
        (stage/'metadata/native-files.json').write_text(json.dumps(inventory,indent=2)+'\n')
        receipt={'format':'scap-ng-native-library-export/1','status':'PASS','streams':len(streams),
            'original_rules':sum(counts.values()),'conversion_statuses':dict(counts),
            'compiled_program_hashes_unchanged':compiled,'retained_proof_hash_pairs':retained,
            'native_documents':len(inventory),'max_relative_path':max(map(len,paths),default=0),
            'native_ids_and_payloads':'UNCHANGED','automatic_shared_promotions':0,
            'index_check':report,'seconds':time.perf_counter()-started,
            'source_archive_sha256':DRAFT_SHA,'source_artifact':DRAFT_LOCATOR,
            'source_archive_verified':bool(pinned_files),
            'limitations':['Layout-only; no new source proof or runtime evaluation',
                'Profiles remain embedded; global sharing scope unchanged',
                'Generic direct-slice Benchmark IDs retained in distinct private library namespaces',
                'Manual/blocked sources are records linked to original artifact, not native placeholders']}
        (stage/'metadata/export-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        index.close()
        if output.exists():raise ValueError('destination appeared during export; refusing replacement')
        stage.rename(output)
        return receipt
    except BaseException:
        index.close();shutil.rmtree(stage)
        raise
