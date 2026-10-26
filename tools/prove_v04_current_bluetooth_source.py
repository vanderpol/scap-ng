"""Current Bluetooth applicability proof from original SCAP, not preview JSON.

The historical archive is deliberately not an input. The pinned original graph
has a direct include Filter and no Set; an invented singleton UNION is rejected.
Only this inventory Definition is certified, not a complete Windows 11 policy.
Refs #251.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

from v04_direct_scap_source import SourceModel, OVAL, XCCDF, ensure
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_yaml import authoring_yaml as render_yaml
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_source_proof_contract import validators, compile_proofs
from v04_canonical_source_ir import validate_docs
from validate_v04_oval_5123 import check

ZIP_SHA = 'e4b8d55b58aa80124bd0974977af4c7f7bde35c748e2940e02857419292d8c3d'
XML_SHA = 'cfc5061d275235f6c5e0719cc384fb887f8624ae6e0dbac03f4a9cb3f43c06a5'
DEFINITION = 'oval:navy.navwar.niwcatlantic.scc.windows:def:102'
TEST = 'oval:navy.navwar.niwcatlantic.scc.windows:tst:101'
IDENTITY = 'original-windows11-bluetooth-applicability-assessment'
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-current-source-proofs/windows11-signed.zip'


def original_context(source):
    """Independently bind the original CPE check through the checklist catalog."""
    language = '{http://cpe.mitre.org/language/2.0}'
    matches = [n for n in source.benchmark.iter(language + 'check-fact-ref')
               if n.get('id-ref') == DEFINITION]
    ensure(len(matches) == 1, 'one original Bluetooth applicability check required')
    check_ref, = matches
    ensure(set(check_ref.attrib) == {'id-ref', 'href', 'system'} and
           check_ref.get('system') == OVAL, 'unsupported applicability check attributes')
    component = source.catalog[check_ref.get('href')]
    definition = source.node(component, DEFINITION, 'definition')
    parent = source.parents[check_ref]
    ensure(parent.tag == language + 'logical-test' and len(parent) == 1 and
           parent.get('operator') == 'AND' and parent.get('negate') == 'false',
           'unsupported surrounding applicability Boolean expression')
    platform = source.parents[parent]
    ensure(platform.tag == language + 'platform' and
           platform.findall(language + 'logical-test') == [parent] and
           all(n.tag in (language + 'title', language + 'logical-test') for n in platform),
           'unsupported surrounding applicability platform')
    return component, definition, {'platform_id': platform.get('id'),
        'check': dict(check_ref.attrib), 'logical_test': dict(parent.attrib),
        'uses': [dict(n.attrib) for n in source.benchmark.iter('{' + XCCDF + '}platform')
                 if n.get('idref', '').lstrip('#') == platform.get('id', '').lstrip('#')]}


def convert_original(source):
    component, definition, context = original_context(source)
    converter = AssessmentConverter(source, component, load_mappings())
    expression = converter.reference(DEFINITION, 'definition')
    assessment = {'id': IDENTITY, 'version': int(definition.get('version')),
        'assessment_title': definition.findtext('{' + OVAL + '}metadata/{' + OVAL + '}title').strip(),
        'mode': 'automated', 'class': definition.get('class'), 'purpose': 'applicability',
        'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'},
        'tests': converter.tests, 'evaluate': expression}
    ensure(not converter.shared_objects and not converter.variables, 'unexpected Bluetooth dependency expansion')
    return {'assessment': assessment}, context


def verify_original(source, document):
    """Independent OVAL/native term readers compare the complete original Test."""
    component, definition, context = original_context(source)
    assessment = document['assessment']
    ensure(assessment['class'] == definition.get('class') == 'inventory' and
           assessment['purpose'] == 'applicability', 'Bluetooth applicability purpose/class mismatch')
    original = ExpandedSource(source.components[component])
    native = ExpandedNative(assessment)
    ensure(original.expression(DEFINITION) == {'test': TEST}, 'original applicability criteria changed')
    ensure(len(assessment['tests']) == 1 and set(assessment['evaluate']) == {'test'},
           'native applicability Boolean graph changed')
    tid, = assessment['tests']
    ensure(assessment['evaluate'] == {'test': tid}, 'native applicability reference changed')
    expected, actual = original.test(TEST), native.test(tid)
    ensure(expected == actual, 'Bluetooth original-source/native operand mismatch')
    return {'outcome': 'PROVED', 'source_test': TEST, 'native_test': tid,
            'source_term': expected, 'native_term': actual, 'context': context,
            'original_set_present': False, 'synthetic_union_introduced': False}


def prove(source_path, output):
    source = SourceModel(source_path, ZIP_SHA)
    ensure(source.xml_sha256 == XML_SHA, 'original Windows 11 XML hash changed')
    document, context = convert_original(source)
    proof = verify_original(source, document)
    validate_docs({'authoring/bluetooth.json': document}, validators())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    text = render_yaml(document)
    ensure(yaml.safe_load(text) == document, 'Bluetooth YAML/JSON mismatch')
    (output / 'bluetooth.assessment.yaml').write_text(text)
    (output / 'bluetooth.assessment.json').write_text(json.dumps(document, indent=2) + '\n')
    component, _, _ = original_context(source)
    # XSD-check the complete selected closure, retaining original nodes and
    # generator. The full component also contains unrelated Windows constructs;
    # the independent-platform umbrella must not claim to validate those.
    original = ExpandedSource(source.components[component])
    closure = original.closure(DEFINITION)
    selected = {row['id'] for row in closure['nodes']}
    subset = deepcopy(source.components[component])
    for section in list(subset):
        if section.tag.rsplit('}', 1)[-1] in ('definitions', 'tests', 'objects', 'states', 'variables'):
            for child in list(section):
                if child.get('id') not in selected:
                    section.remove(child)
            if not len(section):
                subset.remove(section)
    original_xml = output / 'original-oval-closure.xml'
    original_xml.write_bytes(ET.tostring(subset, encoding='utf-8', xml_declaration=True))
    xsd = check(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3', original_xml, 'independent')
    ensure(xsd['status'] == 'PASS', 'original OVAL XSD failure: ' + str(xsd['diagnostics']))
    rejected = []
    for kind in ('synthetic_union', 'missing_filter', 'wrong_action', 'wrong_value', 'item_absence'):
        changed = deepcopy(document)
        test, = changed['assessment']['tests'].values()
        obj = test['object']
        if kind == 'synthetic_union':
            test['object'] = {'set': {'operator': 'union', 'operands': [{'object': obj}]}}
        elif kind == 'missing_filter':
            del obj['filters']
        elif kind == 'wrong_action':
            obj['filters'][0]['exclude'] = obj['filters'][0].pop('include')
        elif kind == 'wrong_value':
            obj['filters'][0]['include']['stdout_line']['case_insensitive_equals'] = 'WiFi'
        else:
            test['require']['items_found'] = 'none'
        try:
            verify_original(source, changed)
        except ValueError:
            rejected.append(kind)
        else:
            raise ValueError('accepted Bluetooth mutation: ' + kind)
    proof.update(source_zip_sha256=ZIP_SHA, source_xml_sha256=XML_SHA,
                 source_definition=DEFINITION, source_member=source.member,
                 original_xsd=xsd, original_closure=closure, mutations_rejected=rejected,
                 compilation=compile_proofs([document], output / 'compiled'),
                 historical_archive_used=False, scanner_parity=False)
    (output / 'current-source-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-scap', type=Path, default=FIXTURE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prove(args.original_scap, args.output), indent=2))
