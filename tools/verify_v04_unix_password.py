#!/usr/bin/env python3
"""Source-backed UNIX password batch, with unproved Rules kept out of packages.

Select by dependency capability, not Rule identity. Fixtures are complete
original OVAL closures plus pinned XCCDF provenance, never converter exports.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from lxml import etree as original_xml

from oval_source_validation import SourceValidator
from inventory_v04_six_source_requirements import closure_validity
from v04_direct_converter import assemble_subset, convert_rule, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL, digest, xml_identity
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from v04_direct_yaml import authoring_yaml
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]


def snapshot(source, binding, rule_id):
    reader = ExpandedSource(source.components[binding['component']])
    closure = reader.closure(binding['definition'])
    original = ET.Element('{' + OVAL + '}oval_definitions')
    generator = source.components[binding['component']].find('{' + OVAL + '}generator')
    if generator is not None:
        original.append(deepcopy(generator))
    for kind in ('definitions', 'tests', 'objects', 'states', 'variables'):
        entries = [n for n in closure['nodes'] if n['kind'] == kind]
        if entries:
            section = ET.SubElement(original, '{' + OVAL + '}' + kind)
            section.extend(deepcopy(reader.nodes[n['id']]) for n in entries)
    return {'source_zip_sha256': source.zip_sha256, 'source_xml_sha256': source.xml_sha256,
            'component': binding['component'], 'rule': rule_id,
            'rule_sha256': digest(xml_identity(source.rules[rule_id])),
            'title': source.rules[rule_id].findtext('{http://checklists.nist.gov/xccdf/1.2}title'),
            'definition': binding['definition'], 'closure': closure,
            'source_xml': ET.tostring(original, encoding='unicode'),
            'scope': 'Complete original primary OVAL closure, not applicability or a fabricated source Rule'}


def run(inputs, output, fixtures=None):
    output.mkdir(parents=True, exist_ok=False)
    pins = json.loads((ROOT / 'tests/fixtures/v04-direct-six-sources.json').read_text())['sources']
    mappings = load_mappings()
    validators = build_validators(ROOT / 'schema/v0.4.0')
    source_validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
    report = {'capability': 'unix.password', 'platforms': {}, 'new_conversion_algorithms': 0}
    for platform in ('rhel_9', 'oracle_linux_9'):
        pin = pins[platform]
        source = SourceModel(inputs / pin['file'], pin['sha256'])
        with zipfile.ZipFile(inputs / pin['file']) as archive:
            original = original_xml.fromstring(archive.read(source.member),
                original_xml.XMLParser(resolve_entities=False, no_network=True))
        source_checks = {c.get('id'): source_validator.validate(c[0])
                         for c in original.findall('{http://scap.nist.gov/schema/scap/source/1.2}component')
                         if c[0].tag == '{' + OVAL + '}oval_definitions'}
        documents, bindings, results = {}, [], []
        for row in SourceInventory(source).rules():
            if 'unix.password' not in row['needed_capabilities']:
                continue
            result = {'rule': row['source_rule'], 'outcome': 'BLOCKED'}
            try:
                validity = closure_validity(row['dependencies'], source_checks)
                if validity['status'] != 'VALID' or any(i['kind'] == 'deprecated' for i in validity['issues']):
                    raise ValueError('original OVAL closure invalid/deprecated: ' + json.dumps(validity['issues']))
                native, binding = convert_rule(source, row['source_rule'], mappings)
                for document in native.values():
                    kind, = document
                    errors = list(document_errors(validators[kind + '.schema.json'], document))
                    if errors:
                        raise ValueError(errors[0].message)
                assessment = next(d['assessment'] for d in native.values() if 'assessment' in d)
                proof = expanded_compare(ExpandedSource(source.components[binding['component']]),
                                         binding['definition'], assessment)
                result.update(outcome=proof['outcome'], proof=proof)
                if proof['outcome'] != 'PROVED':
                    results.append(result)
                    continue
                documents.update(native)
                bindings.append(binding)
                if fixtures:
                    fixtures.mkdir(parents=True, exist_ok=True)
                    case = snapshot(source, binding, row['source_rule'])
                    (fixtures / (platform + '-' + assessment['id'] + '.json')).write_text(json.dumps(case, indent=2) + '\n')
            except (UnsupportedSource, ValueError) as error:
                result['diagnostic'] = str(error)
            results.append(result)
        documents, trace = assemble_subset(source, documents, bindings, mappings)
        proofs = verify_original(source.root, documents, trace)
        bundle, _ = build_bundle(documents)
        programs = verify_compiled(documents, bundle)
        destination = output / platform
        destination.mkdir()
        for path, document in documents.items():
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(document, indent=2) + '\n')
            target.with_suffix('.yaml').write_text(authoring_yaml(document))
        (destination / 'primary-subset.scapng').write_bytes(bundle)
        report['platforms'][platform] = {'source': pin, 'rules': results, 'source_proved': len(proofs),
            'compiled': len(programs), 'programs': programs,
            'scope': 'Primary automated subset; original applicability remains separately inventoried/unproved'}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--fixtures', type=Path)
    args = parser.parse_args()
    report = run(args.inputs, args.output, args.fixtures)
    print(json.dumps({p: {'proved': r['source_proved'], 'compiled': r['compiled']}
                      for p, r in report['platforms'].items()}, indent=2))
