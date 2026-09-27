#!/usr/bin/env python3
"""Regression tests for OVAL 5.12.3 set, filter, and collection-flag semantics."""
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("oval_ir",HERE/"oval_semantic_ir.py")
oval_ir=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

a={"id":"a","path":"/support/txt"}
b={"id":"b","path":"/support/txt/txtfile"}
c={"id":"c","path":"/support/txt/txtfile/subtxtfile"}

assert oval_ir.oval_set_items("COMPLEMENT",[[a,b,c],[b,c]]) == [a]
assert oval_ir.oval_set_items("INTERSECTION",[[a,b,c],[b,c]]) == [b,c]
assert oval_ir.oval_set_items("UNION",[[a],[b,c]]) == [a,b,c]
assert oval_ir.oval_set_items("UNION",[[a,b],[b,c]]) == [a,b,c]

# Default filter action is exclude: matching b/c leaves a.
filtered=oval_ir.oval_apply_filter([a,b,c],[False,True,True])
assert filtered==[a],filtered

# Explicit include retains only matches.
included=oval_ir.oval_apply_filter([a,b,c],[False,True,True],"include")
assert included==[b,c],included

# Multiple filters are sequential.
seq=oval_ir.oval_apply_filters(
    [a,b,c],
    [
        ("exclude",lambda item:item["id"]=="c"),
        ("include",lambda item:item["id"] in {"a","b"}),
    ],
)
assert seq==[a,b],seq

# Nested set pattern from Self-Assertion: ((A-B) INTERSECTION (A UNION B)) == {a}
nested=oval_ir.oval_set_items(
    "INTERSECTION",
    [
        oval_ir.oval_set_items("COMPLEMENT",[[a,b,c],[b,c]]),
        oval_ir.oval_set_items("UNION",[[a],[b,c]]),
    ],
)
assert nested==[a],nested

# Representative flag combinations copied from OVAL 5.12.3 schema charts.
assert oval_ir.oval_set_flag("UNION","complete","does_not_exist")=="complete"
assert oval_ir.oval_set_flag("UNION","complete","incomplete")=="incomplete"
assert oval_ir.oval_set_flag("INTERSECTION","error","does_not_exist")=="does_not_exist"
assert oval_ir.oval_set_flag("INTERSECTION","complete","not_collected")=="not_collected"
assert oval_ir.oval_set_flag("COMPLEMENT","complete","does_not_exist")=="complete"
assert oval_ir.oval_set_flag("COMPLEMENT","does_not_exist","complete")=="does_not_exist"
assert oval_ir.oval_set_flag("COMPLEMENT","complete","not_applicable")=="error"

print("PASS: OVAL set membership, filters, nesting, and flag propagation preserved")
