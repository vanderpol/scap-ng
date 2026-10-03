"""Experimental Object/requirement evaluator over supplied observations only.

This is a small executable language experiment, not a scanner or NG replacement.
No commands, filesystem access, native-schema changes, or OVAL lowering occur.
"""
from dataclasses import dataclass


@dataclass
class Value:
    value: object = None
    status: str = 'observed'


@dataclass
class Item:
    key: str
    fields: dict


@dataclass
class Population:
    items: list
    status: str = 'complete'


# Closed experimental contracts; relationships preserve their parent Item.
TYPES = {
    'file': {'permissions': 'permissions'},
    'zone': {'signed': 'boolean', 'integrated': 'boolean', 'records': ('records', 'rr')},
    'rr': {'type': 'string'},
    'installation': {'main': ('records', 'directive'), 'loaded': ('records', 'directive')},
    'directive': {'name': 'string', 'value': 'scalar'},
}
CAPABILITIES = {
    'unix.file': 'file',
    'windows.dns.forward-zones': 'zone',
    'apache.installations': 'installation',
}
RIGHTS = {'owner': {'read': 0o400, 'write': 0o200, 'execute': 0o100},
          'group': {'read': 0o40, 'write': 0o20, 'execute': 0o10},
          'other': {'read': 0o4, 'write': 0o2, 'execute': 0o1},
          'special': {'setuid': 0o4000, 'setgid': 0o2000, 'sticky': 0o1000}}


def combine(kind, results):
    """Small native proof contract, independent of inherited OVAL helper.

    Only evaluated true/false/error/unknown enter this prototype. Existing six-
    state legacy support is retained elsewhere; this is not complete conformance.
    """
    if kind not in ('all', 'any') or any(r not in ('true', 'false', 'error', 'unknown') for r in results):
        raise ValueError('outside bounded Boolean proof domain')
    if kind == 'all' and 'false' in results:
        return 'false'
    if kind == 'any' and 'true' in results:
        return 'true'
    if 'error' in results:
        return 'error'
    if 'unknown' in results:
        return 'unknown'
    return 'true' if kind == 'all' else 'false'


def permission_mask(allowance):
    if not isinstance(allowance, dict) or set(allowance) != set(RIGHTS):
        raise ValueError('permission allowance must state all four categories')
    mask = 0
    for category, allowed in allowance.items():
        if not isinstance(allowed, list) or any(not isinstance(x, str) for x in allowed):
            raise ValueError('permission allowance must use named rights')
        if len(allowed) != len(set(allowed)) or set(allowed) - set(RIGHTS[category]):
            raise ValueError('unknown or repeated permission right')
        for name in allowed:
            mask |= RIGHTS[category][name]
    return mask


