import itertools,json,re,sys,unittest
from pathlib import Path
from lxml import etree
import yaml
from semantic_models import *

STUDY=Path(__file__).resolve().parents[1]

def original_patterns():
    tree=etree.parse(str(STUDY/'evidence/rhel_9/SV-258179/source-oval.xml'))
    nodes={e.get('id'):e for e in tree.iter() if e.get('id')}
    def value(node):
        tag=etree.QName(node).localname
        if tag=='variable_component': return value(nodes[node.get('var_ref')])
        if tag in ('constant_variable','local_variable','concat'): return ''.join(value(c) for c in node if etree.QName(c).localname!='notes')
        if tag in ('value','literal_component'): return node.text or ''
        raise ValueError(tag)
    patterns=[]
    for e in tree.iter():
        if etree.QName(e).localname=='pattern':
            patterns.append(value(nodes[e.get('var_ref')]) if e.get('var_ref') else e.text)
    return sorted(patterns)

def expanded_patterns():
    doc=yaml.safe_load((STUDY/'proposals/audit-pattern-table.proposal.yaml').read_text())
    a=doc['assessment']; result=[]
    for row in a['tests']['test-audit-patterns']['rows']:
        template=a['variables'][row['template']]['expression']['literal']
        result.append(template.replace('${syscall}',row['syscall']).replace('${arch}',row['arch']).replace('${auid}',row['auid']))
    return sorted(result)

