"""Generate proposal-only semantic research from reviewed, source-linked records."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'independent.shellcommand', 'windows.registry', 'unix.file', 'windows.file',
            'windows.service', 'linux.rpminfo', 'linux.partition', 'independent.textfilecontent'}


def load(name):
    return json.loads((ROOT / 'docs/metadata' / name).read_text(encoding='utf-8'))


def validate(research, vectors, content, lineage):
    from developer_guide import pointer
    if research['status'] != 'research_not_adopted' or vectors['status'] != 'research_not_adopted':
        raise ValueError('Research must remain separate from adopted semantics')
    if set(research['capabilities']) != EXPECTED or set(content['capabilities']) != EXPECTED:
        raise ValueError('Semantic research must cover exactly the eight requested capabilities')
    ids = set()
    for case in vectors['vectors']:
        cap = case['capability']
        if case['id'] in ids or cap not in EXPECTED:
            raise ValueError('Invalid semantic vector identity')
        if case['topic'] not in {topic['id'] for topic in research['capabilities'][cap]['topics']}:
            raise ValueError('Cross-capability vector topic')
        if case['example'] != research['capabilities'][cap]['example']:
            raise ValueError('Vector example does not match its capability')
        ids.add(case['id'])
        if case['status'] != 'proposed_not_scanner_verified':
            raise ValueError('Proposed outcomes cannot claim scanner qualification')
        if case['proposed_outcome'] not in {'true', 'false', 'error', 'unknown', 'unresolved'}:
            raise ValueError('Invalid proposed outcome')
    for cap, record in research['capabilities'].items():
        if record['runtime_qualification'] != 'not_established' or record['status'] != 'research_recommendations_not_adopted':
            raise ValueError('Research cannot silently qualify or adopt a contract')
        for reference in record['native_refs']:
            filename, fragment = reference.split('#')
            path = ROOT / filename
            if not path.resolve().is_relative_to(ROOT / 'schema'):
                raise ValueError('Native facts must reference the pinned schema tree')
            pointer(json.loads(path.read_text(encoding='utf-8')), fragment)
        if not record['legacy_nodes'] or any(node not in lineage['nodes'] or not node.startswith(cap + '/')
                                            for node in record['legacy_nodes']):
            raise ValueError('Missing or cross-capability legacy source provenance')
        for topic in record['topics']:
            if topic['disposition'] != 'proposal_not_native_requirement' or not all(
                    topic.get(key) for key in ('gap', 'recommendation', 'compatibility')):
                raise ValueError('Gap needs a separately classified recommendation and compatibility statement')
        example = ROOT / record['example']
        if json.loads(example.read_text())['assessment']['tests']['sample-test']['capability'] != cap:
            raise ValueError('Example capability mismatch')


def render(version, frontmatter, table):
    research = load('developer-guide-semantic-research.json')
    vectors = load('developer-guide-semantic-vectors.json')
    content = load('developer-guide-content-audit.json')
    lineage = load('developer-guide-oval-audit.json')
    validate(research, vectors, content, lineage)
    pages = {}
    for family in sorted({cap.split('.')[0] for cap in EXPECTED}):
        lines = [frontmatter(f'{family} semantic contract research', version),
                 '**Recommendations only; not adopted native behavior.** Expected outcomes below are proposed '
                 'regression oracles, not scanner results. Frozen schema acceptance/rejection remains unchanged. '
                 '[Evidence, compatibility and reproduction](../developer-guide/semantic-research.md).\n\n']
        for cap, record in sorted(research['capabilities'].items()):
            if cap.split('.')[0] != family:
                continue
            lines += [f'## {cap}\n\n', '**Recorded native contract:** ' + record['native_facts'] + '\n\n',
                      '**Legacy observations, not normative:** ' + record['legacy_observations'] + '\n\n',
                      'Native sources: ' + ', '.join(f'[{ref.split("#")[0].split("/")[-1]}](../../{ref})'
                                                     for ref in record['native_refs']) + '.\n\n',
                      'Legacy audit nodes: ' + ', '.join(f'`{node}`' for node in record['legacy_nodes']) +
                      ' ([pinned XSD inventory](../metadata/developer-guide-oval-audit.json)).\n\n']
            result = content['capabilities'][cap]
            lines += [f'**Converted-content comparison:** {result["counts"].get("tests", 0)} historical Test occurrences; '
                      f'{len(result["examples"])} pinned specimens with original signed-source dependencies. '
                      'These are historical grammar, not current validation or scanner proof. '
                      '[Content evidence](../metadata/developer-guide-content-audit.json).\n\n']
            for specimen in result['examples']:
                lines += ['Historical Object (preserved spelling):\n\n```json\n' +
                          json.dumps(specimen['object'], sort_keys=True, ensure_ascii=False) + '\n```\n\n']
            lines += [f'[Research Assessment example](../../{record["example"]}) — structurally validated only.\n\n']
            for topic in record['topics']:
                lines += [f'### {topic["id"]}\n\n', '**Gap:** ' + topic['gap'] + '\n\n',
                          '**Recommendation:** ' + topic['recommendation'] + '\n\n',
                          '**Compatibility:** ' + topic['compatibility'] + '\n\n']
                if topic['alternatives']:
                    lines += ['Alternatives: ' + ' '.join(topic['alternatives']) + '\n\n']
            cases = [case for case in vectors['vectors'] if case['capability'] == cap]
            lines += ['### Proposed regression expectations\n\n',
                      'Each row references the research example; explicit input flags or selectors identify a variant. '
                      '`unresolved` means a contract-dependent scenario or different requirement must be selected before '
                      'an executable native outcome can be asserted. Full input fixtures are in the '
                      '[vector ledger](../metadata/developer-guide-semantic-vectors.json).\n\n',
                      table(['Vector', 'Proposed outcome', 'Expected evidence / assumption'],
                            [(case['id'], case['proposed_outcome'], case['expected_evidence']) for case in cases]), '\n']
        pages[f'developer-contract-research-{family}.md'] = ''.join(lines).rstrip() + '\n'
    index = [frontmatter('Semantic contract research index', version),
             'Eight capabilities reviewed; all runtime qualification remains **not established**. '
             'Recommendations require the decisions identified in the [decision packet](../developer-guide/semantic-research.md).\n\n',
             table(['Capability', 'Historical Test occurrences', 'Pinned specimens', 'Immediate owner decision'],
                   [(f'[{cap}](developer-contract-research-{cap.split(".")[0]}.md#{cap.replace(".", "")})',
                     content['capabilities'][cap]['counts'].get('tests', 0),
                     len(content['capabilities'][cap]['examples']),
                     'yes' if record['owner_decision'] else 'no; continue acquisition research')
                    for cap, record in sorted(research['capabilities'].items())]),
             f'\n{len(vectors["vectors"])} proposed runtime vectors and {len(vectors["schema_probes"])} '
             'frozen-schema probes are kept separate. No compiler or scanner equivalence is inferred.\n']
    pages['developer-contract-research-index.md'] = ''.join(index)
    return pages