def compile_spec(doc):
    """Validate the whole fixed AST before any evaluation, including exceptions."""
    if not isinstance(doc, dict) or set(doc) != {'objects', 'tests', 'evaluate'}:
        raise ValueError('expected objects/tests/evaluate')
    env = {}
    for name, declaration in doc['objects'].items():
        if set(declaration) - {'capability', 'scope'} or 'capability' not in declaration:
            raise ValueError('invalid Object declaration')
        if declaration['capability'] not in CAPABILITIES:
            raise ValueError('capability is outside this experiment')
        env[name] = CAPABILITIES[declaration['capability']]

    def source_type(path, names):
        if not isinstance(path, str):
            raise ValueError('Object reference must be a literal name')
        parts = path.split('.')
        if len(parts) == 1 and parts[0] in env:
            return env[parts[0]]
        if len(parts) == 2 and parts[0] in names:
            field = TYPES[names[parts[0]]].get(parts[1])
            if isinstance(field, tuple):
                return field[1]
        raise ValueError('unknown Object or relationship: ' + path)

    def predicate(p, item_type):
        if not isinstance(p, dict) or not p:
            raise ValueError('empty or invalid requirement')
        for field, comparison in p.items():
            ft = TYPES[item_type].get(field)
            if ft is None or not isinstance(comparison, dict) or len(comparison) != 1:
                raise ValueError('unknown field or ambiguous comparison: ' + field)
            op, expected = next(iter(comparison.items()))
            if op == 'at_most' and ft == 'permissions':
                permission_mask(expected)
            elif op == 'include' and ft == ('records', 'rr'):
                if not isinstance(expected, list) or not expected or any(not isinstance(x, str) for x in expected):
                    raise ValueError('include requires named record types')
                if len(expected) != len(set(expected)):
                    raise ValueError('duplicate required record type')
            elif op == 'settings' and ft == ('records', 'directive'):
                if not isinstance(expected, dict) or not expected:
                    raise ValueError('settings require named expectations')
                for setting, rule in expected.items():
                    if not isinstance(setting, str) or not isinstance(rule, dict) or rule.get('presence') not in ('required', 'optional'):
                        raise ValueError('setting presence must be explicit')
                    predicate({'value': {k:v for k,v in rule.items() if k != 'presence'}}, 'directive')
            elif op == 'equals' and ((ft == 'boolean' and type(expected) is bool) or
                                    (ft == 'string' and isinstance(expected, str)) or
                                    (ft == 'scalar' and type(expected) in (str, int))):
                pass
            elif op == 'at_least' and ft == 'scalar' and type(expected) is int:
                pass
            else:
                raise ValueError('comparison incompatible with field: ' + field)

    def node(n, names):
        if not isinstance(n, dict):
            raise ValueError('invalid Test body')
        if set(n) in ({'all'}, {'any'}):
            children = next(iter(n.values()))
            if not isinstance(children, list) or not children:
                raise ValueError('Boolean expression needs children')
            for child in children:
                node(child, names)
            return
        if set(n) - {'every', 'as', 'empty', 'where', 'require', 'unless'} or not {'every', 'as', 'empty', 'require'} <= set(n):
            raise ValueError('expected every/as/empty/require')
        typ = source_type(n['every'], names)
        if not isinstance(n['as'], str) or n['as'] in env or n['as'] in names:
            raise ValueError('invalid or shadowing Item name')
        if n['empty'] not in ('allowed', 'violation'):
            raise ValueError('empty population behavior must be explicit')
        scoped = {**names, n['as']: typ}
        if 'where' in n:
            predicate(n['where'], typ)
        if 'unless' in n:
            node(n['unless'], names)
        if set(n['require']) in ({'all'}, {'any'}) or 'every' in n['require']:
            node(n['require'], scoped)
        else:
            predicate(n['require'], typ)

    if not doc['tests'] or doc['evaluate'] != 'all':
        raise ValueError('prototype evaluates all named Tests')
    for test in doc['tests'].values():
        node(test, {})
    return doc


