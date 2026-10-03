"""Research-only finite publisher tables; no runtime macros or target acquisition."""
from copy import deepcopy
import re


def expand(table):
    """Emit ordinary named Objects/States/Tests, retaining one Test per row.

    Input is intentionally a closed two-kind experiment, not a general template
    interpreter. It never reads Organizational Input, runs commands, or opens
    paths named in the table. Identity belongs to rows, not matching predicates.
    """
    if not isinstance(table, dict) or set(table) != {'kind', 'id', 'defaults', 'templates', 'rows'}:
        raise ValueError('unexpected or missing table fields')
    kind = table['kind']
    if kind not in ('audit_patterns', 'crypto_backends') or not isinstance(table['rows'], list) or not table['rows']:
        raise ValueError('unsupported or empty table')
    default_fields = ({'full_path', 'existence', 'match', 'instance', 'collect', 'filesystem'}
                      if kind == 'audit_patterns' else {'capability', 'existence', 'match'})
    if not isinstance(table['defaults'], dict) or set(table['defaults']) != default_fields:
        raise ValueError('invalid publisher defaults')
    if not isinstance(table['id'], str) or not table['id']:
        raise ValueError('missing native assessment identity')
    templates = table['templates']
    if not isinstance(templates, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k,v in templates.items()):
        raise ValueError('invalid templates')
    if kind == 'crypto_backends' and templates:
        raise ValueError('backend rows do not use templates')
    if kind == 'audit_patterns':
        defaults = table['defaults']
        if defaults['instance'] != {'value': '1', 'operation': 'greater_or_equal', 'datatype': 'integer'}:
            raise ValueError('unsupported text-instance selection')
        expected_collect = {'ignore_case': False, 'multiline': True, 'singleline': False,
                            'item_creation': 'all_object_elements_fullfilled'}
        if defaults['collect'] != expected_collect or defaults['filesystem'] != 'any':
            raise ValueError('unsupported text collection contract')
        if not isinstance(defaults['full_path'], str) or not defaults['full_path'].startswith('/'):
            raise ValueError('publisher filepath must be absolute')
    a = dict(id=table['id'], version=1, assessment_title='Experimental finite-row expansion',
             mode='automated', **{'class': 'compliance'}, purpose='assessment',
             specification={'id': 'scap-ng.pre-alpha.assessment', 'version': '0.1.0'},
             objects={}, states={}, tests={}, evaluate={'all': []})
    seen = set()
    for row in table['rows']:
        allowed = ({'id', 'template', 'syscall', 'arch', 'existence'} if kind == 'audit_patterns'
                   else {'id', 'capability', 'full_path', 'field', 'expected', 'existence'})
        required = ({'id', 'template', 'syscall', 'arch'} if kind == 'audit_patterns'
                    else {'id', 'full_path', 'field', 'expected'})
        if not isinstance(row, dict) or set(row) - allowed or not required.issubset(row) or not isinstance(row.get('id'), str):
            raise ValueError('invalid row shape')
        name = row['id']
        if not re.fullmatch(r'[a-z][a-z0-9-]*', name) or name in seen:
            raise ValueError('duplicate or invalid row identity')
        seen.add(name)
        settings = deepcopy(table['defaults'])
        settings.update(row)
        if settings['existence'] not in ('all', 'some') or settings['match'] != 'all':
            raise ValueError('unsupported quantifiers')
        if kind == 'audit_patterns':
            if settings['syscall'] not in ('setxattr', 'fsetxattr', 'lsetxattr',
                                          'removexattr', 'fremovexattr', 'lremovexattr'):
                raise ValueError('syscall is outside the publisher vocabulary')
            if settings['arch'] not in ('b32', 'b64'):
                raise ValueError('invalid architecture')
            if not isinstance(settings['template'], str) or settings['template'] not in templates:
                raise ValueError('unknown template')
            pattern = templates[settings['template']]
            pattern = pattern.replace('${syscall}', settings['syscall']).replace('${arch}', settings['arch'])
            if '${' in pattern:
                raise ValueError('unresolved template input')
            cap = 'independent.textfilecontent54'
            select = {'full_path': {'value': settings['full_path'], 'operation': 'equal', 'datatype': 'string'},
                      'pattern': {'value': pattern, 'operation': 'match', 'datatype': 'string'},
                      'instance': deepcopy(settings['instance'])}
            obj = {'capability': cap, 'object_title': name, 'select': select,
                   'filesystem': settings['filesystem'], 'collect': deepcopy(settings['collect'])}
        else:
            cap = settings['capability']
            if not isinstance(settings['full_path'], str) or not settings['full_path'].startswith('/') or not isinstance(settings['expected'], str):
                raise ValueError('invalid publisher backend values')
            if (cap, settings['field']) not in (('unix.symlink', 'canonical_path'), ('unix.file', 'type')):
                raise ValueError('unsupported backend predicate')
            obj = {'capability': cap, 'object_title': name,
                   'select': {'full_path': {'value': settings['full_path'], 'operation': 'equal', 'datatype': 'string'}}}
            a['states']['state-' + name] = {'capability': cap, 'state_title': name,
                'state': {'field': settings['field'], 'value': settings['expected'], 'operation': 'equal',
                          'datatype': 'string', 'match': 'all', 'existence': 'some'}}
        a['objects']['object-' + name] = obj
        test = {'test_title': name, 'capability': cap, 'object': 'object-' + name,
                'existence': settings['existence'], 'match': settings['match']}
        if kind == 'crypto_backends':
            test['states'] = ['state-' + name]
        a['tests']['test-' + name] = test
        a['evaluate']['all'].append({'test': 'test-' + name})
    if not a['states']:
        del a['states']
    return {'assessment': a}
