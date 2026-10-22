#!/usr/bin/env python3
"""Scoped 0.4.0 grammar acceptance tests; not full corpus schema conformance."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator, RefResolver

root=Path("schema/v0.4.0")
d=json.loads((root/"assessment-language.schema.json").read_text())
url=d["$id"]
resolver=RefResolver.from_schema(d,store={url:d})
validator=Draft202012Validator({"$ref":"#/$defs/all_items_requirement","$defs":d["$defs"]},resolver=resolver)
good=[
 {"items":"one_or_more","all_items_must":[{"and":[{"type":{"require":"at_least_one_exists_and_all_match","equals":"dword"}},{"value":{"require":"at_least_one_exists_and_all_match","equals":0}}]}]},
 {"items":"may_be_absent","all_items_must":[{"or":[{"value":{"require":"at_least_one_exists_and_all_match","equals":"Enterprise"}},{"value":{"require":"at_least_one_exists_and_all_match","equals":"EnterpriseS"}}]}]}
]
bad=[
 {"items":"one_or_more","all_items_must":[]},
 {"items":"one_or_more"},
 {"all_items_must":[{"value":{"require":"at_least_one_exists_and_all_match","equals":0}}]},
 {"items":"sometimes","all_items_must":[{"value":{"require":"at_least_one_exists_and_all_match","equals":0}}]},
 {"items":"one_or_more","all_items_must":[{"and":[]}]},
]
for x in good:
    errors=list(validator.iter_errors(x))
    if errors:raise AssertionError(f"Valid 0.4 requirement rejected: {x}; {errors[0]}")
for x in bad:
    if not list(validator.iter_errors(x)):raise AssertionError(f"Invalid 0.4 requirement accepted: {x}")
print(f"PASS: {len(good)} positive and {len(bad)} negative scoped 0.4 all-items schema cases")

presence=Draft202012Validator({"$ref":"#/$defs/item_presence_requirement","$defs":d["$defs"]},resolver=resolver)
for x in ({"items":"one_or_more"},{"items":"none"},{"items":"exactly_one"},{"items":"all"},{"items":"may_be_absent"}):
    assert not list(presence.iter_errors(x)), x
for x in ({"items":"unexpected"},{"items":"none","all_items_must":[]},{}):
    assert list(presence.iter_errors(x)), x
# Scoped field cardinality must be retained on a Boolean State group,
# rather than silently promoted into Test Item existence.
scoped={
 "items":"one_or_more",
 "all_items_must":[{"and":[
    {"type":{"require":"at_least_one_exists_and_all_match","equals":"dword"}},
    {"value":{"require":"at_least_one_exists_and_all_match","equals":0}}
 ],"state_fields_require":"at_least_one_exists_and_all_match"}]
}
assert not list(validator.iter_errors(scoped)), "Scoped field requirement rejected"
scoped_bad=json.loads(json.dumps(scoped))
scoped_bad["all_items_must"][0]["state_fields_require"]="invented_requirement"
assert list(validator.iter_errors(scoped_bad)), "Invalid scoped field requirement accepted"
print("PASS: State-free structured presence required/invalid cases")

# Strict context: inherited field predicates require explicit group or Test
# require.field_requirement. No implicit fallback is valid.
test_validator=Draft202012Validator({"$ref":"#/$defs/test","$defs":d["$defs"]},resolver=resolver)
no_field_scope={
  "require":{"items":"one_or_more","all_items_must":[
    {"fields":{"type":{"equals":"dword"},"value":{"equals":0}}}
  ]}
}
test_level_scope=json.loads(json.dumps(no_field_scope))
test_level_scope["require"]["field_requirement"]="at_least_one_exists_and_all_match"
assert list(test_validator.iter_errors(no_field_scope)), "Unscoped predicates cannot omit field require"
assert not list(test_validator.iter_errors(test_level_scope)), "Explicit Test field requirement rejected"
group_scope=json.loads(json.dumps(no_field_scope))
group_scope["require"]["all_items_must"][0]["field_requirement"]="at_least_one_exists_and_all_match"
assert not list(test_validator.iter_errors(group_scope)), "Scoped Boolean group rejected"
print("PASS: explicit Test/group State-field cardinality guards")

# Legacy State-bearing imported checks are permitted only with an explicitly
# declared Test-level State-field requirement, preserving OVAL cardinality.
legacy={
 "states":[{"subexpression":{"matches_regex":"type=omfwd"}},{"subexpression":{"matches_regex":"action=gtls"}}],
 "states_match":"all",
 "require":"at_least_one_exists_and_some_match"
}
legacy_scope=json.loads(json.dumps(legacy))
legacy_scope["state_fields_require"]="at_least_one_exists_and_all_match"
assert list(test_validator.iter_errors(legacy)), "Missing field scope must not silently pass"
assert not list(test_validator.iter_errors(legacy_scope)), "Explicit legacy State scope rejected"
print("PASS: legacy State field scope requires explicit declaration")
