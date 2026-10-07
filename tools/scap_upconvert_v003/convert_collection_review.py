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
from scap_upconvert_v003.native_capability_mapping import apply_ready_capability_mappings
from scap_upconvert_v003.foreach_modernization import modernize_foreach_v1
from scap_upconvert_v003.conditional_modernization import modernize_conditionals_v1
from validate_generated_capability_semantics import validate_assessment_capability_semantics
from scap14_rule_splitter import (
    find_datastream, embedded_components, oval_source_roots,
    resolve_oval_components, OvalComponent, component_kind,
)
import yaml

ROOT = Path(__file__).resolve().parents[2]
NATIVE_CAPABILITY_MAPPING_DIR = (
    ROOT / "schema/v0.2.0/capability-mappings/supported"
)


def capability_mapping_dir(version):
    if version not in {"0.2.0", "0.3.0"}:
        raise ValueError(f"Unsupported target SCAP-NG version: {version}")
    return ROOT / f"schema/v{version}/capability-mappings/supported"


def postprocess_automated_assessment(
    native,
    *,
    target_ng_version="0.2.0",
    modernize_foreach=False,
    modernize_conditionals=False,
):
    """Apply versioned native mappings and optional 0.3 modernization passes.

    The default 0.2 path intentionally preserves the existing converter
    behavior. Modernization passes are legal only for an explicit 0.3 target.
    """
    if modernize_foreach and target_ng_version != "0.3.0":
        raise ValueError("--modernize-foreach-v1 requires target SCAP-NG 0.3.0")
    if modernize_conditionals and target_ng_version != "0.3.0":
        raise ValueError("--modernize-conditionals-v1 requires target SCAP-NG 0.3.0")

    result=align_assessment_vocabulary(native)
    assessment=result.get("assessment",{})
    specification=assessment.setdefault("specification",{
        "id":"scap-ng.pre-alpha.assessment",
        "version":target_ng_version,
    })
    if target_ng_version != "0.2.0":
        specification["version"]=target_ng_version

    # Both 0.2 and the current 0.3 draft require explicit reporting selection.
    # Preserve the complete SCAP 1.4/OVAL evidence surface during conversion.
    for test in assessment.get("tests",{}).values():
        test["reported_elements"]="all"

    result=apply_ready_capability_mappings(
        result,
        capability_mapping_dir(target_ng_version),
    )

    foreach_report=None
    conditional_report=None
    if modernize_foreach:
        result,foreach_report=modernize_foreach_v1(result,enabled=True)
        diagnostics=validate_assessment_capability_semantics(result)
        foreach_diagnostics=[
            row for row in diagnostics
            if str(row.get("code","")).startswith("foreach.")
        ]
        if foreach_diagnostics:
            raise ValueError(
                "foreach modernization semantic validation failed: "
                + repr(foreach_diagnostics)
            )

    if modernize_conditionals:
        result,conditional_report=modernize_conditionals_v1(result,enabled=True)

    if modernize_foreach and modernize_conditionals:
        modernization={
            "foreach":foreach_report,
            "conditional":conditional_report,
        }
    elif modernize_foreach:
        modernization=foreach_report
    elif modernize_conditionals:
        modernization=conditional_report
    else:
        modernization=None

    return result,modernization

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

