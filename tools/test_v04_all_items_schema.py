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
 {"items":"one_or_more","all_items_must":[{"and":[{"type":{"equals":"dword"}},{"value":{"equals":0}}]}]},
 {"items":"may_be_absent","all_items_must":[{"or":[{"value":{"equals":"Enterprise"}},{"value":{"equals":"EnterpriseS"}}]}]}
]
bad=[
 {"items":"one_or_more","all_items_must":[]},
 {"items":"one_or_more"},
 {"all_items_must":[{"value":{"equals":0}}]},
 {"items":"sometimes","all_items_must":[{"value":{"equals":0}}]},
 {"items":"one_or_more","all_items_must":[{"and":[]}]},
]
for x in good:
    errors=list(validator.iter_errors(x))
    if errors:raise AssertionError(f"Valid 0.4 requirement rejected: {x}; {errors[0]}")
for x in bad:
    if not list(validator.iter_errors(x)):raise AssertionError(f"Invalid 0.4 requirement accepted: {x}")
print(f"PASS: {len(good)} positive and {len(bad)} negative scoped 0.4 all-items schema cases")
