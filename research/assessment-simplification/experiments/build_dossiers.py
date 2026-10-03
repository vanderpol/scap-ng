#!/usr/bin/env python3
"""Deterministic research presentation; does not call/modify the production converter."""
import json,re,sys
from pathlib import Path
from lxml import etree
import yaml

STUDY=Path(__file__).resolve().parents[1]
def dump(path,doc):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('# EXPERIMENTAL research notation; not accepted v0.1.0 grammar.\n'+yaml.safe_dump(doc,sort_keys=False,width=100))

def document(rid,objects,states,tests,variables=None):
    a={'id':'research.'+rid,'version':1,'assessment_title':'Experimental '+rid,
       'mode':'automated','class':'compliance','purpose':'assessment'}
    if objects:a['objects']=objects
    if variables:a['variables']=variables
    if states:a['states']=states
    a['tests']=tests;a['evaluate']={'all':[{'test':t} for t in tests]}
    return {'assessment':a}

def record_proposal(rid,cap,selection,predicates,empty='false'):
    return document(rid,{'records':{'capability':cap,'select':selection,'record_identity':'key','collection_contract':'typed-status-per-key-v1'}},
       {'state-required-fields':{'capability':cap,'state':{'all':[{'field':field,'operation':op,'value':v} for field,op,v in predicates]}}},
       {'test-each-required-record':{'test_title':'Each required record satisfies all fields','capability':cap,
           'object':'records','states':['state-required-fields'],'existence':'some','match':'all',
           'required_key_coverage':True,'empty_result':empty}})

