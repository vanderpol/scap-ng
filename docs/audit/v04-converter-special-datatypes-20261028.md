# Shared datatype and integer bitwise conversion

Continuation of [#251](https://github.com/vanderpol/scap-ng/issues/251) from
`43846988003cbfea8e54de1aed21783d34af0341`, whose nine workflows passed,
including 3,203 maintained tests (zero failures/errors, one existing skip).
The authoritative schema remains `d3132ae57`; no schema, mapping, generator,
compiler, scanner, editor, existing OVAL payload or 0.3 file was changed.

## Implementation

The existing visitor delegates lexical values, datatype names and approved
comparison names to one small [datatype module](../../tools/v04_direct_datatypes.py).
Version/package-version, binary and address values retain their original strings.
Typed operators preserve the selected algorithm: version comparison is not
ordinary string comparison, and a package name does not imply RPM/Debian ordering
when the original explicitly requested another datatype. Arrays and references
retain explicit datatypes and independent `value_match` quantifiers.

Integer bitwise AND/OR use the existing native comparison properties, whose
contracts explicitly require OVAL bitwise semantics. They do not become logical
AND/OR of predicates. Unknown operators, inappropriate datatype/operator pairs,
cross-datatype Variable references and float serialization remain unsupported.
No output defaults, artificial Items or new authoring grammar were introduced.

Independent proof has its own frozen datatype/operator identities; it imports
no converter normalization helper. Negative tests erase types while retaining
schema-valid output, change operators, introduce conflicting types, and mutate
Variable quantifiers. Those changes cannot establish source equivalence.

## Original-source evidence

Six [byte-exact original files](../../tests/fixtures/v04-direct-special-datatypes/provenance.json)
contain **114 Tests**: version 48, RPM-EVR 16, IPv4 13, IPv6 13, binary 4 and
integer 20. All pass original XSD/Schematron, native validation, compilation,
compiled-operand checks and independent typed-term comparison. Sixteen integer
cases were previously supported; this is not a claim of 114 entirely new proofs.
Controlled static-array/named-Variable tests separately exercise all four
`var_check` operations and preserve duplicate values.

The full pinned 803-Test corpus now has **512 independent term proofs**, up
from 406; **510** additionally have valid, nondeprecated original closures.
**520/710** configured Tests compile. There are zero mismatches. All preceding
406 proof identities and source-term hashes remain intact; 405 program hashes
are unchanged. The sole expected change, original literal-component Test 52,
uses canonical `integer` instead of the former function-literal `int` label;
its values, dependency graph and normalized source meaning are unchanged.

The six original primary subsets prove **1,012/1,396 OVAL Rules**. Every preceding
1,010 program hash remains unchanged. Windows 11 adds exactly:

| Rule | Original construct now preserved |
| --- | --- |
| SV-253263r1016364 | Registry version comparisons `>= 6.3` and `>= 22621` use version ordering. |
| SV-253264r1186372 | The cmdlet record field `productstate` uses integer bitwise AND with mask 4096. |

The proof floor adds these two reviewed identities. The old Windows proof
packet 03 also becomes independently provable; its source, assessment, compiled
program and historical unsupported outcome remain immutable. A new regression
records the discharged version obligation and rejects string-type erasure.
Three literal-component Tests (238 binary, 388 RPM-EVR, 728 version) likewise
retain their typed literal/Variable/comparison boundaries. Their exact proof
expectation changes from 3/7 to 6/7; float Test 127 remains blocked. Original
XML and hashes are unchanged. Two original DPKG Tests likewise become provable through their explicitly
requested **version** ordering; their prior blockers are retained in provenance.

The [receipt](v04-converter-special-datatypes-20261028.json) contains each changed
program, original pins, new primary identities, exact coverage and regression
counts. Exact published SHA and hosted CI are recorded in
[issue #251](https://github.com/vanderpol/scap-ng/issues/251).

## Remaining boundaries

Capability activation remains **47/51** in the approved platform scope,
**47/100** globally. The four inactive mappings and grouped runtime enum/
acquisition obligations remain in the
[existing handoff](v04-converter-revised-schemas-20261027.md). This increment
extends shared functionality within enabled capabilities.

A negative test exposed another validation gap: the current schema can accept
`version_equals: '1.0'` together with `datatype: string`. Independent semantic
proof rejects the conflict. Correct converter output always agrees with its
operator, so this does not block these conversions. The
[dependency register](../../tests/fixtures/v04-converter-schema-dependencies.json)
records the gap for the owner's coordinated datatype/schema review under #255.
The converter does not tighten the schema or treat its permissiveness as proof.

Float work remains deferred under [#218](https://github.com/vanderpol/scap-ng/issues/218),
which explicitly reserves the IEEE-32/nonfinite representation decision for
owner review. An isolated finite-precision experiment does not activate float
conversion or establish a new representation contract.

All claims here concern original-source typed terms, dependency/provenance graphs
and compiled operands. Scanner execution, complete policy/applicability,
publisher trust and release equivalence remain separate gates.
