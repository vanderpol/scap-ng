"""Disposable SQLite navigation cache; native YAML remains authoritative."""
from collections import defaultdict, deque
from difflib import unified_diff
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import time

from . import REPORT_FORMAT
from .documents import (canonical_yaml, digest, edges, parse, read, scope_for,
                        title, validate, version)

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


def diagnostic(root, row, code, message, *, severity='error', field=None, consumers=None):
    return {'code': code, 'severity': severity, 'message': message,
            'file_uri': (root/row['path']).absolute().as_uri(), 'path': row['path'],
            'document_id': row.get('id'), 'kind': row.get('kind'), 'scope': row.get('scope'),
            'span': None, 'source_field': field, 'reason': message,
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
            self.root.parent/'metadata/library.sqlite' if self.root.name=='content' else
            self.root.parent/'.scap-ng-index'/(self.root.name+'-'+sha256(str(self.root).encode()).hexdigest()[:8]+'.sqlite'))
        if self.cache.resolve().is_relative_to(self.root):
            raise ValueError('generated index must remain outside editable authoring tree')
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        self.parsed = 0
        self.diagnostics = []
        self.loaded_cache = False
        self.removed_proofs = {}
        if self.cache.is_file():
            with sqlite3.connect(self.cache.resolve().as_uri()+'?mode=ro', uri=True) as saved:
                saved.backup(self.db)
            if self.db.execute('PRAGMA user_version').fetchone()[0] != 1:
                raise ValueError('unsupported disposable index version; rebuild explicitly')
            self.loaded_cache = True
        else:
            self.db.executescript(SCHEMA)
            self.db.execute('PRAGMA user_version=1')

    def close(self):
        self.db.close()

    def rows(self, where='', values=(), *, payload=False):
        columns = '*' if payload else 'path,scope,kind,id,version,title,source_sha,authoring_sha,program_sha,status,warnings,size,mtime,specification,mode,exact_sha'
        return [dict(r) for r in self.db.execute('SELECT '+columns+' FROM nodes '+where, values)]

    def update(self, relative, raw, *, provenance=None, check_schema=True):
        relative = Path(relative).as_posix()
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise ValueError('changed path must be within authoring root')
        previous = self.rows('WHERE path=?', (relative,), payload=True)
        prior = previous[0] if previous else {}
        if prior and raw is None:
            self.removed_proofs[(prior['scope'],prior['kind'],prior['id'])] = json.loads(prior['baseline'])
        self.db.execute('DELETE FROM edges WHERE source=?', (relative,))
        self.db.execute('DELETE FROM nodes WHERE path=?', (relative,))
        if raw is None:
            return
        if len(relative)>190 or '\\' in relative or any(
                p.endswith((' ','.')) or any(c in p for c in '<>:"|?*') or
                Path(p).stem.casefold() in {'con','prn','aux','nul',*(f'com{i}' for i in range(10)),*(f'lpt{i}' for i in range(10))}
                for p in Path(relative).parts):
            raise ValueError('nonportable authoring path')
        self.parsed += 1
        doc = parse(raw)
        kind, body = next(iter(doc.items()))
        scope = scope_for(relative)
        if scope == 'shared' and kind != 'assessment':
            raise ValueError('only Assessments may occupy the existing shared namespace')
        program = validate(doc) if check_schema else None
        body_sha = digest(body)
        proof = provenance if provenance is not None else json.loads(prior.get('baseline') or '{}')
        if not proof:
            same = self.rows('WHERE scope=? AND kind=? AND id=?',(scope,kind,body['id']),payload=True)
            if len(same)==1:proof=json.loads(same[0]['baseline'])
            else:proof=self.removed_proofs.get((scope,kind,body['id']),{})
        proof = {k:v for k,v in proof.items() if k in {'conversion_status','conversion_warnings',
            'authoring_sha256','program_sha256','source_rule','source_rule_sha256','source_zip_sha256'}}
        status = proof.get('conversion_status', 'UNVERIFIED')
        warnings = proof.get('conversion_warnings') or []
        if kind == 'assessment' and status == 'CONVERTED_VERIFIED' and (proof.get('authoring_sha256') != body_sha or
                                              proof.get('program_sha256') != program):
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
        if not self.root.is_dir():
            raise ValueError('authoring root is not a directory')
        existing = {r['path']:r for r in self.rows()}
        if changed is not None:
            paths = sorted(set(Path(p).as_posix() for p in changed))
        else:
            discovered = {p.relative_to(self.root).as_posix() for p in self.root.rglob('*')
                          if p.is_file() and p.suffix.casefold() in ('.yaml','.yml') and p.name != 'catalog.yaml'}
            paths = sorted(set(existing) | discovered)
        for relative in paths:
            path = self.root/relative
            try:
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
        # A global shared Assessment must not shadow a private one, even unused.
        shared = self.rows("WHERE scope='shared'")
        for row in shared:
            others = self.rows("WHERE id=? AND scope!='shared'",(row['id'],))
            for other in others:
                problems.append(diagnostic(self.root,other,'ambiguous-identity','local/shared identity collision: '+row['id']))
        adjacency = defaultdict(list)
        benchmark_specs = {}
        for b in self.rows("WHERE kind='benchmark'",payload=True):
            body = json.loads(b['payload'])['benchmark']
            benchmark_specs[b['scope']] = [json.dumps(x,sort_keys=True) for x in body.get('assessment_specifications',[])]
            actual = {r['id'] for r in nodes if r['scope']==b['scope'] and r['kind']=='rule'}
            declared = body.get('rules') or []
            if len(declared)!=len(set(declared)) or set(declared)!=actual:
                problems.append(diagnostic(self.root,b,'rule-inventory','Benchmark membership differs from private Rule inventory'))
        for edge in self.db.execute('SELECT * FROM edges ORDER BY source,field'):
            source = by_path[edge['source']]
            try:
                target = self.resolve(source,edge['kind'],edge['id'],edge['version'])
                adjacency[source['path']].append(target['path'])
                if source['kind']=='assessment' and edge['purpose']:
                    body=json.loads(self.rows('WHERE path=?',(target['path'],),payload=True)[0]['payload'])['assessment']
                    if edge['purpose']!=body.get('purpose'):
                        raise ValueError('purpose-mismatch: '+target['id'])
                if source['kind']=='rule' and target['kind']=='assessment':
                    if source['scope'] in benchmark_specs:
                        if target['mode']=='automated' and target['specification'] not in benchmark_specs[source['scope']]:
                            raise ValueError('incompatible-assessment-specification: '+target['id'])
                    else:
                        raise ValueError('missing-benchmark: Rule requires its private Benchmark namespace')
            except ValueError as error:
                problems.append(diagnostic(self.root,source,str(error).split(':')[0],str(error),field=edge['field']))
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
                problems.append(diagnostic(self.root,row,'proof-no-longer-matches','edited Assessment cannot inherit frozen proof',severity='warning',consumers=self.consumers(row,transitive=True)))
        for problem in problems:
            source=by_path.get(problem.get('path'))
            if source and not problem['affected_consumers']:
                problem['affected_consumers']=self.consumers(source,transitive=True)
        affected = []
        if changed:
            affected = sorted({c['path'] for r in nodes if r['path'] in changed for c in self.consumers(r,transitive=True)})
        return {'format':REPORT_FORMAT,'mode':'check','status':'FAIL' if any(p['severity']=='error' for p in problems) else 'PASS',
                'validation_scope':'changed_notifications_and_indexed_reference_graph' if changed is not None else 'library',
                'diagnostics':problems,'counts':dict(self.db.execute('SELECT kind,COUNT(*) FROM nodes GROUP BY kind')),
                'affected_consumers':affected,'metrics':{'parsed_documents':self.parsed,'indexed_documents':len(nodes),
                    'used_read_only_cache':self.loaded_cache,'reference_check_seconds':time.perf_counter()-started},
                'scanner_evaluated':False,'semantic_deduplication_performed':False}

    def search(self, *, query='', scope=None, limit=100):
        if not 1<=limit<=1000:raise ValueError('search limit must be 1..1000')
        where = 'WHERE (id LIKE ? OR title LIKE ?)'
        args = ['%'+query+'%','%'+query+'%']
        if scope:where+=' AND scope=?';args.append(scope)
        rows = self.rows(where+' ORDER BY scope,kind,id,path LIMIT ?',(*args,limit))
        return [{**r,'file_uri':(self.root/r['path']).as_uri()} for r in rows]

    def persist(self, path=None):
        target = Path(path) if path else self.cache
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary = target.with_name(target.name+'.tmp')
        if temporary.exists():raise ValueError('index staging path already exists')
        self.db.commit()
        try:
            with sqlite3.connect(temporary) as output:self.db.backup(output)
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
