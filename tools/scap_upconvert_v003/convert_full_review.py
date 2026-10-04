#!/usr/bin/env python3
"""Build a current full SCAP-NG research review from a pinned local SCAP ZIP.

Uses source parsing/lowering helpers, never historical generator main functions.
Deprecated OVAL Tests are rejected from automation; where verified source manual
checks exist, affected Rules may be emitted as manual-only review content.
Not a finalized language implementation or a target-runtime conformance claim.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import yaml
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scap_upconvert_v003 import convert_collection_review as review
from scap_upconvert_v003 import build_rhel9_review_slice as source
from scap_upconvert_v003.audit_profile_selection import (
    extract_selection, expected_selections, native_profile_id, audit)
from scap_upconvert_v003.cleanliness import assert_native_clean
from check_current_authoring_contract import violations
from scap_upconvert_v003.assessment_oval_vocabulary import (align_assessment_vocabulary, WORKING_ASSESSMENT_SPECIFICATION_ID, WORKING_ASSESSMENT_SPECIFICATION_VERSION)
from scap_upconvert_v003.native_capability_mapping import apply_ready_capability_mappings
from scap_ng_roundtrip_v003.native_assessment_to_oval import build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def profile_description(element):
    value=source.text(element)
    if value and value.startswith('<ProfileDescription'):
        wrapper=ET.fromstring(value)
        if source.local(wrapper.tag)!='ProfileDescription': raise ValueError('Unexpected Profile description wrapper')
        return source.text(wrapper)
    return value


def _typed_xccdf_value(raw, kind):
    if raw is None:
        return None
    if kind == "boolean":
        value=raw.strip().lower()
        if value in ("true","1"): return True
        if value in ("false","0"): return False
        raise ValueError("Invalid XCCDF boolean Value: "+raw)
    if kind == "number":
        value=raw.strip()
        try:
            return int(value,10)
        except ValueError:
            try:
                return float(value)
            except ValueError as exc:
                raise ValueError("Invalid XCCDF number Value: "+raw) from exc
    return raw


def render_parameters(xr):
    """Render the scalar XCCDF Value surface proven by the pinned corpus."""
    parameters=[]
    source_to_native={}
    used=set()
    for node in xr.findall(".//x:Value",source.NS):
        source_id=node.get("id")
        if not source_id:
            raise ValueError("XCCDF Value missing id")
        kind=node.get("type") or "string"
        if kind not in ("string","boolean","number"):
            raise ValueError("Unsupported XCCDF Value type: "+kind)
        base=[child for child in node.findall("x:value",source.NS) if child.get("selector") is None]
        if len(base)!=1:
            raise ValueError(source_id+": expected exactly one unselected XCCDF value")
        native_id=source.safe_id(source_id.split("_value_",1)[-1])
        if native_id in used:
            raise ValueError("Duplicate native Parameter id: "+native_id)
        used.add(native_id); source_to_native[source_id]=native_id
        choices=[]
        for child in node.findall("x:value",source.NS):
            selector=child.get("selector")
            if selector is None:
                continue
            choices.append({
                "selector":selector,
                "value":_typed_xccdf_value(source.text(child),kind),
            })
        description=source.text(node.find("x:description",source.NS)) or source.text(node.find("x:title",source.NS))
        constraints={}
        operator=node.get("operator") or "equals"
        if operator!="equals":
            constraints["comparison_operator"]=operator
        if choices:
            constraints["choices"]=choices
        parameters.append({
            "id":native_id,
            "type":kind,
            "description":description,
            "source":"publisher",
            "value":_typed_xccdf_value(source.text(base[0]),kind),
            "tailorable":(node.get("prohibitChanges") or "false").lower() not in ("true","1"),
            "required":False,
            "constraints":constraints,
        })
    return parameters,source_to_native


def check_parameter_bindings(check, parameter_ids):
    bindings={}
    for export in check.findall("x:check-export",source.NS):
        variable=export.get("export-name"); value_id=export.get("value-id")
        if not variable or not value_id:
            raise ValueError("Invalid XCCDF check-export")
        if value_id not in parameter_ids:
            raise ValueError("Unresolved XCCDF Value binding: "+value_id)
        prior=bindings.get(variable)
        if prior and prior!=parameter_ids[value_id]:
            raise ValueError("Conflicting XCCDF check-export binding: "+variable)
        bindings[variable]=parameter_ids[value_id]
    return bindings


def render_profiles(xr, resolved, baseline, expected):
    if not all(baseline.values()):
        raise ValueError('Source baseline disables Rules; native Benchmark membership enables every Rule')
    originals={p.get('id'):p for p in xr.findall('x:Profile',source.NS)}
    profiles=[]
    for profile in resolved:
        pid=native_profile_id(profile['id']);effective=expected[pid]
        if effective['problems'] or profile.get('unresolved_targets'): raise ValueError('Unresolved Profile: '+pid)
        if any(a['kind']!='select' for a in profile['effective_actions']): raise ValueError('Unsupported Profile action: '+pid)
        original=originals[profile['id']]
        if original.findall('x:platform',source.NS): raise ValueError('Profile-specific applicability needs representation')
        parent_id=native_profile_id(profile['extends']) if profile.get('extends') else None
        inherited=expected[parent_id]['enabled'] if parent_id else baseline
        if any(value and not inherited[rid] for rid,value in effective['enabled'].items()):
            raise ValueError('Profile re-enables an ancestor-disabled Rule: '+pid)
        row={'id':pid,'title':source.text(original.find('x:title',source.NS)),
             'description':profile_description(original.find('x:description',source.NS))}
        if parent_id: row['extends']=parent_id
        disabled=sorted(rid for rid,value in effective['enabled'].items() if not value and inherited[rid])
        row['disabled_rules']=disabled
        profiles.append(row)
    return profiles


def cpe_applicability_id(cpe_name):
    return 'platform.'+source.semantic_id(cpe_name,'platform')


def platform_sources(package):
    predicates={}; dictionary={}
    with zipfile.ZipFile(package) as archive:
        for name in sorted(archive.namelist()):
            if not name.lower().endswith('.xml'): continue
            root=ET.fromstring(archive.read(name))
            for node in root.iter():
                kind=source.local(node.tag)
                if kind=='platform' and node.get('id'):
                    key=node.get('id'); target=predicates
                elif kind=='cpe-item':
                    keys=[node.get('name')]
                    keys.extend(
                        child.get('name') for child in node.iter()
                        if source.local(child.tag)=='cpe23-item' and child.get('name')
                    )
                    target=dictionary
                    for key in [value for value in keys if value]:
                        if key in target and ET.tostring(target[key])!=ET.tostring(node):
                            raise ValueError('Conflicting platform source: '+key)
                        target[key]=node
                    continue
                else: continue
                if key in target and ET.tostring(target[key])!=ET.tostring(node):
                    raise ValueError('Conflicting platform source: '+key)
                target[key]=node
    return predicates, dictionary


def validate_native_tree(root):
    identities={}; documents={}
    for path in sorted(root.rglob('*.yaml')):
        doc=yaml.safe_load(path.read_text(encoding='utf-8'))
        assert_native_clean(doc)
        errors=violations(doc)
        if errors: raise ValueError(str(path)+': '+str(errors))
        if len(doc)!=1: raise ValueError('Expected one native document: '+str(path))
        kind=next(iter(doc)); identity=doc[kind].get('id')
        if identity:
            if identity in identities: raise ValueError('Duplicate native identity: '+identity)
            identities[identity]=path.relative_to(root).as_posix()
        documents[path.resolve()]=doc
    def resolve(owner, ref, kind):
        path=(owner.parent/ref).resolve()
        if not path.is_relative_to(root.resolve()): raise ValueError('Reference escapes package: '+ref)
        if path not in documents or kind not in documents[path]:
            raise ValueError('Missing or wrong-type reference: '+ref)
        return documents[path][kind]
    benchmark_path=(root/'benchmark.yaml').resolve()
    benchmark=documents[benchmark_path]['benchmark']
    rule_ids=benchmark['rules']
    if len(rule_ids)!=len(set(rule_ids)): raise ValueError('Duplicate Benchmark Rule')
    registry_path=(root/benchmark['applicability_catalog']).resolve()
    registry=resolve(benchmark_path,benchmark['applicability_catalog'],'applicability')
    for binding in registry['conditions'].values():
        resolve(registry_path,binding['assessment'],'assessment')
    for rid in rule_ids:
        path=(root/identities[rid]).resolve(); rule=documents[path]['rule']
        choices=rule['assessment_choices']
        if rule['default_assessment_choice'] not in choices: raise ValueError('Missing default choice: '+rid)
        for choice in choices.values(): resolve(path,choice['assessment'],'assessment')
        if set(rule['applicability'])-set(registry['conditions']): raise ValueError('Unresolved Rule applicability: '+rid)
        for key in ('requires','conflicts'):
            if set(rule[key])-set(rule_ids): raise ValueError('Unknown Rule '+key+': '+rid)
    if set(benchmark['platform']['applicability']['conditions'])-set(registry['conditions']):
        raise ValueError('Unresolved Benchmark applicability')
    grouped=[]
    def group_members(groups):
        for group in groups:
            grouped.extend(group.get('rules',[]));group_members(group.get('groups',[]))
    group_members(benchmark['groups'])
    if Counter(grouped)!=Counter(rule_ids): raise ValueError('Grouping lost/duplicated Rules')
    return {'yaml_files':len(documents),'rules':len(rule_ids),'identities':identities,
            'relative_references':'passed','native_cleanliness':'passed','presentation_order':'passed',
            'group_membership':'passed'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--sha256', required=True, help='Expected SHA256, or "auto" for a source already pinned by repository revision/path')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--benchmark-id', default='rhel9-stig-current-full')
    parser.add_argument('--platform-id', default='enterprise-linux.9')
    parser.add_argument('--platform-title', default='Enterprise Linux 9 family')
    parser.add_argument('--split-root', type=Path, help='Optional component-resolved rule-split corpus from scap14_rule_splitter.py')
    parser.add_argument('--schema', type=Path, default=Path(__file__).resolve().parents[2]/'third_party/scap-1.4-schemas/omni-schema.xsd')
    args=parser.parse_args(argv)
    actual_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest()
    if args.sha256!='auto' and actual_sha256!=args.sha256:
        raise ValueError('Source checksum mismatch')
    if args.output.exists() and any(args.output.iterdir()): raise ValueError('Output must be new or empty')
    if args.split_root:
        xr=review.source_benchmark(args.input); oval=None
    else:
        xr,oval=review.source_components(args.input)
    rs=source.records(xr); by_source={r['source_rule_id']:r['id'] for r in rs}
    if len(rs)!=len(by_source) or len(rs)!=len({r['id'] for r in rs}): raise ValueError('Duplicate Rules')
    # Reject unsupported policy forms rather than flattening them silently.
    if xr.findall('.//x:complex-check',source.NS):
        raise ValueError('Full review does not yet support complex-check')
    parameters,parameter_ids=render_parameters(xr)
    sr,sg,ancestry,resolved=extract_selection(args.input)
    baseline,expected=expected_selections(sr,sg,ancestry,resolved)
    profiles=render_profiles(xr,resolved,baseline,expected)
    selection_evidence=[]
    for profile in resolved:
        pid=native_profile_id(profile['id']); effective=expected[pid]
        selection_evidence.append({'profile':pid, 'source':deepcopy(profile),
                                   'effective_selection':effective['enabled']})
    with tempfile.TemporaryDirectory() as temporary:
        temp=Path(temporary)
        schema=etree.XMLSchema(etree.parse(str(args.schema)))
        if args.split_root:
            evidence={'status':'prototype_collection_graph_review','source_sha256':actual_sha256,'rules':[],
                      'limits':['Component-resolved per-Rule conversion evidence; not target-runtime equivalence.',
                                'Deprecated OVAL Tests are skipped only when a verified source manual fallback exists.',
                                'Manual procedures copied from inline source Check Text; full OCIL logic not assessed.']}
            blocked=False
            for rec in rs:
                split_path=args.split_root/'rules'/rec['source_rule_id']/'oval.xml'
                if split_path.exists():
                    original=ET.parse(split_path).getroot()
                else:
                    original=ET.Element('{'+review.OD+'}oval_definitions')
                    for name in ('definitions','tests','objects','states','variables'):
                        ET.SubElement(original,'{'+review.OD+'}'+name)
                result,failed_rule=review.convert_rule(
                    rec,original,args.output,schema,temp,
                    parameter_ids=parameter_ids,
                    assessment_namespace=args.benchmark_id,
                )
                evidence['rules'].append(result); blocked=blocked or failed_rule
            quarantined=sum(
                len(row.get('source_defect_fallbacks',[]))
                for row in evidence['rules']
            )
            evidence['source_defect_quarantine_count']=quarantined
            evidence['status']=(
                'blocked' if blocked
                else 'converted_with_source_defect_quarantine'
                if quarantined
                else 'prototype_dataflow_and_roundtrip_checks_passed'
            )
            write_json(args.output/'evidence.json',evidence)
            if blocked: raise ValueError('Assessment conversion blocked; see evidence.json')
        else:
            rule_list=temp/'rules.json'
            write_json(rule_list,[r['id'] for r in rs])
            status=review.main(['--input',str(args.input),'--sha256',actual_sha256,'--output',str(args.output),
                                '--rules-file',str(rule_list),'--schema',str(args.schema)])
            evidence=json.loads((args.output/'evidence.json').read_text(encoding='utf-8'))
            if status:
                blocked_rows=[]
                unexpected=[]
                for row in evidence.get('rules',[]):
                    for assessment in row.get('assessments',[]):
                        if assessment.get('status')!='blocked':
                            continue
                        unsupported=assessment.get('unsupported') or []
                        reason=review.source_defect_features_reason(unsupported)
                        if reason and row.get('selectors',{}).get('manual'):
                            blocked_rows.append({
                                'rule_id':row.get('rule_id'),
                                'source_definition':assessment.get('source_definition'),
                                'reason':reason,
                                'unsupported':unsupported,
                                'manual_assessment':row['selectors']['manual'],
                            })
                        else:
                            unexpected.append({
                                'rule_id':row.get('rule_id'),
                                'assessment':assessment,
                            })
                if unexpected or not blocked_rows:
                    raise ValueError('Assessment conversion blocked; see evidence.json')
                evidence['source_defect_quarantine_count']=len(blocked_rows)
                evidence['source_defect_quarantine']=blocked_rows
                evidence['status']='converted_with_source_defect_quarantine'
                write_json(args.output/'evidence.json',evidence)
        results={r['rule_id']:r for r in evidence['rules']}
        if args.split_root:
            app_split=args.split_root/'applicability'/'oval.xml'
            app_oval=ET.parse(app_split).getroot() if app_split.exists() else ET.Element('{'+review.OD+'}oval_definitions')
        else:
            app_oval=oval
        original_path=temp/'original-applicability.xml'; ET.ElementTree(app_oval).write(original_path,encoding='utf-8')
        predicates,dictionary=platform_sources(args.input)
        split_platform_definitions={}
        split_inventory={}
        if args.split_root:
            split_manifest_path=args.split_root/'manifest.json'
            if split_manifest_path.exists():
                split_manifest=json.loads(split_manifest_path.read_text(encoding='utf-8'))
                split_inventory={row.get('cpe_name'):row for row in split_manifest.get('cpe_inventory',[])
                                 if row.get('cpe_name') and row.get('status')=='split_valid'}
            provenance_path=args.split_root/'applicability'/'provenance.json'
            if provenance_path.exists():
                provenance_doc=json.loads(provenance_path.read_text(encoding='utf-8'))
                for row in provenance_doc.get('checks',[]):
                    platform_id=(row.get('platform_id') or '').lstrip('#')
                    definition_id=row.get('definition_id') or row.get('name')
                    if platform_id and definition_id:
                        prior=split_platform_definitions.get(platform_id)
                        if prior and prior!=definition_id:
                            raise ValueError('Conflicting split applicability binding: '+platform_id)
                        split_platform_definitions[platform_id]=definition_id
        referenced={ref.lstrip('#') for r in rs for ref in r['platforms']}
        referenced.update(n.get('idref').lstrip('#') for n in xr.findall('x:platform',source.NS))
        app_ids={}; app_evidence=[]; registry={}; blocked_applicability={}
        for ref in sorted(referenced):
            negate=False
            if ref in predicates:
                node=predicates[ref];did=split_platform_definitions.get(ref) or source.source_platform_definition_id(node)
                logical=next(n for n in node if source.local(n.tag)=='logical-test')
                negate=(logical.get('negate') or 'false') in ('true','1')
                title=source.text(next((n for n in node if source.local(n.tag)=='title'),None))
                app_id=args.benchmark_id+'.condition.'+source.semantic_id(title,'applicability')
            elif ref in dictionary:
                node=dictionary[ref];checks=[n for n in node if source.local(n.tag)=='check']
                if len(checks)!=1: raise ValueError('Unsupported dictionary binding')
                did=source.text(checks[0]);title=source.text(next((n for n in node if source.local(n.tag)=='title'),None))
                # CPE names are the stable source identity. Human titles are
                # presentation metadata and are not unique (for example the
                # Windows Server 2012 / 2012 R2 dictionary entries).
                app_id=args.benchmark_id+'.'+cpe_applicability_id(ref)
            else: raise ValueError('Unresolved applicability source: '+ref)
            if not did or app_id in registry: raise ValueError('Missing or colliding applicability identity: '+ref)
            definition_oval=app_oval
            definition_original_path=original_path
            inventory_row=split_inventory.get(ref)
            if inventory_row is None and ref in dictionary:
                inventory_row=split_inventory.get(dictionary[ref].get('name'))
            if inventory_row:
                did=inventory_row.get('definition_id') or did
                inventory_path=args.split_root/inventory_row['path']
                definition_oval=ET.parse(inventory_path).getroot()
                definition_original_path=temp/('inventory-'+source.safe_id(ref)+'.xml')
                ET.ElementTree(definition_oval).write(definition_original_path,encoding='utf-8')
            unsupported=source.unsupported_definition_features(definition_oval,did)
            if unsupported:
                deprecated_only=all(x.get('feature')=='deprecated_oval_test' for x in unsupported)
                if deprecated_only:
                    blocked_applicability[ref]={
                        'native_condition':app_id,
                        'source_definition':did,
                        'unsupported':unsupported,
                        'reason':'deprecated_oval_test',
                    }
                    app_ids[ref]=None
                    app_evidence.append({
                        'source_platform':ref,
                        'native_condition':app_id,
                        'source_definition':did,
                        'status':'skipped_deprecated_oval_test_manual_fallback',
                        'unsupported':unsupported,
                    })
                    continue
                defect=review.source_defect_features_reason(unsupported)
                if defect:
                    defect_error=defect+":"+json.dumps(unsupported,sort_keys=True,separators=(",",":"))
                    blocked_applicability[ref]={
                        'native_condition':app_id,
                        'source_definition':did,
                        'unsupported':unsupported,
                        'classification':'source_content_defect',
                        'reason':defect,
                        'error':defect_error,
                    }
                    app_ids[ref]=None
                    app_evidence.append({
                        'source_platform':ref,
                        'native_condition':app_id,
                        'source_definition':did,
                        'status':'skipped_source_defect_applicability',
                        'classification':'source_content_defect',
                        'reason':defect,
                        'unsupported':unsupported,
                    })
                    continue
                raise ValueError('Applicability source blocked: '+str(unsupported))
            provenance={};native,error=source.lower_definition(definition_oval,did,app_id+'.assessment',collection_graph=True,provenance=provenance)
            if error:
                defect=review.source_defect_reason(error)
                if defect:
                    blocked_applicability[ref]={
                        'native_condition':app_id,
                        'source_definition':did,
                        'classification':'source_content_defect',
                        'reason':defect,
                        'error':error,
                    }
                    app_ids[ref]=None
                    app_evidence.append({
                        'source_platform':ref,
                        'native_condition':app_id,
                        'source_definition':did,
                        'status':'skipped_source_defect_applicability',
                        'classification':'source_content_defect',
                        'reason':defect,
                        'error':error,
                    })
                    continue
                raise ValueError('Applicability: '+str(error))
            tree,new_id=build(native);schema.assertValid(etree.fromstring(ET.tostring(tree.getroot())))
            reverse=temp/'reverse.xml';tree.write(reverse,encoding='utf-8')
            parity=compare(definition_original_path,reverse,did,new_id,root_only=True)
            if not parity['equal']: raise ValueError('Applicability round-trip mismatch: '+app_id)
            # Compare the source definition before applying the separate source-platform negation.
            if negate: native['assessment']['evaluate']={'not':native['assessment']['evaluate']}
            native['assessment']['purpose']='applicability';native['assessment']['assessment_title']=title
            native=align_assessment_vocabulary(native)
            native=apply_ready_capability_mappings(
                native, review.NATIVE_CAPABILITY_MAPPING_DIR
            )
            errors=violations(native)
            if errors: raise ValueError('Current vocabulary guard: '+str(errors))
            path='assessments/applicability/'+app_id+'.assessment.yaml'
            review.write_yaml(args.output/path,native)
            registry[app_id]={'assessment':path};app_ids[ref]=app_id
            app_evidence.append({'source_platform':ref,'native_condition':app_id,'source_definition':did,
                                 'negate':negate,'source_graph_bindings':provenance,'definition_comparator_equal':True,
                                 'reverse_omni_schema_valid':True})
        for rec in rs:
            rid=rec['id'];element=rec['element'];result=results[rid]
            choices={key:{'assessment':'../'+ref} for key,ref in result['selectors'].items()}
            source_selectors=[(c.get('selector') or '').strip() or 'default' for c in rec['checks']]
            if len(source_selectors)!=len(set(source_selectors)): raise ValueError('Duplicate Rule selector: '+rid)
            blocked_refs=[x.lstrip('#') for x in rec['platforms'] if x.lstrip('#') in blocked_applicability]
            if blocked_refs:
                manual_ref=(
                    result['selectors'].get('manual')
                    or result.get('manual_fallback_assessment')
                    or result.get('source_defect_manual_fallback_assessment')
                )
                if not manual_ref:
                    raise ValueError('Blocked applicability requires source manual fallback for '+rid)
                choices={'default':{'assessment':'../'+manual_ref},'manual':{'assessment':'../'+manual_ref}}
                blocked_rows=[blocked_applicability[x] for x in blocked_refs]
                reasons=sorted({row.get('classification') or row.get('reason') for row in blocked_rows})
                result['applicability_manual_fallback']={
                    'source_platforms':blocked_refs,
                    'reasons':reasons,
                    'manual_assessment':manual_ref,
                }
                deprecated_refs=[x for x in blocked_refs if blocked_applicability[x].get('reason')=='deprecated_oval_test']
                defect_refs=[x for x in blocked_refs if blocked_applicability[x].get('classification')=='source_content_defect']
                if deprecated_refs:
                    existing={row['selector'] for row in result.get('manual_fallbacks',[])}
                    for selector in source_selectors:
                        if selector!='manual' and selector not in existing:
                            result.setdefault('manual_fallbacks',[]).append({
                                'selector':selector,
                                'source_definition':None,
                                'unsupported':[{
                                    'feature':'deprecated_oval_test',
                                    'detail':'Rule applicability uses a deprecated OVAL Test',
                                }],
                                'reason':'deprecated_applicability',
                            })
                if defect_refs:
                    existing={row['selector'] for row in result.get('source_defect_fallbacks',[])}
                    for selector in source_selectors:
                        if selector!='manual' and selector not in existing:
                            first=blocked_applicability[defect_refs[0]]
                            result.setdefault('source_defect_fallbacks',[]).append({
                                'selector':selector,
                                'source_definition':first.get('source_definition'),
                                'classification':'source_content_defect',
                                'reason':first.get('reason'),
                                'error':first.get('error'),
                                'context':'applicability',
                            })
                    result['source_defect_manual_fallback_assessment']=manual_ref
            default='default' if 'default' in choices else next(iter(choices),None)
            if default is None: raise ValueError('Rule has no Assessment: '+rid)
            content=source.rule_content(element)
            extensions={key:content.pop(key,None) for key in ('documentable','false_positives','false_negatives','mitigations','potential_impacts','responsibility')}
            for key in ('requires','conflicts'):
                if set(rec[key])-set(by_source): raise ValueError('Unresolved Rule dependency: '+rid)
            rule={'id':rid,'version':rec['version'],'title':rec['title'],'severity':rec['severity'],
                  'role':rec['role'] or 'full','weight':float(rec['weight'] or '1'),
                  'discussion':content.get('discussion'),'rationale':content.get('rationale'),
                  'extensions':{'disa_stig':extensions},'warnings':content.get('warnings',[]),
                  'identifiers':[{'scheme':'stig','value':rec['stig_id']},
                                 {'scheme':'vulnerability','value':rec['vulnerability_id']}]+content.get('identifiers',[]),
                  'references':content.get('references',[]),'requires':[by_source[x] for x in rec['requires']],
                  'conflicts':[by_source[x] for x in rec['conflicts']],
                  'applicability':[app_ids[x.lstrip('#')] for x in rec['platforms'] if app_ids.get(x.lstrip('#'))],
                  'parameters':{},'remediation':content.get('remediation'),
                  'organizational_input_requirements':{},
                  'assessment_choices':choices,'default_assessment_choice':default}
            review.write_yaml(args.output/'rules'/f'{rid}.rule.yaml',{'rule':rule})
            result['source_selection']={'rule_selected':element.get('selected'),
                                        'effective_default':baseline[rid],'source_group_ancestry':ancestry[rid]}
            result['source_attributes']={key:{'explicit':element.get(key),'effective':rule[key]}
                                         for key in ('role','weight')}
            result['default_selector']=default
        metadata,unsupported=source.benchmark_metadata(xr)
        if unsupported: raise ValueError('Unsupported Benchmark metadata: '+str(unsupported))
        front,_=source.normalize_front_matter(xr);rear,_=source.normalize_rear_matter(xr)
        groups,grouping=source.build_groups(rs);version=xr.find('x:version',source.NS)
        # Keep Benchmark discovery metadata aligned with each automated Assessment.
        # The identifier is explicitly provisional until the OVAL Board adopts
        # the successor specification identity.
        benchmark={'id':args.benchmark_id,'ng_schema_version':None,'use_case':'compliance',
                   'assessment_specifications':[{'id':WORKING_ASSESSMENT_SPECIFICATION_ID,'version':WORKING_ASSESSMENT_SPECIFICATION_VERSION}],
                   'title':source.localized_texts(xr,'title'),'description':source.localized_texts(xr,'description'),
                   'language':xr.get('{http://www.w3.org/XML/1998/namespace}lang'),
                   'status':source.benchmark_status(xr),'version':{'value':source.text(version),'time':version.get('time'),'update':version.get('update')},
                   'metadata':metadata,'notices':source.benchmark_notices(xr),'front_matter':front,'rear_matter':rear,
                   'references':source.benchmark_references(xr),'text_blocks':source.benchmark_text_blocks(xr),
                   'platform':{'id':args.platform_id,'title':args.platform_title,
                               'applicability':{'operator':'any','conditions':[app_ids[n.get('idref').lstrip('#')] for n in xr.findall('x:platform',source.NS) if app_ids.get(n.get('idref').lstrip('#'))]}},
                   'applicability_catalog':'applicability.yaml','scoring':source.benchmark_scoring(xr),
                   'parameters':parameters,'default_selection':next(iter(baseline.values())),
                   'groups':groups,'profiles':profiles,'rules':[r['id'] for r in rs]}
        review.write_yaml(args.output/'benchmark.yaml',{'benchmark':benchmark})
        review.write_yaml(args.output/'applicability.yaml',{'applicability':{'id':args.benchmark_id+'.applicability','conditions':registry}})
        parity=audit(args.input,args.output/'benchmark.yaml')
        if parity['issues']: raise ValueError('Profile selection mismatch: '+str(parity['issues']))
        write_json(args.output/'profile-selection-audit.json',parity)
        from scap_upconvert_v003.audit_full_review import audit as audit_rules
        rule_parity=audit_rules(args.input,args.output)
        if rule_parity['issues']: raise ValueError('Rule source audit failed: '+str(rule_parity['issues']))
        write_json(args.output/'rule-source-audit.json',rule_parity)
        write_json(args.output/'profile-selection-provenance.json',selection_evidence)
        write_json(args.output/'grouping-provenance.json',grouping)
        write_json(args.output/'applicability-evidence.json',app_evidence)
        validation=validate_native_tree(args.output)
        write_json(args.output/'validation.json',validation)
        evidence['status']='full_research_review_structural_and_representation_checks_passed'
        evidence['limits']=['Prototype grammar: capability binding and quantifier vocabulary remain pending.',
                            'Representation equality and schema validation do not prove target runtime equivalence.',
                            'Manual procedures copied from inline source Check Text; full OCIL logic not assessed.',
                            'ng_schema_version remains null until an NG schema is assigned.',
                            'Platform execution evidence is recorded separately by CI.']
        evidence['profile_rule_comparisons']=len(rs)*len(profiles)
        evidence['applicability_conditions']=len(registry)
        evidence['blocked_applicability']=list(blocked_applicability.values())
        evidence['source_revision']=source.SOURCE_REVISION
        evidence['source_sha256']=actual_sha256
        write_json(args.output/'evidence.json',evidence)
    print(json.dumps({'status':evidence['status'],'rules':len(rs),'profiles':len(profiles),
                      'applicability':len(registry),'yaml_files':validation['yaml_files']},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
