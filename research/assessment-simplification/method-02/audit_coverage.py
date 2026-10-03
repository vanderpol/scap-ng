"""Semantic event-coverage research: restricted ordered audit exit rules.

Not a Linux audit interpreter. Does not acquire rules or access targets. Supported
conditions are arch, syscall lists and conjunctions of audit-user-ID comparisons.
Unexpected syntax returns unknown, never silently disappears.
"""
from dataclasses import dataclass
import re
import shlex

MAX_AUID = 2**32 - 1
SYSCALLS = ('setxattr', 'fsetxattr', 'lsetxattr', 'removexattr', 'fremovexattr', 'lremovexattr')


@dataclass
class Rule:
    action: str
    arch: str
    syscalls: frozenset
    predicates: tuple
    line: int


def parse(lines):
    rules = []
    for number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        words = shlex.split(line)
        action, arch, syscalls, predicates = None, None, set(), []
        i = 0
        while i < len(words):
            if i + 1 >= len(words):
                raise ValueError('unpaired option')
            flag, value = words[i:i+2]
            i += 2
            if flag == '-a' and action is None:
                parts = value.split(',')
                if len(parts) != 2 or 'exit' not in parts or not ({'always', 'never'} & set(parts)):
                    raise ValueError('unsupported rule action/list')
                action = next(x for x in parts if x != 'exit')
            elif flag == '-S':
                if arch is None:
                    # auditctl resolves syscall names through the current arch
                    # table; treating a later arch as equivalent is unsafe.
                    raise ValueError('arch must precede syscall name lookup')
                names = value.split(',')
                if any(not re.fullmatch(r'[a-z][a-z0-9_]*', x) for x in names):
                    raise ValueError('numeric or invalid syscall name')
                syscalls.update(names)
            elif flag == '-k':
                if not re.fullmatch(r'[-\w]+', value):
                    raise ValueError('unsupported key')
            elif flag == '-F':
                if value.startswith('arch=') and arch is None and value[5:] in ('b32', 'b64'):
                    arch = value[5:]
                elif value.startswith('key=') and re.fullmatch(r'[-\w]+', value[4:]):
                    pass
                else:
                    match = re.fullmatch(r'auid(>=|<=|!=|=|>|<)(unset|-1|\d+)', value)
                    if not match:
                        raise ValueError('unsupported condition: ' + value)
                    op, literal = match.groups()
                    val = MAX_AUID if literal in ('unset', '-1') else int(literal)
                    if not 0 <= val <= MAX_AUID:
                        raise ValueError('audit user ID outside unsigned domain')
                    predicates.append((op, val))
            else:
                raise ValueError('unsupported or repeated rule option: ' + flag)
        if action is None or arch is None or not syscalls:
            raise ValueError('rule must declare action, arch and syscall')
        rules.append(Rule(action, arch, frozenset(syscalls), tuple(predicates), number))
    return rules


def matches(rule, arch, syscall, auid):
    if rule.arch != arch or (syscall not in rule.syscalls and 'all' not in rule.syscalls):
        return False
    for op, val in rule.predicates:
        if not {'=': auid == val, '!=': auid != val, '>=': auid >= val,
                '<=': auid <= val, '>': auid > val, '<': auid < val}[op]:
            return False
    return True


def interval_coverage(rules, arch, syscall, low, high, maximum_cells=10000):
    """Exact finite partition for this conjunction/comparison grammar.

    Each predicate is constant between its boundary and adjacent integer.
    Examine every cell, not one representative user for the whole actor class.
    """
    boundaries = {low, high + 1}
    for rule in rules:
        if rule.arch == arch and (syscall in rule.syscalls or 'all' in rule.syscalls):
            for _, val in rule.predicates:
                for point in (val, val + 1):
                    if low <= point <= high + 1:
                        boundaries.add(point)
    if len(boundaries) - 1 > maximum_cells:
        raise OverflowError('coverage resource limit')
    sorted_points = sorted(boundaries)
    witnesses, gaps = [], []
    for left, right in zip(sorted_points, sorted_points[1:]):
        first = next((r for r in rules if matches(r, arch, syscall, left)), None)
        cell = {'auid': [left, right - 1], 'rule_line': first.line if first else None}
        (witnesses if first and first.action == 'always' else gaps).append(cell)
    return {'result': 'false' if gaps else 'true', 'witnesses': witnesses, 'gaps': gaps}


def evaluate(spec, lines, *, status='complete', source='loaded', maximum_cells=10000):
    if set(spec) != {'source', 'architectures', 'syscalls', 'actors'}:
        raise ValueError('invalid coverage requirement')
    if spec['source'] not in ('loaded', 'persisted') or spec['source'] != source:
        raise ValueError('observed/required rule sources differ')
    domains = {'root-logins': (0, 0), 'user-logins': (1000, MAX_AUID - 1)}
    for field, allowed in [('architectures', {'b32', 'b64'}), ('syscalls', set(SYSCALLS)), ('actors', set(domains))]:
        values = spec[field]
        if not isinstance(values, list) or not values or any(not isinstance(x, str) for x in values) or len(values) != len(set(values)) or set(values) - allowed:
            raise ValueError('invalid publisher coverage domain: ' + field)
    if status != 'complete':
        # Missing order/rules can alter first-match outcome in either direction.
        return {'result': 'error' if status == 'error' else 'unknown', 'reason': 'rule inventory not complete'}
    try:
        rules = parse(lines)
    except ValueError as error:
        return {'result': 'unknown', 'reason': 'unsupported rule semantics: ' + str(error)}
    rows = []
    try:
        for arch in spec['architectures']:
            for syscall in spec['syscalls']:
                for actor in spec['actors']:
                    row = interval_coverage(rules, arch, syscall, *domains[actor], maximum_cells=maximum_cells)
                    rows.append({'architecture': arch, 'syscall': syscall, 'actor': actor, **row})
    except OverflowError as error:
        return {'result': 'error', 'reason': str(error)}
    return {'result': 'false' if any(r['result'] == 'false' for r in rows) else 'true', 'coverage': rows}
