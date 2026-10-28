# Remaining converter contract handoff

This is a non-normative engineering handoff for
[#251](https://github.com/vanderpol/scap-ng/issues/251), not a language change.
The converter work continues to use the committed 0.4 schemas/mappings. No
candidate syntax below is implemented or accepted as a new contract.

## Decision needed before extending Variable function syntax

The remaining configured corpus has 67 unsupported function cases: arithmetic
2, begin 4, end 4, escape_regex 2, glob_to_regex 20, substring 5, and
time_difference 30. These counts describe implementation gaps, not completed
capabilities or a claim that every original closure is source-valid.

A source-valid pinned counterexample is original
`agnostic/oval-def_substring_function.xml`, Test
`oval:org.mitre.oval.test:tst:174`, from Self-Assertion revision
`e3538595c5083b9c34d937a81d319234df9bbfaa`. Its file SHA-256 is
`892d18d9fa055cb59882b470a8e97e43c4069b968d4c136984b0692fcbd73e97`.
The source has local string Variable `var:136`, whose `substring` uses start
3, length 2 and a reference to multivalued constant string Variable `var:389`.
This is a real dependency/multiplicity obligation, not an invented literal case.
The converter reports `unsupported function: substring`; original validity is
`VALID` with no deprecation issues for the pinned closure.

The committed Assessment schema permits opaque Variable declaration objects.
It does not constrain the operand/option fields of these functions. A read-only
experiment with simple literals (not a conversion of Test 174) demonstrated
that **both** competing research-only trees below
validate and compile with their authored operands retained:

```json
{"substring":{"value":{"literal":{"datatype":"string","value":"abcdef"}},"start":1,"length":3}}
```

```json
{"substring":{"components":[{"literal":{"datatype":"string","value":"abcdef"}}],"substring_start":1,"substring_length":3}}
```

Neither example is a proposed conversion or evidence of executable semantics.
The independent native reader reports `native function proof unavailable:
substring` for both. The acquisition Object visitor recognizes function names
and possible reference positions, but that is not a complete function signature
or evaluation contract. Selecting payload keys merely because the schema and
compiler accept them would violate the owner's restriction against introducing
new authoring grammar and would not prove semantic preservation.

**Required owner clarification:** identify the authoritative existing 0.4
function payload/evaluation contracts, or approve one grouped clarification of
those contracts before the converter emits additional functions. This is one
cross-function issue, not a request for separate capability approvals. Source
operations/defaults, argument multiplicity, casts, unknown/error/incomplete
results and compiled operands must remain independently checkable. No schema,
compiler or scanner change is authorized by this packet.

## Other preserved boundaries

- Runtime enum strings outside known closed graphs or matching-domain
  projections still require an approved status/cardinality-preserving adapter.
  Closed literal/reference/unique graphs are implemented and proved.
- Source `all_exist`, Variable-source Sets/Filters and external Variable bindings
  require source-exact population/identity/binding contracts. They are not
  replaced with weaker quantifiers, value deduplication or unbound defaults.
- The existing 15-parameter acquisition review groups shellcommand, SQL512,
  cmdlet and WMI multiplicity/correlation obligations. Record member references
  remain supported; whole-record `var_ref` remains prohibited by original XSD.
- Float/IEEE-32/nonfinite representation remains reserved for owner review in
  [#218](https://github.com/vanderpol/scap-ng/issues/218).
- Inactive mappings remain SSHD (nil filepath contract/source counterexamples),
  deprecated RPM-verify source fields, and SQL512/YAML without an original
  source proof in the pinned corpus. The current upstream Self-Assertion tree
  remains the same pinned revision and contains no SQL512/YAML examples.
- Original Schematron rejects `none_exist` Tests with State references and
  inconsistent Variable/entity datatypes. Those examples remain invalid source;
  they are not repaired or used to inflate converter coverage.

The consolidated report retains semantic categories and original identities.
The current [acquisition proof receipt](v04-windows-acquisition-proofs-20261028.json)
contains exact coverage and retention evidence. All claims remain distinct from
scanner execution, complete policy/applicability, publisher trust and release
conformance. Exact commits and hosted validation are recorded in issue #251.
