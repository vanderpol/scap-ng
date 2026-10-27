#!/usr/bin/env python3
"""Convert and independently accept primary OVAL subsets of all six originals.

Every Rule gets a result. Schema-only/unproved output never enters packages.
Applicability has its own inventory and is not claimed proved by primary output.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import zipfile

from lxml import etree as E

from audit_v04_direct_benchmark import verify_compiled, verify_original
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_converter import assemble_subset, convert_rule, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_platform_inventory import platform_inventory
from v04_direct_scap_source import OVAL, SourceModel, UnsupportedSource
from v04_direct_yaml import authoring_yaml
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from v04_native_bundle_compiler import build_bundle, compile_assessment_program
from audit_v04_eight_assessment_pilot import verify_program
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
DS = '{http://scap.nist.gov/schema/scap/source/1.2}'


def verify_proof_floor(platform, evidence, baseline):
    """Retain every pinned proof and program; additional proved Rules are allowed."""
    if evidence['source']['sha256'] != baseline['source_sha256']:
        raise ValueError(platform + ': original source pin changed')
    cases = {r['rule']: r for r in evidence['cases'] if r['outcome'] == 'PROVED'}
    programs = {p['assessment']: p['program_sha256'] for p in evidence['programs']}
    for rule, expected in baseline['rules'].items():
        case = cases.get(rule)
        if case is None or case['assessment'] != expected['assessment']:
            raise ValueError(platform + ': previously proved primary Rule lost: ' + rule)
        if programs.get(case['assessment']) != expected['program_sha256']:
            raise ValueError(platform + ': previously proved compiled program changed: ' + rule)


def run(inputs, output):
    output.mkdir(parents=True, exist_ok=False)
    pins = json.loads((ROOT / 'tests/fixtures/v04-direct-six-sources.json').read_text())
    baseline = json.loads((ROOT / 'tests/fixtures/v04-six-primary-proof-floor.json').read_text())
    mappings = load_mappings()
    source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
    validators = build_validators(ROOT / 'schema/v0.4.0')
    report = {'format': 'scap-ng/direct-six-primary-acceptance/1',
              'scope': 'Primary OVAL only; applicability separately inventoried, not complete policy/scanner equivalence',
              'source_pin': pins, 'enabled_capabilities': [m['capability'] for m in mappings], 'sources': {}}
    for platform, pin in pins['sources'].items():
        path = inputs / pin['file']
        source = SourceModel(path, pin['sha256'], inventory_broken_references=True)
        inventory = SourceInventory(source)
        with zipfile.ZipFile(path) as archive:
            original = E.fromstring(archive.read(source.member), E.XMLParser(resolve_entities=False, no_network=True))
        checks = {c.get('id'): source_validator.validate(c[0]) for c in original.findall(DS + 'component')
                  if c[0].tag == '{' + OVAL + '}oval_definitions'}
        documents, bindings, cases = {}, [], []
        for row in inventory.rules():
            result = {'rule': row['source_rule'], 'required_capabilities': row['needed_capabilities'],
                      'outcome': 'BLOCKED', 'proof_scope': 'primary OVAL'}
            if not any(c['system'] == OVAL for c in row['checks']):
                result['outcome'] = 'MANUAL_OCIL_ONLY'
                cases.append(result)
                continue
            try:
                if row['inventory_problems']:
                    raise UnsupportedSource(json.dumps(row['inventory_problems'], sort_keys=True))
                validity = closure_validity(row['dependencies'], checks)
                if validity['status'] != 'VALID' or any(i['kind'] == 'deprecated' for i in validity['issues']):
                    result['source_validity'] = validity
                    raise UnsupportedSource('original OVAL closure invalid/deprecated')
                native, binding = convert_rule(source, row['source_rule'], mappings)
                for document in native.values():
                    kind, = document
                    errors = list(document_errors(validators[kind + '.schema.json'], document))
                    if errors:
                        raise ValueError('native schema: ' + errors[0].message)
                assessment = next(d['assessment'] for d in native.values() if 'assessment' in d)
                proof = expanded_compare(ExpandedSource(source.components[binding['component']]),
                                         binding['definition'], assessment)
                if proof['outcome'] != 'PROVED':
                    result.update(outcome=proof['outcome'], proof=proof)
                    cases.append(result)
                    continue
                verify_program(assessment, compile_assessment_program(assessment))
                documents.update(native)
                bindings.append(binding)
                result.update(outcome='PROVED', assessment=assessment['id'])
            except (UnsupportedSource, ValueError) as error:
                result['diagnostic'] = str(error)
            cases.append(result)
        destination = output / platform
        destination.mkdir()
        documents, trace = assemble_subset(source, documents, bindings, mappings)
        programs = []
        if bindings:
            verify_original(source.root, documents, trace)
            bundle, _ = build_bundle(documents)
            programs = verify_compiled(documents, bundle)
            (destination / 'primary-subset.scapng').write_bytes(bundle)
            for path, document in documents.items():
                target = destination / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(document, indent=2) + '\n')
                target.with_suffix('.yaml').write_text(authoring_yaml(document))
        own = {'source': pin, 'cases': cases, 'programs': programs,
               'outcomes': dict(Counter(r['outcome'] for r in cases)),
               'catalog_errors': source.catalog_errors,
               'applicability': platform_inventory(source, inventory)}
        verify_proof_floor(platform, own, baseline['sources'][platform])
        (destination / 'acceptance.json').write_text(json.dumps(own, indent=2) + '\n')
        report['sources'][platform] = {k: v for k, v in own.items() if k not in ('cases', 'applicability')}
        print(platform, json.dumps(own['outcomes']), flush=True)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.inputs, args.output)
