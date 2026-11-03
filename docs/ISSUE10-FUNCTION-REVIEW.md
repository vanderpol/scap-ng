# Bounded 0.4 function amendment review — 2026-11-03

Owner direction: [pursue the coordinated pre-release amendment](https://github.com/vanderpol/scap-ng-tools/issues/14#issuecomment-6592397246).
Tracking: [canonical #10](https://github.com/vanderpol/scap-ng/issues/10) and
[tools #14](https://github.com/vanderpol/scap-ng-tools/issues/14).
The dated human decision authorizes this three-operation scope. This packet and
passing checks do not constitute subsequent human acceptance, Board ratification,
a scanner release, or a new full65 library.

## Problem and exact syntax

The preceding active schema rejects every `function` envelope. This amendment
adds only `arithmetic`, `substring`, and `split` to the active expression union:

```json
{"function":{"name":"arithmetic","arguments":[{"literal":[1,2]},{"literal":[3,4,5]}],"options":{"arithmetic_operation":"add"}}}
```

Every call requires `name`, `arguments`, and `options`; no extra properties,
implicit options or direct Input expression are added. Arithmetic requires two
or more arguments and add/multiply; substring and split take one argument.
Substring requires signed 32-bit `substring_start` and `substring_length`. Split
requires a literal string `delimiter`. The broad 13-function candidate remains
unchanged, inactive and unreferenced.

## Source-backed before/after and domain boundaries

Original sources are signed Q3 2026 NIWC ZIPs at
`8c8e5dff860af6b1290ee9273a282db24278f8d5`. Exact ZIP/Variable pins and
source adapter tests are in the coordinated tools branch.

| Source subgraph | Before | New subgraph / qualification |
| --- | --- | --- |
| Amazon Linux 2023 SV-274067, partition size | unsupported arithmetic | multiply collected block_size and total_space in source order; numeric projection validates; original local Variable declares string and is **not** silently cast |
| Windows Server 2016 SV-224975, database drive | unsupported substring | explicit start 1 / length 1 over registry value; subgraph validates; whole Rule remains blocked by WMI Object |
| Solaris 11 x86 SV-216066, init paths | unsupported split | literal colon delimiter over collected subexpression; complete focused Rule draft validates |

These are preserved ASTs, not computed values or source-equivalence proofs.
Arithmetic operands/results are numeric (integer/float, float on mixed numeric
inputs), never string/Boolean/record coercions. String functions require string
operands/results. Named Variables retain their declared domains. A collected
field's possible domain set can be constrained by an explicit string signature,
consistent with existing consuming-type constraints; this does not convert
incompatible runtime data or treat possible domains as a mixed literal array.
No new numeric-to-string declaration cast is introduced. Source declaration
mismatches and unsupported Input composition remain blockers.

## Evaluation, multiplicity and status boundaries

The reference is official OVAL 5.12.3 at
`2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`,
[oval-definitions-schema.xsd](https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/oval-definitions-schema.xsd),
ArithmeticFunctionType, SplitFunctionType and SubstringFunctionType.

Arithmetic specifies a Cartesian product, not zip: the six additions in the
example remain represented by two populations. Split maps each source string,
retaining duplicates and leading/trailing/adjacent empty strings: `-a-a-` with
`-` has four values; `---` has four empty values. Delimiters are literal, never
regular expressions. Substring uses one-based starts; start below 1 means 1 at
evaluation, start beyond string length is an error, and negative/oversized length
means the remainder. Source options are preserved, not normalized or executed.
An empty delimiter is syntactically a string under the upstream XSD; this packet
does not invent its runtime behavior.

The compiler preserves the source AST and does not execute these operations.
Collection flags, incomplete/error/unknown/absent populations and lexical errors
remain runtime boundaries. Empty strings are values, not missing populations;
no branch invents zero, false, empty string or success for failure. No Result
wire format, Item population lowering, collector, Input provision rule or source
semantic proof is added.

## Compatibility and provenance

All seven previous expression forms and constant restrictions remain exactly
unchanged, checked by an inverse against the pinned preceding schema. The broad
candidate, other 142 JSON files, all 100 mappings, legacy 0.3, and native Result
wire contracts remain unchanged. Family fingerprint changes from
`04074a04cf3e5378fcc99e4f7780ff2e10f032e400751c35cea960aa0c42d971` to
`f19246c60814f7768a5564cd335675b4c2c6ae721ebd6a464ee9a6f17185e0a3`:
143 JSON files, 34 roots, 244 root references. Old artifacts/proofs are not
relabelled or rebuilt as new evidence.

Coordinated compiler programs containing an active function use program/0.3,
`variable_function_contract_version: 1`, and an exact sorted name/source-path/
source-hash inventory. Programs without functions retain formats/bytes 0.1 or
0.2, including Input presence. Presence and function metadata can coexist.
The independent package reader reconstructs its own AST inventory and rejects
missing/forged inventories and mismatched format/version. Literal records and
Object selector payloads are opaque, not interpreted as functions. Package
consistency remains distinct from full source semantic/type/scanner proof.

## Rejected alternatives and validation

Blanket candidate activation, constant folding, zip products, regex delimiters,
silent declaration casts, direct Input composition and all_exist lowering are
outside this amendment. WMI expansion or source population lowering needs
separate evidence and authorization.

Schema tests cover complete options, unsupported names, arities, signed integer
limits, no implicit result casts and exact old-grammar restoration. Coordinated
portable/compiler tests cover domains, numeric widening, collections, empty
values, nested legacy forms, opaque records, exact old program hashes, presence
coexistence and rehashed package inventory mutants. Source tests compare signed
source options, argument order and Object projections. Maintained suites and
exact CI links are recorded in the issue/PR on completion.