def evaluate(doc, observations):
    compile_spec(doc)
    findings = []

    def valid_population(population):
        if not isinstance(population, Population) or population.status not in ('complete', 'incomplete', 'error', 'not_collected'):
            return False
        if not isinstance(population.items, list) or any(not isinstance(x, Item) or not isinstance(x.key, str) or not x.key or not isinstance(x.fields, dict) for x in population.items):
            return False
        if len({x.key for x in population.items}) != len(population.items):
            return False
        return all(valid_population(v) if isinstance(v, Population) else isinstance(v, Value)
                   for item in population.items for v in item.fields.values())

    if not isinstance(observations, dict) or any(not valid_population(p) for p in observations.values()):
        return {'result': 'error', 'tests': {}, 'findings': [{'reason': 'malformed observation population or duplicate Item identity'}]}

    def source(path, names):
        parts = path.split('.')
        if len(parts) == 1:
            return observations.get(path, Population([], 'not_collected'))
        return names[parts[0]].fields.get(parts[1], Population([], 'error'))

    def gate(status):
        if status == 'complete':
            return 'true'
        if status in ('incomplete', 'not_collected'):
            return 'unknown'
        return 'error'

    def predicate(p, item, test, retain=True):
        results = []
        for field, comparison in p.items():
            op, expected = next(iter(comparison.items()))
            actual = item.fields.get(field, Value(status='error'))
            detail = None
            if op == 'settings':
                if not isinstance(actual, Population):
                    result = 'error'
                else:
                    setting_results = []
                    detail = {'settings': []}
                    for setting, requirement in expected.items():
                        outcomes = []
                        observed = []
                        for record in actual.items:
                            selected = predicate({'name': {'equals': setting}}, record, test, False)
                            if selected == 'false':
                                continue
                            if selected != 'true':
                                outcomes.append(selected)
                                continue
                            comparison = {'value': {k:v for k,v in requirement.items() if k != 'presence'}}
                            outcome = predicate(comparison, record, test, False)
                            outcomes.append(outcome)
                            observed.append({'occurrence': record.key, 'result': outcome})
                        if not outcomes:
                            outcome = ('true' if requirement['presence'] == 'optional' else 'false') if actual.status == 'complete' else gate(actual.status)
                        else:
                            outcome = combine('all', outcomes + [gate(actual.status)])
                        setting_results.append(outcome)
                        detail['settings'].append({'name': setting, 'result': outcome, 'occurrences': observed})
                    result = combine('all', setting_results)
            elif op == 'include':
                if not isinstance(actual, Population) or actual.status not in ('complete', 'incomplete', 'error', 'not_collected'):
                    result = 'error'
                else:
                    known, unresolved = set(), []
                    for record in actual.items:
                        value = record.fields.get('type', Value(status='error'))
                        if not isinstance(value, Value):
                            unresolved.append('error')
                        elif value.status == 'observed' and isinstance(value.value, str):
                            known.add(value.value)
                        else:
                            unresolved.append('error' if value.status == 'error' else 'unknown')
                    missing = set(expected) - known
                    # Positive witnesses prove monotone containment even in a
                    # partial population. Negative absence needs complete data.
                    result = (gate(actual.status) if actual.status in ('error', 'not_collected') else
                              'true' if not missing else combine('all', unresolved + [gate(actual.status)])
                              if unresolved or actual.status != 'complete' else 'false')
                    detail = {'missing': sorted(missing)}
            elif not isinstance(actual, Value):
                result = 'error'
            elif actual.status != 'observed':
                result = {'error': 'error', 'unknown': 'unknown', 'missing': 'false'}.get(actual.status, 'error')
            elif op == 'equals':
                result = ('true' if actual.value == expected else 'false') if type(actual.value) is type(expected) else 'error'
            elif op == 'at_least':
                result = ('true' if actual.value >= expected else 'false') if type(actual.value) is int else 'error'
            else:
                mode = actual.value
                if type(mode) is not int or not 0 <= mode <= 0o7777:
                    result = 'error'
                else:
                    excess = mode & ~permission_mask(expected)
                    result = 'false' if excess else 'true'
                    detail = {'forbidden': [category + '.' + name for category, rights in RIGHTS.items()
                                           for name, bit in rights.items() if excess & bit]}
            results.append(result)
            if retain:
                findings.append({'test': test, 'item': item.key, 'field': field,
                                 'operator': op, 'result': result, 'detail': detail})
        return combine('all', results)

    def node(n, names, test):
        if set(n) in ({'all'}, {'any'}):
            kind, children = next(iter(n.items()))
            return combine(kind, [node(child, names, test) for child in children])
        if 'unless' in n:
            exception = node(n['unless'], names, test)
            if exception == 'true':
                findings.append({'test': test, 'exception': 'satisfied', 'result': 'true'})
                return 'true'
        else:
            exception = 'false'
        population = source(n['every'], names)
        if not isinstance(population, Population):
            return 'error'
        if len({x.key for x in population.items}) != len(population.items):
            return 'error'
        status = gate(population.status)
        rows = []
        for item in population.items:
            if 'where' in n:
                selected = predicate(n['where'], item, test, False)
                if selected == 'false':
                    continue
                if selected != 'true':
                    rows.append(selected)
                    continue
            scoped = {**names, n['as']: item}
            req = n['require']
            rows.append(node(req, scoped, test) if set(req) in ({'all'}, {'any'}) or 'every' in req
                        else predicate(req, item, test))
        if not rows:
            result = ('true' if n['empty'] == 'allowed' else 'false') if status == 'true' else status
        else:
            result = combine('all', rows + [status])
        return combine('any', [exception, result])

    results = {name: node(test, {}, name) for name, test in doc['tests'].items()}
    return {'result': combine('all', list(results.values())), 'tests': results, 'findings': findings}
