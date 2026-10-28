# Closed enum Variable graphs and dependency inventory

Continuation of [#251](https://github.com/vanderpol/scap-ng/issues/251) from
`a4c5f47e68eaf6146290a987a9b301b17c6183f7`. That checkpoint passed all nine
workflows and 3,207 maintained tests (zero failures/errors, one existing skip).
The schema baseline remains `d3132ae57`; no schema, mapping, generator,
compiler, scanner, editor, original OVAL bytes or 0.3 file changes are included.

## Original source and conversion

Original registry Test `oval:navy.navwar.niwcatlantic.scc.test:tst:4000` uses
local Variable `oval:navy.navwar.niwcatlantic.scc.test:var:4000`, whose literal
is `HKEY_LOCAL_MACHINE`, as its Object hive selector. The native enum spelling
is `local_machine`. Previously, the guard for arbitrary runtime strings also
rejected this complete closed expression.

The [shared handler](../../tools/v04_direct_enum_variables.py) translates known
string literals through the approved bijective alias map, retaining local
Variables, shared references, constant arrays and `unique` boundaries. It emits
consumer-specific typed Variable copies using existing native expression forms.
The original declarations remain available to generic string consumers. This
avoids changing a shared raw string into an enum spelling in another context.
`enum_variable_equivalences` in the external source trace records every copy's
original Variable ID, original native declaration and exact alias map.

No arbitrary runtime mapping function, acquisition fanout, artificial Item,
implicit OR or source quantifier default was introduced. Unknown values, casts,
external inputs, arbitrary runtime strings and functions that do not commute
with this rename remain unsupported. Existing matching-domain ObjectComponent
projections retain their preceding behavior and source-domain guards.

## Verification and retention

The original Test validates, compiles with independently checked operands and
compares independently against its original OVAL typed terms. Its existing
[byte-pinned source](../../tests/fixtures/v04-direct-proof-aliases/provenance.json)
is unchanged. The independent reader has its own frozen alias identities and
closed-expression traversal; it imports no converter translation helper.

Controlled, separately labeled source compositions validate under the original
XSD/Schematron and cover all six hashing algorithms, duplicate values, `unique`,
all four Variable quantifiers, Object and State comparisons, and shared generic
string use in both conversion orders. Negative tests retain unknown values,
casts, arbitrary runtime strings and concatenation as unsupported. Changed
translations and changed `value_match` fail independent term comparison.
The former closed-literal negative now explicitly proves that literal case and
continues to reject a genuinely computed string expression; no test was disabled.

The 803-Test corpus has **521/710 configured Tests compiled**, **513 independent
term proofs**, and **511** original-valid, nondeprecated proofs. The sole new
original proof is registry Test 4000. All preceding **512 proof identities,
source/native term hashes and program hashes remain unchanged**. There are zero
mismatches or unexplained differences. The Registry alias fixture's exact count
changes from 14 to 15 (24 to 25 across its three files), with the new source
identity individually recorded in provenance.

All six primary sources retain **1,012/1,396 OVAL Rule proofs** and every
preceding program hash; there are no newly admitted primary Rules in this
increment. All 100 regenerated capability contracts match their unchanged
parity hashes (141 selectors, 694 State entries). Fifty-nine distinct focused
regressions pass, including the existing hash, alias, source-package, expanded
proof and benchmark inventory/isolation checks.

The [compact receipt](v04-converter-enum-variable-graphs-20261028.json) records
retention hashes, focused counts and the six-source gate. Hosted exact-commit
mandatory results and SHA are recorded in [issue #251](https://github.com/vanderpol/scap-ng/issues/251).
Capability activation remains **47/51** in scope and **47/100** globally. These
are typed-term, dependency/provenance and compiled-operand claims, with scanner
execution, full policy/applicability and release equivalence remaining separate.

## Stack-safe inventory

Dependency discovery formerly raised `RecursionError` on a controlled 5,000-node
chain. An explicit traversal stack now retains every node. Exit frames preserve
the active path, source edge order, shared-node handling and cycle/missing-edge/
wrong-kind diagnostics, including wrong-kind references to previously visited
nodes. Component scope and source immutability are unchanged.

Two controlled regressions cover deep/shared/scoped graphs and ordered failure
evidence. Differential comparison with the preceding traversal matches 2,000
seeded graphs, all six pinned primary inventories (1,567 original Rules), and
all 168 Definition closures across 145 pinned OVAL documents, with zero
changes. This improves discovery only; it does not claim that recursive lowering
or independent readers can convert and prove arbitrary-depth source graphs.
