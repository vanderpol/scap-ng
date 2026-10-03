#!/usr/bin/env python3
"""Reproducible static research guards; never executes a collector."""
import hashlib,json,sys
from pathlib import Path
from lxml import etree
import yaml

STUDY=Path(__file__).resolve().parents[1];ROOT=STUDY.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    manifest=json.loads((STUDY/'sample-manifest.json').read_text())
    for f in manifest['files']: assert sha(STUDY/f['path'])==f['sha256'],f['path']
    for p in (STUDY/'evidence').glob('*/*/graph.json'):
        if p.parent.name=='applicability':continue
        graph=json.loads(p.read_text())
        assert graph['source_oval_sha256']==sha(p.parent/'source-oval.xml')
        assert graph['source_rule_sha256']==sha(p.parent/'source-rule.xml')
        for closure in graph['closures']:
            ids=set(closure['ids']);assert not closure['missing']
            assert all(e['from'] in ids and e['to'] in ids for e in closure['edges'])
    xsd=ROOT/'third_party/scap-1.4-schemas';schema=etree.XMLSchema(etree.parse(str(xsd/'omni-schema.xsd')))
    ovschema={}
    for p in (xsd/'oval_5.12.3').glob('*-definitions-schema.xsd'):
        t=etree.parse(str(p));ns=t.getroot().get('targetNamespace')
        for e in t.getroot().findall('{http://www.w3.org/2001/XMLSchema}element'):
            ovschema[(ns,e.get('name'))]=(p,e)
    overrides=json.loads((ROOT/'specification/migration/oval-test-support-overrides.json').read_text())
    reinstated={x['qualified_name'] for x in overrides['overrides'] if x['effective_status']=='supported_reinstated'}
    validation=[];tests={};used=set()
    for p in sorted((STUDY/'evidence').glob('*/*/*.xml')):
        if p.name=='source-rule.xml':continue
        t=etree.parse(str(p));valid=schema.validate(t)
        validation.append({'path':str(p.relative_to(STUDY)),'valid':valid,'errors':[str(e) for e in schema.error_log]})
        assert valid,(p,schema.error_log)
        for node in t.iter():
            q=etree.QName(node)
            if not q.localname.endswith('_test'):continue
            schema_path,decl=ovschema[(q.namespace,q.localname)];used.add(schema_path)
            info=decl.findall('.//{http://oval.mitre.org/XMLSchema/oval-common-5}deprecated_info')
            key=q.namespace+'#'+q.localname
            status='supported_reinstated' if key in reinstated else 'deprecated' if info else 'supported'
            tests[key]={'status':status,'schema':str(schema_path.relative_to(ROOT)),'schema_sha256':sha(schema_path)}
            assert status!='deprecated',(key,'must flag replacement and block experimental support')
    (STUDY/'evidence/source-xsd.json').write_text(json.dumps(validation,indent=2)+'\n')
    schemas=[xsd/'omni-schema.xsd',xsd/'oval_5.12.3/oval-definitions-schema.xsd',xsd/'oval_5.12.3/oval-results-schema.xsd',*sorted(used)]
    report={'sample_hashes_verified':len(manifest['files']),'original_oval_documents_xsd_valid':len(validation),
      'effective_test_support':tests,'schema_hashes':{str(p.relative_to(ROOT)):sha(p) for p in schemas},
      'override_sha256':sha(ROOT/'specification/migration/oval-test-support-overrides.json'),
      'limits':'Static closure, hash, support and XSD evidence only; no target evaluator or upstream Self-Assertion execution.'}
    (STUDY/'evidence/static-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    for p in (STUDY/'proposals').glob('*.yaml'):assert isinstance(yaml.safe_load(p.read_text()),dict)
    print(json.dumps({'sample_hashes':len(manifest['files']),'oval_documents':len(validation),'supported_test_types':len(tests)},indent=2))

if __name__=='__main__':main()
