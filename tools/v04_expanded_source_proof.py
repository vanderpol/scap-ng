#!/usr/bin/env python3
"""Bounded independent proof expansion; no production lowering or evaluator (#251).

OVAL rule anchors and native obligations are documented in the engineering
packet. Reading additional syntax never automatically discharges an obligation.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from functools import lru_cache
import xml.etree.ElementTree as ET

from v04_source_package_semantics import (Source, Native, Unsupported, OD, META, OPS,
    boolean, compare, digest, keys, literal, local, need, xml_term, REGISTRY_HIVES, CHECK, FOUND,
    closed_string_enum)
import v04_scalar_source_proof as scalar_proof

ROOT = Path(__file__).resolve().parents[1]
EXTRA = {OD + '#unix}file': 'unix.file', OD + '#unix}password': 'unix.password',
         OD + '#independent}textfilecontent54': 'independent.textfilecontent54',
         OD + '#windows}userright': 'windows.userright', OD + '#windows}service': 'windows.service',
         OD + '#windows}fileeffectiverights53': 'windows.fileeffectiverights53',
         OD + '#windows}cmdlet': 'windows.cmdlet', OD + '#windows}ntuser': 'windows.ntuser',
         OD + '#windows}appcmd': 'windows.appcmd', OD + '#windows}appcmdlistconfig': 'windows.appcmdlistconfig',
         OD + '#independent}environmentvariable58': 'independent.environmentvariable58',
         OD + '#independent}yamlfilecontent': 'independent.yamlfilecontent'}
SCALAR_ACQUISITIONS = {
    'windows.ntuser': ('key', 'name'),
    'windows.appcmd': ('identifier_type', 'identifier', 'parameter'),
    'windows.appcmdlistconfig': ('identifier_type', 'identifier', 'section', 'parameter'),
    'independent.environmentvariable58': ('pid', 'name'),
}
NAMES = {'filepath': 'full_path', 'path': 'directory', 'filename': 'name'}
FILE_FIELDS = {**NAMES, 'group_id': 'owner_gid', 'user_id': 'owner_uid',
               'a_time': 'access_time', 'c_time': 'change_time', 'm_time': 'modify_time',
               'size': 'size', 'has_extended_acl': 'has_extended_acl',
               'uread': 'owner_read', 'uwrite': 'owner_write', 'uexec': 'owner_execute', 'gread': 'group_read',
               'suid': 'setuid', 'sgid': 'setgid', 'gwrite': 'group_write',
               'gexec': 'group_execute', 'oread': 'other_read', 'owrite': 'other_write',
               'oexec': 'other_execute'}
APPROVED_SOURCE = ROOT / 'research/assessment-simplification/evidence/rhel_9/SV-258179/source-oval.xml'
APPROVED_SHA = '463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9'
APPROVED_DEF = 'oval:mil.disa.stig.defs:def:230413'
DECISION = 'https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6388735943'
AUDIT = 'windows.auditeventpolicysubcategories'
SYSTEM_POLICIES = frozenset({'windows.passwordpolicy', 'windows.lockoutpolicy'})

# Independently frozen native type/operator identities; no converter imports.
TYPED_FAMILIES = {
    'binary': {'equals', 'not_equal'},
    **{t: {'equals', 'not_equal', 'greater_than', 'greater_than_or_equal',
           'less_than', 'less_than_or_equal'} for t in
       ('version', 'rpm_evr', 'debian_evr', 'fileset_revision', 'ios_version')},
    **{t: {'equals', 'not_equal', 'greater_than', 'greater_than_or_equal',
           'less_than', 'less_than_or_equal', 'subset_of', 'superset_of'}
       for t in ('ipv4', 'ipv6')},
}
TYPED_OPERATORS = {t + '_' + op: (t, op) for t, ops in TYPED_FAMILIES.items() for op in ops}


@lru_cache(maxsize=1)
def original_password_fields():
    """Identity-named password entities from the pinned original source XSD."""
    schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/unix-definitions-schema.xsd').getroot()
    xs = '{http://www.w3.org/2001/XMLSchema}'
    declaration = schema.find(xs + 'element[@name="password_state"]')
    return {n.get('name') for n in declaration.findall('.//' + xs + 'sequence/' + xs + 'element')}


@lru_cache(maxsize=1)
def original_audit_contract():
    """Independent field/value boundaries from original OVAL, not native mapping."""
    schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd').getroot()
    xs = '{http://www.w3.org/2001/XMLSchema}'
    state = schema.find(xs + 'element[@name="auditeventpolicysubcategories_state"]')
    fields = {e.get('name') for e in state.findall('.//' + xs + 'sequence/' + xs + 'element')
              if not any(local(n) == 'deprecated_info' for n in e.iter())}
    datatype = schema.find(xs + 'complexType[@name="EntityStateAuditType"]')
    values = {e.get('value') for e in datatype.findall('.//' + xs + 'enumeration') if e.get('value')}
    return fields, values


def predicate_order(term):
    """Only State conjunction/disjunction commutes; not Filters/functions/evaluate.

    Preserve duplicate operands, quantifier scopes and all six-state operators.
    OVAL AND/OR tables are commutative; no Boolean two-state identities used.
    """
    if isinstance(term, dict) and len(term) == 1 and next(iter(term)) in ('and', 'or'):
        op, values = next(iter(term.items()))
        return boolean(op, sorted((predicate_order(v) for v in values), key=digest))
    return term


def actual_items_evidence(status, items, *, claims_complete_success=False):
    """Proof admission guard, not a Test/collector evaluator. Preserve diagnostics."""
    need(status in ('complete', 'incomplete', 'error', 'not_collected', 'does_not_exist', 'not_applicable'),
         'unknown collection flag')
    need(all(i in ('exists', 'error', 'not_collected') for i in items),
         'synthetic nonexistent Item outside approved contract')
    need(status != 'does_not_exist' or not items, 'absent collection contains Items')
    need(status != 'complete' or all(i == 'exists' for i in items),
         'error/unknown evidence cannot become complete')
    need(not claims_complete_success or status == 'complete',
         'incomplete/error/unknown evidence cannot claim complete success')
    return {'collection_status': status, 'item_statuses': list(items)}


@lru_cache(maxsize=1)
def original_registry_hive_contract():
    """Independent finite relation proof from original Object AND Item domains.

    Empty Item hives are error placeholders. They remain in the relation table;
    no native empty hive or successful Item is manufactured. Collection flags
    and entity statuses remain outside this literal-selector equivalence.
    """
    xs = '{http://www.w3.org/2001/XMLSchema}'
    domains, hashes = {}, {}
    for filename, type_name in (
            ('windows-definitions-schema.xsd', 'EntityObjectRegistryHiveType'),
            ('windows-system-characteristics-schema.xsd', 'EntityItemRegistryHiveType')):
        path = ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3' / filename
        root = ET.parse(path).getroot()
        node = root.find(xs + 'complexType[@name="' + type_name + '"]')
        need(node is not None, 'original Registry hive type unavailable')
        domain = {e.get('value') for e in node.findall('.//' + xs + 'enumeration')}
        need(domain == REGISTRY_HIVES | {''}, 'original Registry hive domain changed')
        domains[type_name] = sorted(domain)
        hashes[filename] = sha256(path.read_bytes()).hexdigest()
    pairs = [(a, b) for a in domains['EntityObjectRegistryHiveType']
             for b in domains['EntityItemRegistryHiveType']]
    need(all((a == b) == (a.casefold() == b.casefold()) for a, b in pairs),
         'Registry hive equality relation differs')
    return {'domains': domains, 'literal_pairs_proved': len(pairs), 'source_xsd_sha256': hashes}


@lru_cache(maxsize=1)
def original_userright_contract():
    """Original field/enum boundaries, independently of converter mappings."""
    xs = '{http://www.w3.org/2001/XMLSchema}'
    schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd').getroot()
    state = schema.find(xs + 'element[@name="userright_state"]')
    fields = {n.get('name') for n in state.findall('.//' + xs + 'sequence/' + xs + 'element')}
    enum = schema.find(xs + 'complexType[@name="EntityObjectUserRightType"]')
    values = {n.get('value') for n in enum.findall('.//' + xs + 'enumeration') if n.get('value')}
    return fields, values


@lru_cache(maxsize=2)
def original_policy_contract(cap):
    """Read required fixed types and literal restrictions from original OVAL."""
    need(cap in SYSTEM_POLICIES, 'unknown system policy')
    xs = '{http://www.w3.org/2001/XMLSchema}'
    root = ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3'
    schema = ET.parse(root / 'windows-definitions-schema.xsd').getroot()
    core = ET.parse(root / 'oval-definitions-schema.xsd').getroot()
    state = schema.find(xs + 'element[@name="' + cap.split('.')[-1] + '_state"]')
    fields = {}
    for field in state.findall('.//' + xs + 'sequence/' + xs + 'element'):
        typename = field.get('type').split(':')[-1]
        typed = core.find(xs + 'complexType[@name="' + typename + '"]')
        attribute = typed.find('.//' + xs + 'attribute[@name="datatype"]')
        need(attribute.get('use') == 'required', 'original policy type requirement changed')
        datatype = attribute.get('fixed')
        need(datatype in ('int', 'boolean'), 'unknown original policy datatype')
        assertions = [n.get('test') for n in field.iter() if local(n) == 'assert']
        need(all(t == '(@var_ref and string-length(.)=0) or (number(.) >= 0)' for t in assertions),
             'unhandled original policy range assertion')
        fields[field.get('name')] = (datatype, bool(assertions))
    return fields


@lru_cache(maxsize=1)
def original_service_contract():
    """Original service State fields and enum domains, without native mappings."""
    xs = '{http://www.w3.org/2001/XMLSchema}'
    schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd').getroot()
    state = schema.find(xs + 'element[@name="service_state"]')
    fields = {}
    types = {'oval-def:EntityStateStringType': 'string',
             'oval-def:EntityStateIntType': 'int', 'oval-def:EntityStateBoolType': 'boolean'}
    for field in state.findall('.//' + xs + 'sequence/' + xs + 'element'):
        typename = field.get('type')
        enums = set()
        if typename not in types:
            typed = schema.find(xs + 'complexType[@name="' + typename.split(':')[-1] + '"]')
            restriction = typed.find(xs + 'simpleContent/' + xs + 'restriction')
            need(restriction.get('base') == 'oval-def:EntityStateStringType', 'unhandled original service type')
            enums = {n.get('value') for n in restriction.findall(xs + 'enumeration')}
        fields[field.get('name')] = (types.get(typename, 'string'), enums)
    return fields


@lru_cache(maxsize=2)
def original_file_rights_contract(cap='windows.fileeffectiverights53'):
    """Original typed rights and the non-expanding SID acquisition defaults."""
    xs = '{http://www.w3.org/2001/XMLSchema}'
    schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd').getroot()
    need(cap in ('windows.fileeffectiverights53', 'windows.regkeyeffectiverights53'), 'unknown direct-SID rights contract')
    name = cap.split('.')[-1]
    state = schema.find(xs + 'element[@name="' + name + '_state"]')
    fields = {}
    for field in state.findall('.//' + xs + 'sequence/' + xs + 'element'):
        if any(local(n) == 'deprecated_info' for n in field.iter()):
            continue
        kind = field.get('type')
        if kind == 'win-def:EntityStateRegistryHiveType':
            restriction = schema.find(xs + 'complexType[@name="EntityStateRegistryHiveType"]/' + xs + 'simpleContent/' + xs + 'restriction')
            need(restriction.get('base') == 'oval-def:EntityStateStringType' and
                 {n.get('value') for n in restriction.findall(xs + 'enumeration')} == REGISTRY_HIVES | {''},
                 'original rights hive domain changed')
            kind = 'oval-def:EntityStateStringType'
        need(kind in ('oval-def:EntityStateStringType', 'oval-def:EntityStateBoolType'), 'unknown original rights type')
        fields[field.get('name')] = 'string' if kind.endswith('StringType') else 'boolean'
    obj = schema.find(xs + 'element[@name="' + name + '_object"]')
    typename = obj.find('.//' + xs + 'element[@name="behaviors"]').get('type').split(':')[-1]
    behaviors = schema.find(xs + 'complexType[@name="' + typename + '"]')
    defaults = {n.get('name'): n.get('default') for n in behaviors.findall('.//' + xs + 'attribute')}
    need(defaults == {'include_group': 'true', 'resolve_group': 'false'}, 'original direct-SID defaults changed')
    return fields, defaults


class ExpandedSource(Source):
    def __init__(self, oval):
        super().__init__(oval)
        self.normalization_ids, self.normalizations = set(), []
        self.selector_equivalences = {}

    def admit_pinned_rhel_normalization(self, definition, trace):
        raw = APPROVED_SOURCE.read_bytes()
        need(sha256(raw).hexdigest() == APPROVED_SHA, 'approved normalization fixture hash changed')
        approved = Source(ET.fromstring(raw))
        closure = approved.closure(APPROVED_DEF)
        current = self.closure(definition)
        approved_nodes = {n['id']: n for n in closure['nodes']}
        # Original wrapper is permitted only for the exact full SCAP/Rule pin.
        need(trace['source_zip_sha256'] == '70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5'
             and definition == 'oval:mil.disa.stig.rhel9os:def:258179', 'unapproved RHEL source scope')
        expected = [n for n in current['nodes'] if n['id'] != definition]
        need(len(expected) == len(closure['nodes']) and all(approved_nodes.get(n['id']) == n for n in expected),
             'original closure differs from approved normalization source')
        ids = {n['id'] for n in expected if n['kind'] == 'tests' and
               self.nodes[n['id']].get('check_existence') == 'all_exist'}
        need(len(ids) == 16 and all(not any(local(c) == 'state' for c in self.nodes[i]) for i in ids),
             'approved all_exist Test population changed')
        self.normalization_ids = ids
        schema = ROOT / 'schema/v0.4.0/collected-item.schema.json'
        need(set(json.loads(schema.read_text())['properties']['status']['enum']) ==
             {'exists', 'error', 'not_collected'}, 'actual-Items schema contract changed')
        self.item_schema_sha256 = sha256(schema.read_bytes()).hexdigest()

    def capability(self, n, suffix):
        if n.tag == '{' + OD + '#independent}variable' + suffix:
            return 'variable.value'
        registered = scalar_proof.source_capability(n, suffix)
        if registered:
            return registered
        for cap in SYSTEM_POLICIES:
            if n.tag == '{' + OD + '#windows}' + cap.split('.')[-1] + suffix:
                return cap
        if n.tag == '{' + OD + '#windows}auditeventpolicysubcategories' + suffix:
            return AUDIT
        return EXTRA.get(n.tag[1:].removesuffix(suffix)) or super().capability(n, suffix)

    def function(self, n):
        name = local(n)
        if name == 'object_component':
            obj = self.get(n.get('object_ref'), 'objects')
            if obj.tag == '{' + OD + '#independent}variable_object':
                keys(n, {'object_ref', 'item_field'}, 'Variable value projection')
                need(not len(n) and n.get('item_field') == 'value', 'Variable value projection field')
                return self.object(n.get('object_ref'))['variable']
            value = super().function(n)
            capability = self.capability(obj, '_object')
            record = scalar_proof.contract(capability)
            field = n.get('item_field')
            if record:
                need(field in record['fields'], 'unknown original scalar projection field')
                value['values']['field'] = record['fields'][field]
                if field in record.get('field_aliases', {}):
                    # A generic string consumer cannot silently borrow the
                    # native enum vocabulary; a checked enum consumer removes
                    # this source marker only after proving the translation.
                    value['values']['source_alias_domain'] = record['field_aliases'][field]
            elif capability == 'unix.file':
                fields = {**FILE_FIELDS, 'type': 'type', 'sticky': 'sticky'}
                need(field in fields, 'unknown original file projection field')
                value['values']['field'] = fields[field]
            elif capability in ('independent.textfilecontent54', 'windows.fileeffectiverights53'):
                value['values']['field'] = NAMES.get(field, field)
            return value
        if name not in ('regex_capture', 'merge', 'unique'):
            value = super().function(n)
            # A one-valued typed constant component is exactly a literal,
            # with no dynamic status or aggregation boundary to erase.
            if name == 'variable_component' and 'constant_values' in value:
                if len(value['constant_values']) == 1 and value['constant_values'][0]['datatype'] == 'string':
                    return {'literal': value['constant_values'][0]}
            return value
        need(n.tag == '{' + OD + '}' + name, 'foreign function namespace')
        keys(n, {'pattern'} if name == 'regex_capture' else
             {'delimiter', 'sort', 'order'} if name == 'merge' else set(), 'function ' + name)
        values = [self.function(c) for c in n]
        need(values, 'empty function')
        if name == 'regex_capture':
            need(len(values) == 1 and 'pattern' in n.attrib, 'regex_capture operand/pattern')
            return {'regex_capture': {'pattern': n.get('pattern'), 'value': values[0]}}
        if name == 'unique':
            need(len(values) == 1, 'multi-component unique proof not in this batch')
            return {'unique': values[0]}
        need(len(values) == 1, 'multi-component merge proof not in this batch')
        need(n.get('sort', 'document') in ('document', 'lexical', 'numeric', 'natural') and
             n.get('order', 'ascending') in ('ascending', 'descending'), 'original merge sort/order')
        return {'merge': {'delimiter': n.get('delimiter', ''), 'sort': n.get('sort', 'document'),
                          'order': n.get('order', 'ascending'), 'values': values[0]}}

    def state(self, ident, cap):
        if cap == 'independent.yamlfilecontent':
            from v04_yaml_source_proof import source_state
            return predicate_order(source_state(self, ident))
        if cap == 'variable.value':
            node = self.get(ident, 'states')
            need(all(c.tag == '{' + OD + '#independent}value' for c in node),
                 'separate Variable identity State predicate is not represented')
        registered = scalar_proof.source_state(self, ident, cap)
        if registered is not None:
            return predicate_order(registered)
        if cap == 'windows.cmdlet':
            need(all(c.tag == '{' + OD + '#windows}value' and c.get('datatype') == 'record'
                     for c in self.get(ident, 'states')), 'cmdlet State outside bounded value-record proof')
        if cap == 'windows.fileeffectiverights53':
            contract, _ = original_file_rights_contract()
            for entity in self.get(ident, 'states'):
                name = local(entity)
                need(entity.tag == '{' + OD + '#windows}' + name and name in contract,
                     'unknown original file-rights State field')
                need(entity.get('datatype', 'string') == contract[name], 'original rights field datatype')
        if cap == 'independent.textfilecontent54':
            allowed = {'filepath', 'path', 'filename', 'pattern', 'instance', 'text', 'subexpression'}
            need(all(c.tag == '{' + OD + '#independent}' + local(c) and local(c) in allowed
                     for c in self.get(ident, 'states')), 'unsupported original text-file State field')
        if cap == 'windows.service':
            contract = original_service_contract()
            for entity in self.get(ident, 'states'):
                name = local(entity)
                need(entity.tag == '{' + OD + '#windows}' + name and name in contract,
                     'unknown original service State field')
                datatype, enums = contract[name]
                need(entity.get('datatype', 'string') == datatype, 'original service field datatype')
                if enums:
                    operand = self.entity(entity)['operand']
                    constants = operand.get('constant_values', [operand])
                    need(all(v.get('datatype') == 'string' and v.get('value') in enums - {''}
                             for v in constants), 'unknown/dynamic original service enum')
        if cap in SYSTEM_POLICIES:
            original = self.get(ident, 'states')
            contract = original_policy_contract(cap)
            for entity in original:
                name = local(entity)
                need(entity.tag == '{' + OD + '#windows}' + name and name in contract,
                     'unknown original policy State field')
                datatype, nonnegative = contract[name]
                need(entity.get('datatype') == datatype, 'original policy requires explicit field datatype')
                if nonnegative and not entity.get('var_ref'):
                    need(int(entity.text or '') >= 0, 'original policy literal range')
            return predicate_order(super().state(ident, cap))
        if cap == 'windows.userright':
            fields, values = original_userright_contract()
            for entity in self.get(ident, 'states'):
                need(entity.tag == '{' + OD + '#windows}' + local(entity) and local(entity) in fields,
                     'unknown original user-rights State field')
                need(entity.get('datatype', 'string') == 'string', 'user-rights field datatype')
                if local(entity) == 'userright' and not entity.get('var_ref'):
                    need(entity.text in values, 'unknown original user-right enum')
        if cap == AUDIT:
            fields, values = original_audit_contract()
            for entity in self.get(ident, 'states'):
                need(entity.tag == '{' + OD + '#windows}' + local(entity) and local(entity) in fields,
                     'unknown/deprecated original audit field')
                need(entity.get('datatype', 'string') == 'string', 'audit value datatype')
                if not entity.get('var_ref'):
                    need(entity.text in values, 'invalid original audit value')
        if cap == 'unix.file':
            need(all(local(c) in set(FILE_FIELDS) | {'type', 'sticky'} for c in self.get(ident, 'states')),
                 'file State field outside bounded proof rules')
        if cap == 'unix.password':
            need(all(c.tag == '{' + OD + '#unix}' + local(c) and local(c) in original_password_fields()
                     for c in self.get(ident, 'states')), 'unknown original password State field')
        value = super().state(ident, cap)
        def rename(n):
            if 'field' in n:
                if cap == 'windows.ntuser' and n['field'] == 'type':
                    # OVAL EntityStateRegistryTypeType permits the empty lexical
                    # value; NTUSER's approved State domain preserves it exactly.
                    # Keep this source reader independent of converter metadata.
                    aliases = {'reg_sz': 'string', 'reg_dword': 'dword', 'reg_dword_little_endian': 'dword', '': ''}
                    operand = n['predicate']['operand']
                    n = deepcopy(n)
                    n['predicate']['operand'] = closed_string_enum(operand, aliases)
                names = FILE_FIELDS if cap == 'unix.file' else NAMES if cap in (
                    'independent.textfilecontent54', 'windows.fileeffectiverights53') else {}
                return {**n, 'field': names.get(n['field'], n['field'])}
            op, children = next(iter(n.items()))
            return {op: [rename(c) for c in children]}
        value = rename(value)
        if cap == 'windows.wmi.query':
            # Original WMI57 calls the collected query field wql. Native
            # authoring uses query; this is the same field as in acquisition.
            def query_name(term):
                if 'field' in term:
                    return {**term, 'field': 'query' if term['field'] == 'wql' else term['field']}
                op, children = next(iter(term.items()))
                return {op: [query_name(c) for c in children]}
            value = query_name(value)
        return predicate_order(value)

    def filters(self, nodes, cap):
        result = []
        for n in nodes:
            need(n.tag == '{' + OD + '}filter', 'foreign Filter namespace')
            keys(n, {'action'}, 'Filter')
            action = n.get('action', 'exclude')
            need(action in ('include', 'exclude'), 'Filter action')
            result.append({action: self.state((n.text or '').strip(), cap)})
        return result

    def set_term(self, n, cap):
        keys(n, {'set_operator'}, 'Set')
        op = {'UNION': 'union', 'INTERSECTION': 'intersection', 'COMPLEMENT': 'difference'}.get(
            n.get('set_operator', 'UNION'))
        need(op, 'Set operator')
        refs = [c for c in n if local(c) in ('object_reference', 'set')]
        filters = [c for c in n if local(c) == 'filter']
        need(1 <= len(refs) <= 2 and len(refs) + len(filters) == len(n), 'Set children/arity')
        need(not filters or all(local(c) == 'object_reference' for c in refs), 'filters on nested Sets')
        operands = []
        for c in refs:
            need(c.tag == '{' + OD + '}' + local(c), 'Set child namespace')
            if local(c) == 'set':
                operand = {'capability': cap, 'set': self.set_term(c, cap)}
            else:
                keys(c, set(), 'object_reference')
                operand = self.object((c.text or '').strip())
                need(operand['capability'] == cap, 'Set Object family')
            operands.append({'object': operand, 'filters': self.filters(filters, cap)})
        # SetOperatorEnumeration explicitly makes EVERY one-operand Set the
        # complete referenced object (after its Filters), including COMPLEMENT.
        return {'operator': 'identity' if len(operands) == 1 else op, 'operands': operands}

    def object(self, ident):
        n = self.get(ident, 'objects')
        cap = self.capability(n, '_object')
        if cap == 'independent.yamlfilecontent':
            from v04_yaml_source_proof import source_object
            return source_object(self, ident)
        if cap == 'variable.value':
            keys(n, META, 'original Variable source Object')
            need(len(n) == 1 and n[0].tag == '{' + OD + '#independent}var_ref' and
                 not n[0].attrib and not len(n[0]), 'Variable source must be one unmodified var_ref')
            need(ident not in self.active, 'cyclic Variable source Object')
            self.active.add(ident)
            try:
                return {'capability': cap, 'variable': self.variable((n[0].text or '').strip())}
            finally:
                self.active.remove(ident)
        if cap == 'windows.regkeyeffectiverights53':
            original_file_rights_contract(cap)
        registered = scalar_proof.source_object(self, ident, cap)
        if registered is not None:
            return registered
        if cap in SYSTEM_POLICIES | {AUDIT}:
            keys(n, META, 'system singleton Object')
            need(not len(n), 'system singleton has acquisition children')
            return {'capability': cap, 'selectors': {}}
        sets = n.findall('{' + OD + '}set')
        if sets:
            # SetType belongs to the common OVAL Object grammar, independent
            # of collector family. Never fall back to leaf selector reading.
            need(ident not in self.active, 'cyclic Object')
            keys(n, META, 'Set Object')
            need(len(n) == 1 and len(sets) == 1, 'Set mixed with leaf acquisition')
            self.active.add(ident)
            try:
                return {'capability': cap, 'set': self.set_term(sets[0], cap)}
            finally:
                self.active.remove(ident)
        if cap in SCALAR_ACQUISITIONS:
            need(ident not in self.active, 'cyclic Object')
            keys(n, META, 'scalar acquisition Object')
            self.active.add(ident)
            try:
                fields, fs, behaviors = {}, [], None
                nil = '{http://www.w3.org/2001/XMLSchema-instance}nil'
                for child in n:
                    if child.tag == '{' + OD + '}filter':
                        fs.append(child); continue
                    name = local(child)
                    if cap == 'windows.ntuser' and child.tag == '{' + OD + '#windows}behaviors':
                        need(behaviors is None, 'duplicate NTUSER behaviors')
                        behaviors = child
                        continue
                    need(child.tag.rsplit('}', 1)[0] == n.tag.rsplit('}', 1)[0] and
                         name in SCALAR_ACQUISITIONS[cap] and name not in fields, 'unknown/duplicate scalar selector')
                    if nil in child.attrib:
                        from v04_windows_acquisition_source_proof import nil_selector
                        fields[name] = nil_selector(child, cap, name)
                    else:
                        fields[name] = self.entity(child, selector=True)
                need(set(fields) == set(SCALAR_ACQUISITIONS[cap]), 'scalar acquisition fields')
                if cap == 'windows.ntuser':
                    from v04_windows_acquisition_source_proof import ntuser_behaviors
                    fields.update(ntuser_behaviors(behaviors, fields.get('key')))
                value = {'capability': cap, 'selectors': fields}
                if fs:
                    value['filters'] = self.filters(fs, cap)
                return value
            finally:
                self.active.remove(ident)
        if cap == 'windows.cmdlet':
            need(ident not in self.active, 'cyclic Object')
            keys(n, META, 'cmdlet Object')
            allowed = {'module_name', 'module_id', 'module_version', 'verb', 'noun', 'parameters', 'select'}
            self.active.add(ident)
            try:
                fields, fs = {}, []
                for child in n:
                    if child.tag == '{' + OD + '}filter':
                        fs.append(child); continue
                    name = local(child)
                    need(child.tag == '{' + OD + '#windows}' + name and name in allowed and name not in fields,
                         'unknown/duplicate original cmdlet input')
                    fields[name] = self.cmdlet_input(child)
                need(set(fields) == allowed, 'missing original cmdlet input')
                value = {'capability': cap, 'selectors': fields}
                if fs:
                    value['filters'] = self.filters(fs, cap)
                return value
            finally:
                self.active.remove(ident)
        if cap in ('windows.userright', 'windows.service'):
            need(ident not in self.active, 'cyclic Object')
            keys(n, META, 'Windows scalar-selector Object')
            self.active.add(ident)
            try:
                selector = 'userright' if cap == 'windows.userright' else 'service_name'
                entities = [c for c in n if c.tag == '{' + OD + '#windows}' + selector]
                filters = [c for c in n if c.tag == '{' + OD + '}filter']
                need(len(entities) == 1 and len(n) == len(entities) + len(filters), 'scalar acquisition shape')
                need(entities[0].get('datatype', 'string') == 'string', 'Windows selector datatype')
                value = {'capability': cap, 'selectors': {selector: self.entity(entities[0], selector=True)}}
                if cap == 'windows.userright':
                    operand = value['selectors'][selector]['operand']
                    constants = operand.get('constant_values', [operand])
                    need(all(v.get('datatype') == 'string' and v.get('value') in original_userright_contract()[1]
                             for v in constants), 'unknown/dynamic original user-right enum')
                if filters:
                    value['filters'] = self.filters(filters, cap)
                return value
            finally:
                self.active.remove(ident)
        if cap == 'windows.fileeffectiverights53':
            need(ident not in self.active, 'cyclic Object')
            keys(n, META, 'file-rights Object')
            original_file_rights_contract()
            self.active.add(ident)
            try:
                fields = {}
                fs = [c for c in n if c.tag == '{' + OD + '}filter']
                for child in n:
                    if child in fs:
                        continue
                    name = local(child)
                    target = NAMES.get(name, name)
                    need(child.tag == '{' + OD + '#windows}' + name and name in ('filepath', 'path', 'filename', 'trustee_sid')
                         and target not in fields, 'unsupported original rights acquisition field')
                    need(child.get('datatype', 'string') == 'string', 'rights selector datatype')
                    if '{http://www.w3.org/2001/XMLSchema-instance}nil' in child.attrib:
                        from v04_windows_acquisition_source_proof import nil_selector
                        fields[target] = nil_selector(child, cap, name)
                    else:
                        fields[target] = self.entity(child, selector=True)
                need(set(fields) in ({'full_path', 'trustee_sid'}, {'directory', 'name', 'trustee_sid'}),
                     'rights path/SID acquisition required')
                value = {'capability': cap, 'selectors': {**fields, 'filesystem': 'all'}}
                if fs:
                    value['filters'] = self.filters(fs, cap)
                return value
            finally:
                self.active.remove(ident)
        if cap not in ('unix.file', 'unix.password', 'independent.textfilecontent54'):
            if cap == 'windows.registry':
                # Leaf Registry Filters also constrain Object projections used
                # by Variables. Read them in source order, at collection scope.
                fs = n.findall('{' + OD + '}filter')
                need(all(not len(f) for f in fs), 'Registry Filter children unsupported')
                original = self.nodes[ident]
                if fs:
                    leaf = deepcopy(n)
                    for f in leaf.findall('{' + OD + '}filter'):
                        leaf.remove(f)
                    self.nodes[ident] = leaf
                try:
                    value = super().object(ident)
                finally:
                    self.nodes[ident] = original
                if fs:
                    self.active.add(ident)
                    try:
                        value['filters'] = self.filters(fs, cap)
                    finally:
                        self.active.remove(ident)
                hive = value['selectors'].get('hive')
                if hive and hive['operation'] == 'case_insensitive_equals':
                    contract = deepcopy(original_registry_hive_contract())
                    need(hive['comparison_datatype'] == 'string', 'Registry hive comparison datatype')
                    hive['operation'] = 'equals'
                    entity = n.find('{' + OD + '#windows}hive')
                    self.selector_equivalences[ident] = {'source_object': ident,
                        'source_selector': {'tag': entity.tag, 'attributes': dict(entity.attrib), 'value': entity.text},
                        'native_comparator': 'equals', 'domain_proof': contract}
                return value
            if cap == 'independent.shellcommand':
                # shellcommand.pattern is an intrinsic regex collector parameter
                # (its 5.12.3 element documentation), not an equals selector.
                n = deepcopy(n)
                fs = n.findall('{' + OD + '}filter')
                for f in fs:
                    n.remove(f)
                behaviors = n.findall('{' + OD + '#independent}behaviors')
                need(len(behaviors) <= 1, 'duplicate command behaviors')
                flags = {'error_if_exit_status_not_0': False, 'error_if_stderr_exists': False}
                if behaviors:
                    behavior = behaviors[0]
                    keys(behavior, set(flags), 'command behaviors')
                    need(not len(behavior) and not (behavior.text or '').strip(), 'nonempty command behaviors')
                    for name in flags:
                        value = behavior.get(name, 'false')
                        need(value in ('true', 'false', '1', '0'), 'invalid original command error flag')
                        flags[name] = value in ('true', '1')
                    n.remove(behavior)
                for c in n:
                    if local(c) == 'pattern' and 'operation' not in c.attrib:
                        c.set('operation', 'pattern match')
                old = self.nodes[ident]
                self.nodes[ident] = n
                try:
                    result = super().object(ident)
                    result['selectors'].update(flags)
                    if fs:
                        result['filters'] = self.filters(fs, cap)
                    return result
                finally:
                    self.nodes[ident] = old
            return super().object(ident)
        need(ident not in self.active, 'cyclic Object')
        self.active.add(ident)
        keys(n, META, 'Object')
        sets = [c for c in n if local(c) == 'set']
        if sets:
            need(len(n) == 1, 'Set mixed with selectors')
            value = {'capability': cap, 'set': self.set_term(sets[0], cap)}
        else:
            fields, behaviors, seen_behaviors = {}, {}, False
            fs = [c for c in n if local(c) == 'filter']
            for c in n:
                name = local(c)
                if name == 'filter':
                    continue
                need(c.tag.rsplit('}', 1)[0] == n.tag.rsplit('}', 1)[0], 'Object field namespace')
                if name == 'behaviors':
                    need(not seen_behaviors and not len(c) and not (c.text or '').strip(), 'duplicate/nonempty behaviors')
                    seen_behaviors = True
                    behaviors = dict(c.attrib)
                    continue
                allowed = {'unix.password': {'username'}, 'unix.file': {'filepath', 'path', 'filename'},
                           'independent.textfilecontent54': {'filepath', 'path', 'filename', 'pattern', 'instance'}}[cap]
                need(name in allowed and NAMES.get(name, name) not in fields, 'unproved/duplicate selector ' + name)
                nil = '{http://www.w3.org/2001/XMLSchema-instance}nil'
                if cap == 'unix.file' and name == 'filename' and nil in c.attrib:
                    keys(c, {nil, 'datatype', 'operation'}, 'nil filename')
                    need(c.get('operation', 'equals') == 'equals', 'nil filename comparator')
                    need(c.get(nil) in ('true', '1') and c.get('datatype', 'string') == 'string' and
                         not len(c) and not (c.text or '').strip(), 'invalid nil filename')
                    fields['name'] = None
                else:
                    fields[NAMES.get(name, name)] = self.entity(c, selector=True)
            if cap == 'unix.file':
                keys(behaviors, {'max_depth', 'recurse', 'recurse_direction', 'recurse_file_system'}, 'file behaviors')
                direction = behaviors.get('recurse_direction', 'none')
                need(direction in ('none', 'down'), 'unsupported/deprecated file recursion direction')
                depth = int(behaviors.get('max_depth', -1))
                need(depth >= -1, 'invalid original max_depth')
                recurse = behaviors.get('recurse', 'symlinks and directories')
                need(recurse in ('symlinks', 'directories', 'symlinks and directories'), 'deprecated/unproved recursion')
                if (direction == 'down' and 'full_path' not in fields and
                        fields.get('directory', {}).get('operation') == 'equals'):
                    fields['traversal'] = {'max_depth': None if depth == -1 else depth,
                        'recurse': 'symlinks_and_directories' if recurse == 'symlinks and directories' else recurse,
                        'direction': 'down'}
                need(behaviors.get('recurse_file_system', 'all') in ('all', 'local', 'defined'),
                     'invalid original filesystem scope')
                fields['filesystem'] = {'all': 'all', 'local': 'local', 'defined': 'same'}[
                    behaviors.get('recurse_file_system', 'all')]
            elif cap == 'independent.textfilecontent54':
                keys(behaviors, {'ignore_case', 'multiline', 'singleline', 'item_creation'} | scalar_proof.FILE_BEHAVIORS,
                     'textfile behaviors')
                need('full_path' not in fields or not set(behaviors) & {'max_depth', 'recurse_direction'},
                     'invalid original textfile filepath recursion attributes')
                directory = fields.get('directory')
                need(directory is None or directory['operation'] == 'equals' or not set(behaviors) & {
                     'max_depth', 'recurse_direction', 'recurse'}, 'invalid original textfile pattern-path recursion attributes')
                selector = fields.get('full_path', directory)
                need(behaviors.get('recurse_file_system') != 'defined' or selector['operation'] == 'equals',
                     'invalid original textfile filesystem/pattern selection')
                fields.update(scalar_proof.source_traversal(ET.Element('behaviors', behaviors), fields, 'file_traversal'))
                for name, default in (('ignore_case', 'false'), ('multiline', 'true'), ('singleline', 'false')):
                    v = behaviors.get(name, default)
                    need(v in ('true', 'false', '0', '1'), 'behavior boolean')
                    fields[name] = v in ('true', '1')
                fields['item_creation'] = behaviors.get('item_creation', 'all_object_elements_fullfilled')
                need(fields['item_creation'] in ('all_object_elements_fullfilled', 'filepath_exists'),
                     'unknown original item_creation')
            value = {'capability': cap, 'selectors': fields}
            if fs:
                value['filters'] = self.filters(fs, cap)
        self.active.remove(ident)
        return value

    def cmdlet_input(self, n):
        """Independent original record-field selection versus expected matching."""
        nil = '{http://www.w3.org/2001/XMLSchema-instance}nil'
        name = local(n)
        records = name in ('parameters', 'select')
        if nil in n.attrib:
            keys(n, {nil, 'datatype'}, 'cmdlet nil input')
            need(name not in ('verb', 'noun') and n.get(nil) in ('true', '1') and
                 not len(n) and not (n.text or '').strip(), 'invalid original nil input')
            datatype = 'record' if records else 'version' if name == 'module_version' else 'string'
            need(n.get('datatype', 'string' if datatype == 'string' else None) == datatype,
                 'original nil datatype')
            return None
        if not records:
            term = self.entity(n, selector=True)
            need(term['operation'] == 'equals' and term['comparison_datatype'] == 'string', 'cmdlet scalar input')
            from v04_acquisition_source_proof import parameter_operand
            return parameter_operand(term)
        keys(n, {'datatype', 'operation'}, 'cmdlet input record')
        need(n.get('datatype') == 'record' and n.get('operation', 'equals') == 'equals' and
             not (n.text or '').strip(), 'original input record type/comparator')
        fields = {}
        for child in n:
            field = child.get('name')
            need(child.tag == '{' + OD + '}field' and field and field not in fields and
                 not any('A' <= c <= 'Z' for c in field), 'invalid/duplicate input record field')
            check = child.get('entity_check', 'all')
            need(check in CHECK, 'input record entity_check')
            scalar = deepcopy(child)
            scalar.attrib.pop('name'); scalar.attrib.pop('entity_check', None)
            fields[field] = {'predicate': self.entity(scalar, selector=True), 'selection_matching': CHECK[check]}
            if name == 'select':
                need(fields[field]['predicate']['operand'] != literal('string', '*'), 'wildcard output selection')
        return {'fields': fields}

    def test(self, ident):
        n = self.get(ident, 'tests')
        capability = self.capability(n, '_test')
        contract = scalar_proof.contract(capability)
        if contract and contract.get('fixed_result'):
            keys(n, META | {'check', 'check_existence', 'state_operator', 'deprecated'}, 'fixed-result Test')
            need(n.get('deprecated', 'false') == 'false' and not len(n), 'fixed-result Test has source payload')
            need(n.get('check') in CHECK and n.get('check_existence', 'at_least_one_exists') in set(FOUND) | {'all_exist'},
                 'invalid original fixed-result controls')
            return {'capability': capability, 'fixed_result': contract['fixed_result']}
        if n.get('check_existence') != 'all_exist':
            result = super().test(ident)
            if 'condition' in result:
                result['condition'] = predicate_order(result['condition'])
            return result
        need(ident in self.normalization_ids, 'all_exist outside exact approved source proof')
        replacement = deepcopy(n)
        replacement.set('check_existence', 'at_least_one_exists')
        self.nodes[ident] = replacement
        try:
            result = super().test(ident)
        finally:
            self.nodes[ident] = n
        obj_id = next(c.get('object_ref') for c in n if local(c) == 'object')
        obj = self.get(obj_id, 'objects')
        self.normalizations.append({'source_test': ident, 'source_test_version': n.get('version'),
            'source_test_sha256': digest(xml_term(n)), 'source_object': obj_id,
            'source_object_version': obj.get('version'), 'source_object_sha256': digest(xml_term(obj)),
            'approved_source_sha256': APPROVED_SHA, 'owner_decision': DECISION,
            'approved_definition': APPROVED_DEF, 'actual_items_schema_sha256': self.item_schema_sha256,
            'contract': 'scap-ng-0.4.0/actual-items-test-all-exist/1',
            'unrestricted_oval_equivalence': False, 'original': 'all_exist', 'native': 'one_or_more',
            'status_policy': 'preserve error/incomplete/not_collected; no synthetic nonexistent Items'})
        return result


class ExpandedNative(Native):
    def test(self, ident):
        n = self.a['tests'][ident]
        cap = n.get('capability')
        contract = scalar_proof.contract(cap)
        if contract and contract.get('fixed_result'):
            n = self.reference('tests', ident)
            keys(n, {'test_title', 'capability', 'require', 'reported_elements'}, 'fixed-result native Test')
            need(n.get('require') == {'items_found': 'one_or_more'} and n.get('reported_elements', 'all') == 'all',
                 'fixed-result native canonical requirement')
            return {'capability': cap, 'fixed_result': contract['fixed_result']}
        if cap == 'variable.value':
            n = self.reference('tests', ident)
            keys(n, {'capability', 'variable', 'test_title', 'reported_elements', 'require'}, 'Variable Test')
            need(n.get('reported_elements') == 'all', 'Variable reporting/evidence boundary')
            requirement = n['require']
            result = {'capability': cap, 'object': {'capability': cap,
                'variable': self.operand({'variable': n['variable']})}, 'found': requirement['items_found']}
            if set(requirement) != {'items_found'}:
                result.update(matching=requirement['items_satisfying'], condition=self.condition(requirement))
            return result
        if cap not in SYSTEM_POLICIES | {AUDIT} and not scalar_proof.no_object(cap):
            return super().test(ident)
        n = self.reference('tests', ident)
        keys(n, {'capability', 'test_title', 'reported_elements', 'require'}, 'system native Test')
        need(n.get('reported_elements') == 'all', 'system reporting/evidence boundary')
        requirement = n['require']
        result = {'capability': cap, 'object': {'capability': cap, 'selectors': {}},
                  'found': requirement['items_found']}
        if set(requirement) != {'items_found'}:
            result.update(matching=requirement['items_satisfying'], condition=self.condition(requirement))
        return result

    def operand(self, value, datatype='string'):
        if isinstance(value, dict) and set(value) == {'variable'}:
            node = self.reference('variables', value['variable'])
            if node.get('kind') == 'constant':
                keys(node, {'kind', 'datatype', 'expression', 'title'}, 'native constant Variable')
                keys(node['expression'], {'literal'}, 'native constant expression')
                values = node['expression'].get('literal')
                need(isinstance(values, list) and values, 'native constant values must be a nonempty array')
                return {'constant_values': [literal(node['datatype'], v) for v in values]}
        return super().operand(value, datatype)

    def predicate(self, n, inherited=None, selector=False):
        # Independently decode only the approved specialized operator families.
        # The compiler keeps these authored operands intact; do not borrow a
        # converter normalizer or infer an algorithm from a string's spelling.
        need(isinstance(n, dict), 'native predicate type')
        typed = [(*TYPED_OPERATORS[key], key) for key in set(n) & TYPED_OPERATORS.keys()]
        if typed:
            need(len(typed) == 1 and not set(n) & set(OPS.values()), 'mixed native typed comparisons')
            datatype, operation, key = typed[0]
            effective = {**(inherited or {}), **n}
            need(effective.get('datatype', datatype) == datatype, 'conflicting native comparison datatype')
            n = {**n, operation: n[key], 'datatype': datatype}
            del n[key]
        return super().predicate(n, inherited, selector)

    def function(self, n):
        need(isinstance(n, dict) and len(n) == 1, 'function shape')
        op, v = next(iter(n.items()))
        if op == 'function':
            # Independent reader for the approved-direction envelope. Do not
            # import the converter's migration routine: disagreement must
            # remain detectable by source-term comparison.
            need(isinstance(v, dict) and set(v) == {'name', 'arguments', 'options'},
                 'canonical function envelope')
            name, args, options = v['name'], v['arguments'], v['options']
            need(isinstance(args, list) and isinstance(options, dict), 'canonical function arguments/options')
            if name == 'concat':
                need(len(args) >= 2 and not options, 'canonical concat arity/options')
                return {'concat': [self.function(a) for a in args]}
            if name == 'regex_capture':
                need(len(args) == 1 and set(options) == {'pattern'}, 'canonical regex_capture arity/options')
                return {'regex_capture': {'pattern': options['pattern'], 'value': self.function(args[0])}}
            if name == 'unique':
                need(len(args) == 1 and not options, 'canonical unique arity/options')
                return {'unique': self.function(args[0])}
            if name == 'merge':
                need(len(args) == 1 and set(options) == {'delimiter', 'sort', 'order'},
                     'canonical merge arity/options')
                return {'merge': {**options, 'values': self.function(args[0])}}
            raise ValueError(f'canonical function source proof unavailable: {name}')
        if op == 'literal' and not isinstance(v, dict):
            return {'literal': literal('string', v)}
        if op == 'regex_capture':
            keys(v, {'pattern', 'value'}, op)
            need(set(v) == {'pattern', 'value'}, 'regex_capture requires pattern and value')
            return {'regex_capture': {'pattern': v['pattern'], 'value': self.function(v['value'])}}
        if op == 'unique':
            return {'unique': self.function(v)}
        if op == 'merge':
            keys(v, {'delimiter', 'sort', 'order', 'values'}, op)
            need(set(v) == {'delimiter', 'sort', 'order', 'values'}, 'merge requires explicit default parameters')
            return {'merge': {'delimiter': v['delimiter'], 'sort': v['sort'], 'order': v['order'],
                              'values': self.function(v['values'])}}
        return super().function(n)

    def condition(self, n, inherited=None):
        return predicate_order(super().condition(n, inherited))

    def filter_condition(self, n):
        need(isinstance(n, dict) and n, 'Filter predicate')
        if set(n) <= {'and', 'or'}:
            op, values = next(iter(n.items()))
            return predicate_order(boolean(op, [self.filter_condition(c) for c in values]))
        if 'fields' in n:
            return self.condition(n)
        terms = []
        for field, predicate in n.items():
            p = deepcopy(predicate)
            if 'require' in p:
                need(p.pop('require') == 'at_least_one_exists_and_all_match', 'unproved Filter field requirement')
                p.update(values_found='one_or_more', values_matching='every')
            terms.append({'field': field, 'predicate': self.predicate(p)})
        return predicate_order(boolean('and', terms))

    def filters(self, fs):
        result = []
        for f in fs:
            need(isinstance(f, dict) and len(f) == 1, 'native Filter')
            action, predicate = next(iter(f.items()))
            need(action in ('include', 'exclude'), 'native Filter action')
            result.append({action: self.filter_condition(predicate)})
        return result

    def set_term(self, n, cap):
        keys(n, {'operator', 'operands'}, 'native Set')
        need(n['operator'] in ('union', 'intersection', 'difference') and 1 <= len(n['operands']) <= 2,
             'native Set operator/arity')
        operands = []
        for operand in n['operands']:
            if 'set' in operand:
                keys(operand, {'set'}, 'nested Set operand')
                obj = {'capability': cap, 'set': self.set_term(operand['set'], cap)}
            else:
                keys(operand, {'object', 'filters'}, 'Set operand')
                obj = self.object(operand['object'], cap)
            need(obj['capability'] == cap, 'Set family')
            operands.append({'object': obj, 'filters': self.filters(operand.get('filters', []))})
        return {'operator': 'identity' if len(operands) == 1 else n['operator'], 'operands': operands}

    def object(self, n, cap=None):
        if isinstance(n, str):
            return super().object(n, cap)
        cap = n.get('capability', cap)
        if cap == 'independent.yamlfilecontent' and 'set' not in n:
            from v04_yaml_source_proof import native_object
            return native_object(self, n)
        registered = scalar_proof.native_object(self, n, cap)
        if registered is not None:
            return registered
        if cap in ('independent.shellcommand', 'windows.registry') and 'set' not in n and 'filters' in n:
            acquisition = deepcopy(n)
            filters = acquisition.pop('filters')
            result = super().object(acquisition, cap)
            if filters:
                result['filters'] = self.filters(filters)
            return result
        if cap in SCALAR_ACQUISITIONS and 'set' not in n:
            allowed = set(SCALAR_ACQUISITIONS[cap])
            defaults = {'include_default': False, 'item_creation': 'key_and_name_exist'} if cap == 'windows.ntuser' else {}
            keys(n, allowed | set(defaults) | {'capability', 'object_title', 'filters'} |
                 ({'traversal'} if cap == 'windows.ntuser' else set()), 'native scalar acquisition')
            need(allowed | set(defaults) <= set(n), 'native scalar acquisition fields')
            fields = {k: None if n[k] is None else self.predicate(n[k], selector=True) for k in sorted(allowed)}
            fields.update({k: n[k] for k in defaults})
            if cap == 'windows.ntuser':
                need(isinstance(n['include_default'], bool) and
                     n['item_creation'] in ('key_and_name_exist', 'every_ntuser'), 'native NTUSER collection parameters')
                if 'traversal' in n:
                    from v04_source_package_semantics import native_hierarchy
                    fields['traversal'] = native_hierarchy(n['traversal'])
            result = {'capability': cap, 'selectors': fields}
            if n.get('filters'):
                result['filters'] = self.filters(n['filters'])
            return result
        if cap == 'windows.cmdlet' and 'set' not in n:
            allowed = {'module_name', 'module_id', 'module_version', 'verb', 'noun', 'parameters', 'select'}
            keys(n, allowed | {'capability', 'object_title', 'filters'}, 'native cmdlet Object')
            need(allowed <= set(n), 'missing native cmdlet input')
            fields = {}
            for name in sorted(allowed):
                value = n[name]
                if value is None:
                    need(name not in ('verb', 'noun'), 'native required command identity')
                    fields[name] = None
                elif name in ('parameters', 'select'):
                    keys(value, {'fields'}, 'native collector record')
                    fields[name] = {'fields': {}}
                    for field, predicate in value['fields'].items():
                        scalar = deepcopy(predicate)
                        selection = scalar.pop('selection_match', None)
                        need(selection in CHECK.values(), 'missing native field selection matching')
                        fields[name]['fields'][field] = {'predicate': self.predicate(scalar, selector=True),
                                                        'selection_matching': selection}
                else:
                    fields[name] = self.operand(value)
            result = {'capability': cap, 'selectors': fields}
            if n.get('filters'):
                result['filters'] = self.filters(n['filters'])
            return result
        if cap == 'windows.fileeffectiverights53' and 'set' not in n:
            allowed = {'full_path', 'directory', 'name', 'trustee_sid'}
            keys(n, allowed | {'capability', 'object_title', 'filesystem', 'filters'}, 'native rights Object')
            selectors = set(n) & allowed
            need(selectors in ({'full_path', 'trustee_sid'}, {'directory', 'name', 'trustee_sid'})
                 and 'filesystem' in n, 'native rights acquisition fields')
            need(all(n[k] is not None or k == 'name' for k in selectors), 'native nil rights selector')
            value = {'capability': cap, 'selectors': {
                k: None if n[k] is None else self.predicate(n[k], selector=True)
                for k in ('full_path', 'directory', 'name', 'trustee_sid') if k in n}}
            value['selectors']['filesystem'] = n['filesystem']
            if n.get('filters'):
                value['filters'] = self.filters(n['filters'])
            return value
        if cap in ('windows.userright', 'windows.service') and 'set' not in n:
            selector = 'userright' if cap == 'windows.userright' else 'service_name'
            keys(n, {'capability', 'object_title', selector, 'filters'}, 'native Windows scalar-selector Object')
            need(selector in n, 'missing native Windows selector')
            value = {'capability': cap, 'selectors': {selector: self.predicate(n[selector], selector=True)}}
            if n.get('filters'):
                value['filters'] = self.filters(n['filters'])
            return value
        if 'collect' in n:
            keys(n, {'capability', 'collect', 'object_title'}, 'embedded Object')
            return self.object({**n['collect'], 'capability': cap})
        if 'set' in n:
            keys(n, {'set', 'capability', 'object_title'}, 'Set Object')
            return {'capability': cap, 'set': self.set_term(n['set'], cap)}
        if cap not in ('unix.file', 'unix.password', 'independent.textfilecontent54'):
            return super().object(n, cap)
        allowed = {'unix.password': {'username'}, 'unix.file': {'directory', 'name', 'full_path', 'filesystem', 'traversal'},
                   'independent.textfilecontent54': {'directory', 'name', 'full_path', 'pattern', 'instance',
                      'filesystem', 'traversal', 'ignore_case', 'singleline', 'multiline', 'item_creation'}}[cap]
        keys(n, allowed | {'capability', 'object_title', 'filters', 'for_each'}, 'Object')
        fields = {}
        for k, v in n.items():
            if k in ('capability', 'object_title', 'filters', 'for_each'):
                continue
            if k == 'traversal':
                if cap == 'independent.textfilecontent54':
                    need('directory' in n and self.predicate(n['directory'], selector=True)['operation'] == 'equals',
                         'native textfile traversal requires an equality directory')
                    need(isinstance(v, dict), 'native textfile traversal shape')
                    depth = v.get('max_depth')
                    need(set(v) == {'max_depth', 'recurse'} and
                         (depth is None or type(depth) is int and depth >= 0) and
                         v['recurse'] in ('directories', 'symlinks', 'symlinks_and_directories'),
                         'native textfile traversal depth/recurse type')
                keys(v, {'max_depth', 'recurse'}, 'traversal')
                fields[k] = {**v, 'direction': 'down'}
            elif k in ('filesystem', 'ignore_case', 'singleline', 'multiline', 'item_creation'):
                if cap == 'independent.textfilecontent54' and k in ('ignore_case', 'singleline', 'multiline'):
                    need(type(v) is bool, 'native textfile Boolean behavior type')
                fields[k] = v
            elif cap == 'unix.file' and k == 'name' and v is None:
                fields[k] = None
            elif isinstance(v, dict) and set(v) == {'from'}:
                loop = n.get('for_each')
                need(cap == 'unix.file' and loop and k == 'directory', 'unproved collection expansion')
                keys(loop, {'in', 'item'}, 'for_each')
                prefix = loop['item'] + '.'
                need(v['from'].startswith(prefix), 'for_each scope')
                fields[k] = {'operation': 'equals', 'comparison_datatype': 'string',
                    'operand': {'local': {'datatype': 'string', 'expression': {'values': {
                        'object': self.object(loop['in']), 'field': v['from'][len(prefix):]}}}},
                    'expected_matching': 'one_or_more'}
            else:
                fields[k] = self.predicate(v, selector=True)
        if 'for_each' in n:
            need(any(isinstance(v, dict) and 'from' in v for v in n.values()), 'unused collection expansion')
        value = {'capability': cap, 'selectors': fields}
        if n.get('filters'):
            value['filters'] = self.filters(n['filters'])
        return value


def expanded_compare(source, definition, assessment):
    result = compare(source, definition, assessment, native_type=ExpandedNative)
    if result['outcome'] == 'PROVED' and source.selector_equivalences:
        result['selector_equivalences'] = list(source.selector_equivalences.values())
    if result['outcome'] == 'PROVED' and source.normalizations:
        for row in source.normalizations:
            row['native_test'] = result['test_bindings'][row['source_test']]
        result.update(outcome='PROVED_WITH_EXPLICIT_APPROVED_NORMALIZATION',
                      normalizations_applied=source.normalizations)
    return result
