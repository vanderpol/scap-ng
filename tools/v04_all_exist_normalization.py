"""Owner-approved, versioned Test-only normalization contract (Refs #251).

This is a conversion admission/provenance contract, not a scanner evaluator.
Never use it to change field/record quantifiers or discard error evidence.
"""
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

CONTRACT = 'scap-ng-0.4.0/actual-items-test-all-exist/1'
DECISION = 'https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6388735943'
SOURCE_SHA256 = '463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9'
DEFINITION = 'oval:mil.disa.stig.defs:def:230413'


def check_population_contract(collection_status, item_statuses):
    """Reject evidence outside the normalization proof; never discard diagnostics.

    This checks conformance evidence only. It neither collects Items nor computes
    a Test result. Real scanners still need independent contract acceptance.
    """
    if collection_status not in {'complete', 'incomplete', 'error', 'not_collected',
                                  'does_not_exist', 'not_applicable'}:
        raise ValueError('unknown collection status')
    if any(s not in {'exists', 'error', 'not_collected'} for s in item_statuses):
        raise ValueError('synthetic or unsupported Item evidence outside normalization contract')
    if collection_status == 'complete' and any(s != 'exists' for s in item_statuses):
        raise ValueError('error/unknown Item evidence cannot be declared complete success')
    if collection_status == 'does_not_exist' and item_statuses:
        raise ValueError('absent collection cannot contain Items')


def contract_evidence(contract):
    if contract != CONTRACT:
        raise ValueError('explicit approved actual-Items normalization contract required')
    schema = Path(__file__).resolve().parents[1] / 'schema/v0.4.0/collected-item.schema.json'
    statuses = json.loads(schema.read_text())['properties']['status']['enum']
    if set(statuses) != {'exists', 'error', 'not_collected'}:
        raise ValueError('actual-Items result schema contract changed; review normalization')
    return {'version': CONTRACT, 'owner_decision': DECISION, 'decision_date': '2026-10-24',
            'scope': 'Test existence only; no State/field/record normalization',
            'original': 'all_exist', 'native': {'items_found': 'one_or_more'},
            'reason': '0.4.0 collection contract represents no synthetic does_not_exist Items',
            'error_unknown_policy': 'Collection error/incomplete/not_collected remain error/unknown; '
                'Item error/not_collected evidence must not be silently dropped or declared complete success',
            'result_schema_sha256': sha256(schema.read_bytes()).hexdigest(),
            'unrestricted_oval_equivalence': False, 'scanner_parity': False}


def source_normalizations(original, definition_id, provenance, projection):
    """Bind the pinned original XML to each explicitly normalized native Test."""
    if sha256(original).hexdigest() != SOURCE_SHA256 or definition_id != DEFINITION:
        raise ValueError('unproved all_exist source; original pinned Definition required')
    root = ET.fromstring(original)
    records = []
    by_id = {n.get('id'): n for n in root.iter() if n.get('id')}
    renames = projection['identity_projection']['tests']
    for source_id, lowered_id in provenance['source_test_bindings'].items():
        test = by_id[source_id]
        if test.get('check_existence', 'at_least_one_exists') != 'all_exist':
            continue
        if any(c.tag.endswith('}state') for c in test):
            raise ValueError('State-bearing all_exist requires its own source proof')
        obj_ref = next(c.get('object_ref') for c in test if c.tag.endswith('}object'))
        obj = by_id[obj_ref]
        records.append({**contract_evidence(CONTRACT), 'source_file_sha256': SOURCE_SHA256,
            'source_definition_id': definition_id, 'source_test_id': source_id,
            'source_test_version': test.get('version'), 'source_object_id': obj_ref,
            'source_object_version': obj.get('version'),
            'source_object_xml_sha256': sha256(ET.tostring(obj)).hexdigest(),
            'source_schema_version': next(n.text for n in root.iter() if n.tag.endswith('}schema_version')),
            'native_test_id': renames[lowered_id]})
    if len(records) != 16:
        raise ValueError('pinned normalization population changed')
    return records
