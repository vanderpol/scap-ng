"""Original applicability bindings, kept separate from Rule criteria truth.

Inventory only. Retain logical-test operator/negation trees verbatim; do not
replace CPE names with filename guesses or merge applicability into requirements.
"""
from v04_direct_scap_source import OVAL, XLINK, UnsupportedSource, digest, xml_identity

LANG = '{http://cpe.mitre.org/language/2.0}'
DICT = '{http://cpe.mitre.org/dictionary/2.0}'
CAT = '{urn:oasis:names:tc:entity:xmlns:xml:catalog}'


def platform_inventory(source, inventory):
    dictionaries, records = {}, {}
    for component, root in source.components.items():
        if root.tag != DICT + 'cpe-list':
            continue
        references = [r for r in source.references.values() if r.get(XLINK) == '#' + component]
        catalog, errors = {}, {}
        for reference in references:
            for uri in reference.iter(CAT + 'uri'):
                try:
                    target = source.component_for_reference(uri.get('uri', '').lstrip('#'))
                    name = uri.get('name')
                    if name in errors or (name in catalog and catalog[name] != target):
                        catalog.pop(name, None)
                        errors[name] = 'ambiguous applicability catalog entry: ' + str(name)
                    else:
                        catalog[name] = target
                except UnsupportedSource as error:
                    errors[uri.get('name')] = str(error)
        for item in root.iter(DICT + 'cpe-item'):
            dictionaries.setdefault(item.get('name'), []).append((item, catalog, errors))

    def check(node, catalog, errors):
        href = node.get('href')
        definition = node.get('id-ref') or (node.text or '').strip()
        component = catalog.get(href)
        result = {'original_attributes': dict(node.attrib), 'href': href,
                  'definition': definition, 'component': component, 'dependencies': [], 'problems': []}
        if node.get('system') != OVAL:
            result['problems'].append('unsupported applicability check system: ' + str(node.get('system')))
        elif component is None:
            result['problems'].append(errors.get(href, 'unresolved applicability catalog href: ' + str(href)))
        else:
            nodes, problems = inventory.closure(component, definition)
            result['dependencies'] = [[n['component'], n['id']] for n in nodes]
            result['problems'].extend(problems)
        return result

    def dictionary(name):
        entries = dictionaries.get(name, [])
        return {'identity': name, 'source_kind': 'CPE dictionary name',
                'problems': [] if len(entries) == 1 else ['CPE name does not resolve to one original dictionary item'],
                'checks': [check(c, catalog, errors) for item, catalog, errors in entries
                           for c in item.findall(DICT + 'check')],
                'original_trees': [xml_identity(item) for item, _, _ in entries]}

    for platform in source.benchmark.iter(LANG + 'platform'):
        identity = '#' + platform.get('id')
        checks = [check(n, source.catalog, {k: v['message'] for k, v in source.catalog_errors.items()})
                  for n in platform.iter(LANG + 'check-fact-ref')]
        fact_names = [n.get('name') for n in platform.iter(LANG + 'fact-ref')]
        for name in fact_names:
            records.setdefault(name, dictionary(name))
        records[identity] = {'identity': identity, 'source_kind': 'CPE language platform',
                             'original_tree': xml_identity(platform), 'checks': checks,
                             'dictionary_dependencies': fact_names, 'problems': []}
    for node in source.benchmark.iter('{http://checklists.nist.gov/xccdf/1.2}platform'):
        identity = node.get('idref')
        if identity not in records:
            records[identity] = dictionary(identity)
    for identity, record in records.items():
        checks = record['checks'] + [c for name in record.get('dictionary_dependencies', [])
                                    for c in records[name]['checks']]
        dependencies = {tuple(ref) for c in checks for ref in c['dependencies']}
        record['problems'].extend(p for name in record.get('dictionary_dependencies', [])
                                  for p in records[name]['problems'])
        record['problems'].extend(p for c in checks for p in c['problems'])
        record['dependencies'] = [list(ref) for ref in sorted(dependencies)]
        record['required_capabilities'] = sorted({inventory.nodes[ref]['capability'] for ref in dependencies
                                                  if inventory.nodes[ref]['capability']})
        record['sha256'] = digest(record)
    return records
