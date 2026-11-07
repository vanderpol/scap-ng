"""Shared author/scanner documentation projection; never a semantic validator."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PILOTS = {'windows', 'unix', 'independent'}


def pointer(document, fragment):
    """Resolve an RFC 6901 pointer without accepting a fallback value."""
    if not fragment.startswith('/'):
        raise ValueError('Contract reference must be an absolute JSON pointer')
    for token in fragment[1:].split('/'):
        if re.search(r'~(?![01])', token):
            raise ValueError('Invalid JSON pointer escape')
        token = token.replace('~1', '/').replace('~0', '~')
        if isinstance(document, list) and not re.fullmatch(r'0|[1-9][0-9]*', token):
            raise ValueError('Invalid JSON pointer array index')
        document = document[int(token)] if isinstance(document, list) else document[token]
    return document


def model(mappings, proposal):
    if proposal.get('format') != 'scap-ng/schema-documentation-pilot/2':
        raise ValueError('Unsupported documentation proposal format')
    if proposal['status'] != 'proposal_only_not_part_of_frozen_0.4_schema':
        raise ValueError('Documentation pilot must not claim normative 0.4 status')
    names = {item['capability'] for _, _, item in mappings}
    if set(proposal['capabilities']) - names:
        raise ValueError('Orphan capability annotations')
    contracts = json.loads((ROOT / 'schema/native-selector-contracts.json').read_text(encoding='utf-8'))
    lineage = json.loads((ROOT / 'docs/metadata/developer-guide-oval-audit.json').read_text(encoding='utf-8'))
    if lineage['status'] != 'legacy_research_not_native_contract':
        raise ValueError('OVAL lineage must remain non-normative')
    overlays = json.loads((ROOT / 'schema/native-selector.schema.json').read_text(encoding='utf-8'))['$defs']
    result = []
    for group, path, item in sorted(mappings, key=lambda row: row[2]['capability']):
        name, native = item['capability'], item.get('native', {})
        annotation = proposal['capabilities'].get(name, {})
        platform = name.split('.')[0]
        if annotation and annotation.get('platform') != platform:
            raise ValueError(f'{name}: annotation platform mismatch')
        selectors = native.get('selector_map', {})
        parameters = native.get('collection_parameters', {})
        properties = annotation.get('properties', {})
        extras = set(properties) - (set(selectors) | set(parameters))
        if extras:
            raise ValueError(f'{name}: undocumented authoring fields {sorted(extras)}')
        for field, value in sorted(properties.items()):
            scanner = value['x-scap-ng-scanner']
            if (not value.get('description') or scanner['documentation_status'] != 'partial'
                    or not scanner.get('known_contract') or not scanner.get('open_question')):
                raise ValueError(f'{name}.{field}: missing known/pending separation')
            if scanner.get('qualification_status') != 'not_established':
                raise ValueError(f'{name}.{field}: documentation cannot qualify a scanner')
            sources = scanner.get('source_lineage', [])
            if not sources:
                raise ValueError(f'{name}.{field}: missing source lineage')
            for source in sources:
                node = source['audit_node']
                if (source['disposition'] != 'legacy_candidate' or node not in lineage['nodes']
                        or not node.startswith(name + '/')):
                    raise ValueError(f'{name}.{field}: invalid legacy lineage {node}')
            refs = scanner.get('contract_refs', [])
            if not refs:
                raise ValueError(f'{name}.{field}: missing contract references')
            for ref in refs:
                # Each annotation is anchored to the current capability mapping only.
                try:
                    pointer(item, ref)
                except (KeyError, IndexError, ValueError, TypeError) as error:
                    raise ValueError(f'{name}.{field}: invalid contract reference {ref}') from error
        resolved = contracts['resolved'].get(name, {}).get('selectors', {})
        fields = sorted(set(native.get('state_field_map', {}).values()))
        result.append(dict(name=name, platform=platform, group=group,
                           path=path.relative_to(ROOT).as_posix(), native=native,
                           selectors=selectors, parameters=parameters, fields=fields,
                           resolved=resolved, annotation=annotation,
                           rules=item.get('semantic_validator_rules', []),
                           overlay=overlays.get(name.replace('.', '_') + '_object')))
    return result


def render(version, mappings, proposal, frontmatter, table):
    records = model(mappings, proposal)
    pages, inventory = {}, []
    platforms = sorted({record['platform'] for record in records})
    for platform in platforms:
        entries = [record for record in records if record['platform'] == platform]
        lines = [frontmatter(f'{platform} application developer guide', version),
                 '**Proposal only:** Curated annotations remain outside the frozen schema. '
                 'Structural facts below come from the same model for authors and implementers. '
                 'Collection behavior is not yet qualified.\n\n',
                 '[Common contracts and reading order](../developer-guide/README.md) · '
                 '[Platform index](developer-guide-index.md) · [Gap inventory](developer-guide-gaps.json). '
                 'Namespace families do not guarantee operating-system availability. '
                 'Acquisition, absence/error mapping and runtime conformance remain unqualified '
                 'for every section. Mapping requirements and shared schema acceptance are distinct.\n\n']
        for record in entries:
            name, native = record['name'], record['native']
            annotation = record['annotation']
            properties = annotation.get('properties', {})
            lines += [f'## {name}\n\n',
                      f'**Scope:** {record["group"]}. **Authority:** '
                      f'[frozen mapping](../../{record["path"]}).\n\n']
            rows = []
            for field in sorted(record['selectors']):
                contract = record['resolved'].get(field, {})
                rows.append((field, properties.get(field, {}).get('description', 'not yet reviewed'),
                             ', '.join(contract.get('value_types', [])) or 'unresolved',
                             ', '.join(contract.get('operators', [])) or 'unresolved',
                             'yes' if field in native.get('nullable_selectors', []) else 'no',
                             ', '.join(native.get('selector_value_enums', {}).get(field, [])) or '—'))
            if rows:
                lines += ['Operators/types: [resolved selector contracts](../../schema/native-selector-contracts.json); unresolved entries need review.\n\n']
                lines += ['### Object selectors\n\n', table(
                    ['Authored name', 'Author help', 'Literal types', 'Native operators', 'Nullable', 'Enum'], rows)]
                alternatives = native.get('object_selector_alternatives', [])
                if alternatives:
                    lines += ['\nMapping selector alternatives: ' + ' OR '.join(
                        ' + '.join(f'`{f}`' for f in alternative) for alternative in alternatives) +
                        '. These mapping requirements are distinct from JSON Schema required-property checks.\n']
            overlay = record['overlay']
            if overlay:
                inline = next(part for part in overlay['oneOf'] if 'properties' in part)
                controls = sorted(set(inline['properties']) - set(record['selectors']) - {'capability'})
                lines += ['\nClosed Object overlay: [native-selector.schema.json](../../schema/native-selector.schema.json). '
                          'Additional declared properties: ' + ', '.join(
                              f'[`{c}`](../../schema/{inline["properties"][c].get("$ref", "native-selector.schema.json")})'
                              for c in controls) +
                          '. Presence here does not assert a complete runtime contract.\n']
            if not overlay:
                lines += ['\nNo dedicated selector overlay is recorded; consult the shared schema and mapping separately.\n']
            if record['parameters']:
                lines += ['\n### Collection parameters\n\n', table(
                    ['Name', 'Type', 'Required by mapping', 'Variable allowed', 'Enum', 'Description'],
                    [(field, info.get('type', 'not recorded'), str(info.get('required', False)).lower(),
                      str(info.get('allow_variable', False)).lower(), ', '.join(map(str, info.get('enum', []))) or '—',
                      properties.get(field, {}).get('description', info.get('description', 'not recorded')))
                     for field, info in sorted(record['parameters'].items())])]
            if record['fields']:
                lines += ['\n### Evidence and comparison fields\n\n', table(
                    ['Native field', 'Source field(s)', 'Collected datatype(s)', 'Comparison datatype override', 'Enum'],
                    [(field, ', '.join(sorted(key for key, value in native['state_field_map'].items() if value == field)),
                      ', '.join(native.get('field_datatypes', {}).get(field, [])) or 'unresolved',
                      ', '.join(native.get('state_field_datatypes', {}).get(field, [])) or 'none separately recorded',
                      ', '.join(map(str, native.get('state_value_enums', {}).get(field, []))) or '—')
                     for field in record['fields']])]
            if annotation:
                lines += ['\n### Reviewed pilot notes\n\n', table(
                    ['Object field', 'Known scanner contract', 'Pending research', 'Mapping pointer(s)', 'Legacy source node(s)'],
                    [(field, value['x-scap-ng-scanner']['known_contract'],
                      value['x-scap-ng-scanner']['open_question'],
                      ', '.join(value['x-scap-ng-scanner']['contract_refs']),
                      ', '.join(source['audit_node'] for source in value['x-scap-ng-scanner']['source_lineage']))
                     for field, value in sorted(annotation['properties'].items())])]
                lines += ['\n[OVAL source review and provenance](../developer-guide/pilot-review.md). '
                          'Legacy details are research candidates, not additional native requirements.\n\n']
                example = ROOT / 'docs/developer-guide/examples' / (name + '.json')
                lines += ['### Structural example\n\n', '```json\n' + example.read_text(encoding='utf-8') + '```\n\n',
                          'Illustrative schema fixture only; no host collection or scanner conformance is asserted.\n\n']
            if record['rules']:
                lines += ['\n### Recorded semantic rules\n\n']
                lines += [f'- `{rule["id"]}`: {rule["rule"]}\n' for rule in record['rules']]
            lines += ['\n']
            inventory.append(dict(capability=name, platform=platform, scope=record['group'],
                                  priority=('P0' if annotation else 'P4' if record['group'] == 'experimental'
                                            else 'P2' if name in {'windows.file', 'windows.service', 'linux.rpminfo',
                                                                 'linux.partition', 'independent.textfilecontent'} else 'P3'),
                                  reviewed_pilot=bool(annotation),
                                  selectors=len(record['selectors']),
                                  unresolved_selectors=sorted(set(record['selectors']) - set(record['resolved'])),
                                  result_fields=len(record['fields']),
                                  missing_result_datatypes=[f for f in record['fields'] if f not in native.get('field_datatypes', {})],
                                  annotated_author_fields=len(annotation.get('properties', {})),
                                  qualification='not_established',
                                  object_validation='closed_overlay' if record['overlay'] else 'no_dedicated_selector_overlay',
                                  gaps=annotation.get('gaps', ['acquisition', 'absence_errors', 'runtime_vectors'])))
        suffix = '-pilot' if platform in PILOTS else ''
        pages[f'developer-guide-{platform}{suffix}.md'] = ''.join(lines).rstrip() + '\n'
    index = [frontmatter('Application developer guide index', version),
             'Read the [common contracts](../developer-guide/README.md), then the namespace families '
             'your application implements. Independent capabilities are optional shared capabilities, '
             'not an instruction to read UNIX documentation. Supported catalog status does not qualify a scanner.\n\n',
             table(['Family', 'Supported', 'Experimental', 'Curated pilots'],
                   [(f'[{p}](developer-guide-{p}{"-pilot" if p in PILOTS else ""}.md)',
                     sum(r['platform'] == p and r['group'] == 'supported' for r in records),
                     sum(r['platform'] == p and r['group'] == 'experimental' for r in records),
                     sum(r['platform'] == p and bool(r['annotation']) for r in records)) for p in platforms]),
             '\n[Expansion priorities and schedule](../developer-guide/plan.md) · '
             '[Proposed annotation ownership](../developer-guide/annotation-proposal.md).\n']
    pages['developer-guide-index.md'] = ''.join(index)
    pages['developer-guide-gaps.json'] = json.dumps(dict(
        format='scap-ng/developer-guide-gaps/1',
        summary=dict(capabilities=len(records), supported=sum(r['group'] == 'supported' for r in records),
                     experimental=sum(r['group'] == 'experimental' for r in records),
                     platform_families=len(platforms), reviewed_pilots=sum(bool(r['annotation']) for r in records),
                     qualified=0, selectors=sum(r['selectors'] for r in inventory),
                     missing_result_datatypes=sum(len(r['missing_result_datatypes']) for r in inventory),
                     unresolved_selectors=sum(len(r['unresolved_selectors']) for r in inventory)),
        capabilities=inventory), indent=2, ensure_ascii=False) + '\n'
    return pages
