#!/usr/bin/env python3
"""Research evidence only. Use maintained source resolver; never execute source commands."""
import argparse, hashlib, json, sys
from pathlib import Path
from lxml import etree
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import scap14_rule_splitter as split

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source_root', type=Path)
    args=ap.parse_args(); study=ROOT/'research/assessment-simplification'
    manifest=json.loads((study/'sample-manifest.json').read_text())
    for f in manifest['files']:
        assert digest(study/f['path']) == f['sha256'], f['path']
    results=[]
    for family in sorted((study/'samples').iterdir()):
        pin=json.loads((family/'source-generation.json').read_text())
        source=args.source_root/pin['source_zip']
        assert digest(source)==pin['source_sha256'], str(source)
        member, data, ds=split.find_datastream(source)
        components, refs=split.embedded_components(ds)
        benchmark=next(v for v in components.values() if split.component_kind(v)=='xccdf')
        ovs=[split.OvalComponent(cid, r) for cid,r in split.oval_source_roots(source,components)]
        app_rows=split.applicability_oval_refs(benchmark)+split.cpe_dictionary_oval_refs(components)
        app_reports=[]
        for n,app in enumerate(app_rows):
            seed=app.get('definition_id')
            if not seed or not seed.startswith('oval:'): continue
            selected=split.resolve_oval_components(ovs,seed,app.get('href'),refs)
            # A duplicated standalone component is not an independent semantic source.
            selected=[c for c in selected if c.component_id in components] or selected
            assert len(selected)==1, (app, [c.component_id for c in selected])
            c=selected[0];ids,missing,edges=c.closure([seed]);assert not missing, missing
            app_reports.append({'binding':app,'component':c.component_id,'ids':sorted(ids),'edges':edges})
            tree,_=split.merge_rule_closures([(c,sorted(ids,key=c.source_order.get))])
            target=study/'evidence'/family.name/'applicability'/f'{n:02d}.xml'
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(etree.tostring(tree,pretty_print=True,encoding='UTF-8',xml_declaration=True))
        write(study/'evidence'/family.name/'applicability/graph.json',{'source':pin,'bindings':app_reports,'note':'Complete benchmark applicability bindings, kept separate from configuration.'})
        rules=split.rule_oval_refs(benchmark)
        for rulefile in sorted((family/'rules').glob('*.yaml')):
            rule=yaml.safe_load(rulefile.read_text())['rule']; rid=rule['id']
            raw=next(r for r in benchmark.iter() if split.local(r.tag)=='Rule' and rid+'r' in (r.get('id') or ''))
            row=next(r for r in rules if r['rule_id']==raw.get('id'))
            out=study/'evidence'/family.name/rid
            out.mkdir(parents=True,exist_ok=True)
            (out/'source-rule.xml').write_bytes(etree.tostring(raw,pretty_print=True,encoding='UTF-8'))
            checks=[c for c in row['checks'] if c.get('name','').startswith('oval:')]
            closures=[]; reports=[]
            for c in checks:
                selected=split.resolve_oval_components(ovs,c['name'],c.get('href'),refs)
                catalog=[n.get('uri','').lstrip('#') for n in ds.iter() if split.local(n.tag)=='uri' and n.get('name')==c.get('href')]
                if catalog:
                    target=refs.get(catalog[0],catalog[0])
                    selected=[comp for comp in ovs if comp.component_id==target]
                assert len(selected)==1, (c, [comp.component_id for comp in selected])
                for comp in selected:
                    ids,missing,edges=comp.closure([c['name']]); assert not missing, missing
                    if not any(old.component_id==comp.component_id and oldids==ids for old,oldids in closures):
                        closures.append((comp,ids))
                    reports.append({'seed':c,'component':comp.component_id,'ids':sorted(ids),'edges':edges,'missing':sorted(missing)})
            tree,counts=split.merge_rule_closures([(c,sorted(ids,key=c.source_order.get)) for c,ids in closures])
            (out/'source-oval.xml').write_bytes(etree.tostring(tree,pretty_print=True,encoding='UTF-8',xml_declaration=True))
            defaults=[]; externals=[]
            for comp,ids in closures:
                for oid in sorted(ids):
                    node=comp.by_id[oid]
                    if split.local(node.tag)=='external_variable': externals.append(split.xccdf_node(node))
                    for n in node.iter():
                        name=split.local(n.tag)
                        if name in ('filter','set','behaviors'):
                            defaults.append({'id':oid,'element':name,'explicit':dict(n.attrib),'text':n.text})
            auto=next((family/'assessments/automated').glob('*'+rid+'*'))
            a=yaml.safe_load(auto.read_text())['assessment']
            report={'source':pin,'datastream_member':member,'datastream_sha256':hashlib.sha256(data).hexdigest(),
                    'rule_id':raw.get('id'),'source_rule_version':raw.get('version'),
                    'checks':row,'closures':reports,'closure_counts':counts,'collection_set_filter_attributes':defaults,
                    'external_inputs':externals,'ng_counts':{s:len(a.get(s,{})) for s in ('objects','variables','states','tests')},
                    'source_oval_sha256':digest(out/'source-oval.xml'),'source_rule_sha256':digest(out/'source-rule.xml')}
            write(out/'graph.json', report)
            results.append({'family':family.name,'rule':rid,'counts':counts,'external_variables':len(externals),'closure_nodes':sum(counts.values())})
    write(study/'evidence/source-verification.json',{'packet_files_verified':len(manifest['files']),'cases':results,'limits':'Reference closure and hashes, not execution equivalence.'})
    print(json.dumps(results,indent=2))

if __name__=='__main__': main()
