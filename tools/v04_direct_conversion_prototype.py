#!/usr/bin/env python3
"""Isolated two-Rule SCAP 1.4 -> 0.4 spike, NOT the production converter (#251).

Only scalar Registry/shellcommand, constants, concat, regex_capture and private
object_component dependencies are admitted. No old NG format or ID dispatch.
XCCDF output is a labeled miniature wrapper, not a whole policy conversion.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DS = 'http://scap.nist.gov/schema/scap/source/1.2'
X = 'http://checklists.nist.gov/xccdf/1.2'
O = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'
HREF = '{http://www.w3.org/1999/xlink}href'
FOUND = {'at_least_one_exists': 'one_or_more', 'none_exist': 'none',
         'only_one_exists': 'exactly_one', 'any_exist': 'may_be_absent'}
MATCH = {'all': 'every', 'at least one': 'one_or_more', 'none satisfy': 'none', 'only one': 'exactly_one'}
OPS = {'equals': 'equals', 'not equal': 'not_equal', 'pattern match': 'matches_regex',
       'case insensitive equals': 'case_insensitive_equals'}


def require(ok, message):
    if not ok:
        raise ValueError('direct prototype: ' + message)


def local(n):
    return n.tag.rsplit('}', 1)[-1]


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def term(n):
    return [n.tag, sorted(n.attrib.items()), n.text if not len(n) else None, [term(c) for c in n]]


def attrs(n, allowed):
    require(set(n.attrib) <= set(allowed), local(n) + ' unsupported attributes ' + str(sorted(set(n.attrib) - set(allowed))))


def name(n, suffix):
    title = n.get('comment') or n.findtext('{' + X + '}title') or n.findtext('{' + O + '}metadata/{' + O + '}title') or local(n)
    slug = re.sub('[^a-z0-9]+', '-', title.lower()).strip('-')[:70]
    return slug + '-' + digest(n.get('id'))[:8] + '-' + suffix


class Model:
    """One XML parse per member; one scoped index per component, never a global OVAL ID map."""
    def __init__(self, path, expected_sha256):
        start = time.perf_counter()
        self.path = Path(path)
        raw = self.path.read_bytes()
        require(sha256(raw).hexdigest() == expected_sha256, 'source ZIP SHA-256 mismatch')
        self.zip_sha256 = expected_sha256
        with zipfile.ZipFile(self.path) as z:
            require(z.testzip() is None and len(z.namelist()) == len(set(z.namelist())), 'ZIP integrity')
            members = [n for n in z.namelist() if n.endswith('.xml')]
            require(len(members) == 1, 'one complete SCAP XML member required by bounded spike')
            self.member = members[0]
            xml = z.read(self.member)
        self.xml_sha256 = sha256(xml).hexdigest()
        self.root = ET.fromstring(xml)
        require(self.root.tag == '{' + DS + '}data-stream-collection', 'not a SCAP datastream collection')
        self.parse_count = 1
        self.index()
        self.parse_index_seconds = time.perf_counter() - start

    def index(self):
        self.components, self.indices, self.component_hashes = {}, {}, {}
        for c in self.root.findall('{' + DS + '}component'):
            ident = c.get('id')
            require(ident and ident not in self.components and len(c) == 1, 'duplicate/invalid SCAP component')
            self.components[ident] = c[0]
            idx = {}
            for n in c[0].iter():
                if n.get('id'):
                    require(n.get('id') not in idx, 'duplicate ID inside component ' + ident)
                    idx[n.get('id')] = n
            self.indices[ident] = idx
            self.component_hashes[ident] = digest(term(c[0]))
        streams = self.root.findall('{' + DS + '}data-stream')
        require(len(streams) == 1 and streams[0].get('scap-version') == '1.4', 'one SCAP 1.4 stream required')
        self.refs = {n.get('id'): n for n in streams[0].iter() if n.tag == '{' + DS + '}component-ref'}
        require(all(self.refs) and len(self.refs) == sum(n.tag == '{' + DS + '}component-ref' for n in streams[0].iter()), 'missing/duplicate stream reference ID')
        checklists = streams[0].findall('{' + DS + '}checklists/{' + DS + '}component-ref')
        require(len(checklists) == 1, 'one checklist required')
        self.checklist = checklists[0]
        self.benchmark_component = self.resolve(self.checklist.get('id'))
        self.benchmark = self.components[self.benchmark_component]
        require(self.benchmark.tag == '{' + X + '}Benchmark', 'checklist is not XCCDF 1.2')
        self.catalog = {}
        for n in self.checklist.findall('.//{urn:oasis:names:tc:entity:xmlns:xml:catalog}uri'):
            require(n.get('name') not in self.catalog and n.get('uri', '').startswith('#'), 'ambiguous/nonlocal checklist catalog')
            self.catalog[n.get('name')] = self.resolve(n.get('uri')[1:])
        self.parents = {child: parent for parent in self.benchmark.iter() for child in parent}
        self.rules = {n.get('id'): n for n in self.benchmark.iter() if n.tag == '{' + X + '}Rule'}

    def resolve(self, ref):
        require(ref in self.refs, 'unresolved datastream component-ref ' + str(ref))
        href = self.refs[ref].get(HREF, '')
        require(href.startswith('#') and href[1:] in self.components, 'unresolved/nonlocal component href ' + href)
        return href[1:]

    def check(self, rule):
        require(not rule.findall('{' + X + '}complex-check'), 'XCCDF complex-check unsupported')
        checks = [c for c in rule if c.tag == '{' + X + '}check' and c.get('system') == O]
        links = []
        for c in checks:
            attrs(c, {'system', 'selector'})
            require(len(c) == 1 and local(c[0]) == 'check-content-ref', 'OVAL check imports/exports unsupported')
            attrs(c[0], {'href', 'name'})
            require(c[0].get('href') in self.catalog, 'unresolved checklist catalog href')
            links.append((self.catalog[c[0].get('href')], c[0].get('name')))
        require(links and len(set(links)) == 1, 'distinct/missing OVAL check alternatives unsupported')
        return links[0]

    def selected(self, rule, profile=None):
        overrides = {}
        if profile is not None:
            attrs(profile, {'id'})
            for c in profile:
                require(local(c) in ('title', 'description', 'select'), 'Profile inheritance/refinement unsupported')
                if local(c) == 'select':
                    attrs(c, {'idref', 'selected'})
                    require(c.get('selected') in ('true', 'false'), 'Profile selected must be explicit boolean')
                    require(c.get('idref') in self.indices[self.benchmark_component], 'unresolved Profile idref')
                    require(local(self.indices[self.benchmark_component][c.get('idref')]) in ('Group', 'Rule'), 'Profile target is not Group/Rule')
                    require(c.get('idref') not in overrides, 'repeated Profile target unsupported')
                    overrides[c.get('idref')] = c.get('selected') == 'true'
        selected, n = True, rule
        while n is not self.benchmark:
            require(n.get('selected', 'true') in ('true', 'false'), 'noncanonical source selected lexical unsupported')
            selected &= overrides.get(n.get('id'), n.get('selected', 'true') == 'true')
            n = self.parents[n]
        return selected


class Conversion:
    """Single recursive source-dependency visitor, scoped to one Assessment."""
    def __init__(self, model, component, mappings):
        self.model, self.component, self.mappings = model, component, mappings
        self.active, self.used, self.variables, self.tests = set(), {}, {}, {}

    def capability(self, node, kind):
        matches = [m for m in self.mappings if node.tag == '{' + m['source']['namespace'] + '}' + m['source'].get(kind, '')]
        require(len(matches) == 1, 'unsupported capability ' + node.tag)
        return matches[0]

    def visit(self, ident, kind):
        require(ident not in self.active, 'cyclic OVAL dependency ' + str(ident))
        idx = self.model.indices[self.component]
        require(ident in idx, 'unresolved component-scoped OVAL dependency ' + str(ident))
        n = idx[ident]
        require(local(n).endswith('_' + kind) or local(n) == kind, 'wrong dependency kind ' + str(ident))
        require(kind not in ('definition', 'variable') or n.tag.startswith('{' + O + '}'), 'Definition/Variable namespace')
        require(kind != 'object' or ident not in self.used, 'shared Object boundary outside bounded prototype')
        attrs(n, {'id', 'version', 'comment'} | {
            'definition': {'class'}, 'variable': {'datatype'}, 'state': {'operator'},
            'test': {'check', 'check_existence', 'state_operator'}, 'object': set()}[kind])
        self.active.add(ident)
        self.used[ident] = {'kind': kind, 'sha256': digest(term(n)),
                            'native_id': name(n, kind) if kind in ('test', 'variable') else None,
                            'representation': 'named component' if kind in ('test', 'variable') else 'inline dependency expression'}
        if kind == 'definition':
            criteria = n.findall('{' + O + '}criteria')
            require(len(criteria) == 1, 'Definition criteria boundary')
            result = self.criteria(criteria[0])
        elif kind == 'variable':
            require(n.get('datatype') in ('string', 'int', 'boolean'), 'Variable datatype unsupported')
            require(local(n) == 'constant_variable' or (local(n) == 'local_variable' and len(n) == 1), 'external/malformed Variable unsupported')
            if local(n) == 'constant_variable':
                require(len(n) > 0 and all(c.tag == '{' + O + '}value' and not c.attrib and not len(c) for c in n), 'constant Variable child')
                result = [self.scalar(n.get('datatype'), c.text or '') for c in n]
                self.used[ident].update(native_id=None, representation='typed literal array; source var_check preserved at consumer')
            else:
                self.variables[name(n, kind)] = {'kind': 'local',
                    'datatype': 'integer' if n.get('datatype') == 'int' else n.get('datatype'), 'expression': self.function(n[0])}
                result = {'variable': name(n, kind)}
        elif kind == 'object':
            m = self.capability(n, kind)
            selectors = m['native'].get('selector_map', {})
            parameters = m['native'].get('collection_parameter_source_map', {})
            result = {'capability': m['capability']}
            for c in n:
                require(c.tag.startswith('{' + m['source']['namespace'] + '}'), 'Object child namespace')
                field = local(c)
                require(field in selectors or field in parameters, 'Object Set/Filter/behavior/field unsupported: ' + field)
                target = selectors.get(field, parameters.get(field))
                require(target not in result, 'repeated Object field unsupported')
                result[target] = self.entity(c, m, True) if field in selectors else self.parameter(c)
            for path, value in m.get('migration_crosswalk', {}).get('materialized_defaults', {}).items():
                require(path.startswith('behaviors.'), 'unknown acquisition default')
                result[path.split('.')[1]] = value
        elif kind == 'state':
            m = self.capability(n, kind)
            fields = []
            seen = set()
            for c in n:
                require(c.tag.startswith('{' + m['source']['namespace'] + '}') and local(c) in m['native']['state_field_map'], 'State field/namespace unsupported')
                require(local(c) not in seen, 'repeated State field unsupported')
                seen.add(local(c))
                fields.append({'fields': {m['native']['state_field_map'][local(c)]: self.entity(c, m)}})
            result = self.logic(n.get('operator', 'AND'), fields)
        else:
            m = self.capability(n, 'test')
            objects = [c for c in n if local(c) == 'object']
            require(len(objects) == 1 and all(local(c) in ('object', 'state') for c in n), 'Test dependency boundary')
            for c in n:
                attrs(c, {'object_ref'} if local(c) == 'object' else {'state_ref'})
                require(not len(c) and c.tag == '{' + m['source']['namespace'] + '}' + local(c), 'Test reference namespace/shape')
            existence = n.get('check_existence', 'at_least_one_exists')
            require(existence in FOUND, 'unsupported Test existence ' + existence)
            req = {'items_found': FOUND[existence]}
            conditions = [self.visit(c.get('state_ref'), 'state') for c in n if local(c) == 'state']
            require(all(self.capability(idx[c.get('state_ref')], 'state')['capability'] == m['capability'] for c in n if local(c) == 'state'), 'Test/State capability mismatch')
            if conditions:
                require(n.get('check') in MATCH and existence != 'none_exist', 'Test check/State existence unsupported')
                req.update(items_satisfying=MATCH[n.get('check')])
                req.update(self.logic(n.get('state_operator', 'AND'), conditions))
            obj = self.visit(objects[0].get('object_ref'), 'object')
            require(obj['capability'] == m['capability'], 'Test/Object capability mismatch')
            obj.pop('capability')  # Test-scoped inheritance; Variable Objects retain their own capability.
            self.tests[name(n, 'test')] = {'capability': m['capability'], 'object': obj, 'require': req,
                'reported_elements': 'all', 'test_title': n.get('comment', '')}
            result = {'test': name(n, 'test')}
        self.active.remove(ident)
        return result

    def logic(self, op, values):
        require(op in ('AND', 'OR') and values, 'unsupported/empty logical operator ' + op)
        return values[0] if len(values) == 1 else {op.lower(): values}

    def criteria(self, n):
        attrs(n, {'operator', 'comment', 'negate'})
        values = []
        for c in n:
            if local(c) == 'criteria':
                value = self.criteria(c)
            else:
                require(local(c) in ('criterion', 'extend_definition'), 'criteria child unsupported')
                key = 'test_ref' if local(c) == 'criterion' else 'definition_ref'
                attrs(c, {key, 'comment', 'negate'})
                value = self.visit(c.get(key), 'test' if key == 'test_ref' else 'definition')
                if c.get('negate', 'false') == 'true':
                    value = {'not': value}
            values.append(value)
        result = self.logic(n.get('operator', 'AND'), values)
        return {'not': result} if n.get('negate', 'false') == 'true' else result

    def scalar(self, datatype, text):
        require(datatype in ('string', 'int', 'boolean'), 'unsupported scalar datatype ' + datatype)
        if datatype == 'boolean':
            require(text in ('true', 'false', '1', '0'), 'invalid boolean')
            return text in ('true', '1')
        return int(text) if datatype == 'int' else text

    def operand(self, n):
        return self.visit(n.get('var_ref'), 'variable') if n.get('var_ref') else self.scalar(n.get('datatype', 'string'), n.text or '')

    def parameter(self, n):
        attrs(n, {'datatype', 'operation', 'var_ref'})
        require(not len(n) and n.get('datatype', 'string') == 'string' and
                n.get('operation', 'equals') == 'equals', 'acquisition parameter comparator/type unsupported')
        value = self.operand(n)
        require(isinstance(value, (str, dict)), 'array acquisition parameter outside bounded proof')
        return value

    def entity(self, n, mapping, selector=False):
        attrs(n, {'datatype', 'operation', 'var_ref', 'var_check'} | (set() if selector else {'entity_check', 'check_existence'}))
        require(not len(n), 'record/nested entity unsupported')
        found = n.get('check_existence', 'at_least_one_exists')
        if found == 'none_exist':
            require(not selector and set(n.attrib) == {'check_existence'} and not n.text, 'comparator-bearing absence blocked')
            return {'values_found': 'none'}
        require(found in FOUND and n.get('operation', 'equals') in OPS, 'unsupported field quantifier/comparator')
        value = self.operand(n)
        crosswalk = mapping['native'].get('selector_value_crosswalk' if selector else 'state_value_crosswalk', {}).get(local(n))
        if crosswalk:
            require(n.get('operation', 'equals') == 'equals', 'non-equality enum crosswalk unsupported')
            require(isinstance(value, str) and value in mapping['migration_crosswalk'][crosswalk], 'dynamic/unknown enum crosswalk unsupported')
            value = mapping['migration_crosswalk'][crosswalk][value]
        out = {OPS[n.get('operation', 'equals')]: value}
        if n.get('datatype', 'string') != 'string':
            out['datatype'] = 'integer' if n.get('datatype') == 'int' else n.get('datatype')
        if n.get('var_ref'):
            require(n.get('var_check', 'all') in MATCH, 'unsupported var_check')
            out['value_match'] = MATCH[n.get('var_check', 'all')]
        if not selector:
            require(n.get('entity_check', 'all') in MATCH, 'unsupported entity_check')
            out.update(values_found=FOUND[found], values_matching=MATCH[n.get('entity_check', 'all')])
        return out

    def function(self, n):
        require(n.tag.startswith('{' + O + '}'), 'function namespace')
        op = local(n)
        if op == 'object_component':
            attrs(n, {'object_ref', 'item_field'})
            require(not len(n), 'object_component children unsupported')
            obj = self.visit(n.get('object_ref'), 'object')
            mapping = next(m for m in self.mappings if m['capability'] == obj['capability'])
            require(n.get('item_field') in mapping['native']['state_field_map'], 'unsupported object_component item_field')
            return {'values': {'object': obj, 'field': mapping['native']['state_field_map'][n.get('item_field')]}}
        if op == 'variable_component':
            attrs(n, {'var_ref'})
            require(not len(n), 'variable_component children unsupported')
            value = self.visit(n.get('var_ref'), 'variable')
            require(isinstance(value, dict), 'constant array in local function requires separate Cartesian proof')
            return value
        if op == 'literal_component':
            attrs(n, {'datatype'})
            require(not len(n), 'literal_component children unsupported')
            return {'literal': {'datatype': n.get('datatype', 'string'), 'value': self.scalar(n.get('datatype', 'string'), n.text or '')}}
        require(op in ('concat', 'regex_capture'), 'unsupported local function ' + op)
        attrs(n, {'pattern'} if op == 'regex_capture' else set())
        require(len(n) > 0 and (op != 'regex_capture' or (len(n) == 1 and 'pattern' in n.attrib)), 'function arity/pattern')
        values = [self.function(c) for c in n]
        return {'concat': values} if op == 'concat' else {'regex_capture': {'pattern': n.get('pattern'), 'value': values[0]}}


def convert(model, rule_ids):
    require(len(rule_ids) == 2 and len(set(rule_ids)) == 2, 'exactly two distinct source Rules required')
    mappings = [json.loads((ROOT / 'schema/v0.4.0/capability-mappings/supported' / (c + '.json')).read_text())
                for c in ('windows.registry', 'independent.shellcommand')]
    require(all(m['specification_version'] == '0.4.0' for m in mappings), 'mapping version')
    documents, trace, links = {}, [], {}
    b = model.benchmark
    for rid in rule_ids:
        require(rid in model.rules, 'source Rule not found ' + rid)
        rule = model.rules[rid]
        cid, definition = model.check(rule)
        converter = Conversion(model, cid, mappings)
        expression = converter.visit(definition, 'definition')
        title = rule.findtext('{' + X + '}title', '')
        native_id = name(rule, 'rule')
        aid = native_id.removesuffix('-rule') + '-assessment'
        a = {'id': aid, 'version': 1, 'assessment_title': title, 'mode': 'automated',
             'class': model.indices[cid][definition].get('class'), 'purpose': 'assessment', 'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'},
             'tests': converter.tests, 'evaluate': expression}
        if converter.variables:
            a['variables'] = converter.variables
        documents['authoring/direct-slice/assessments/' + aid + '.json'] = {'assessment': a}
        r = {'id': native_id, 'title': title, 'version': rule.findtext('{' + X + '}version', ''),
             'severity': rule.get('severity', 'unknown'), 'role': 'full', 'weight': float(rule.get('weight', '1')),
             'discussion': rule.findtext('{' + X + '}description', ''), 'rationale': None,
             'extensions': {}, 'warnings': [], 'identifiers': [], 'references': [], 'requires': [], 'conflicts': [],
             'applicability': [], 'parameters': {}, 'remediation': {}, 'organizational_input_requirements': {},
             'assessment_choices': {'automated': {'assessment': aid}}, 'default_assessment_choice': 'automated'}
        documents['authoring/direct-slice/rules/' + native_id + '.json'] = {'rule': r}
        links[rid] = native_id
        trace.append({'source_rule': rid, 'source_rule_sha256': digest(term(rule)), 'component': cid,
                      'definition': definition, 'native_rule': native_id, 'assessment': aid, 'dependencies': converter.used,
                      'omitted_rule_children': [local(c) for c in rule if local(c) not in ('title', 'version', 'description')],
                      'source_platforms': [c.get('idref') for c in rule.findall('{' + X + '}platform')]})
    defaults = {rid: model.selected(model.rules[rid]) for rid in rule_ids}
    require(all(defaults.values()), 'disabled source defaults not supported by miniature wrapper')
    profiles, profile_trace = [], []
    for p in b.findall('{' + X + '}Profile'):
        effective = {rid: model.selected(model.rules[rid], p) for rid in rule_ids}
        profiles.append({'id': name(p, 'profile'), 'title': p.findtext('{' + X + '}title'),
                         'disabled_rules': [links[rid] for rid, selected in effective.items() if not selected]})
        profile_trace.append({'source_id': p.get('id'), 'source_sha256': digest(term(p)), 'native_id': name(p, 'profile'), 'selected': effective})
    bench = {'id': 'direct-slice', 'version': {'value': b.findtext('{' + X + '}version', '')}, 'ng_schema_version': '0.4.0',
        'use_case': 'compliance', 'assessment_specifications': [{'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}],
        'title': [{'text': '[TWO-RULE PROTOTYPE SUBSET] ' + b.findtext('{' + X + '}title', ''), 'language': 'en'}],
        'description': [{'text': b.findtext('{' + X + '}description', ''), 'language': 'en'}],
        'language': b.get('{http://www.w3.org/XML/1998/namespace}lang'), 'status': [{'value': c.text, **c.attrib} for c in b.findall('{' + X + '}status')],
        'metadata': {'prototype_subset': True, 'omitted_rule_count': len(model.rules) - 2},
        'notices': [], 'front_matter': [], 'rear_matter': [], 'references': [], 'text_blocks': [],
        'platform': {'id': 'fixture-platform', 'title': 'Compilation fixture; applicability not converted', 'applicability': {}},
        'applicability_catalog': 'fixture-applicability', 'scoring': [], 'parameters': [], 'default_selection': True,
        'groups': [], 'profiles': profiles, 'rules': list(links.values())}
    documents['authoring/direct-slice/benchmark.json'] = {'benchmark': bench}
    documents['authoring/direct-slice/applicability.json'] = {'applicability': {'id': 'fixture-applicability', 'conditions': {}}}
    evidence = {'format': 'direct-0.4-two-rule-prototype/1', 'source_zip_sha256': model.zip_sha256, 'source_member': model.member,
        'source_benchmark_component': model.benchmark_component, 'source_benchmark_id': b.get('id'),
        'source_checklist_ref': model.checklist.get('id'),
        'source_xml_sha256': model.xml_sha256, 'component_hashes': model.component_hashes,
        'rules': trace, 'profiles': profile_trace, 'source_benchmark_metadata': [term(c) for c in b if local(c) not in ('Group', 'Rule', 'Profile', 'Value')],
        'omitted_rules': sorted(set(model.rules) - set(rule_ids)), 'scope': 'Assessment operands and subset Profile selection; miniature wrapper, NOT full XCCDF/policy conversion',
        'unsupported': ['other Rules', 'manual alternatives', 'CPE/platform execution', 'full remediation/scoring/Rule metadata', 'Sets/Filters/behaviors/shared Objects', 'all_exist', 'records', 'other capabilities/functions'],
        'mapping_sha256': {m['capability']: digest(m) for m in mappings}, 'xml_parse_calls': model.parse_count,
        'component_index_passes': len(model.indices), 'scanner_evaluated': False, 'coverage_promoted': False}
    return documents, evidence


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--sha256', required=True)
    p.add_argument('--rule', action='append', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    model = Model(args.source, args.sha256)
    start = time.perf_counter()
    documents, proof = convert(model, args.rule)
    metrics = {'parse_index': model.parse_index_seconds, 'conversion': time.perf_counter() - start}
    import yaml
    require(not args.output.exists(), 'output already exists; refusing overwrite')
    for path, doc in documents.items():
        target = args.output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(doc, indent=2) + '\n')
        text = yaml.safe_dump(doc, sort_keys=False)
        require(yaml.safe_load(text) == doc, 'YAML/JSON parsed mismatch')
        target.with_suffix('.yaml').write_text(text)
    (args.output / 'source-trace.json').write_text(json.dumps(proof, indent=2) + '\n')
    try:
        import resource
        metrics['process_peak_rss_kib_linux'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:
        metrics['process_peak_rss_kib_linux'] = None
    (args.output / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
    print(json.dumps(metrics))
