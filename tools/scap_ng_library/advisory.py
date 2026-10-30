"""Bounded sharing proposals, never promotion or proof of semantic parity."""
from collections import defaultdict
from itertools import combinations
import json

from .documents import digest


def differences(left,right,path='$',limit=30):
    out=[]
    def visit(a,b,where):
        if len(out)>=limit:return
        if type(a)!=type(b):out.append({'path':where,'before':a,'after':b});return
        if isinstance(a,dict):
            for key in sorted(set(a)|set(b)):
                if key not in a or key not in b:out.append({'path':where+'/'+key,'before':a.get(key),'after':b.get(key)})
                else:visit(a[key],b[key],where+'/'+key)
                if len(out)>=limit:break
        elif isinstance(a,list):
            if len(a)!=len(b):out.append({'path':where+'/length','before':len(a),'after':len(b)})
            for i,(x,y) in enumerate(zip(a,b)):visit(x,y,where+'/'+str(i))
        elif a!=b:out.append({'path':where,'before':a,'after':b})
    visit(left,right,path)
    return out


def census(library,*,near=False,max_pairs=100):
    if not 0<=max_pairs<=1000:raise ValueError('advisory pair budget must be 0..1000')
    exact,shapes=defaultdict(list),defaultdict(list)
    rows=library.rows("WHERE kind='assessment' ORDER BY scope,id,path",payload=near)
    bodies={}
    def skeleton(value):
        if isinstance(value,dict):return {k:skeleton(v) for k,v in value.items() if k not in ('id','assessment_title')}
        if isinstance(value,list):return [skeleton(v) for v in value]
        return type(value).__name__
    for row in rows:
        exact[row['exact_sha']].append(row)
        if near:
            body=json.loads(row['payload'])['assessment'];bodies[row['path']]=body
            shapes[digest(skeleton(body))].append(row)
    def consumer(row):
        return {'scope':row['scope'],'id':row['id'],'path':row['path'],
                'proof_status':row['status'],'warnings':json.loads(row['warnings']),
                'authoring_sha256':row['authoring_sha'],'program_sha256':row['program_sha'],
                'used_by':library.consumers(row,transitive=True)}
    candidates=[{'fingerprint':key,'comparison':'all native fields except Assessment ID are identical',
                 'proposal_only':True,'members':[consumer(r) for r in group]}
                for key,group in sorted(exact.items()) if len(group)>1]
    pairs=[];seen=0
    if near:
        for _,group in sorted(shapes.items()):
            for a,b in combinations(group,2):
                if seen>=max_pairs:break
                seen+=1
                delta=differences(bodies[a['path']],bodies[b['path']])
                if delta:pairs.append({'proposal_only':True,'left':consumer(a),'right':consumer(b),
                                       'differences':delta,'difference_limit':30})
            if seen>=max_pairs:break
    return {'format':'scap-ng-library-reuse-census/1','exact_candidates':candidates,'near_candidates':pairs,
            'near_pairs_examined':seen,'pair_budget':max_pairs,'near_enabled':near,
            'unreferenced_definitions':[consumer(r) for r in rows if not library.consumers(r)],
            'semantic_equivalence_proved':False,'promotion_performed':False,
            'limitations':['ID-neutral structural candidates require independent proof and explicit promotion task',
                           'near-duplicate skeleton is advisory; all reported field differences remain visible',
                           'standalone unused Assessments are valid authoring, not missing Benchmark errors']}