def source_rule_resolver(package):
    """Return the XCCDF Benchmark and an href-scoped OVAL document resolver.

    SCAP datastreams may reuse the same OVAL id in distinct components. XCCDF
    check-content-ref therefore identifies automated content by both href and
    Definition id; flattening all OVAL components into one namespace is unsafe.
    """
    from lxml import etree

    _, _, datastream = find_datastream(package)
    components, component_refs = embedded_components(datastream)
    benchmarks = [
        root for root in components.values()
        if component_kind(root) == "xccdf"
    ]
    if len(benchmarks) != 1:
        raise ValueError(
            f"Expected one embedded XCCDF Benchmark component, found {len(benchmarks)}"
        )
    oval_components = [
        OvalComponent(component_id, root)
        for component_id, root in oval_source_roots(package, components)
    ]
    if not oval_components:
        raise ValueError("No OVAL Definitions components found")

    cache = {}

    def resolve(href, definition_id):
        matches = resolve_oval_components(
            oval_components,
            definition_id,
            href,
            component_refs,
        )
        if len(matches) != 1:
            status = "unresolved" if not matches else "ambiguous"
            raise ValueError(
                f"{status} OVAL check-content-ref: href={href!r} "
                f"definition={definition_id!r} matches={len(matches)}"
            )
        component = matches[0]
        if component.component_id not in cache:
            cache[component.component_id] = ET.fromstring(
                etree.tostring(component.root, encoding="UTF-8")
            )
        return cache[component.component_id]

    benchmark = ET.fromstring(etree.tostring(benchmarks[0], encoding="UTF-8"))
    return benchmark, resolve


def write_yaml(path,doc):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(yaml.safe_dump(doc,sort_keys=False,allow_unicode=True,width=110),encoding='utf-8')

def manual_response_contract():
    """Return the native human response vocabulary for migrated compliance checks."""
    return {
        'type':'compliance',
        'choices':[
            {'value':'pass','label':'Pass','outcome':'true'},
            {'value':'fail','label':'Fail','outcome':'false'},
            {'value':'unknown','label':'Unknown','outcome':'unknown'},
            {'value':'not_applicable','label':'Not applicable','outcome':'not_applicable'},
        ],
        'allow_comment':True,
        'allow_evidence':True,
    }


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
    "var_ref_datatype_mismatch:",
    "invalid_textfilecontent54_pattern_operation:",
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
    if detail.startswith("var_ref_datatype_mismatch:"):
        return "var_ref_datatype_mismatch"
    if detail.startswith("invalid_textfilecontent54_pattern_operation:"):
        return "invalid_textfilecontent54_pattern_operation"
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
    if names == {"invalid_textfilecontent54_pattern_operation"}:
        return "invalid_textfilecontent54_pattern_operation"
    return None


def source_defect_fallback(selector, did, error):
    return {
        "selector": selector,
        "source_definition": did,
        "classification": "source_content_defect",
        "reason": source_defect_reason(error),
        "error": error,
    }

def scoped_assessment_id(namespace, local_id):
    """Return a repository-safe generated Assessment ID."""
    return f"{namespace}.{local_id}" if namespace else local_id


