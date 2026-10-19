#!/usr/bin/env python3
"""Refs #245: source-backed audit of private Objects inside derived Variables.

Non-normative, read-only C authoring research. A direct field-of-private-Object
acquisition can be presented as ONE derived-value card without rewriting the
collector, original Variable DAG, or provenance. Named shared Objects, Set/
Filter/foreach populations and dynamic commands remain explicit boundaries.
No scanner, OVAL runtime, authoring grammar, caching or source migration proof.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json

from v04_a_dataflow_index import index_assessment_dataflow


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False)


def digest(value):
    return sha256(canonical_json(value).encode('utf-8')).hexdigest()


def _walk(node, path=()):
    if isinstance(node, dict):
        yield path, node
        for key, child in node.items():
            yield from _walk(child, path+(key,))
    elif isinstance(node, list):
        for index, child in enumerate(node):
            yield from _walk(child, path+(index,))


def inspect_private_value_sources(assessment):
    """Classify, but NEVER rewrite, collection boundaries in Variables.

    Source graph is validated before any view. Unknown inline shapes are
    explicitly not presented as a safe single-value acquisition.
    """
    if not isinstance(assessment, dict) or assessment.get('mode') != 'automated':
        raise ValueError('automated Assessment required')
    variables = assessment.get('variables')
    if not isinstance(variables, dict) or not variables:
        raise ValueError('named derived Variables required')
    graph = index_assessment_dataflow(assessment)
    referenced = Counter(e['to_id'] for e in graph['edges']
                         if e['role']=='variable_value')
    cards=[]
    for name, var in sorted(variables.items()):
        if not isinstance(var, dict) or not isinstance(var.get('expression'), dict):
            raise ValueError('source Variable expression required')
        expression = var['expression']
        sources=[]
        unexpected=[]
        for path, node in _walk(expression):
            if isinstance(node, dict) and 'object' in node:
                obj = node['object']
                if len(path)>=1 and path[-1]=='values' and (
                    isinstance(obj, (dict, str))
                ) and isinstance(node.get('field'), str) and node['field']:
                    source_kind = ('inline_private' if isinstance(obj, dict)
                                   else 'named_shared')
                    hazards=[]
                    if source_kind=='named_shared':
                        hazards.append('named_acquisition_scope')
                    else:
                        for _, member in _walk(obj):
                            if 'set' in member: hazards.append('set_population')
                            if 'filters' in member: hazards.append('filter_population')
                            if 'for_each' in member: hazards.append('foreach_lineage')
                        if isinstance(obj.get('collect'), dict):
                            if any(isinstance(v, dict) for v in obj['collect'].values()):
                                hazards.append('dynamic_collection_arguments')
                        if isinstance(obj.get('select'), dict):
                            if any(isinstance(v, dict) and ('from' in v or
                                any(isinstance(x, dict) for x in v.values()))
                                for v in obj['select'].values()):
                                hazards.append('dynamic_selector')
                    sources.append({
                        'at': list(path)+['object'],
                        'source_kind': source_kind,
                        'field': node['field'],
                        'original_object_sha256': digest(obj),
                        'hazards': sorted(set(hazards)),
                    })
                else:
                    # An 'object' key at another position may denote another
                    # provider source; do not silently drop this dependency.
                    unexpected.append(list(path)+['object'])
        is_simple=(len(sources)==1 and sources[0]['source_kind']=='inline_private'
                   and not unexpected and not any(h in sources[0]['hazards']
                    for h in ('set_population','filter_population','foreach_lineage')))
        cards.append({
            'source_variable_id': name,
            'source_title': var.get('title', var.get('variable_title')),
            'datatype': var.get('datatype'),
            'source_variable_sha256': digest(var),
            'direct_source_consumers': referenced.get(name, 0),
            'value_sources': sources,
            'unsupported_object_contexts': unexpected,
            'candidate': ('PRIVATE_VALUE_WITH_OBJECT_INSIDE' if is_simple else
                          'NAMED_SOURCE_OR_COMPLEX_VALUE_GRAPH_KEEP_EXPLICIT'),
            'display_as_one_derived_value': is_simple,
            'explicit_dependency_required': (
                referenced.get(name,0)>1 or any(s['hazards'] for s in sources)
                or len(sources)!=1 or bool(unexpected)),
            'compiler_may_inline_or_deduplicate': False,
        })
    return {
        'stage': 'C_READ_ONLY_PRIVATE_OBJECT_VALUE_SCOPE_AUDIT',
        'assessment_id': assessment.get('id'),
        'source_sha256': digest(assessment),
        'source_graph_sha256': digest(graph),
        'variables': cards,
        'summary': {
            'named_variables': len(cards),
            'private_value_cards': sum(x['display_as_one_derived_value'] for x in cards),
            'inline_object_acquisitions': sum(s['source_kind']=='inline_private'
                for x in cards for s in x['value_sources']),
            'named_shared_object_value_sources': sum(s['source_kind']=='named_shared'
                for x in cards for s in x['value_sources']),
            'unclassified_object_contexts': sum(len(x['unsupported_object_contexts'])
                for x in cards),
        },
        'source_unchanged': True,
        'scanner_executed': False,
        'source_parity_proven': False,
        'automatic_migration_authorized': False,
    }


def verify_private_value_source_view(report, assessment):
    if (not isinstance(report, dict) or report != inspect_private_value_sources(assessment)):
        raise ValueError('C private Object view changed, source drifted or unsupported')
    return deepcopy(assessment)
