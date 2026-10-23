#!/usr/bin/env python3
"""Direct Test.require schema checks for the 0.4.0 authoring candidate."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator


root = Path(__file__).resolve().parents[1] / 'schema/v0.4.0'
schema = json.loads((root / 'assessment-language.schema.json').read_text())
defs = schema['$defs']
condition = Draft202012Validator({'$ref': '#/$defs/canonical_all_items_requirement',
                                  '$defs': defs})
presence = Draft202012Validator({'$ref': '#/$defs/item_presence_requirement',
                                 '$defs': defs})
test = Draft202012Validator({'$ref': '#/$defs/test', '$defs': defs})

count = {'values_found': 'one_or_more', 'values_matching': 'every'}
good = [
    {'items_found': 'one_or_more', 'items_satisfying': 'every',
     'fields': {'type': {'equals': 'dword', **count},
                'value': {'equals': 0, **count}}},
    {'items_found': 'may_be_absent', 'items_satisfying': 'one_or_more',
     'field_requirement': count,
     'or': [{'fields': {'value': {'equals': 'Enterprise'}}},
            {'fields': {'value': {'equals': 'EnterpriseS'}}}]},
    {'items_found': 'exactly_one', 'items_satisfying': 'none',
     'and': [{'fields': {'value': {'equals': 'Enterprise', **count}}},
             {'fields': {'type': {'equals': 'string', **count}}}]},
]
bad = [
    {'items_found': 'one_or_more', 'items_satisfying': 'every'},
    {'items_found': 'one_or_more', 'fields': {'value': {'equals': 0, **count}}},
    {'items_satisfying': 'every', 'fields': {'value': {'equals': 0, **count}}},
    {'items_found': 'one_or_more', 'items_satisfying': 'all',
     'fields': {'value': {'equals': 0, **count}}},
    {'items_found': 'one_or_more', 'items_satisfying': 'every',
     'or': []},
    {'items_found': 'one_or_more', 'items_satisfying': 'every',
     'fields': {'value': {'equals': 0}}},
]
for value in good:
    assert not list(condition.iter_errors(value)), value
for value in bad:
    assert list(condition.iter_errors(value)), value

for quantity in ('none', 'exactly_one', 'one_or_more', 'may_be_absent'):
    assert not list(presence.iter_errors({'items_found': quantity})), quantity
for value in ({}, {'items': 'one_or_more'}, {'items_found': 'every'},
              {'items_found': 'one_or_more', 'items_satisfying': 'every'}):
    assert list(presence.iter_errors(value)), value

scope = {'require': {'items_found': 'one_or_more', 'items_satisfying': 'every',
                     'field_requirement': count,
                     'fields': {'type': {'equals': 'dword'},
                                'value': {'equals': 0}}}}
assert not list(test.iter_errors(scope)), 'Test scope did not provide field requirements'
no_scope = json.loads(json.dumps(scope))
del no_scope['require']['field_requirement']
assert list(test.iter_errors(no_scope)), 'Missing field scope accepted'
group_scope = {'require': {'items_found': 'one_or_more', 'items_satisfying': 'every',
                           'and': [{'field_requirement': count,
                                    'fields': {'value': {'equals': 0}}}]}}
assert not list(test.iter_errors(group_scope)), 'Group scope rejected'

legacy = {'states': [{'value': {'equals': 0}}], 'states_match': 'all',
          'require': 'at_least_one_exists_and_all_match'}
assert list(test.iter_errors(legacy)), 'Legacy State structure accepted'
print(f'PASS: {len(good)} positive and {len(bad)} negative Test cardinality cases, '
      'State-free presence, inherited fields, and legacy rejection')