def convert_rule(
    rec,
    original,
    output,
    schema,
    temp_root,
    parameter_ids=None,
    assessment_namespace=None,
    target_ng_version="0.2.0",
    modernize_foreach=False,
    modernize_conditionals=False,
):
    """Convert one Rule while keeping generated Assessment identities repository-safe.

    assessment_namespace is a native Benchmark identity. When supplied, generated
    manual/automated Assessment IDs are scoped to that Benchmark. Semantic
    normalization intentionally ignores Assessment IDs, so exact cross-Benchmark
    reuse remains discoverable.
    """
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
            aid=scoped_assessment_id(assessment_namespace, rid+'.manual'+('' if not manual_done else '-'+str(len(manual_done)+1)))
            ref='assessments/manual/'+aid+'.assessment.yaml'
            write_yaml(output/ref,{'assessment':{'id':aid,'version':1,'assessment_title':rec['title'],'mode':'manual',
                'purpose':'assessment','class':'compliance','procedure':procedure,'response':manual_response_contract()}})
            manual_done[key]=ref
            result.setdefault('manual_source_bindings',[]).append({'path':ref,'source_binding':binding,
                'procedure_origin':'matching shared source binding' if not text(c.find('x:check-content',NS)) else 'inline check text'})
            result['selectors'][selector]=ref
            continue
        source_ref=c.find('x:check-content-ref',NS)
        did=source_ref.get('name')
        if did in done:
            result['selectors'][selector]=done[did]; continue
        aid=scoped_assessment_id(assessment_namespace, rid+'.automated'+('' if not done else '-'+str(len(done)+1)))
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
        try:
            native,modernization=postprocess_automated_assessment(
                native,
                target_ng_version=target_ng_version,
                modernize_foreach=modernize_foreach,
                modernize_conditionals=modernize_conditionals,
            )
        except ValueError as exc:
            mapping_error=str(exc)
            fallback_reason=None
            if mapping_error.startswith("deprecated source capability windows.wmi"):
                fallback_reason="deprecated_or_legacy_wmi_source"
            elif mapping_error.startswith("unsupported deprecated OVAL behavior semantics:"):
                fallback_reason="deprecated_oval_behavior"
            if fallback_reason and has_manual:
                source_defect_selector_fallbacks.append({
                    "selector":selector,
                    "source_definition":did,
                    "classification":"unsupported_automated_source",
                    "reason":fallback_reason,
                    "error":mapping_error,
                })
                result["assessments"].append({
                    "status":"skipped_unsupported_automated_manual_fallback",
                    "source_definition":did,
                    "classification":"unsupported_automated_source",
                    "reason":fallback_reason,
                    "error":mapping_error,
                })
                continue
            raise
        errors=violations(native)
        if errors: raise ValueError('Current vocabulary guard: '+str(errors))
        ref='assessments/automated/'+aid+'.assessment.yaml'
        write_yaml(output/ref,native); done[did]=ref; result['selectors'][selector]=ref
        assessment_row={'status':'representation_comparator_equal','path':ref,
            'source_graph_bindings':provenance,'tests':len(native['assessment']['tests']),
            'objects':len(native['assessment']['objects']),
            'states':len(native['assessment'].get('states',{})),
            'variables':len(native['assessment'].get('variables',{})),'reverse_omni_schema_valid':True}
        if modernize_foreach:
            assessment_row['foreach_modernization']=(
                modernization['foreach']
                if modernize_conditionals else modernization
            )
        if modernize_conditionals:
            assessment_row['conditional_modernization']=(
                modernization['conditional']
                if modernize_foreach else modernization
            )
        result['assessments'].append(assessment_row)
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