def main():
    notes=json.loads((STUDY/'experiments/case-notes.json').read_text()); index=[]
    proposals={
     'SV-214228':record_proposal('SV-214228','apache.configuration',{'representation':'explicit_directives','directives':['KeepAlive','MaxKeepAliveRequests'],'scope':'installation-context','source_groups':['main_and_includes','loaded_files']}, [('keepalive','equal_ci','On'),('max_keep_alive_requests','greater_or_equal',100),('keepalive_explicit','equal',True),('max_keep_alive_requests_explicit','equal',True)]),
     'SV-214268':record_proposal('SV-214268','apache.configuration',{'representation':'cookie_records','scope':'installation-context-cookie'}, [('session_enabled','equal',True),('cookie_attributes','superset',['HttpOnly','Secure']),('session_cookie_module_loaded','equal',True)]),
     'SV-214292':record_proposal('SV-214292','unix.file',{'directories':{'object_field':'document-roots','field':'directory'},'name':'index.html','name_comparison':'equal_ci','traversal':None}, [('exists','equal',True)]),
     'SV-278028':record_proposal('SV-278028','windows.iis.site',{'bindings':'ftp','path_interpretation':'configured_and_native_resolved'}, [('physical_path','not_within_system_area',True)]),
     'SV-278138':record_proposal('SV-278138','windows.fileeffectiverights53',{'directory_sources':{'registry_values':['Database log files path','DSA Database file','DSA Working Directory'],'hive':'HKLM','key':'SYSTEM\\CurrentControlSet\\Services\\NTDS\\Parameters'},'principal_scope':'source-behaviors-preserved'}, [('system_full_rights','equal',True),('administrators_full_rights','equal',True),('other_effective_rights','equal',False)]),
     'SV-278001':record_proposal('SV-278001','windows.registry.ace',{'hive':'HKLM','keys':['SECURITY','SOFTWARE','SYSTEM'],'view':'explicit_aces','role_source':'authored-domain-role'}, [('ace','allowed_by_published_default_table',True)]),
     'SV-259350':record_proposal('SV-259350','windows.dns.zone',{'zones':'source-forward-zone-selection','rr_types':['RRSIG','NSEC3','DNSKEY']}, [('signed','equal',True),('rrsig_count','greater_than',0),('nsec3_count','greater_than',0),('dnskey_count','greater_than',0)]),
     'SV-259345':record_proposal('SV-259345','windows.dns.signingkey',{'zones':'source-forward-zone-selection','key_types':['KSK','ZSK'],'duration_representation':'seconds'}, [('dnskey_validity_seconds','greater_or_equal',172800),('dnskey_validity_seconds','less_or_equal',604800)]),
     'SV-259374':record_proposal('SV-259374','windows.network.interface',{'status':'Up','address_family':'IPv4','identity_fields':['ifIndex','address']}, [('address','nonempty',True),('prefix_length','nonempty',True),('gateway','nonempty',True),('suffix_origin','equal','Manual')],empty='true')
    }
    # These prototypes are complete sketches of acquisition/evaluation, not deployable documents.
    # Resolve paths/role/zone-selection explicitly rather than leave opaque identifiers.
    proposals['SV-214292']['assessment']['objects']={'document-roots':{'capability':'apache.configuration','select':{'representation':'explicit_DocumentRoot','source_groups':['main_and_includes','loaded_files']}}, **proposals['SV-214292']['assessment']['objects']}
    proposals['SV-278001']['assessment']['objects']['authored-domain-role']={'capability':'windows.wmi.query','select':{'namespace':'root\\cimv2','query':'SELECT DomainRole FROM Win32_ComputerSystem'}}
    for rid in ('SV-259345','SV-259350'):
        proposals[rid]['assessment']['objects']['records']['select']['zones']={'exclude_types':['Forwarder'],'exclude_names':['TrustAnchors'],'autocreated':False,'reverse':False}
    # Native file-control example preserves the explicit permission booleans.
    proposals['SV-257889']=document('SV-257889',{
       'accounts':{'capability':'unix.password','select':{'username':{'operation':'match','value':'[\\w]+'}}},
       'normal-users':{'capability':'unix.password','source':'accounts','filters':[{'field':'user_id','operation':'greater_or_equal','value':1000},{'field':'home_dir','operation':'not_equal','value':'/'}]},
       'root-users':{'capability':'unix.password','source':'accounts','filters':[{'field':'user_id','operation':'less_or_equal','value':0},{'field':'home_dir','operation':'not_equal','value':'/'}]},
       **{kind+'-files':{'capability':'unix.file','select':{'directory':{'variable':kind+'-homes'},'name':{'operation':'match','value':'^\\.[^\\s\\.]+'}},'filters':[{'field':'type','operation':'not_equal','value':'directory'}],'traversal':{'max_depth':1,'follow_links':True,'filesystem':'any'}} for kind in ('normal','root')}},
       {'state-permitted-bits':{'capability':'unix.file','state':{'all':[{'field':f,'operation':'equal','value':False} for f in ['setuid','setgid','sticky','group_write','group_execute','other_read','other_write','other_execute']]}}},
       {f'test-{kind}-files':{'test_title':kind+' initialization permissions','capability':'unix.file','object':kind+'-files','states':['state-permitted-bits'],'existence':'optional' if kind=='normal' else 'some','match':'all'} for kind in ('normal','root')},
       {kind+'-homes':{'kind':'local','datatype':'string','expression':{'values':{'object':kind+'-users','field':'home_dir'}}} for kind in ('normal','root')})
    # Required-row template is a build-time idea, not a new runtime collector.
    fam=STUDY/'samples/rhel_9'
    crypto=yaml.safe_load(next((fam/'assessments/automated').glob('*258236*')).read_text())['assessment']
    crypto_rows=[]
    for t in crypto['tests'].values():
        o=crypto['objects'][t['object']];s=crypto['states'][t['states'][0]]['state']
        crypto_rows.append({'capability':t['capability'],'full_path':next(iter(o['select'].values()))['value'],'field':s['field'],'operation':'equal','expected':s['value'],'existence':'some','match':'all'})
    proposals['SV-258236']=document('SV-258236',{}, {}, {'test-required-backends':{'test_title':'Required back-end rows','capability':'research.required_rows','phase':'authoring_expansion','rows':crypto_rows}})
    # AD rights are a finite authoring-table proposal over the unchanged native
    # graph, not a collector returning policy-derived "full_rights" Booleans.
    adfamily=STUDY/'samples/ms_windows_server_2025'
    ad=yaml.safe_load(next((adfamily/'assessments/automated').glob('*278138*')).read_text())['assessment']
    proposals['SV-278138']=document('SV-278138',ad['objects'],ad['states'],
       {'test-directory-principal-rows':{'test_title':'Directory/principal rights rows','capability':'research.required_rows',
          'phase':'authoring_expansion','rows':list(ad['tests'].values())}},ad['variables'])
    audit=yaml.safe_load(next((fam/'assessments/automated').glob('*258179*')).read_text())['assessment']
    def value(x):
        if isinstance(x,str):return x
        if 'variable' in x:return value(audit['variables'][x['variable']]['expression'])
        if 'concat'in x:return ''.join(value(y) for y in x['concat'])
        if 'literal'in x:return value(x['literal'])
        return x['value']
    templates={};rows=[];grammar_ids={}
    calls=['fremovexattr','lremovexattr','removexattr','fsetxattr','lsetxattr','setxattr']
    for testname,t in audit['tests'].items():
        o=audit['objects'][t['object']]; pattern=value(o['select']['pattern']['value'])
        call=next(c for c in calls if c in pattern); arch=re.search('arch=(b32|b64)',pattern)[1]
        grammar=pattern.replace(call,'${syscall}').replace(arch,'${arch}')
        if grammar not in grammar_ids:
            name='pattern-template-'+str(len(grammar_ids)+1);grammar_ids[grammar]=name
            templates[name]={'title':'Source-preserving regex grammar','kind':'constant','datatype':'string','expression':{'literal':grammar}}
        rows.append({'template':grammar_ids[grammar],'syscall':call,'arch':arch,'auid':'root' if 'auid=0' in pattern else 'user','instance':o['select'].get('instance'),'collection_options':o.get('collect',{}),'filesystem':o.get('filesystem'),'existence':t['existence'],'match':t['match']})
    proposals['SV-258179']=document('SV-258179',{'persisted-rules':{'capability':'independent.textfilecontent54','select':{'full_path':'/etc/audit/audit.rules'},'collect':{'ignore_case':False,'multiline':True,'singleline':False,'item_creation':'source-per-row'}}}, {},
        {'test-audit-patterns':{'test_title':'Preserved audit pattern rows','capability':'research.required_rows','phase':'authoring_expansion','object':'persisted-rules','rows':rows}},templates)
    for family in sorted((STUDY/'samples').iterdir()):
        for rf in sorted((family/'rules').glob('*.yaml')):
            rule=yaml.safe_load(rf.read_text())['rule'];rid=rule['id'];note=notes[rid]
            af=next((family/'assessments/automated').glob('*'+rid+'*'));a=yaml.safe_load(af.read_text())['assessment']
            mf=next((family/'assessments/manual').glob('*'+rid+'*'));manual=yaml.safe_load(mf.read_text())['assessment']
            ev=STUDY/'evidence'/family.name/rid;graph=json.loads((ev/'graph.json').read_text())
            raw=etree.parse(str(ev/'source-rule.xml'))
            exact=[etree.tostring(n,encoding='unicode') for n in raw.iter() if etree.QName(n).localname=='check-content']
            prop=note['proposal'];dump(STUDY/'proposals'/prop,proposals[rid])
            lines=[f'# {rid}: {rule["title"]}', '', '**Experimental research dossier. No runtime equivalence claim.**','',
              '## Source and policy', '', f'Inherited Rule revision `{rule["version"]}`; package `{graph["source"]["source_zip"]}`.',
              f'NIWC commit `{graph["source"]["source_revision"]}`, ZIP SHA-256 `{graph["source"]["source_sha256"]}`.',
              f'Pinned package: https://github.com/niwc-atlantic/scap-content-library/blob/{graph["source"]["source_revision"]}/{graph["source"]["source_zip"]}',
              '',note['plain'],'','### Original Check Text', '',
              'Exact XML serialization and complete selectors/links are retained in [source-rule.xml](../evidence/'+family.name+'/'+rid+'/source-rule.xml). Text below is the inherited generated procedure, with presentation whitespace normalized:', '', '> '+manual['procedure'],
              '', '### Applicability', '',f'Rule applicability IDs: `{json.dumps(rule.get("applicability",[]))}`. Benchmark platform and complete family catalog are inherited in [context](../samples/{family.name}/benchmark-context.json) and [applicability](../samples/{family.name}/applicability.yaml). Applicability Tests remain outside this configuration proposal. Rule role remains `{rule.get("role")}`.',
              '', '## Complete baseline dependency explanation','',note['baseline'],'',
              f'Closure counts: `{json.dumps(graph["closure_counts"],sort_keys=True)}`; [original OVAL](../evidence/{family.name}/{rid}/source-oval.xml), [typed dependency edges and source attributes](../evidence/{family.name}/{rid}/graph.json), [unchanged before Assessment](../samples/{family.name}/assessments/automated/{af.name}).',
              '', '### Necessary semantics versus representation overhead', '',note['finding'],'',
              'Object status/completeness, Item and entity existence, item/state/variable quantifiers, Boolean nesting and acquisition scope are necessary semantics. Source comment/title, separate serialization wrappers and repeated command/regex construction are not independent security requirements. Named shared Objects and Variables SHALL remain referenceable.',
              '', '## Methods investigated', '',note['alternatives'],'',f'[Complete after sketch](../proposals/{prop}) — all invented fields use the [experimental contract](../FEATURES.md). This sketch shows the proposed method, not a deployable lossless conversion; applicability/bindings remain unchanged unless separately reviewed. A no-change baseline remains valid.',
              '', '## Cases and falsification', '',note['counterexamples'],'',
              'Executed cases are in [test_semantics.py](../experiments/test_semantics.py) and [results](../evidence/test-results.txt). Additional acquisition/OS cases above are specified, not executed. Per-record missing/error/unknown/multiple-match/partial-collection fixtures are synthetic language experiments, not evidence that source collectors behave that way.',
              '', '## Cost, confidence and unresolved decisions', '',note['cost'],'',
              'Established: inherited source graph and references. Inferred: intended scope explained from Check Text, separately from source behavior. Unresolved: collector execution, target reachability of synthetic boundaries and independent assessor agreement. See [comparison](../COMPARISON.md) and [questions](../DECISIONS.md).',
              '', '## Readable node inventory (all reachable NG configuration nodes)', '']
            for section in ('objects','variables','states','tests'):
                lines.extend(['### '+section,''])
                for name,node in a.get(section,{}).items():
                    lines.append('- `'+name+'`: '+str(node.get('object_title',node.get('test_title',node.get('state_title',node.get('title')))))+'; '+str(node.get('capability',node.get('kind'))))
                lines.append('')
            lines.extend(['### Existing evaluation','', '```yaml',yaml.safe_dump(a['evaluate'],sort_keys=False).rstrip(),'```','',
                'Provenance: Inherited source extracts/snapshots; Adapted graph presentation and experimental examples; Common original bounded models; Evidence/Audit findings, counterexamples and measurements.'])
            matrices=json.loads((STUDY/'experiments/case-matrices.json').read_text())
            lines.extend(['','## Concrete result matrix','',
              'Results below isolate the stated comparison/scope model. They are not complete source target executions. `Specified` cases require future collector/target tests; `Executed` cases have bounded fixtures. Error/unknown columns retain distinctions; they are not forced to Boolean compliance.','',
              '| Case | Published contract/model | Proposed contract/model | Evidence |','| --- | --- | --- | --- |'])
            for row in matrices[rid]: lines.append('| '+' | '.join(row)+' |')
            (STUDY/'dossiers').mkdir(exist_ok=True); (STUDY/'dossiers'/f'{rid}.md').write_text('\n'.join(lines)+'\n')
            index.append({'family':family.name,'rule':rid,'before_nodes':sum(graph['ng_counts'].values()),'proposed_visible_nodes':sum(len(proposals[rid]['assessment'].get(s,{})) for s in ('objects','variables','states','tests')),'note':'Counts exclude nested predicates/rows; not semantic or runtime reduction.'})
    (STUDY/'evidence/authoring-counts.json').write_text(json.dumps(index,indent=2)+'\n')
    print(f'Built {len(index)} dossiers and proposals')

if __name__=='__main__':main()
