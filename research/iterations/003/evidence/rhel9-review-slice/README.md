# RHEL 9 Review Slice — Iteration 003

## Status

This directory records evidence for the first accepted clean SCAP-NG 003
conversion subset from the published RHEL 9 V2R9 enhanced SCAP 1.4 package.

The corresponding native source is:

    source/split-policy-assessment/rhel9-review-slice/

## Accepted Rules

The current slice contains:

- RHEL-09-211010
- RHEL-09-211030
- RHEL-09-211040

For these Rules, the 003 converter preserves the source semantics represented
by this checkpoint, including:

- publisher-facing Rule identity, title, severity, weight, discussion,
  documentability, CCI identifiers, references, and remediation guidance;
- source check-selector behavior, including default, automated, and manual
  alternatives;
- Manual Assessment procedure text;
- automated Boolean definition composition;
- collection capability and selection operands;
- test existence/check semantics;
- state alternatives and state operators;
- Benchmark Profile selection deltas projected over this review subset.

The native source passes the iteration-003 legacy-residue validator.

## Evidence separation

Legacy source identifiers, namespaces, component references, and package
lineage are retained only in this evidence directory.

They are intentionally absent from native SCAP-NG source.

## Expansion blockers

This review slice does not imply that the entire RHEL 9 Benchmark is currently
convertible.

The converter SHALL continue to reject rather than approximate constructs that
have not yet been lowered exactly, including as applicable:

- Rule-specific applicability predicates;
- variable-dependent objects or states;
- object sets and filters;
- collection behaviors not yet normalized;
- remediation substitutions or platform-qualified remediation;
- other source constructs whose exact NG semantics are not yet proven.

As each blocker is implemented, representative cases should be added to the
review corpus before attempting full-benchmark generation.
