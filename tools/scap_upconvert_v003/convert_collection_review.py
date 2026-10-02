#!/usr/bin/env python3
"""Local, source-driven Assessment review conversion; NOT a full Benchmark compiler.

Windows-compatible Python entry point. No downloads, shell helpers or GitHub
credentials. Capability placement/quantifier spelling are prototype syntax.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scap_upconvert_v003.build_rhel9_review_slice import (
    NS, local, records, lower_definition, check_kind, text,
    unsupported_definition_features)
from scap_ng_roundtrip_v003.native_assessment_to_oval import build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare, OD
from check_current_authoring_contract import violations
from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary
import yaml

def source_benchmark(package):
    benchmarks=[]
    with zipfile.ZipFile(package) as z:
        for name in sorted(z.namelist()):
            if not name.lower().endswith('.xml'): continue
            root=ET.fromstring(z.read(name))
            for node in root.iter():
                if local(node.tag)=='Benchmark': benchmarks.append(node)
    if len(benchmarks)!=1: raise ValueError('Expected one source Benchmark')
    return benchmarks[0]

def source_components(package):
    benchmarks=[];oval=[]
    with zipfile.ZipFile(package) as z:
        for name in sorted(z.namelist()):
            if not name.lower().endswith('.xml'):continue
            root=ET.fromstring(z.read(name))
            for node in root.iter():
                if local(node.tag)=='Benchmark':benchmarks.append(node)
                elif local(node.tag)=='oval_definitions':oval.append(node)
    if len(benchmarks)!=1: raise ValueError('Expected one source Benchmark')
    combined=ET.Element('{'+OD+'}oval_definitions')
    sections={name:ET.SubElement(combined,'{'+OD+'}'+name) for name in ('definitions','tests','objects','states','variables')}
    seen={}
    for root in oval:
        for section in root:
            if local(section.tag) not in sections:continue
            for node in section:
                identity=node.get('id')
                raw=ET.tostring(node)
                if identity in seen:
                    if seen[identity]!=raw:raise ValueError('Conflicting source identity: '+identity)
                    continue
                seen[identity]=raw
                sections[local(section.tag)].append(deepcopy(node))
    return benchmarks[0],combined

def write_yaml(path,doc):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(yaml.safe_dump(doc,sort_keys=False,allow_unicode=True,width=110),encoding='utf-8')

def manual_procedure(rec, c):
    source_ref=c.find('x:check-content-ref',NS)
    binding=(c.get('system'),source_ref.get('href'),source_ref.get('name')) if source_ref is not None else None
    procedure=text(c.find('x:check-content',NS))
    candidates=[text(other.find('x:check-content',NS)) for other in rec['checks']
                if binding is not None and other.get('system')==binding[0]
                and other.find('x:check-content-ref',NS) is not None
                and (other.find('x:check-content-ref',NS).get('href'),
                     other.find('x:check-content-ref',NS).get('name'))==binding[1:]]
    procedures={value for value in candidates if value}
    if len(procedures)>1: raise ValueError(rec['id']+': conflicting procedures for shared manual source binding')
    procedure=procedure or next(iter(procedures),None)
    if not procedure: raise ValueError(rec['id']+': manual source has no verified inline procedure')
    return binding, procedure


SOURCE_DEFECT_ERROR_PREFIXES = (
    "invalid_oval_record_datatype",
    "test_collection_capability_mismatch:",
    "test_state_capability_mismatch:",
    "Filter capability mismatch:",
)


def source_defect_reason(error):
    """Return a stable source-defect class for positively identified bad OVAL.

    Unknown conversion errors deliberately return None and remain hard blockers.
    The Collection-graph validator may wrap a lower-level semantic mismatch;
    unwrap only that known envelope before applying the narrow allowlist.
    """
    if not isinstance(error, str):
        return None
    detail=error
    prefix="collection_graph_type_binding:"
    if detail.startswith(prefix):
        detail=detail[len(prefix):]
    if detail == "invalid_oval_record_datatype":
        return "invalid_oval_record_datatype"
    if detail.startswith("test_collection_capability_mismatch:"):
        return "test_collection_capability_mismatch"
    if detail.startswith("test_state_capability_mismatch:"):
        return "test_state_capability_mismatch"
    if detail.startswith("Filter capability mismatch:"):
        return "filter_collection_capability_mismatch"
    return None


def source_defect_features_reason(features):
    """Classify positively identified source-invalid feature findings.

    Feature-level quarantine stays deliberately narrower than ordinary
    unsupported-feature handling.  OVAL 5.12.3 Schematron explicitly requires
    an entity var_ref datatype to match its referenced Variable datatype.
    """
    if not features:
        return None
    names={item.get("feature") for item in features}
    if names == {"var_ref_datatype_mismatch"}:
        return "var_ref_datatype_mismatch"
    return None


def source_defect_fallback(selector, did, error):
    return {
        "selector": selector,
        "source_definition": did,
        "classification": "source_content_defect",
        "reason": source_defect_reason(error),
        "error": error,
    }

def convert_rule(rec, original, output, schema, temp_root, parameter_ids=None):
    from lxml import etree
    rid=rec['id']
    result={'rule_id':rid,'title':rec['title'],'selectors':{},'assessments':[]}
    done={}; manual_done={}; deprecated_selector_fallbacks=[]; source_defect_selector_fallbacks=[]
    has_manual=any(check_kind(check)=='manual' for check in rec['checks'])
    original_path=Path(temp_root)/(rid+'-source.xml')
    ET.ElementTree(original).write(original_path,encoding='utf-8')
    failed=False
    for c in rec['checks']:
        selector=(c.get('selector') or '').strip() or 'default'
        if check_kind(c)=='manual':
            binding,procedure=manual_procedure(rec,c)
            key=binding or ('inline',procedure)
            if key in manual_done:
                result['selectors'][selector]=manual_done[key]; continue
            aid=rid+'.manual'+('' if not manual_done else '-'+str(len(manual_done)+1))
            ref='assessments/manual/'+aid+'.assessment.yaml'
            write_yaml(output/ref,{'assessment':{'id':aid,'version':1,'assessment_title':rec['title'],'mode':'manual',
                'purpose':'assessment','class':'compliance','procedure':procedure,'inputs':{},'evidence':[]}})
            manual_done[key]=ref
            result.setdefault('manual_source_bindings',[]).append({'path':ref,'source_binding':binding,
                'procedure_origin':'matching shared source binding' if not text(c.find('x:check-content',NS)) else 'inline check text'})
            result['selectors'][selector]=ref
            continue
        source_ref=c.find('x:check-content-ref',NS)
        did=source_ref.get('name')
        if did in done:
            result['selectors'][selector]=done[did]; continue
        aid=rid+'.automated'+('' if not done else '-'+str(len(done)+1))
        provenance={}
        unsupported=unsupported_definition_features(original,did)
        if unsupported:
            deprecated_only=all(x.get('feature')=='deprecated_oval_test' for x in unsupported)
            if deprecated_only and has_manual:
                deprecated_selector_fallbacks.append({'selector':selector,'source_definition':did,'unsupported':unsupported})
                result['assessments'].append({'status':'skipped_deprecated_oval_test_manual_fallback',
                                              'source_definition':did,'unsupported':unsupported})
                continue
            defect=source_defect_features_reason(unsupported)
            if defect and has_manual:
                error=defect+":"+json.dumps(unsupported,sort_keys=True,separators=(",",":"))
                source_defect_selector_fallbacks.append(source_defect_fallback(selector,did,error))
                result['assessments'].append({
                    'status':'skipped_source_defect_manual_fallback',
                    'source_definition':did,
                    'classification':'source_content_defect',
                    'reason':defect,
                    'unsupported':unsupported,
                })
                continue
            failed=True; result['assessments'].append({'status':'blocked','source_definition':did,'unsupported':unsupported}); continue
        external_bindings={}
        for export in c.findall('x:check-export',NS):
            source_variable=export.get('export-name')
            source_value=export.get('value-id')
            if not source_variable or not source_value:
                failed=True
                result['assessments'].append({'status':'blocked','error':'invalid_xccdf_check_export'})
                external_bindings=None
                break
            if parameter_ids is None or source_value not in parameter_ids:
                failed=True
                result['assessments'].append({
                    'status':'blocked',
                    'error':'unresolved_xccdf_value_binding:'+source_value,
                })
                external_bindings=None
                break
            external_bindings[source_variable]=parameter_ids[source_value]
        if external_bindings is None:
            continue
        native,error=lower_definition(
            original,did,aid,collection_graph=True,provenance=provenance,
            external_bindings=external_bindings,
        )
        if error:
            defect=source_defect_reason(error)
            if defect and has_manual:
                fallback=source_defect_fallback(selector,did,error)
                source_defect_selector_fallbacks.append(fallback)
                result['assessments'].append({
                    'status':'skipped_source_defect_manual_fallback',
                    'source_definition':did,
                    'classification':'source_content_defect',
                    'reason':defect,
                    'error':error,
                })
                continue
            failed=True; result['assessments'].append({'status':'blocked','error':error}); continue
        # Round-trip the semantic intermediate before presentation vocabulary
        # alignment so legacy parity evidence remains independent of the native
        # naming decision.
        tree,new_id=build(native); schema.assertValid(etree.fromstring(ET.tostring(tree.getroot())))
        regenerated=Path(temp_root)/(rid+'-'+aid.replace('.','-')+'.xml'); tree.write(regenerated,encoding='utf-8')
        parity=compare(original_path,regenerated,did,new_id,root_only=True)
        if not parity['equal']:
            failed=True; result['assessments'].append({'status':'blocked','parity':parity}); continue
        native=align_assessment_vocabulary(native)
        errors=violations(native)
        if errors: raise ValueError('Current vocabulary guard: '+str(errors))
        ref='assessments/automated/'+aid+'.assessment.yaml'
        write_yaml(output/ref,native); done[did]=ref; result['selectors'][selector]=ref
        result['assessments'].append({'status':'representation_comparator_equal','path':ref,
            'source_graph_bindings':provenance,'tests':len(native['assessment']['tests']),
            'objects':len(native['assessment']['objects']),
            'states':len(native['assessment'].get('states',{})),
            'variables':len(native['assessment'].get('variables',{})),'reverse_omni_schema_valid':True})
    if deprecated_selector_fallbacks:
        manual_ref=result['selectors'].get('manual') or (next(iter(manual_done.values())) if manual_done else None)
        if manual_ref is None:
            failed=True; result.setdefault('errors',[]).append('deprecated automated source has no usable manual fallback')
        else:
            for fallback in deprecated_selector_fallbacks:
                if fallback['selector']=='default': result['selectors']['default']=manual_ref
            result['manual_fallbacks']=deprecated_selector_fallbacks
            result['manual_fallback_assessment']=manual_ref
    if source_defect_selector_fallbacks:
        manual_ref=result['selectors'].get('manual') or (next(iter(manual_done.values())) if manual_done else None)
        if manual_ref is None:
            failed=True
            result.setdefault('errors',[]).append('source-invalid automated Assessment has no usable manual fallback')
        else:
            for fallback in source_defect_selector_fallbacks:
                if fallback['selector']=='default':
                    result['selectors']['default']=manual_ref
            result.setdefault('source_defect_fallbacks',[]).extend(source_defect_selector_fallbacks)
            result['source_defect_manual_fallback_assessment']=manual_ref
    return result, failed

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rule',action='append',default=[])
    p.add_argument('--rules-file',type=Path)
    p.add_argument('--schema',type=Path,default=Path(__file__).resolve().parents[2]/'third_party/scap-1.4-schemas/omni-schema.xsd')
    args=p.parse_args(argv)
    digest=hashlib.sha256(args.input.read_bytes()).hexdigest()
    if digest!=args.sha256:raise SystemExit('Source archive checksum mismatch')
    wanted=set(args.rule)
    if args.rules_file:
        data=json.loads(args.rules_file.read_text(encoding='utf-8'))
        wanted.update(data if isinstance(data,list) else data['summary']['selected_rules'])
    if not wanted:raise SystemExit('Select explicit Rules for the review; full regeneration is held')
    if args.output.exists() and any(args.output.iterdir()):raise SystemExit('Output directory must be new or empty')
    args.output.mkdir(parents=True,exist_ok=True)
    xr,original=source_components(args.input)
    all_records={r['id']:r for r in records(xr)}
    if wanted-set(all_records):raise SystemExit('Unknown Rule IDs: '+str(sorted(wanted-set(all_records))))
    evidence={'status':'prototype_collection_graph_review','source_sha256':digest,
              'rules':[],'limits':['Assessment/dataflow review only; not a full Benchmark/Rule renderer.',
                                  'Variable collection_capabilities binding and item_quantifier spelling remain review candidates.',
                                  'Round-trip equality is representation evidence, not scanner execution equivalence.',
                                  'Windows execution not yet performed.',
                                  'Manual procedures copied from inline source Check Text; full OCIL logic not assessed.']}
    from lxml import etree
    schema=etree.XMLSchema(etree.parse(str(args.schema)))
    evidence['reverse_validation_schema_sha256']=hashlib.sha256(args.schema.read_bytes()).hexdigest()
    failed=False
    with tempfile.TemporaryDirectory() as tmp:
        original_path=Path(tmp)/'source.xml';ET.ElementTree(original).write(original_path,encoding='utf-8')
        for rid in sorted(wanted):
            rec=all_records[rid]
            result={'rule_id':rid,'title':rec['title'],'selectors':{},'assessments':[]}
            done={}
            manual_done={}
            deprecated_selector_fallbacks=[]
            source_defect_selector_fallbacks=[]
            has_manual=any(check_kind(check)=='manual' for check in rec['checks'])
            for c in rec['checks']:
                selector=(c.get('selector') or '').strip() or 'default'
                if check_kind(c)=='manual':
                    binding,procedure=manual_procedure(rec,c)
                    key=binding or ('inline',procedure)
                    if key in manual_done:
                        result['selectors'][selector]=manual_done[key]
                        continue
                    aid=rid+'.manual'+('' if not manual_done else '-'+str(len(manual_done)+1))
                    ref='assessments/manual/'+aid+'.assessment.yaml'
                    write_yaml(args.output/ref,{'assessment':{'id':aid,'version':1,'assessment_title':rec['title'],'mode':'manual',
                        'purpose':'assessment','class':'compliance','procedure':procedure,
                        'inputs':{},'evidence':[]}})
                    manual_done[key]=ref
                    result.setdefault('manual_source_bindings',[]).append({'path':ref,'source_binding':binding,
                        'procedure_origin':'matching shared source binding' if not text(c.find('x:check-content',NS)) else 'inline check text'})
                    result['selectors'][selector]=ref
                    continue
                source_ref=c.find('x:check-content-ref',NS)
                did=source_ref.get('name')
                if did in done:
                    result['selectors'][selector]=done[did]
                    continue
                aid=rid+'.automated'+('' if not done else '-'+str(len(done)+1))
                provenance={}
                unsupported=unsupported_definition_features(original,did)
                if unsupported:
                    deprecated_only=all(x.get('feature')=='deprecated_oval_test' for x in unsupported)
                    if deprecated_only and has_manual:
                        deprecated_selector_fallbacks.append({
                            'selector': selector,
                            'source_definition': did,
                            'unsupported': unsupported,
                        })
                        result['assessments'].append({
                            'status':'skipped_deprecated_oval_test_manual_fallback',
                            'source_definition':did,
                            'unsupported':unsupported,
                        })
                        continue
                    failed=True;result['assessments'].append({'status':'blocked','source_definition':did,'unsupported':unsupported});continue
                native,error=lower_definition(original,did,aid,collection_graph=True,provenance=provenance)
                if error:
                    defect=source_defect_reason(error)
                    if defect and has_manual:
                        fallback=source_defect_fallback(selector,did,error)
                        source_defect_selector_fallbacks.append(fallback)
                        result['assessments'].append({
                            'status':'skipped_source_defect_manual_fallback',
                            'source_definition':did,
                            'classification':'source_content_defect',
                            'reason':defect,
                            'error':error,
                        })
                        continue
                    failed=True;result['assessments'].append({'status':'blocked','error':error});continue
                tree,new_id=build(native)
                schema.assertValid(etree.fromstring(ET.tostring(tree.getroot())))
                regenerated=Path(tmp)/(rid+'.xml');tree.write(regenerated,encoding='utf-8')
                parity=compare(original_path,regenerated,did,new_id,root_only=True)
                if not parity['equal']:
                    failed=True;result['assessments'].append({'status':'blocked','parity':parity});continue
                native=align_assessment_vocabulary(native)
                errors=violations(native)
                if errors:raise ValueError('Current vocabulary guard: '+str(errors))
                ref='assessments/automated/'+aid+'.assessment.yaml'
                write_yaml(args.output/ref,native)
                done[did]=ref;result['selectors'][selector]=ref
                result['assessments'].append({'status':'representation_comparator_equal',
                    'path':ref,'source_graph_bindings':provenance,
                    'tests':len(native['assessment']['tests']),
                    'objects':len(native['assessment']['objects']),
                    'states':len(native['assessment'].get('states',{})),
                    'variables':len(native['assessment'].get('variables',{})),
                    'reverse_omni_schema_valid':True})
            if deprecated_selector_fallbacks:
                manual_ref=result['selectors'].get('manual')
                if manual_ref is None and manual_done:
                    manual_ref=next(iter(manual_done.values()))
                if manual_ref is None:
                    failed=True
                    result.setdefault('errors',[]).append('deprecated automated source has no usable manual fallback')
                else:
                    for fallback in deprecated_selector_fallbacks:
                        if fallback['selector']=='default':
                            result['selectors']['default']=manual_ref
                    result['manual_fallbacks']=deprecated_selector_fallbacks
                    result['manual_fallback_assessment']=manual_ref
            if source_defect_selector_fallbacks:
                manual_ref=result['selectors'].get('manual')
                if manual_ref is None and manual_done:
                    manual_ref=next(iter(manual_done.values()))
                if manual_ref is None:
                    failed=True
                    result.setdefault('errors',[]).append('source-invalid automated Assessment has no usable manual fallback')
                else:
                    for fallback in source_defect_selector_fallbacks:
                        if fallback['selector']=='default':
                            result['selectors']['default']=manual_ref
                    result.setdefault('source_defect_fallbacks',[]).extend(source_defect_selector_fallbacks)
                    result['source_defect_manual_fallback_assessment']=manual_ref
            evidence['rules'].append(result)
    evidence['status']='blocked' if failed else 'prototype_dataflow_and_roundtrip_checks_passed'
    (args.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':evidence['status'],'rules':len(wanted),
        'automated_assessments':sum(len(r['assessments']) for r in evidence['rules']),
        'source_sha256':digest},indent=2))
    return 1 if failed else 0

if __name__=='__main__':raise SystemExit(main())
