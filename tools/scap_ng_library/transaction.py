"""Explicit reviewed presentation edits with stale-plan checks and rollback."""
from hashlib import sha256
import os
from pathlib import Path
import tempfile

from .documents import digest, parse, read
from .index import Library


def atomic_write(path, raw):
    mode = path.stat().st_mode
    fd, temporary = tempfile.mkstemp(prefix='.scapng-edit-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as output:
            output.write(raw);output.flush();os.fsync(output.fileno())
        os.chmod(temporary,mode)
        os.replace(temporary,path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def apply_plan(library, plan):
    if plan.get('format')!='scap-ng-library-plan/1' or plan.get('plan_sha256')!=digest(plan.get('changes')):
        raise ValueError('invalid/stale change manifest digest')
    before, after = {}, {}
    # Discover source changes; validate staged references while reusing unchanged
    # indexed YAML. Periodic full hash/schema census remains an explicit action.
    staged = Library(library.root,cache=library.cache)
    try:
        staged.refresh()
        initial = staged.check()
        if initial['status']!='PASS':raise ValueError('source library must pass before presentation apply')
        for change in plan['changes']:
            relative = change['path']
            raw = read(library.root,relative)
            replacement = change['replacement'].encode('utf-8')
            if sha256(raw).hexdigest()!=change['before_sha256']:
                raise ValueError('stale plan; file changed: '+relative)
            if sha256(replacement).hexdigest()!=change['after_sha256']:
                raise ValueError('replacement digest mismatch: '+relative)
            old, new = parse(raw), parse(replacement)
            if old!=new or digest(new)!=change['native_payload_sha256']:
                raise ValueError('only independently equal parsed native documents may be applied')
            staged.update(relative,replacement)
            before[relative]=raw;after[relative]=replacement
        checked = staged.check()
        if checked['status']!='PASS':raise ValueError('staged validation failed; nothing written')
        written = []
        try:
            for relative in sorted(after):
                if read(library.root,relative)!=before[relative]:raise ValueError('concurrent edit; transaction aborted')
                written.append(relative)
                atomic_write(library.root/relative,after[relative])
            final = Library(library.root,cache=library.cache)
            try:
                final.refresh()
                if final.check()['status']!='PASS':raise ValueError('post-write validation failed')
                # Publishing a regenerated cache is explicit in apply, not in check.
                final.persist()
            finally:final.close()
        except BaseException:
            conflicts=[]
            for relative in reversed(written):
                current=read(library.root,relative)
                if current==before[relative]:continue
                if current!=after[relative]:
                    conflicts.append(relative);continue
                atomic_write(library.root/relative,before[relative])
            if conflicts:raise ValueError('concurrent external edit preserved during rollback: '+', '.join(conflicts))
            raise
        return {'event':'applied','changed_files':sorted(written),'plan_sha256':plan['plan_sha256'],
                'native_payloads_unchanged':True,'semantic_deduplication_performed':False}
    finally:
        staged.close()
