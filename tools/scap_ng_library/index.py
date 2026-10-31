"""Disposable SQLite navigation cache; native YAML remains authoritative."""
from collections import defaultdict, deque
from difflib import unified_diff
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
import time
import yaml

from . import REPORT_FORMAT
from .documents import (canonical_yaml, digest, edges, parse, read, scope_for,
                        title, validate, version)
from verify_v04_package_consumer import UniqueYaml

SCHEMA = '''
CREATE TABLE nodes(path TEXT PRIMARY KEY, folded TEXT UNIQUE, scope TEXT, kind TEXT,
 id TEXT, version TEXT, title TEXT, payload TEXT, source_sha TEXT, authoring_sha TEXT,
 program_sha TEXT, status TEXT, warnings TEXT, baseline TEXT, size INTEGER, mtime INTEGER,
 specification TEXT, mode TEXT, exact_sha TEXT);
CREATE INDEX identities ON nodes(kind,id,scope);
CREATE TABLE edges(source TEXT, kind TEXT, id TEXT, version TEXT, field TEXT, purpose TEXT);
CREATE INDEX consumers ON edges(kind,id);
CREATE INDEX sources ON edges(source);
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);
'''
PROOF_KEYS=frozenset({'conversion_status','conversion_warnings','authoring_sha256',
    'program_sha256','source_rule','source_rule_sha256','source_zip_sha256','document_authoring_sha256'})


def diagnostic(root, row, code, message, *, severity='error', field=None, consumers=None, reference=None):
    span=None
    if reference:
        try:
            matches=[]
            for n,line in enumerate(read(root,row['path']).decode().splitlines()):
                offset=line.find(reference)
                if offset>=0 and re.search(r'(?:assessment|applicability_catalog):|^\s*-\s',line):
                    matches.append({'start':{'line':n,'character':offset},
                                    'end':{'line':n,'character':offset+len(reference)}})
            if len(matches)==1:span=matches[0]
        except (ValueError,OSError,UnicodeError):pass
    return {'code': code, 'severity': severity, 'message': message,
            'file_uri': (root/row['path']).absolute().as_uri(), 'path': row['path'],
            'document_id': row.get('id'), 'kind': row.get('kind'), 'scope': row.get('scope'),
            'span': span, 'source_field': field, 'reason': message,
            'proposed_change': None, 'patch': None, 'affected_consumers': consumers or [],
            'proof_status': row.get('status', 'UNVERIFIED'),
            'warnings': json.loads(row.get('warnings') or '[]')}


