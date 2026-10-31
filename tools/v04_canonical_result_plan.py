#!/usr/bin/env python3
"""Canonical 0.4.0 six-state expression plan, with supplied Test outcomes only.

Compiles canonical Boolean syntax and owner-approved ordered conditional
branches over supplied outcomes. No Test/State/Item/Variable collection,
host execution or scanner parity is claimed.

This is the first bounded logical-result backend, NOT an executable scanner.
Refs #232 #229.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from collections import Counter

from v04_a_authoring_graph_index import canonical_json
from v04_a_truth_plan import (
    compile_expression, execute_supplied_results, UnsupportedExpression,
)

STAGE = "CANONICAL_040_SUPPLIED_TEST_RESULTS_ONLY_NOT_SCANNER"
SPEC = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
OP_ALIASES = {"and": "all", "or": "any", "xor": "odd"}
OPERATORS = frozenset(("and", "or", "one", "xor"))
MAX_NODES = 16384


def _legacy_result_tree(source, *, max_nodes=MAX_NODES):
    """Rewrite only equivalent operator names, preserving all other source."""
    count = 0

    def visit(node, depth):
        nonlocal count
        count += 1
        if count > max_nodes or depth > 256:
            raise ValueError("canonical expression resource budget exceeded")
        if not isinstance(node, dict):
            raise ValueError("canonical expression node must be an object")
        if 'if' in node:
            if not {'if', 'then', 'else'} <= set(node) or set(node) - {'if', 'then', 'else', 'else_if'}:
                raise ValueError('conditional requires if/then/final else')
            branches = node.get('else_if', [])
            if not isinstance(branches, list) or ('else_if' in node and not branches):
                raise ValueError('else_if requires a nonempty ordered list')
            fallback = visit(node['else'], depth + 1)
            for branch in reversed(branches):
                if not isinstance(branch, dict) or set(branch) != {'if', 'then'}:
                    raise ValueError('else_if entry requires exactly if/then')
                fallback = {'if': visit(branch['if'], depth + 1),
                            'then': visit(branch['then'], depth + 1), 'else': fallback}
            return {'if': visit(node['if'], depth + 1), 'then': visit(node['then'], depth + 1), 'else': fallback}
        if len(node) != 1:
            raise ValueError("expression must have exactly one operator")
        kind, payload = next(iter(node.items()))
        if kind in OPERATORS:
            if not isinstance(payload, list) or not payload:
                raise ValueError(f"operator {kind} requires nonempty children")
            return {OP_ALIASES.get(kind, kind):
                    [visit(child, depth + 1) for child in payload]}
        if kind == "not":
            return {"not": visit(payload, depth + 1)}
        if kind in ('not_applicable', 'not_evaluated'):
            if (not isinstance(payload, dict) or set(payload) != {'reason'}
                    or not isinstance(payload['reason'], str) or not payload['reason'].strip()):
                raise ValueError(f'{kind} requires an explicit nonempty reason')
            return {kind: deepcopy(payload)}
        if kind in ("test", "assessment"):
            return {kind: deepcopy(payload)}
        raise UnsupportedExpression(f"unsupported 0.4.0 result operator: {kind}")

    return visit(source, 0)


def _control_plan(assessment, tree, field):
    """Static references for all branches; nested blocks execute lazily (#255)."""
    refs = {'tests': set(), 'dependencies': set()}
    total = 0

    def block(node, path):
        nonlocal total
        total += 1
        if total > MAX_NODES or len(path) > 256:
            raise ValueError('conditional expression resource budget exceeded')
        if 'if' in node:
            branches = [{'condition': block(node['if'], path + ['if']),
                         'then': block(node['then'], path + ['then']), 'path': path}]
            for i, branch in enumerate(node.get('else_if', [])):
                at = path + ['else_if', i]
                branches.append({'condition': block(branch['if'], at + ['if']),
                                 'then': block(branch['then'], at + ['then']), 'path': at})
            return [{'op': 'select_first_true', 'branches': branches,
                     'else': block(node['else'], path + ['else']), 'path': path}]
        kind, payload = next(iter(node.items()))
        if kind in ('test', 'assessment'):
            group = 'tests' if kind == 'test' else 'dependencies'
            if not isinstance(payload, str) or payload not in assessment.get(group, {}):
                raise ValueError(f'{path}: unresolved {kind} reference {payload!r}')
            refs[group].add(payload)
            return [{'op': 'read_' + kind, 'id': payload, 'path': path}]
        if kind in ('not_applicable', 'not_evaluated'):
            return [{'op': kind, 'reason': payload['reason'], 'path': path}]
        if kind == 'not':
            return block(payload, path + [kind]) + [{'op': 'not', 'path': path}]
        instructions = []
        for i, child in enumerate(payload):
            instructions.extend(block(child, path + [OP_ALIASES.get(kind, kind), i]))
        return instructions + [{'op': OP_ALIASES.get(kind, kind), 'count': len(payload), 'path': path}]

    instructions = block(tree, [field])
    return {'instructions': instructions, 'instruction_count': total,
            'requires': {key: sorted(values) for key, values in refs.items()}}


def _has_control(tree):
    if isinstance(tree, dict):
        return bool({'if', 'not_evaluated', 'not_applicable'} & set(tree)) or any(_has_control(v) for v in tree.values())
    return isinstance(tree, list) and any(_has_control(v) for v in tree)


def compile_canonical_result_plan(assessment, field="evaluate"):
    if not isinstance(assessment, dict) or assessment.get("specification") != SPEC:
        raise ValueError("0.4.0 Assessment specification required")
    if assessment.get("mode") != "automated":
        raise ValueError("automated 0.4.0 Assessment required")
    if field not in ("evaluate", "applicability") or field not in assessment:
        raise ValueError("explicit 0.4.0 evaluate/applicability required")
    normalized = deepcopy(assessment)
    normalized[field] = _legacy_result_tree(assessment[field])
    control = _has_control(assessment[field])
    original_plan = (_control_plan(assessment, assessment[field], field) if control
                     else compile_expression(normalized, field))
    return {
        "stage": STAGE,
        "assessment_id": assessment["id"],
        "field": field,
        "source_sha256": sha256(canonical_json(assessment[field])).hexdigest(),
        "normalized_source_sha256": sha256(canonical_json(normalized[field])).hexdigest(),
        "instructions": original_plan["instructions"],
        "instruction_count": original_plan["instruction_count"],
        "requires": original_plan["requires"],
        "scanner_executed": False,
        "tests_evaluated": False,
        "conditional_semantics_implemented": control,
    }


def evaluate_supplied_results(plan, test_results, dependency_results=None):
    """Full OVAL six-state Boolean composition; no hidden Test defaults."""
    if not isinstance(plan, dict) or plan.get("stage") != STAGE:
        raise ValueError("unsupported native 0.4 result plan")
    if plan.get('conditional_semantics_implemented'):
        return _evaluate_control(plan, test_results, dependency_results)
    # Delegate six-state truth algebra to audited OVAL-aligned operator core.
    legacy = {
        "stage": "RESEARCH_SUPPLIED_RESULTS_ONLY_NOT_SCANNER",
        "assessment_id": plan["assessment_id"],
        "expression_field": plan["field"],
        "instructions": plan["instructions"],
        "instruction_count": plan["instruction_count"],
        "requires": plan["requires"],
    }
    result = execute_supplied_results(legacy, test_results, dependency_results)
    return {
        **result,
        "stage": STAGE,
        "scanner_executed": False,
        "tests_evaluated": False,
        "outcomes_provided_by_caller": True,
    }


def _evaluate_control(plan, tests, dependencies):
    from v04_a_truth_plan import SIX, combine
    deps = dependencies or {}
    if not isinstance(tests, dict) or not isinstance(deps, dict):
        raise ValueError('supplied outcomes must be mappings')
    for supplied, key in ((tests, 'tests'), (deps, 'dependencies')):
        if set(supplied) - set(plan['requires'][key]):
            raise ValueError('undeclared supplied outcome')
    trace, terminals = [], []

    def execute(instructions):
        stack = []
        for instruction in instructions:
            op = instruction['op']
            if op in ('read_test', 'read_assessment'):
                values = tests if op == 'read_test' else deps
                if instruction['id'] not in values:
                    raise ValueError('missing supplied outcome for selected ' + instruction['id'])
                value = values[instruction['id']]
                if type(value) is not str or value not in SIX:
                    raise ValueError('invalid six-state supplied outcome')
            elif op in ('not_applicable', 'not_evaluated'):
                value = op
                terminals.append({'outcome': op, 'reason': instruction['reason'], 'path': instruction['path']})
            elif op == 'select_first_true':
                for branch in instruction['branches']:
                    condition = execute(branch['condition'])
                    if condition == 'true':
                        value = execute(branch['then'])
                        break
                    if condition != 'false':
                        value = condition
                        break
                else:
                    value = execute(instruction['else'])
            elif op == 'not':
                if not stack:
                    raise ValueError('malformed conditional unary stack')
                previous = stack.pop()
                value = {'true': 'false', 'false': 'true'}.get(previous, previous)
            elif op in ('all', 'any', 'one', 'odd'):
                count = instruction['count']
                if type(count) is not int or count < 1 or count > len(stack):
                    raise ValueError('malformed conditional operator count')
                values = stack[-count:]
                del stack[-count:]
                value = combine(op, values)
            else:
                raise ValueError('unsupported conditional instruction')
            stack.append(value)
            trace.append({'path': instruction['path'], 'operation': op, 'outcome': value})
        if len(stack) != 1:
            raise ValueError('malformed conditional expression stack')
        return stack[0]

    outcome = execute(plan['instructions'])
    return {'stage': STAGE, 'assessment_id': plan['assessment_id'], 'expression_field': plan['field'],
            'outcome': outcome, 'trace': trace, 'explicit_terminal_outcomes': terminals,
            'manual_follow_up_required': outcome == 'not_evaluated' and any(t['outcome'] == outcome for t in terminals),
            'tests_supplied': len(tests), 'dependencies_supplied': len(deps),
            'scanner_executed': False, 'tests_evaluated': False, 'outcomes_provided_by_caller': True}


def census_authoring(documents):
    """Report exact result-plan eligibility; unsupported cases stay visible."""
    counts = Counter()
    examples = {}
    plans = []
    for path, doc in sorted(documents.items()):
        assessment = doc.get("assessment")
        if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
            continue
        counts["automated_assessments"] += 1
        try:
            plan = compile_canonical_result_plan(assessment)
        except UnsupportedExpression as error:
            counts["unsupported_result_expressions"] += 1
            if len(examples) < 12:
                examples[path] = str(error)
        else:
            counts["compiled_supplied_result_plans"] += 1
            counts["compiled_result_instructions"] += plan["instruction_count"]
            plans.append({
                "path": path,
                "assessment_id": plan["assessment_id"],
                "source_sha256": plan["source_sha256"],
                "instruction_count": plan["instruction_count"],
                "required_tests": len(plan["requires"]["tests"]),
                "required_dependencies": len(plan["requires"]["dependencies"]),
            })
    return {
        "stage": STAGE,
        "counts": dict(sorted(counts.items())),
        "unsupported_examples": examples,
        "plan_manifest_sha256": sha256(canonical_json(plans)).hexdigest(),
        "scanner_executed": False,
        "tests_evaluated": False,
        "conditional_semantics_implemented": True,
    }
