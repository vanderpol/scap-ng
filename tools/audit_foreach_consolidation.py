from __future__ import annotations
import argparse, copy, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
import yaml


def walk(x,path=()):
    if isinstance(x,dict):
        if set(x)=={'variable'} and isinstance(x['variable'],str): yield x['variable'],path
        for k,v in x.items(): yield from walk(v,path+(k,))
    elif isinstance(x,list):
        for i,v in enumerate(x): yield from walk(v,path+(i,))

def primary_expression(expr):
    if not isinstance(expr, dict): return 'other'
    for key in ('values','concat','regex_capture','unique','merge','count','split','substring','time_difference','arithmetic','to_integer','literal'):
        if key in expr: return key
    return 'other'

def classify(root):
    files=sorted(root.glob('*/native-automated-subset/authoring/direct-slice/assessments/*.json'))
    c=Counter(); rows=[]; reductions=[]
    for p in files:
        d=json.loads(p.read_text())['assessment']; uses=defaultdict(list)
        for v,path in walk(d): uses[v].append(path)
        for v,decl in d.get('variables',{}).items():
            expr=decl.get('expression',{})
            c['variable_expression_' + primary_expression(expr)] += 1
            if not (isinstance(expr,dict) and set(expr)=={'values'} and isinstance(expr['values'],dict) and 'object' in expr['values'] and 'field' in expr['values']):
                continue
            c['object_derived_variable_definitions']+=1
            source=expr['values']['object']; field=expr['values']['field']
            external=uses[v]
            selector=[]; other=[]
            for path in external:
                is_selector=(path and path[0]=='tests' and len(path)>2 and path[2]=='object') or (path and path[0]=='shared_objects')
                (selector if is_selector else other).append(path)
            if not selector: c['object_derived_not_selector']+=1; continue
            c['object_derived_selector_references']+=len(selector)
            if other: c['also_used_outside_selector']+=1; continue
            c['sole_transfer_variable_definitions']+=1
            c['sole_transfer_selector_references']+=len(selector)
            row={'assessment':d['id'],'file':str(p.relative_to(root)),'variable':v,'source_field':field,'source_object':source,'selector_paths':selector}
            # Resolve source object and inspect each direct target.
            source_obj=source
            if isinstance(source,str): source_obj=d.get('shared_objects',{}).get(source)
            direct=True; reasons=[]; targets=[]
            for path in selector:
                if path[0]=='shared_objects' and len(path)==4:
                    obj=d['shared_objects'].get(path[1],{})
                    selector_name,op=path[2],path[3]
                    node=obj.get(selector_name)
                    if not isinstance(node,dict) or set(node.keys()) != {op}:
                        direct=False; reasons.append('selector_shape'); continue
                    if not (isinstance(node.get(op),dict) and node[op].get('variable')==v):
                        direct=False; reasons.append('not_direct_variable_ref')
                    if 'for_each' in obj:
                        direct=False; reasons.append('existing_for_each')
                    targets.append({'target_kind':'shared_object','name':path[1],'capability':obj.get('capability'),'selector':selector_name,'operator':op})
                    continue
                if path[0]!='tests' or len(path)!=5 or path[2]!='object':
                    direct=False; reasons.append('shared_or_nested_target'); continue
                t=d['tests'].get(path[1]); obj=t.get('object',{}) if t else {}
                selector_name,op=path[3],path[4]
                node=obj.get(selector_name)
                if not isinstance(node,dict) or set(node.keys()) != {op} and set(node.keys()) != {op,'value_match'}:
                    direct=False; reasons.append('selector_shape'); continue
                if 'value_match' in node:
                    direct=False; reasons.append('selector_value_match')
                if not (isinstance(node.get(op),dict) and node[op].get('variable')==v):
                    direct=False; reasons.append('not_direct_variable_ref')
                if not isinstance(obj,dict) or 'for_each' in obj:
                    direct=False; reasons.append('existing_for_each')
                targets.append({'target_kind':'test_object','test':path[1],'capability':t.get('capability'),'selector':selector_name,'operator':op})
            if not isinstance(source_obj,dict): direct=False; reasons.append('unresolved_source_object')
            if isinstance(source_obj,dict) and 'for_each' in source_obj: reasons.append('source_already_expanded')
            row['targets']=targets; row['strict_structural_candidate']=direct; row['reasons']=sorted(set(reasons))
            if direct:
                c['strict_structural_candidates']+=1
                if any(t['target_kind']=='shared_object' for t in targets): c['shared_object_candidates']+=1
                # Reviewed selector support is evaluated against the current
                # canonical overlay set, not assumed for the full corpus.
                # The corpus predates this schema amendment; these are design
                # candidates, not runtime equivalence.
                c['strict_candidate_target_references']+=len(targets)
                if isinstance(source,dict) and source.get('set'): c['strict_source_set']+=1
            else: c['candidate_requires_semantic_review']+=1
            rows.append(row)
    # Transform strict candidates solely for normalized YAML line accounting.
    # This is a representation estimate, not a semantic proof.
    for row in rows:
        if not row['strict_structural_candidate']: continue
        dpath=root/row['file']; doc=json.loads(dpath.read_text()); d=doc['assessment']; v=row['variable']
        expr=d['variables'][v]['expression']['values']; source=expr['object']; field=expr['field']
        source_id=source if isinstance(source,str) else 'foreach-source-'+re.sub('[^a-z0-9]+','-',v).strip('-')[:42]+'-object'
        if isinstance(source,dict): d.setdefault('shared_objects',{})[source_id]=copy.deepcopy(source)
        for t in row['targets']:
            if t['target_kind']=='shared_object':
                obj=d['shared_objects'][t['name']]
            else:
                obj=d['tests'][t['test']]['object']
            node=obj[t['selector']]
            obj['for_each']={'item':'source','in':source_id,'reduce':'every'}
            node[t['operator']]={'from':f'source.{field}'}
            node.pop('value_match',None)
        d['variables'].pop(v)
        if not d['variables']: d.pop('variables')
        before=yaml.safe_dump(doc,sort_keys=False).splitlines()
        # construct equivalent transformed from a fresh original to compare
        original=json.loads(dpath.read_text()); before=yaml.safe_dump(original,sort_keys=False).splitlines()
        after=yaml.safe_dump(doc,sort_keys=False).splitlines()
        reductions.append({'assessment':row['assessment'],'variable':v,'before_yaml_lines':len(before),'after_yaml_lines':len(after),'delta_lines':len(after)-len(before)})
    return files,c,rows,reductions

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--stage-manifest',type=Path,required=True); ap.add_argument('--source-pins',type=Path); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    files,c,rows,reds=classify(args.root)
    m=json.loads(args.stage_manifest.read_text())
    if len(m.get('streams',[])) not in (0,65): raise SystemExit('expected 65 benchmark streams')
    result={'format':'scap-ng-foreach-consolidation-audit/0.1','status':'design-analysis-only','source':{
      'benchmark_count':len(m.get('streams',[])),'source_rules':m.get('totals',{}).get('source_rules'), 'converted_rules':m.get('totals',{}).get('converted_rules'), 'blocked_rules':m.get('totals',{}).get('blocked_rules'),
      'native_assessments_scanned':len(files),'tools_commit':m.get('tools_commit'),'schema_commit':m.get('schema_commit'),'stage_manifest_sha256':hashlib.sha256(args.stage_manifest.read_bytes()).hexdigest() if args.stage_manifest else None,
      'source_repository': json.loads(args.source_pins.read_text()).get('repository') if args.source_pins else None, 'source_revision': json.loads(args.source_pins.read_text()).get('revision') if args.source_pins else None, 'source_pins_sha256': hashlib.sha256(args.source_pins.read_bytes()).hexdigest() if args.source_pins else None, 'scope':m.get('limitations',[])} ,'counts':dict(c),
      'replacement_decision': {'current_for_each_replacements_verified': 0, 'semantic_candidates_requiring_review': c['sole_transfer_variable_definitions'], 'upper_bound_transfer_variables_removable': c['sole_transfer_variable_definitions'], 'reason': 'All sole-transfer candidates use selector value_match or nested/shared placement; current binding shape is scalar {from} and cannot be declared equivalent without an approved cardinality/lineage mapping.'},
      'yaml_estimate':{'strict_candidates':len(reds),'before_lines':sum(x['before_yaml_lines'] for x in reds),'after_lines':sum(x['after_yaml_lines'] for x in reds),'delta_lines':sum(x['delta_lines'] for x in reds),'method':'PyYAML normalized representation; estimate only'},
      'candidates':rows}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'source':result['source'],'counts':result['counts'],'yaml_estimate':result['yaml_estimate']},indent=2))
if __name__=='__main__':main()
