#!/usr/bin/env python3
"""Consolidate original six-source and OVAL conversion gaps, without admission."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import PIN, OvalDocument, closure, file_inventory, xml_documents
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_inventory import SourceInventory
from v04_conversion_diagnostics import classify_failure, summarize_failures

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = ROOT / 'tests/fixtures/v04-converter-schema-dependencies.json'


def additional_source_failures(dependencies):
    """Keep additional probe cohorts separate from STIG/Self-Assertion totals.

    Receipts are diagnostic evidence, never an admission shortcut. Check source
    bytes and original validity again before classifying a reported gap.
    """
    records, coverage = [], []
    validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
    for cohort in dependencies.get('additional_source_cohorts', []):
        directory = ROOT / cohort['fixture_directory']
        pin = json.loads((directory / 'provenance.json').read_text())
        validities = {}
        for item in pin['files']:
            raw = (directory / item['path']).read_bytes()
            if sha256(raw).hexdigest() != item['sha256']:
                raise ValueError('additional original source pin mismatch: ' + item['path'])
            if item['path'].endswith('.xml'):
                validities[item['path']] = validator.validate(etree.fromstring(raw))
        cases = json.loads((directory / 'conversion-evidence.json').read_text())['cases']
        valid_proved = 0
        for case in cases:
            validity = validities[case['source']]
            valid = validity['status'] == 'VALID' and not any(i['kind'] == 'deprecated' for i in validity['issues'])
            if valid and case['source_proof'] == 'PROVED':
                valid_proved += 1
                continue
            dependency = dependency_for(case['source'], case['test'], {'cases': cohort.get('dependencies', [])})
            diagnostics = case['diagnostics'] or [{'stage': 'source_proof', 'message': 'Original source proof unavailable'}]
            records.append({'scope': 'additional_original_test', 'source': cohort['id'],
                'source_pin': {'repository': pin['repository'], 'commit': pin['commit']},
                'document': case['source'], 'test': case['test'], 'capability': pin['capability'],
                'source_validity': validity, 'counterexample': str(directory.relative_to(ROOT) / case['source']),
                'failures': [classify_failure(d['message'], stage=d['stage'], validity=validity,
                                              dependency=dependency) for d in diagnostics]})
        coverage.append({'id': cohort['id'], 'repository': pin['repository'], 'commit': pin['commit'],
            'original_tests': len(cases), 'compiled': sum(c['compiled'] for c in cases),
            'typed_term_proved': sum(c['source_proof'] == 'PROVED' for c in cases),
            'source_valid_nondeprecated_and_term_proved': valid_proved,
            'scope': 'Additional probe fixtures, excluded from Self-Assertion/production denominators; no runtime equivalence claim.'})
    return records, coverage


def dependency_for(document, test, dependencies):
    for row in dependencies['cases']:
        if row['document'] == document and test in row['test_ids']:
            return row
    return None


def original_validities(source_root, cases):
    """Validate pinned originals; never repair or execute corpus payloads."""
    pin = json.loads(PIN.read_text())
    expected = pin['files']
    # The collection manifest is a map in the existing corpus audit.
    if file_inventory(source_root) != expected:
        raise ValueError('original corpus file inventory differs from pinned source')
    wanted = {c['document'] for c in cases}
    result = {}
    validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
    by_document = {}
    for c in cases:
        by_document.setdefault(c['document'], []).append(c)
    for name, raw in xml_documents(source_root):
        if name not in wanted:
            continue
        root = ET.fromstring(raw)
        report = validator.validate(etree.fromstring(raw))
        nodes = {i: n for (_, i), n in SourceInventory(OvalDocument(root, name)).nodes.items()}
        for case in by_document[name]:
            ids, problems = closure(nodes, case['test'])
            validity = closure_validity([nodes[i] for i in ids], {name: report})
            if problems:
                validity['status'] = 'INVALID'
                validity['issues'] += [{'kind': 'invalid', 'message': p} for p in problems]
            result[name, case['test']] = validity
    if set(result) != {(c['document'], c['test']) for c in cases}:
        raise ValueError('missing original case for source validity')
    return result


def corpus_failures(report, validities, dependencies):
    records = []
    for case in report['cases']:
        conversion = case.get('configured_baseline', case)
        validity = validities[case['document'], case['test']]
        invalid = validity['status'] != 'VALID' or any(i['kind'] == 'deprecated' for i in validity['issues'])
        if conversion['source_proof'] == 'PROVED' and not invalid:
            continue
        dependency = dependency_for(case['document'], case['test'], dependencies)
        diagnostics = conversion['diagnostics'] or [{'stage': 'source_proof',
            'message': 'Original closure invalid/deprecated' if invalid else 'Independent source proof unavailable'}]
        record = {k: case[k] for k in ('document', 'test', 'capability')}
        record['scope'] = 'configured' if 'configured_baseline' in case else 'diagnostic_only_not_enabled'
        record['source_validity'] = validity
        record['conversion_source_proof'] = conversion['source_proof']
        record['failures'] = [classify_failure(d['message'], stage=d['stage'], validity=validity,
                                              dependency=dependency) for d in diagnostics]
        records.append(record)
    return records


def acceptance_failures(report, source):
    records = []
    for case in report['cases']:
        if case['outcome'] in ('PROVED', 'NOT_SELECTED', 'MANUAL_OCIL_ONLY'):
            continue
        diagnostics = [case['diagnostic']] if case.get('diagnostic') else [
            str(x) for x in case.get('proof', {}).get('unsupported_obligations', [])]
        validity = case.get('source_validity')
        if validity is None and case.get('diagnostic'):
            # The existing acceptance gate serializes typed reference issues
            # before conversion. Retain that evidence, rather than treating an
            # unresolved original catalog binding as missing implementation.
            try:
                issues = json.loads(case['diagnostic'])
            except json.JSONDecodeError:
                issues = []
            if isinstance(issues, list):
                invalid = [i for i in issues if isinstance(i, dict) and i.get('category') == 'source-invalid']
                if invalid:
                    validity = {'status': 'INVALID', 'issues': [{'kind': 'invalid', **i} for i in invalid]}
        records.append({'source': source, 'rule': case['rule'], 'outcome': case['outcome'],
            'source_pin': report.get('source'),
            'required_capabilities': case['required_capabilities'],
            'failures': [classify_failure(d, validity=validity)
                         for d in diagnostics or ['Independent proof unavailable']]})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--original-root', type=Path, required=True)
    parser.add_argument('--acceptance-root', type=Path)
    parser.add_argument('--external-failures', type=Path, help='JSON list of {source, message, evidence_url}; failures only')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    dependencies = json.loads(DEPENDENCIES.read_text())
    corpus = json.loads(args.corpus.read_text())
    validities = original_validities(args.original_root, corpus['cases'])
    records = corpus_failures(corpus, validities, dependencies)
    additional, additional_coverage = additional_source_failures(dependencies)
    records.extend(additional)
    if args.acceptance_root:
        for path in sorted(args.acceptance_root.glob('*/acceptance.json')):
            records.extend(acceptance_failures(json.loads(path.read_text()), path.parent.name))
    if args.external_failures:
        for row in json.loads(args.external_failures.read_text()):
            records.append({**row, 'failures': [classify_failure(row['message'], stage='infrastructure')]})
    configured = [c for c in corpus['cases'] if 'configured_baseline' in c]
    valid_proofs = [c for c in configured if c['configured_baseline']['source_proof'] == 'PROVED'
                    and validities[c['document'], c['test']]['status'] == 'VALID'
                    and not any(i['kind'] == 'deprecated' for i in validities[c['document'], c['test']]['issues'])]
    result = {'format': 'scap-ng/conversion-gaps/1', 'authority': 'Diagnostic only; never admits or changes a conversion',
              'source_pin': corpus['pin'], 'dependencies': dependencies,
              'coverage': {'original_tests': len(corpus['cases']), 'configured_tests': len(configured),
                  'configured_compiled': sum(c['configured_baseline']['compiled'] for c in configured),
                  'configured_term_proved': sum(c['configured_baseline']['source_proof'] == 'PROVED' for c in configured),
                  'configured_original_valid_nondeprecated_and_term_proved': len(valid_proofs)},
              'additional_source_coverage': additional_coverage,
              'summary': summarize_failures(records), 'cases': records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