class Library:
    """An isolated in-memory session, optionally seeded by a read-only cache.

    Neither analyze/check nor changed-document sessions write authoring/cache.
    Explicit index/export/apply operations own persistence. A supplied changed
    list is the editor's complete notification set, not a full census claim.
    """
    def __init__(self, root, *, cache=None):
        self.root = Path(root).resolve()
        self.cache = Path(cache) if cache else (
            self.root.parent/'metadata/library.sqlite' if self.root.name in ('content','authoring') else
            self.root.parent/'.scap-ng-index'/(self.root.name+'-'+sha256(str(self.root).encode()).hexdigest()[:8]+'.sqlite'))
        if self.cache.resolve().is_relative_to(self.root):
            raise ValueError('generated index must remain outside editable authoring tree')
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        self.parsed = 0
        self.diagnostics = []
        self.loaded_cache = False
        self.removed_proofs = {}
        self.scope_provenance = {}
        self.benchmark_declarations = None
        if self.cache.is_file():
            saved=sqlite3.connect(self.cache.resolve().as_uri()+'?mode=ro', uri=True)
            try:saved.backup(self.db)
            finally:saved.close()
            if self.db.execute('PRAGMA user_version').fetchone()[0] != 1:
                raise ValueError('unsupported disposable index version; rebuild explicitly')
            self.loaded_cache = True
        else:
            self.db.executescript(SCHEMA)
            self.db.execute('PRAGMA user_version=1')

    def close(self):
        self.db.close()

    def provenance_for(self, scope, kind, ident):
        """Rebuild disposable proof labels from durable per-stream sidecars."""
        if scope not in self.scope_provenance:
            values={};path=self.root.parent/'records/streams'/(scope+'.json')
            if path.is_file():
                if path.is_symlink() or not path.resolve().is_relative_to(self.root.parent/'records/streams'):
                    raise ValueError('provenance sidecar escapes source area')
                record=json.loads(path.read_text());prefix=record['source_stream']+'/'
                mappings={m['source_path']:(m['kind'],m['id'],m['authoring_sha256']) for m in record['native_path_mapping']}
                for row in record['original_ledger']['rules']:
                    for source in row.get('artifacts') or []:
                        if not source.endswith('.json'):continue
                        target=mappings.get(prefix+source.removesuffix('.json')+'.yaml')
                        if target:
                            target_kind,target_id,body_hash=target
                            values[(target_kind,target_id)]={**{k:v for k,v in row.items() if k in PROOF_KEYS},
                                                           'document_authoring_sha256':body_hash}
            self.scope_provenance[scope]=values
        return self.scope_provenance[scope].get((kind,ident),{})

    def benchmark_scope(self, relative, body, prior):
        """Relocate a declared source owner; never pick a scope by newest ID."""
        if prior.get('kind')=='benchmark':return prior['scope']
        ident,body_hash=body['id'],digest(body)
        exact={r['scope'] for r in self.rows("WHERE kind='benchmark' AND id=? AND authoring_sha=?",(ident,body_hash))}
        exact.update(scope for (scope,kind,i),p in self.removed_proofs.items()
                     if kind=='benchmark' and i==ident and p.get('document_authoring_sha256')==body_hash)
        if not exact:
            removed={scope for (scope,kind,i) in self.removed_proofs if kind=='benchmark' and i==ident}
            if len(removed)==1:return next(iter(removed))
            if self.benchmark_declarations is None:
                declared=[];manifest=self.root.parent/'metadata/native-files.json'
                if manifest.is_file():declared=json.loads(manifest.read_text())
                else:
                    for path in sorted((self.root.parent/'records/streams').glob('*.json')):
                        if path.name.endswith('.source-trace.json'):continue
                        declared.extend(json.loads(path.read_text()).get('native_path_mapping',[]))
                self.benchmark_declarations=[r for r in declared if r['kind']=='benchmark']
            exact.update(scope_for(r['path']) for r in self.benchmark_declarations
                         if r['id']==ident and r['authoring_sha256']==body_hash)
        if len(exact)>1:raise ValueError('ambiguous declared Benchmark scope; no filename/first-match guess')
        return next(iter(exact)) if exact else scope_for(relative)

    def rows(self, where='', values=(), *, payload=False):
        columns = '*' if payload else 'path,scope,kind,id,version,title,source_sha,authoring_sha,program_sha,status,warnings,size,mtime,specification,mode,exact_sha'
        return [dict(r) for r in self.db.execute('SELECT '+columns+' FROM nodes '+where, values)]

    def update(self, relative, raw, *, provenance=None, check_schema=True):
        relative = Path(relative).as_posix()
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise ValueError('changed path must be within authoring root')
        previous = self.rows('WHERE path=?', (relative,), payload=True)
        prior = previous[0] if previous else {}
        if prior:
            saved=json.loads(prior['baseline']);saved.setdefault('document_authoring_sha256',prior['authoring_sha'])
            self.removed_proofs[(prior['scope'],prior['kind'],prior['id'])] = saved
        self.db.execute('DELETE FROM edges WHERE source=?', (relative,))
        self.db.execute('DELETE FROM nodes WHERE path=?', (relative,))
        if raw is None:
            return
        if relative=='catalog.yaml':
            header=yaml.load(raw,Loader=UniqueYaml)
            if (isinstance(header,dict) and header.get('format')=='scap-ng-library-catalog/1'
                    and header.get('generated') is True and set(header)=={
                        'format','generated','authoring_source_of_truth','benchmarks'}):
                return  # Generated navigation metadata, never native dispatch by filename alone.
        if len(relative)>190 or '\\' in relative or any(
                p.endswith((' ','.')) or any(c in p for c in '<>:"|?*') or
                Path(p).stem.casefold() in {'con','prn','aux','nul',*(f'com{i}' for i in range(10)),*(f'lpt{i}' for i in range(10))}
                for p in Path(relative).parts):
            raise ValueError('nonportable authoring path')
        self.parsed += 1
        doc = parse(raw)
        kind, body = next(iter(doc.items()))
        scope = self.benchmark_scope(relative,body,prior) if kind=='benchmark' else scope_for(relative)
        if scope == 'shared' and kind != 'assessment':
            raise ValueError('only Assessments may occupy the existing shared namespace')
        program = validate(doc) if check_schema else None
        body_sha = digest(body)
        proof = provenance if provenance is not None else json.loads(prior.get('baseline') or '{}')
        if not proof:
            same = self.rows('WHERE scope=? AND kind=? AND id=?',(scope,kind,body['id']),payload=True)
            if len(same)==1:
                proof=json.loads(same[0]['baseline']);proof.setdefault('document_authoring_sha256',same[0]['authoring_sha'])
            else:proof=self.removed_proofs.get((scope,kind,body['id']),{})
        if not proof:proof=self.provenance_for(scope,kind,body['id'])
        proof = {k:v for k,v in proof.items() if k in PROOF_KEYS}
        if provenance:
            proof['document_authoring_sha256']=body_sha
        elif prior and not proof.get('document_authoring_sha256'):
            proof['document_authoring_sha256']=prior['authoring_sha']
        status = proof.get('conversion_status', 'UNVERIFIED')
        warnings = proof.get('conversion_warnings') or []
        if kind == 'assessment' and status == 'CONVERTED_VERIFIED' and (proof.get('authoring_sha256') != body_sha or
                                              proof.get('program_sha256') != program):
            status = 'MODIFIED_UNVERIFIED'
        if kind == 'rule' and status == 'CONVERTED_VERIFIED' and proof.get('document_authoring_sha256')!=body_sha:
            status = 'MODIFIED_UNVERIFIED'
        path = self.root/relative
        stat = path.stat() if path.exists() else None
        values = (relative, relative.casefold(), scope, kind, body['id'], json.dumps(version(body)),
                  title(body), json.dumps(doc, ensure_ascii=False), sha256(raw).hexdigest(), body_sha,
                  program, status, json.dumps(warnings), json.dumps(proof), len(raw),
                  stat.st_mtime_ns if stat else 0, json.dumps(body.get('specification'),sort_keys=True),body.get('mode'),
                  digest({k:v for k,v in body.items() if k!='id'}) if kind=='assessment' else None)
        try:
            self.db.execute('INSERT INTO nodes VALUES ('+','.join('?' for _ in values)+')', values)
        except sqlite3.IntegrityError as error:
            raise ValueError('case-insensitive source path collision: '+relative) from error
        for edge in edges(doc):
            self.db.execute('INSERT INTO edges VALUES (?,?,?,?,?,?)',
                (relative, edge['kind'], edge['id'], json.dumps(edge['version']), edge['field'], edge['purpose']))

    def refresh(self, changed=None, *, full=False):
        self.parsed=0
        if not self.root.is_dir():
            raise ValueError('authoring root is not a directory')
        existing = {r['path']:r for r in self.rows()}
        if changed is not None:
            paths = sorted(set(Path(p).as_posix() for p in changed))
        else:
            discovered = {p.relative_to(self.root).as_posix() for p in self.root.rglob('*')
                          if p.is_file() and p.suffix.casefold() in ('.yaml','.yml')}
            paths = sorted(set(existing) | discovered)
        self.diagnostics=[d for d in self.diagnostics if d.get('path') not in paths]
        # Pair rename/delete notifications before additions, independently of
        # lexical filename order. Existing source-owner scopes survive renames.
        for relative in paths:
            if relative in existing and not Path(relative).is_absolute() and '..' not in Path(relative).parts:
                if not (self.root/relative).exists():self.update(relative,None)
        for relative in paths:
            path = self.root/relative
            try:
                if Path(relative).is_absolute() or '..' in Path(relative).parts or '\\' in relative:
                    raise ValueError('changed path must be normalized and relative to the authoring root')
                if not path.exists():
                    self.update(relative, None)
                    continue
                previous = existing.get(relative)
                stat = path.stat()
                if changed is None and previous and not full and (
                        previous['size'],previous['mtime']) == (stat.st_size,stat.st_mtime_ns):
                    continue
                self.update(relative, read(self.root,relative))
            except (ValueError, TypeError, OSError, RecursionError) as error:
                row = existing.get(relative, {'path':relative})
                item = diagnostic(self.root,row,'invalid-document',str(error))
                mark = getattr(error,'problem_mark',None)
                if mark:item['span']={'start':{'line':mark.line,'character':mark.column}}
                self.diagnostics.append(item)
            except Exception as error:
                # YAML syntax errors carry accurate source spans.
                import yaml
                if not isinstance(error,yaml.YAMLError):raise
                row = existing.get(relative, {'path':relative})
                item = diagnostic(self.root,row,'invalid-yaml',str(error))
                mark = getattr(error,'problem_mark',None)
                if mark:item['span']={'start':{'line':mark.line,'character':mark.column}}
                self.diagnostics.append(item)
        return paths

    def resolve(self, source, kind, ident, expected=None):
        scopes = ('shared',) if source['scope']=='shared' else (source['scope'],'shared')
        placeholders = ','.join('?' for _ in scopes)
        candidates = self.rows(f'WHERE kind=? AND id=? AND scope IN ({placeholders})', (kind,ident,*scopes))
        if not candidates:
            anywhere = self.rows('WHERE id=?',(ident,))
            if anywhere:
                label = 'wrong-kind' if any(r['scope'] in scopes and r['kind']!=kind for r in anywhere) else 'cross-scope'
                raise ValueError(label+': '+kind+'/'+ident)
            raise ValueError('missing-target: '+kind+'/'+ident)
        if len(candidates)!=1:
            raise ValueError('ambiguous-target: '+kind+'/'+ident)
        target = candidates[0]
        if expected != 'null' and expected is not None and target['version'] != expected:
            raise ValueError('version-mismatch: '+kind+'/'+ident)
        return target

    def consumers(self, row, *, transitive=False):
        result, pending, seen = {}, deque([row]), set()
        while pending:
            target = pending.popleft()
            if target['path'] in seen:continue
            seen.add(target['path'])
            for edge in self.db.execute('SELECT * FROM edges WHERE kind=? AND id=?',(target['kind'],target['id'])):
                sources = self.rows('WHERE path=?',(edge['source'],))
                if not sources:continue
                source = sources[0]
                try:resolved = self.resolve(source,edge['kind'],edge['id'],edge['version'])
                except ValueError:continue
                if resolved['path'] != target['path']:continue
                result[source['path']] = {'path':source['path'],'file_uri':(self.root/source['path']).as_uri(),
                    'kind':source['kind'],'id':source['id'],'scope':source['scope']}
                if transitive:pending.append(source)
        return [result[k] for k in sorted(result)]

    def check(self, *, changed=None):
        started = time.perf_counter()
        problems = list(self.diagnostics)
        nodes = self.rows('ORDER BY scope,kind,id,path')
        scope_names=defaultdict(set)
        for row in nodes:scope_names[row['scope'].casefold()].add(row['scope'])
        for row in nodes:
            if len(scope_names[row['scope'].casefold()])>1:
                problems.append(diagnostic(self.root,row,'scope-case-collision','private namespaces collide on case-insensitive filesystems'))
        by_path = {r['path']:r for r in nodes}
        duplicates = self.db.execute('SELECT scope,id FROM nodes GROUP BY scope,id HAVING COUNT(*)>1').fetchall()
        for scope,ident in duplicates:
            for row in self.rows('WHERE scope=? AND id=?',(scope,ident)):
                problems.append(diagnostic(self.root,row,'duplicate-identity','duplicate identity in eligible scope: '+ident))
        for value in self.db.execute("SELECT id FROM nodes WHERE kind='assessment' GROUP BY id HAVING COUNT(*)>1"):
            for row in self.rows("WHERE kind='assessment' AND id=?", (value['id'],)):
                problems.append(diagnostic(self.root,row,'duplicate-assessment-identity',
                    'Assessment ID must be unique across the compiled library: '+row['id']))
        # A global shared Assessment must not shadow a private one, even unused.
        shared = self.rows("WHERE scope='shared'")
        for row in shared:
            others = self.rows("WHERE id=? AND scope!='shared'",(row['id'],))
            for other in others:
                problems.append(diagnostic(self.root,other,'ambiguous-identity','local/shared identity collision: '+row['id']))
        adjacency = defaultdict(list)
        benchmark_specs = {}
        benchmark_bodies = {}
        for b in self.rows("WHERE kind='benchmark'",payload=True):
            body = json.loads(b['payload'])['benchmark']
            benchmark_bodies[b['scope']]=body
            benchmark_specs[b['scope']] = [json.dumps(x,sort_keys=True) for x in body.get('assessment_specifications',[])]
            actual = {r['id'] for r in nodes if r['scope']==b['scope'] and r['kind']=='rule'}
            declared = body.get('rules') or []
            if len(declared)!=len(set(declared)) or set(declared)!=actual:
                problems.append(diagnostic(self.root,b,'rule-inventory','Benchmark membership differs from private Rule inventory'))
        bindings={}
        for row in self.db.execute('SELECT path,payload FROM nodes WHERE kind=\'rule\' AND instr(payload,\'"inputs"\')>0'):
            choices=json.loads(row['payload'])['rule'].get('assessment_choices',{})
            bindings[row['path']]={label:choice.get('inputs') for label,choice in choices.items() if choice.get('inputs')}
        conditions={}
        for row in self.rows("WHERE kind='applicability'",payload=True):
            conditions.setdefault(row['scope'],set()).update(json.loads(row['payload'])['applicability']['conditions'])
        # Match the existing independent package reader's policy-ID checks;
        # these are source bindings, not a new policy evaluator or grammar.
        policy_query='''SELECT path,payload FROM nodes WHERE kind='rule' AND
            (instr(payload,'"applicability": []')=0 OR instr(payload,'"requires": []')=0
             OR instr(payload,'"conflicts": []')=0)'''
        for value in self.db.execute(policy_query):
            source=by_path[value['path']];body=json.loads(value['payload'])['rule']
            b=benchmark_bodies.get(source['scope'],{})
            policy_ids=set(b.get('rules',[]))|{g['id'] for g in b.get('groups',[]) if isinstance(g,dict) and 'id' in g}
            try:
                for condition in body.get('applicability',[]):
                    if not isinstance(condition,str) or condition not in conditions.get(source['scope'],set()):
                        raise ValueError('unresolved Rule applicability condition')
                targets=[]
                for clause in body.get('requires',[]):
                    if isinstance(clause,str):targets.append(clause)
                    elif isinstance(clause,dict) and isinstance(clause.get('any_of'),list):targets.extend(clause['any_of'])
                    else:raise ValueError('unsupported policy reference shape')
                targets.extend(body.get('conflicts',[]))
                if not all(isinstance(t,str) and t in policy_ids for t in targets):
                    raise ValueError('unresolved policy Rule/Group')
            except ValueError as error:
                problems.append(diagnostic(self.root,source,'policy-reference',str(error)))
        for edge in self.db.execute('SELECT * FROM edges ORDER BY source,field'):
            source = by_path[edge['source']]
            try:
                target = self.resolve(source,edge['kind'],edge['id'],edge['version'])
                adjacency[source['path']].append(target['path'])
                # Typed Rule/applicability/dependency edges determine use;
                # an Assessment has no intrinsic purpose to compare or infer.
                if source['kind']=='rule' and target['kind']=='assessment':
                    if source['scope'] in benchmark_specs:
                        if target['mode']=='automated' and target['specification'] not in benchmark_specs[source['scope']]:
                            raise ValueError('incompatible-assessment-specification: '+target['id'])
                        label=edge['field'].removeprefix('/rule/assessment_choices/').replace('~1','/').replace('~0','~')
                        bound=bindings.get(source['path'],{}).get(label)
                        if bound:
                            assessment=json.loads(self.rows('WHERE path=?',(target['path'],),payload=True)[0]['payload'])['assessment']
                            declared_inputs=assessment.get('inputs') or {}
                            parameters={p['id'] for p in benchmark_bodies[source['scope']].get('parameters',[])}
                            for name,ref in bound.items():
                                parameter=ref if isinstance(ref,str) else ref.get('parameter')
                                if name not in declared_inputs:raise ValueError('input-binding: undeclared target Input '+name)
                                if parameter not in parameters:raise ValueError('input-binding: missing Benchmark Parameter '+str(parameter))
                    else:
                        raise ValueError('missing-benchmark: Rule requires its private Benchmark namespace')
            except ValueError as error:
                problems.append(diagnostic(self.root,source,str(error).split(':')[0],str(error),field=edge['field'],reference=edge['id']))
        # Iterative cycle validation includes dependency-only/standalone graphs.
        colors = {}
        for start in sorted(adjacency):
            if colors.get(start)==2:continue
            stack = [(start,False)]
            while stack:
                path,exit_node = stack.pop()
                if exit_node:colors[path]=2;continue
                if colors.get(path)==2:continue
                if colors.get(path)==1:
                    problems.append(diagnostic(self.root,by_path[path],'reference-cycle','cyclic source document dependency'))
                    continue
                colors[path]=1;stack.append((path,True))
                stack.extend((target,False) for target in reversed(sorted(set(adjacency[path]))) if colors.get(target)!=2)
        for row in nodes:
            if row['status']=='MODIFIED_UNVERIFIED':
                problems.append(diagnostic(self.root,row,'proof-no-longer-matches','edited native document cannot inherit frozen proof',severity='warning',consumers=self.consumers(row,transitive=True)))
        for problem in problems:
            source=by_path.get(problem.get('path'))
            if source and not problem['affected_consumers']:
                problem['affected_consumers']=self.consumers(source,transitive=True)
        affected = []
        if changed:
            affected = sorted({c['path'] for r in nodes if r['path'] in changed for c in self.consumers(r,transitive=True)})
        return {'format':REPORT_FORMAT,'mode':'check','status':'FAIL' if any(p['severity']=='error' for p in problems) else 'PASS',
                'summary':f"Native source/reference check: {len(nodes)} documents, "
                          f"{sum(p['severity']=='error' for p in problems)} errors, "
                          f"{sum(p['severity']=='warning' for p in problems)} warnings; no new semantic proof.",
                'validation_scope':'changed_notifications_and_indexed_reference_graph' if changed is not None else 'library',
                'diagnostics':problems,'counts':dict(self.db.execute('SELECT kind,COUNT(*) FROM nodes GROUP BY kind')),
                'affected_consumers':affected,'metrics':{'parsed_documents':self.parsed,'indexed_documents':len(nodes),
                    'used_read_only_cache':self.loaded_cache,'reference_check_seconds':time.perf_counter()-started},
                'scanner_evaluated':False,'semantic_deduplication_performed':False}

    def search(self, *, query='', scope=None, kind=None, status=None, limit=100):
        if not 1<=limit<=1000:raise ValueError('search limit must be 1..1000')
        where = 'WHERE (id LIKE ? OR title LIKE ?)'
        args = ['%'+query+'%','%'+query+'%']
        if scope:where+=' AND scope=?';args.append(scope)
        if kind:where+=' AND kind=?';args.append(kind)
        if status:where+=' AND status=?';args.append(status)
        rows = self.rows(where+' ORDER BY scope,kind,id,path LIMIT ?',(*args,limit))
        result=[]
        for row in rows:
            proof_status=row['status']
            if row['kind']=='rule' and proof_status=='CONVERTED_VERIFIED':
                body=json.loads(self.rows('WHERE path=?',(row['path'],),payload=True)[0]['payload'])['rule']
                label=body['default_assessment_choice'].replace('~','~0').replace('/','~1')
                field='/rule/assessment_choices/'+label
                selected=self.db.execute('SELECT * FROM edges WHERE source=? AND field=?',(row['path'],field)).fetchone()
                if selected:
                    try:
                        target=self.resolve(row,'assessment',selected['id'],selected['version'])
                        if target['status']!='CONVERTED_VERIFIED':proof_status='UNVERIFIED_DEPENDENCY'
                    except ValueError:proof_status='UNRESOLVED'
            result.append({**row,'proof_status':proof_status,'file_uri':(self.root/row['path']).as_uri()})
        return result

    def persist(self, path=None):
        target = Path(path) if path else self.cache
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary = target.with_name(target.name+'.tmp')
        if temporary.exists():raise ValueError('index staging path already exists')
        self.db.commit()
        try:
            output=sqlite3.connect(temporary)
            try:self.db.backup(output)
            finally:output.close()
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)

    def plan(self, paths=None):
        changes = []
        for row in self.rows('ORDER BY path'):
            if paths is not None and row['path'] not in paths:continue
            before = read(self.root,row['path'])
            doc = parse(before)
            after = canonical_yaml(doc)
            if before==after:continue
            changes.append({'path':row['path'],'file_uri':(self.root/row['path']).as_uri(),
                'document_id':row['id'],'scope':row['scope'],'kind':row['kind'],
                'before_sha256':sha256(before).hexdigest(),'after_sha256':sha256(after).hexdigest(),
                'native_payload_sha256':digest(doc),'replacement':after.decode(),
                'patch':''.join(unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),
                                            fromfile=row['path'],tofile=row['path'])),
                'proposed_change':'canonical YAML presentation only; comments may change: review patch',
                'reason':'same parsed native document','affected_consumers':self.consumers(row,transitive=True),
                'proof_status':row['status'],'warnings':json.loads(row['warnings'])})
        return {'format':'scap-ng-library-plan/1','changes':changes,'semantic_mutations':False,
                'plan_sha256':digest(changes)}

    def compile_scope(self, scope):
        """Bridge one eligible native scope to the unchanged public compiler."""
        from v04_native_bundle_compiler import build_bundle
        documents={}
        for row in self.rows("WHERE scope IN (?, 'shared') ORDER BY path",(scope,)):
            raw=read(self.root,row['path']);doc=parse(raw)
            if digest(next(iter(doc.values())))!=row['authoring_sha']:
                raise ValueError('stale source index; refresh before compilation')
            folder='shared' if row['scope']=='shared' else 'library'
            relative='authoring/'+folder+'/'+row['kind']+'/'+sha256(row['id'].encode()).hexdigest()+'.json'
            documents[relative]=doc
        return build_bundle(documents)
