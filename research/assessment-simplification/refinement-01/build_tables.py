"""Adapt prior proposal rows into small typed authoring tables and emit evidence.

Only this fixture builder reads snapshots. The expander itself operates solely
on authored tables. XML comparison uses a separate bounded source projection.
"""
import hashlib
import json
from pathlib import Path
import yaml
from table_expansion import expand
from source_contracts import project_xml, project_native, assert_and_tree, assert_source_and_tree

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    (HERE/'tables').mkdir(exist_ok=True)
    (HERE/'expanded').mkdir(exist_ok=True)
    (HERE/'evidence').mkdir(exist_ok=True)
    report = {'base_commit': '5a36e7b1be002b76f5501e500be2eeb1e0a17764', 'cases': [],
              'limits': 'Bounded static contracts plus supplied observation tests, not target scanner equivalence.'}
    for rid, kind, filename in [('SV-258179', 'audit_patterns', 'audit-pattern-table'),
                                ('SV-258236', 'crypto_backends', 'crypto-backends')]:
        old_path = STUDY/'proposals'/f'{filename}.proposal.yaml'
        old = yaml.safe_load(old_path.read_text())['assessment']
        before_path = next((STUDY/'samples/rhel_9/assessments/automated').glob('*'+rid+'*'))
        before = yaml.safe_load(before_path.read_text())
        rows = next(iter(old['tests'].values()))['rows']
        if kind == 'audit_patterns':
            defaults = {'full_path': '/etc/audit/audit.rules', 'existence': 'all', 'match': 'all',
                        'instance': rows[0]['instance'], 'collect': rows[0]['collection_options'],
                        'filesystem': rows[0]['filesystem']}
            templates = {k: v['expression']['literal'] for k, v in old['variables'].items()}
            new_rows = []
            for test_name, row in zip(before['assessment']['tests'], rows, strict=True):
                # Identity intentionally retains the two distinct b64-named anomalous rows.
                r = {k: row[k] for k in ('template', 'syscall', 'arch')}
                r = {'id': test_name.removeprefix('test-'), **r}
                if row['existence'] != defaults['existence']:
                    r['existence'] = row['existence']
                for key, orig in [('instance', 'instance'), ('collect', 'collection_options'), ('filesystem', 'filesystem')]:
                    if row[orig] != defaults[key]:
                        raise ValueError('heterogeneous source needs a new explicit row override')
                new_rows.append(r)
        else:
            defaults = {'capability': 'unix.symlink', 'existence': 'some', 'match': 'all'}
            templates = {}
            new_rows = []
            for row in rows:
                r = {'id': Path(row['full_path']).stem, **{k: row[k] for k in ('full_path', 'field', 'expected')}}
                if row['capability'] != defaults['capability']:
                    r['capability'] = row['capability']
                new_rows.append(r)
        table = {'kind': kind, 'id': 'research.refinement.'+rid, 'defaults': defaults,
                 'templates': templates, 'rows': new_rows}
        table_path = HERE/'tables'/f'{rid}.yaml'
        table_path.write_text('# EXPERIMENTAL finite publisher-owned table; not runtime NG grammar.\n'+yaml.safe_dump(table, sort_keys=False))
        expanded = expand(table)
        expanded_path = HERE/'expanded'/f'{rid}.assessment.yaml'
        expanded_path.write_text('# EXPERIMENTAL expansion into ordinary Assessment nodes; not approved content.\n'+yaml.safe_dump(expanded, sort_keys=False))
        xml_path = STUDY/'evidence/rhel_9'/rid/'source-oval.xml'
        graph = json.loads((xml_path.parent/'graph.json').read_text())
        tree = assert_source_and_tree(xml_path, graph['closures'][0]['seed']['name'])
        source_by_id = dict(project_xml(xml_path))
        source = [(sid, source_by_id[sid]) for sid in tree]
        emitted = project_native(expanded)
        # Match logical traversal order, never incidental XML storage order.
        if [r for _, r in source] != [r for _, r in emitted]:
            raise ValueError('expanded contracts differ from original XML: '+rid)
        assert_and_tree(before)
        assert_and_tree(expanded)
        mapping = [{'source_test': sid, 'generated_test': name, 'contract_sha256':
                    hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()}
                   for (sid, contract), (name, _) in zip(source, emitted, strict=True)]
        report['cases'].append({'rule': rid, 'xml_sha256': digest(xml_path),
            'before_sha256': digest(before_path), 'prior_proposal_sha256': digest(old_path),
            'table_sha256': digest(table_path), 'expanded_sha256': digest(expanded_path),
            'rows': len(rows), 'source_and_tree_leaves': len(tree), 'mapping': mapping,
            'before_named_nodes': sum(len(before['assessment'].get(k, {})) for k in ('objects','states','variables','tests')),
            'expanded_named_nodes': sum(len(expanded['assessment'].get(k, {})) for k in ('objects','states','variables','tests')),
            'before_bytes': before_path.stat().st_size, 'table_bytes': table_path.stat().st_size,
            'before_lines': len(before_path.read_text().splitlines()), 'table_lines': len(table_path.read_text().splitlines()),
            'static_contract_equal': True})
    (HERE/'evidence/table-contracts.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps([{k:v for k,v in c.items() if k != 'mapping'} for c in report['cases']], indent=2))


if __name__ == '__main__':
    main()
