"""Bounded research models; no collectors, target commands or general OVAL evaluator."""
import re

def all_results(values):
    values=list(values)
    for decisive in ('false','error','unknown','not_evaluated'):
        if decisive in values: return decisive
    return 'true'

def correlated_required(keys, rows, predicates, *, complete=True, empty='false'):
    """Synthetic required-key contract. All known keys require one correlated row.

    Unknown collection cannot prove absence; duplicate keys are ambiguous errors.
    This is a proposed contract, not a replacement for OVAL record semantics.
    """
    if not keys: return empty if complete else 'unknown'
    results=[]
    for key in keys:
        matching=[r for r in rows if r.get('key')==key]
        if len(matching)>1: results.append('error'); continue
        if not matching: results.append('false' if complete else 'unknown'); continue
        row=matching[0]
        if row.get('status') in ('error','unknown'): results.append(row['status']); continue
        checks=[]
        for field, predicate in predicates.items():
            if field not in row: checks.append('error')
            elif row[field] is None: checks.append('unknown')
            else:
                try: checks.append('true' if predicate(row[field]) else 'false')
                except (TypeError,ValueError): checks.append('error')
        results.append(all_results(checks))
    if not complete: results.append('unknown')
    return all_results(results)

def cartesian_concat(left,right): return [a+b for a in left for b in right]
def keyed_concat(left,right):
    return [(key,a+b) for key,a in left for other,b in right if key==other]

def audit_parse(line):
    """Restricted grammar experiment. Reject extra fields rather than claiming auditctl semantics."""
    if line.lstrip().startswith('#'): return None
    tokens=line.split(); result={'syscalls':set()}; i=0
    while i<len(tokens):
        if tokens[i] not in ('-a','-F','-S','-k') or i+1==len(tokens): raise ValueError('unsupported syntax')
        flag,value=tokens[i:i+2]; i+=2
        if flag=='-a':
            if value not in ('always,exit','exit,always'): raise ValueError('unsupported action')
            result['action']='always,exit'
        elif flag=='-S': result['syscalls'].update(value.split(','))
        elif flag=='-k': result['key']=value
        elif value.startswith('arch='): result['arch']=value[5:]
        elif value=='auid>=1000': result['auid_min']=1000
        elif value=='auid=0': result['auid_root']=True
        elif value in ('auid!=-1','auid!=unset','auid!=4294967295'): result['auid_set']=True
        elif value.startswith('key='): result['key']=value[4:]
        else: raise ValueError('unsupported field')
    if 'action' not in result or 'arch' not in result: raise ValueError('missing action/arch')
    return result

def permission_state(mode):
    # Eight independently addressable booleans from the source State.
    return not any(mode & bit for bit in (0o4000,0o2000,0o1000,0o020,0o010,0o004,0o002,0o001))

def apache_occurrences(records):
    """Isolated published predicate model, not its shell acquisition."""
    keep=[v for name,v in records if name=='KeepAlive']
    limit=[int(v) for name,v in records if name=='MaxKeepAliveRequests']
    return bool(keep and limit) and all(v.lower()=='on' for v in keep) and all(v>=100 for v in limit)

def apache_effective(records):
    # Tiny same-scope last-directive model only. Not a complete Apache interpreter.
    values=dict(records)
    return values.get('KeepAlive','On').lower()=='on' and int(values.get('MaxKeepAliveRequests','100'))>=100

def duration_hours_legacy(seconds): return int(seconds//3600)
def duration_exact(seconds): return 172800<=seconds<=604800

def explicit_acl_allowed(aces,allowed):
    """Synthetic structural allowlist; does not calculate effective rights."""
    return bool(aces) and all((a['sid'],a['rights'],a['type']) in allowed for a in aces)

def ordered_access_check(aces,sids,right):
    """Single-bit synthetic ACE order demonstration, excludes privileges/conditional ACEs."""
    for ace in aces:
        if ace['sid'] in sids and right in ace['rights']: return ace['type']=='allow'
    return False