def aggregate_modernization_stats(evidence, *, foreach_enabled=False, conditional_enabled=False):
    """Aggregate per-Assessment modernization reports for machine-readable CI use."""
    stats = {
        "format": "scap-ng-modernization-stats-0.1",
        "foreach": None,
        "conditional": None,
    }

    assessment_rows = [
        assessment
        for rule in evidence.get("rules", [])
        for assessment in rule.get("assessments", [])
        if isinstance(assessment, dict)
    ]

    if foreach_enabled:
        totals = {
            "assessments_examined": 0,
            "assessments_rewritten": 0,
            "variables_total": 0,
            "direct_projection_variables_examined": 0,
            "rewrite_candidates_proven": 0,
            "rewrites_applied": 0,
            "review_required_variables": 0,
            "review_reason_counts": {},
        }
        for row in assessment_rows:
            report = row.get("foreach_modernization")
            if not isinstance(report, dict):
                continue
            totals["assessments_examined"] += 1
            if report.get("rewrite_performed"):
                totals["assessments_rewritten"] += 1
            local = report.get("stats") or {}
            for key in (
                "variables_total",
                "direct_projection_variables_examined",
                "rewrite_candidates_proven",
                "rewrites_applied",
                "review_required_variables",
            ):
                totals[key] += int(local.get(key, 0) or 0)
            for reason, count in (local.get("review_reason_counts") or {}).items():
                totals["review_reason_counts"][reason] = (
                    totals["review_reason_counts"].get(reason, 0) + int(count)
                )
        direct = totals["direct_projection_variables_examined"]
        totals["rewrite_rate_pct_of_direct_projections"] = (
            round(100.0 * totals["rewrites_applied"] / direct, 2)
            if direct else 0.0
        )
        totals["assessment_rewrite_rate_pct"] = (
            round(
                100.0
                * totals["assessments_rewritten"]
                / totals["assessments_examined"],
                2,
            )
            if totals["assessments_examined"] else 0.0
        )
        stats["foreach"] = totals

    if conditional_enabled:
        totals = {
            "assessments_examined": 0,
            "assessments_rewritten": 0,
            "expression_nodes_examined": 0,
            "branch_like_nodes_examined": 0,
            "rewrite_candidates_proven": 0,
            "rewrites_applied": 0,
            "review_required_nodes": 0,
            "applied_pattern_counts": {},
            "review_reason_counts": {},
        }
        for row in assessment_rows:
            report = row.get("conditional_modernization")
            if not isinstance(report, dict):
                continue
            totals["assessments_examined"] += 1
            if report.get("rewrite_performed"):
                totals["assessments_rewritten"] += 1
            local = report.get("stats") or {}
            for key in (
                "expression_nodes_examined",
                "branch_like_nodes_examined",
                "rewrite_candidates_proven",
                "rewrites_applied",
                "review_required_nodes",
            ):
                totals[key] += int(local.get(key, 0) or 0)
            for field in ("applied_pattern_counts", "review_reason_counts"):
                for name, count in (local.get(field) or {}).items():
                    totals[field][name] = totals[field].get(name, 0) + int(count)
        branch_like = totals["branch_like_nodes_examined"]
        totals["rewrite_rate_pct_of_branch_like"] = (
            round(100.0 * totals["rewrites_applied"] / branch_like, 2)
            if branch_like else 0.0
        )
        totals["assessment_rewrite_rate_pct"] = (
            round(
                100.0
                * totals["assessments_rewritten"]
                / totals["assessments_examined"],
                2,
            )
            if totals["assessments_examined"] else 0.0
        )
        stats["conditional"] = totals

    return stats


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rule',action='append',default=[])
    p.add_argument('--rules-file',type=Path)
    p.add_argument('--schema',type=Path,default=Path(__file__).resolve().parents[2]/'third_party/scap-1.4-schemas/omni-schema.xsd')
    p.add_argument(
        '--target-ng-version',
        choices=('0.2.0','0.3.0'),
        default='0.2.0',
        help='Target SCAP-NG authoring version. Default preserves the frozen 0.2.0 review output.',
    )
    p.add_argument(
        '--modernize-foreach-v1',
        action='store_true',
        help='Opt in to the proven 0.3.0 foreach v1 modernization; requires --target-ng-version 0.3.0.',
    )
    p.add_argument(
        '--modernize-conditionals-v1',
        action='store_true',
        help=(
            'Opt in to pattern-based 0.3.0 conditional modernization for exact '
            'complementary-guard branch trees; requires --target-ng-version 0.3.0.'
        ),
    )
    args=p.parse_args(argv)
    if args.modernize_foreach_v1 and args.target_ng_version != '0.3.0':
        p.error('--modernize-foreach-v1 requires --target-ng-version 0.3.0')
    if args.modernize_conditionals_v1 and args.target_ng_version != '0.3.0':
        p.error('--modernize-conditionals-v1 requires --target-ng-version 0.3.0')
    digest=hashlib.sha256(args.input.read_bytes()).hexdigest()
    if digest!=args.sha256:raise SystemExit('Source archive checksum mismatch')
    wanted=set(args.rule)
    if args.rules_file:
        data=json.loads(args.rules_file.read_text(encoding='utf-8'))
        wanted.update(data if isinstance(data,list) else data['summary']['selected_rules'])
    if not wanted:raise SystemExit('Select explicit Rules for the review; full regeneration is held')
    if args.output.exists() and any(args.output.iterdir()):raise SystemExit('Output directory must be new or empty')
    args.output.mkdir(parents=True,exist_ok=True)
    xr,resolve_original=source_rule_resolver(args.input)
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
                        'response':manual_response_contract()}})
                    manual_done[key]=ref
                    result.setdefault('manual_source_bindings',[]).append({'path':ref,'source_binding':binding,
                        'procedure_origin':'matching shared source binding' if not text(c.find('x:check-content',NS)) else 'inline check text'})
                    result['selectors'][selector]=ref
                    continue
                source_ref=c.find('x:check-content-ref',NS)
                href=source_ref.get('href')
                did=source_ref.get('name')
                source_key=(href,did)
                if source_key in done:
                    result['selectors'][selector]=done[source_key]
                    continue
                original=resolve_original(href,did)
                original_path=Path(tmp)/(rid+'-'+hashlib.sha256(
                    ((href or '')+'\\0'+did).encode('utf-8')
                ).hexdigest()[:12]+'-source.xml')
                if not original_path.exists():
                    ET.ElementTree(original).write(original_path,encoding='utf-8')
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
                    defect=source_defect_features_reason(unsupported)
                    if defect and has_manual:
                        error=defect+":"+json.dumps(unsupported,sort_keys=True,separators=(",",":"))
                        source_defect_selector_fallbacks.append(
                            source_defect_fallback(selector,did,error)
                        )
                        result['assessments'].append({
                            'status':'skipped_source_defect_manual_fallback',
                            'source_definition':did,
                            'classification':'source_content_defect',
                            'reason':defect,
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
                modernization=None
                if args.target_ng_version == '0.2.0':
                    # Frozen default path: preserve the historical 0.2.0 selected-rule
                    # converter output exactly.
                    native=align_assessment_vocabulary(native)
                    for test in native.get('assessment',{}).get('tests',{}).values():
                        test['reported_elements']='all'
                else:
                    native,modernization=postprocess_automated_assessment(
                        native,
                        target_ng_version=args.target_ng_version,
                        modernize_foreach=args.modernize_foreach_v1,
                        modernize_conditionals=args.modernize_conditionals_v1,
                    )
                errors=violations(native)
                if errors:raise ValueError('Current vocabulary guard: '+str(errors))
                ref='assessments/automated/'+aid+'.assessment.yaml'
                write_yaml(args.output/ref,native)
                done[source_key]=ref;result['selectors'][selector]=ref
                assessment_row={'status':'representation_comparator_equal',
                    'path':ref,'source_graph_bindings':provenance,
                    'tests':len(native['assessment']['tests']),
                    'objects':len(native['assessment']['objects']),
                    'states':len(native['assessment'].get('states',{})),
                    'variables':len(native['assessment'].get('variables',{})),
                    'reverse_omni_schema_valid':True}
                if args.modernize_foreach_v1:
                    assessment_row['foreach_modernization']=(
                        modernization['foreach']
                        if args.modernize_conditionals_v1 else modernization
                    )
                if args.modernize_conditionals_v1:
                    assessment_row['conditional_modernization']=(
                        modernization['conditional']
                        if args.modernize_foreach_v1 else modernization
                    )
                result['assessments'].append(assessment_row)
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
    modernization_stats = aggregate_modernization_stats(
        evidence,
        foreach_enabled=args.modernize_foreach_v1,
        conditional_enabled=args.modernize_conditionals_v1,
    )
    if args.modernize_foreach_v1 or args.modernize_conditionals_v1:
        evidence['modernization_stats'] = modernization_stats
        (args.output/'modernization-stats.json').write_text(
            json.dumps(modernization_stats,indent=2,sort_keys=True)+'\n',
            encoding='utf-8',
        )
    (args.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({
        'status':evidence['status'],
        'rules':len(wanted),
        'automated_assessments':sum(len(r['assessments']) for r in evidence['rules']),
        'source_sha256':digest,
        'modernization_stats':modernization_stats,
    },indent=2))
    return 1 if failed else 0

if __name__=='__main__':raise SystemExit(main())