class ResearchTests(unittest.TestCase):
    def test_audit_table_preserves_all_24_exact_patterns(self):
        self.assertEqual(len(original_patterns()),24)
        self.assertEqual(original_patterns(), expanded_patterns())

    def test_audit_text_fixtures(self):
        baseline=original_patterns(); proposal=expanded_patterns(); cases=[]
        for arch,call,auid,sentinel,action,key in itertools.product(
            ['b32','b64'], ['setxattr','fsetxattr','lsetxattr','removexattr','fremovexattr','lremovexattr'],
            ['root','user'], ['unset','-1','4294967295'], ['always,exit','exit,always'], ['',' -k perm_mod']):
            suffix='-F auid=0' if auid=='root' else '-F auid>=1000 -F auid!='+sentinel
            cases.append(f'-a {action} -F arch={arch} -S {call} {suffix}{key}')
        cases += ['','# comment','-a never,exit -F arch=b32 -S setxattr -F auid=0',
                  '-a always,exit -F arch=b32 -S other,setxattr,more -F auid=0',
                  '-a always,exit -F arch=b32 -S other -S setxattr -F auid=0',
                  '-a always,exit -F arch=b32 -S setxattr_fake -F auid=0']
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual([bool(re.search(p,text,re.M)) for p in baseline], [bool(re.search(p,text,re.M)) for p in proposal])

    def test_audit_parser_is_not_lossless(self):
        ordered='-a always,exit -F arch=b32 -S lsetxattr -F auid>=1000 -F auid!=unset'
        reordered='-a always,exit -F auid!=unset -F auid>=1000 -S lsetxattr -F arch=b32'
        self.assertEqual(audit_parse(ordered),audit_parse(reordered))
        patterns=original_patterns()
        self.assertNotEqual([bool(re.search(p,ordered,re.M)) for p in patterns], [bool(re.search(p,reordered,re.M)) for p in patterns])
        with self.assertRaises(ValueError): audit_parse(ordered+' -F success=1')

    def test_audit_missing_b64_root_still_matches_two_published_patterns(self):
        patterns=original_patterns()
        for call in ('lsetxattr','removexattr'):
            duplicated=[p for p in patterns if '\\b'+call+'\\b' in p and 'auid=0' in p]
            self.assertEqual(len(duplicated),2)
            self.assertEqual(duplicated[0],duplicated[1]); self.assertIn('arch=b32',duplicated[0])

    def test_permission_exhaustive_and_numeric_counterexample(self):
        for mode in range(0o10000):
            self.assertEqual(permission_state(mode), mode & ~0o740 == 0)
        self.assertTrue(0o604 < 0o740); self.assertFalse(permission_state(0o604))

    def test_keyed_records_exhaustive(self):
        pred={'a':bool,'b':bool}
        for bits in itertools.product([False,True],repeat=4):
            rows=[{'key':'one','a':bits[0],'b':bits[1]},{'key':'two','a':bits[2],'b':bits[3]}]
            expected='true' if all(bits) else 'false'
            self.assertEqual(correlated_required(['one','two'],rows,pred),expected)
        rows=[{'key':'one','a':True,'b':False},{'key':'two','a':False,'b':True}]
        self.assertTrue(any(r['a'] for r in rows) and any(r['b'] for r in rows))
        self.assertEqual(correlated_required(['one','two'],rows,pred),'false')

    def test_missing_partial_unknown_duplicate_and_error(self):
        pred={'a':bool}; good={'key':'one','a':True}
        cases=[([],True,'false'),([],False,'unknown'),([good,good],True,'error'),
               ([{'key':'one'}],True,'error'),([{'key':'one','a':None}],True,'unknown'),
               ([{'key':'one','status':'error'}],True,'error'),([good],False,'unknown')]
        for rows,complete,expected in cases:
            self.assertEqual(correlated_required(['one'],rows,pred,complete=complete),expected)
        self.assertEqual(correlated_required([],[],pred,empty='true'),'true')
        self.assertEqual(correlated_required([],[],pred,empty='true',complete=False),'unknown')

    def test_status_dominance_and_evidence_cap(self):
        self.assertEqual(all_results(['false','error','unknown']),'false')
        self.assertEqual(all_results(['true','error','unknown']),'error')
        self.assertEqual(all_results(['true','unknown']),'unknown')
        results=['true']*50+['false']
        self.assertEqual(all_results(results),'false')
        self.assertEqual(all_results(results[:50]),'true') # demonstrates forbidden result capping

    def test_join_retains_identity(self):
        roots=[('one','/one/'),('two','/two/')]; configs=[('one','a.conf'),('two','b.conf')]
        self.assertEqual(len(cartesian_concat([x[1] for x in roots],[x[1] for x in configs])),4)
        self.assertEqual(keyed_concat(roots,configs),[('one','/one/a.conf'),('two','/two/b.conf')])

    def test_apache_intent_and_source_predicates_diverge(self):
        records=[('KeepAlive','Off'),('KeepAlive','On'),('MaxKeepAliveRequests','100')]
        self.assertFalse(apache_occurrences(records)); self.assertTrue(apache_effective(records))
        self.assertFalse(apache_occurrences([])); self.assertTrue(apache_effective([]))
        for n in [0,99,100,101]:
            self.assertEqual(apache_occurrences([('KeepAlive','On'),('MaxKeepAliveRequests',str(n))]),n>=100)

    def test_dns_duration_boundaries(self):
        for seconds,expected in [(172799,False),(172800,True),(604800,True),(604801,False),(608399,False)]:
            self.assertEqual(duration_exact(seconds),expected)
        self.assertTrue(48<=duration_hours_legacy(604801)<=168)
        self.assertFalse(duration_exact(604801))

    def test_acl_structural_is_not_effective(self):
        allow={'sid':'group','rights':['read'],'type':'allow'}; deny={'sid':'user','rights':['read'],'type':'deny'}
        self.assertFalse(ordered_access_check([deny,allow],{'user','group'},'read'))
        self.assertTrue(ordered_access_check([allow,deny],{'user','group'},'read'))
        self.assertFalse(ordered_access_check([],{'user'},'read'))

    def test_crypto_source_rows_and_required_resource_cases(self):
        tree=etree.parse(str(STUDY/'evidence/rhel_9/SV-258236/source-oval.xml'))
        nodes={e.get('id'):e for e in tree.iter() if e.get('id')}; source=[]
        for t in tree.iter():
            if etree.QName(t).localname not in ('symlink_test','file_test'): continue
            obj=nodes[next(c for c in t if etree.QName(c).localname=='object').get('object_ref')]
            state=nodes[next(c for c in t if etree.QName(c).localname=='state').get('state_ref')]
            field=next(c for c in state if etree.QName(c).localname in ('canonical_path','type'))
            path=next(c for c in obj if etree.QName(c).localname=='filepath').text
            source.append((path,etree.QName(field).localname,field.text))
        proposal=yaml.safe_load((STUDY/'proposals/crypto-backends.proposal.yaml').read_text())['assessment']
        rows=proposal['tests']['test-required-backends']['rows']
        self.assertEqual(sorted(source),sorted((r['full_path'],r['field'],r['expected']) for r in rows))
        self.assertEqual(len(rows),12)
        acquired=[{'key':r['full_path'],'observed':r['expected']} for r in rows]
        for row in rows:
            self.assertEqual(correlated_required([row['full_path']],acquired,{'observed':lambda x:x==row['expected']}),'true')
        self.assertEqual(correlated_required([rows[0]['full_path']],[],{'observed':bool}),'false')
        self.assertEqual(correlated_required([rows[0]['full_path']],[{'key':rows[0]['full_path'],'observed':'wrong'}],{'observed':lambda x:x==rows[0]['expected']}),'false')

    def test_home_account_filter_boundaries(self):
        def normal(uid,home):return uid>=1000 and home!='/'
        def root(uid,home):return uid<=0 and home!='/'
        self.assertFalse(normal(999,'/home/a'));self.assertTrue(normal(1000,'/home/a'))
        self.assertFalse(normal(1000,'/'));self.assertTrue(root(0,'/root'))
        self.assertFalse(root(0,'/'));self.assertFalse(root(1,'/home/a'))

    def test_ftp_bounded_path_relation(self):
        import ntpath
        def within(path,area):
            p=ntpath.normcase(ntpath.normpath(path));a=ntpath.normcase(ntpath.normpath(area))
            return p==a or p.startswith(a.rstrip('\\')+'\\')
        self.assertTrue(within('C:\\Windows\\Temp','C:\\Windows'))
        self.assertFalse(within('C:\\WindowsOld','C:\\Windows'))
        self.assertTrue(within('C:\\','C:\\'))
        self.assertFalse(within('D:\\ftp','C:\\'))

    def test_ad_rights_predicates(self):
        rights=['read','write','delete'] # Synthetic reduced model, not 17-field conformance.
        def no_others(rows):return all(not any(r.values()) for r in rows)
        self.assertTrue(no_others([dict.fromkeys(rights,False)]))
        self.assertFalse(no_others([{'read':False,'write':True,'delete':False}]))
        for missing in rights:
            granted=dict.fromkeys(rights,True);granted[missing]=False
            self.assertFalse(all(granted.values()))

    def test_registry_whitelist_does_not_require_all_principals(self):
        allowed={('system','full','allow'),('administrators','read','allow')}
        subset=[{'sid':'administrators','rights':'read','type':'allow'}]
        self.assertTrue(explicit_acl_allowed(subset,allowed))
        self.assertNotEqual({a['sid'] for a in subset},{'system','administrators'})
        self.assertFalse(explicit_acl_allowed(subset+[{'sid':'everyone','rights':'full','type':'allow'}],allowed))

    def test_dns_required_record_types(self):
        pred={'signed':bool,'rrsig':lambda n:n>0,'nsec3':lambda n:n>0,'dnskey':lambda n:n>0}
        good={'key':'zone-a','signed':True,'rrsig':1,'nsec3':1,'dnskey':1}
        self.assertEqual(correlated_required(['zone-a'],[good],pred),'true')
        for field in ('rrsig','nsec3','dnskey'):
            bad={**good,field:0}; self.assertEqual(correlated_required(['zone-a'],[bad],pred),'false')
        mixed=[{'key':'a','signed':True,'rrsig':1,'nsec3':0,'dnskey':0},
               {'key':'b','signed':True,'rrsig':0,'nsec3':1,'dnskey':0},
               {'key':'c','signed':True,'rrsig':0,'nsec3':0,'dnskey':1}]
        self.assertEqual(correlated_required(['a','b','c'],mixed,pred),'false')
        self.assertTrue(all(any(r[f]>0 for r in mixed) for f in ('rrsig','nsec3','dnskey')))

    def test_dns_key_coverage(self):
        pred={'seconds':duration_exact};key={'key':('zone','KSK'),'seconds':172800}
        self.assertEqual(correlated_required([('zone','KSK'),('zone','ZSK')],[key],pred),'false')
        self.assertEqual(correlated_required([('zone','KSK')],[key],pred,complete=False),'unknown')

    def test_interface_per_address_contract(self):
        pred={'address':bool,'prefix':lambda x:x is not None,'gateway':bool,'origin':lambda x:x=='Manual'}
        good={'key':(1,'10.0.0.1'),'address':'10.0.0.1','prefix':24,'gateway':'10.0.0.254','origin':'Manual'}
        other={**good,'key':(2,'10.1.0.1'),'address':'10.1.0.1'}
        self.assertEqual(correlated_required([good['key'],other['key']],[good,other],pred),'true')
        del other['gateway'];self.assertEqual(correlated_required([good['key'],other['key']],[good,other],pred),'error')
        self.assertEqual(correlated_required([],[],pred,empty='true'),'true')

    def test_apache_cookie_item_correlation_and_tokenization(self):
        cookies=['CookieA;HttpOnly','CookieB;Secure']
        source=lambda s: bool(re.search('HttpOnly',s,re.I) and re.search('Secure',s,re.I))
        typed=lambda s: {'httponly','secure'}<=set(x.lower() for x in s.split(';')[1:])
        self.assertFalse(all(source(c) for c in cookies));self.assertFalse(all(typed(c) for c in cookies))
        fake='SecureCookie;HttpOnlyFake'
        self.assertTrue(source(fake));self.assertFalse(typed(fake))
        for good in ['A;HttpOnly;Secure','B;secure;httponly']:
            self.assertTrue(source(good));self.assertTrue(typed(good))

    def test_apache_root_file_scope_is_not_recursive_policy(self):
        files={'/site/index.html'};directories=['/site','/site/sub']
        self.assertTrue('/site/index.html' in files)
        self.assertFalse(all(d+'/index.html' in files for d in directories))
        defaults={'/site/index.php'}
        self.assertFalse('/site/index.html' in defaults)
        self.assertTrue(any('/site/'+name in defaults for name in ['index.html','index.php']))

if __name__=='__main__': unittest.main()
