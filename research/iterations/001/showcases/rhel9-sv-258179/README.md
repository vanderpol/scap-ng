# RHEL 9 SV-258179 — Flagship Complexity Reduction Case

**Source:** published NIWC SCAP 1.4 content  
**Benchmark:** RHEL 9 V2R9 enhanced V13  
**Rule:** `xccdf_mil.disa.stig_rule_SV-258179r1155601_rule`  
**OVAL definition:** `oval:mil.disa.stig.rhel9os:def:258179`

This case is intentionally retained as a flagship test for whether SCAP-NG
actually reduces assessment complexity.

## Published OVAL closure

The standalone rule split currently contains:

| Construct | Count |
|---|---:|
| Definitions | 7 |
| Tests | 24 |
| Objects | 24 |
| States | 0 |
| Variables | 17 |
| Local variables | 8 |
| Constant variables | 9 |
| `variable_component` references | 64 |
| `concat` operations | 8 |
| Standalone OVAL bytes | 39,135 |

The 17 variables are not incidental. They construct regex fragments used by
objects that test audit-rule text. This is exactly the kind of dependency graph
that a splitter must follow to a fixed point.

## Underlying requirement shape

The source OVAL resolves to 24 audit-rule checks:

```text
6 syscalls
  x 2 architectures
  x 2 subject scopes
  = 24 required coverage cells
```

Syscalls:

- `setxattr`
- `fsetxattr`
- `lsetxattr`
- `removexattr`
- `fremovexattr`
- `lremovexattr`

Architectures:

- `b32`
- `b64`

Subject scopes:

- interactive users: `auid >= 1000` and not unset
- root: `auid = 0`

The OVAL implementation expresses those semantics through repeated
`textfilecontent54` tests and regex-building variables against
`/etc/audit/audit.rules`.

## Candidate SCAP-NG normalization

The candidate NG form expresses the same requirement as:

1. collect normalized configured audit rules once;
2. derive the 6 x 2 x 2 required coverage matrix;
3. assert that every matrix cell is covered.

Two YAML spellings are included:

- `original-ng.yaml`
- `ansible-inspired.yaml`

They intentionally describe the same proposed semantic model.

## Important status

This is currently `requires_review`, not `exact_normalized`.

The smaller representation is compelling, but size/readability are not proof
of equivalence. The normalization must be differential-tested against the
published OVAL using fixtures that cover:

- each syscall;
- both architectures;
- both subject scopes;
- combined syscall lists;
- both accepted action orderings;
- optional audit keys;
- unset AUID spellings;
- missing rules;
- malformed rules;
- duplicate/overlapping rules;
- collection/read failures.

Only then should this pattern be promoted into an automatic normalization rule.

## Why this case matters

This example separates three things that OVAL currently intertwines:

```text
policy requirement
        |
        v
24 semantic coverage conditions
        |
        v
OVAL implementation machinery
  7 definitions
  24 tests
  24 objects
  17 variables
  regex assembly
```

SCAP-NG should preserve the first two while avoiding the need for every content
author to reproduce the third.

That is a stronger adoption argument than "YAML is shorter than XML": it shows
that a reusable semantic collector can move repeated parsing mechanics into a
standardized, conformance-tested capability while leaving the assessment itself
close to the security requirement.
