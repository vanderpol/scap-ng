#!/usr/bin/env python3
"""Measure direct-converter coverage of pinned OVAL Test Content, without admission.

Standalone OVAL documents have no XCCDF Rules. Each Test is therefore attempted
in a clearly synthetic Assessment. No unsupported capability is enabled, and
successful conversion, validation, compilation and source proof stay separate.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET
import zipfile

from v04_direct_converter import AssessmentConverter, dependency_blockers, load_mappings
from v04_direct_inventory import SourceInventory, node_kind
from v04_direct_scap_source import OVAL, SourceModel, UnsupportedSource, digest, ensure, native_identifier

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / 'tests/fixtures/v04-oval-corpus-pin.json'
OVAL_ROOT = '{' + OVAL + '}oval_definitions'


def file_inventory(directory):
    """Hash every collection file, including support payloads never executed here."""
    return {p.relative_to(directory).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob('*')) if p.is_file()}


def xml_documents(directory):
    """Read XML and ZIP-contained XML in place; never extract or execute payloads."""
    for path in sorted(directory.rglob('*')):
        if path.suffix == '.xml':
            yield path.relative_to(directory).as_posix(), path.read_bytes()
        elif path.suffix == '.zip':
            with zipfile.ZipFile(path) as archive:
                ensure(archive.testzip() is None, f'CRC failure: {path.name}')
                ensure(len(archive.namelist()) == len(set(archive.namelist())), 'duplicate ZIP member')
                for name in sorted(archive.namelist()):
                    if name.endswith('.xml'):
                        yield path.relative_to(directory).as_posix() + '!' + name, archive.read(name)


class OvalDocument:
    """File-local source index using the converter's version-neutral reference API.

    This is not a fabricated SCAP datastream: no checklist/Profile claim is made.
    IDs in separate files remain separate, including intentionally repeated IDs.
    """
    node = SourceModel.node
    object_uses = SourceModel.object_uses

    def __init__(self, root, name):
        self.components = {name: root}
        index = {}
        for group in root:
            for element in group:
                if node_kind(element):
                    identifier = element.get('id')
                    ensure(identifier and identifier not in index, f'duplicate/missing ID: {identifier}')
                    index[identifier] = element
        self.nodes = {name: index}


def closure(nodes, identifier):
    """Inventory all edges despite unsupported capabilities, with cycle diagnostics."""
    found, active, problems = set(), [], []

    def visit(identifier, kind):
        if identifier in active:
            problems.append('cyclic dependency: ' + ' -> '.join(active + [identifier]))
            return
        node = nodes.get(identifier)
        if node is None or node['kind'] != kind:
            problems.append(f'unresolved/wrong-kind {kind}: {identifier}')
            return
        if identifier in found:
            return
        found.add(identifier)
        active.append(identifier)
        for edge in node['references']:
            visit(edge['id'], edge['kind'])
        active.pop()

    visit(identifier, 'test')
    return sorted(found), sorted(set(problems))


def assessment_for(visitor, identifier):
    expression = visitor.reference(identifier, 'test')
    source_test = visitor.source.node(visitor.component_id, identifier, 'test')
    assessment = {'id': native_identifier(source_test, 'assessment'), 'version': 1,
                  'assessment_title': source_test.get('comment') or identifier,
                  'mode': 'automated', 'class': 'compliance', 'purpose': 'assessment',
                  'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'},
                  'tests': visitor.tests, 'evaluate': expression}
    for section in ('variables', 'shared_objects'):
        if getattr(visitor, section):
            assessment[section] = getattr(visitor, section)
    return assessment


def check_conversion(visitor, identifier, validator):
    """No exception means only that this stage succeeded, never scanner parity."""
    from validate_native_json_schemas import document_errors
    from v04_native_bundle_compiler import compile_assessment_program
    from audit_v04_eight_assessment_pilot import verify_program
    from v04_expanded_source_proof import ExpandedSource, ExpandedNative
    from v04_source_package_semantics import Unsupported, first_difference

    result = {'converted': False, 'schema_valid': False, 'compiled': False,
              'source_proof': 'NOT_RUN', 'diagnostics': []}
    stage = 'conversion'
    try:
        assessment = assessment_for(visitor, identifier)
        result.update(converted=True, authoring_sha256=digest({'assessment': assessment}))
        stage = 'schema'
        errors = list(document_errors(validator, {'assessment': assessment}))
        if errors:
            result['diagnostics'] = [{'stage': stage, 'path': list(e.absolute_path), 'message': e.message}
                                     for e in errors]
            return result
        result['schema_valid'] = True
        stage = 'compilation'
        program = compile_assessment_program(assessment)
        verify_program(assessment, program)
        result.update(compiled=True, program_sha256=digest(program), compiled_operands_verified=True)
    except (UnsupportedSource, ValueError) as error:
        result['diagnostics'].append({'stage': stage, 'message': str(error)})
        return result
    # The independent reader has its own bounded proof rules. Do not broaden
    # them, substitute compiler output, or count unsupported proof as success.
    try:
        original = ExpandedSource(visitor.source.components[visitor.component_id]).test(identifier)
        native_id = assessment['evaluate']['test']
        native = ExpandedNative(assessment).test(native_id)
        result['source_proof'] = 'PROVED' if original == native else 'MISMATCH'
        result['source_term_sha256'], result['native_term_sha256'] = digest(original), digest(native)
        if original != native:
            difference = first_difference(original, native)
            result['first_divergence'] = difference
            result['source_term'], result['native_term'] = original, native
            result['diagnostics'].append({'stage': 'source_proof', 'message': json.dumps(difference, sort_keys=True)})
    except Unsupported as error:
        result['source_proof'] = 'UNVERIFIABLE'
        result['diagnostics'].append({'stage': 'source_proof', 'message': str(error)})
    return result


def summarize(rows):
    by_capability = defaultdict(list)
    for row in rows:
        by_capability[row['capability'] or row['source_tag']].append(row)
    results = {}
    for capability, cases in sorted(by_capability.items()):
        diagnostics = Counter((d['stage'], d['message']) for r in cases for d in r['diagnostics'])
        results[capability] = {'tests': len(cases), 'scope': dict(Counter(r['scope'] for r in cases)),
            **{key: sum(bool(r[key]) for r in cases) for key in ('converted', 'schema_valid', 'compiled')},
            'source_proof': dict(sorted(Counter(r['source_proof'] for r in cases).items())),
            'diagnostics': [{'stage': s, 'message': m, 'occurrences': n}
                            for (s, m), n in sorted(diagnostics.items())]}
        blockers = Counter(message for r in cases for message in
                           {b['message'] for b in r.get('dependency_blockers', [])})
        results[capability]['closure_blockers'] = [{'message': m, 'tests': n} for m, n in sorted(blockers.items())]
    return results


def audit(directory, pin_path=PIN):
    from validate_native_json_schemas import build_validators
    pin = json.loads(pin_path.read_text())
    actual = file_inventory(directory)
    ensure(actual == pin['files'], 'pinned collection mismatch (missing, extra or changed files)')
    mappings = load_mappings()  # The existing admitted subset, not all mapped capabilities.
    admitted = {m['capability'] for m in mappings}
    validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
    started = time.perf_counter()
    documents, rows = [], []
    for name, raw in xml_documents(directory):
        root = ET.fromstring(raw)
        info = {'path': name, 'sha256': sha256(raw).hexdigest(), 'root': root.tag}
        documents.append(info)
        if root.tag != OVAL_ROOT:
            info['classification'] = 'reference/support (not OVAL definitions)'
            continue
        source = OvalDocument(root, name)
        graph = SourceInventory(source)
        nodes = {identifier: n for (component, identifier), n in graph.nodes.items()}
        original_tests = root.find('{' + OVAL + '}tests')
        ensure(sum(n['kind'] == 'test' for n in nodes.values()) ==
               (len(original_tests) if original_tests is not None else 0),
               f'Test inventory does not reconcile with original document: {name}')
        info.update(classification='OVAL definitions', nodes=nodes)
        for identifier, node in sorted(nodes.items()):
            if node['kind'] != 'test':
                continue
            dependencies, problems = closure(nodes, identifier)
            capability = node['capability']
            scope = ('in_scope' if capability in admitted else
                     'mapped_not_enabled' if capability and not capability.startswith('{') else 'unmapped_reference')
            row = {'document': name, 'test': identifier, 'source_tag': node['tag'], 'capability': capability,
                   'scope': scope, 'dependencies': dependencies, 'inventory_problems': problems,
                   'converted': False, 'schema_valid': False, 'compiled': False,
                   'source_proof': 'NOT_RUN', 'diagnostics': []}
            if scope == 'in_scope':
                visitor = AssessmentConverter(source, name, mappings)
                row.update(check_conversion(visitor, identifier, validator))
                # Probe every closure node, so the first failure cannot conceal
                # independent unsupported constructs further down the graph.
                blockers = []
                for dependency in dependencies:
                    blockers.extend(dependency_blockers(source, nodes[dependency], mappings))
                row['dependency_blockers'] = blockers
            else:
                row['diagnostics'].append({'stage': 'scope', 'message':
                    'capability not enabled in direct converter: ' + node['tag']})
            rows.append(row)
    return {'format': 'scap-ng/direct-oval-test-coverage/1', 'pin': {k: v for k, v in pin.items() if k != 'files'},
            'collection_files': len(actual), 'xml_documents': len(documents),
            'oval_documents': sum(d['root'] == OVAL_ROOT for d in documents),
            'source_parse_count': len(documents), 'tests': len(rows), 'elapsed_seconds': time.perf_counter() - started,
            'enabled_capabilities': sorted(admitted), 'summary': summarize(rows), 'documents': documents, 'cases': rows,
            'limitations': ['Synthetic single-Test Assessments; no XCCDF/Profile or complete Definition proof',
                'No scanner execution, external Variable binding or support payload execution',
                'Compilation is maintained Assessment-program compilation, not full Benchmark packaging',
                'No new capability support or conversion admission; independent proof failures remain visible']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.source_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: report[k] for k in ('collection_files', 'xml_documents', 'oval_documents', 'tests', 'elapsed_seconds')}, indent=2))
    # A coverage corpus expects unsupported input. Infrastructure errors raise;
    # unsupported cases are durable evidence, not a falsely green acceptance.


if __name__ == '__main__':
    main()
