# Findings from Real-World OVAL Migration Prototypes

**Iteration:** 001  
**Status:** Preliminary research findings  
**Scope:** Existing OVAL definitions selected specifically because they stress difficult semantics.

## Implemented corpus

Iteration 001 now contains 12 migration-case directories (plus one cross-case normalization note) covering 16 source OVAL definitions. The cases span RHEL 8/10, Windows Server 2012, and PostgreSQL 16.

The corpus intentionally includes:

- nested AND/OR trees;
- OVAL sets and filters;
- local variables and object components;
- regex capture and string derivation;
- dynamic expected values;
- multi-valued external variables;
- `check="all"` combined with existence semantics;
- recursive filesystem populations;
- runtime audit-rule matrices;
- command-based multi-instance database discovery;
- applicability represented as ordinary OVAL Boolean logic;
- package verification;
- heterogeneous evidence sources.

All current translations are labeled `prototype_native_translation`. None should yet be called `exact_native` because differential execution against the source OVAL has not been completed.

## Descriptive source-size comparison

The following byte counts are useful as an authoring-complexity observation only. They are **not** a claim of semantic equivalence and are not a fair implementation-cost comparison by themselves.

| Case | Source OVAL bytes | Prototype split assessment bytes | Approx. source-size ratio |
|---|---:|---:|---:|
| RHEL 10 SV-281055 | 34,270 | 2,806 | 12.2× |
| RHEL 8 SV-230385 | 5,008 | 739 | 6.8× |
| Windows 2012 SV-226208 | 3,772 | 834 | 4.5× |
| PostgreSQL SV-261875 | 2,570 | 837 | 3.1× |
| RHEL 10 SV-281050 | 20,646 | 2,552 | 8.1× |
| RHEL 10 SV-281053 | 20,540 | 2,552 | 8.0× |
| RHEL 10 SV-281063 | 49,035 | 1,302 | 37.7× |
| RHEL 10 SV-281101 | 37,417 | 875 | 42.8× |
| RHEL 10 SV-281054 | 22,895 | 1,334 | 17.2× |
| RHEL 10 SV-281008 | 20,814 | 884 | 23.5× |
| PostgreSQL SV-261956 + SV-261957 | 8,790 | 1,643 assessment + bindings | 5.3× |
| Four RHEL audit-syscall definitions | 125,112 | 1,987 assessment + bindings | 63.0× |

The large reductions occur because NG prototypes express intent through higher-level semantic capabilities. Complexity is **not eliminated**; some moves from every content file into standardized capability contracts and scanner implementations.

That tradeoff should be evaluated explicitly. A capability is justified when many assessments can rely on one clear, testable evidence contract. Moving one-off complexity into an opaque scanner-specific capability would merely hide the problem.

## Finding 1 — derived values need a first-class model

OVAL local variables are not all accidental XML complexity. Several production-style definitions genuinely derive one value from another.

Examples include:

- selecting the configured audit log path;
- taking its directory name;
- selecting a default when `log_group` is absent;
- resolving a group name to a numeric GID;
- constructing or extracting values with regex operations;
- counting unique values to detect ambiguous configuration.

The NG prototypes therefore use a declarative `derive` phase between collection and assertion.

Proposed conceptual pipeline:

```text
collect typed evidence
        ↓
derive deterministic values
        ↓
assert policy semantics
        ↓
produce decisive explanation
```

Derived values must remain side-effect-free, typed, deterministic, and traceable back to evidence.

## Finding 2 — set/filter is often implementation machinery, not policy semantics

Several large RHEL definitions use many OVAL set/filter objects to construct populations such as:

> files whose permission bit differs from the allowed state

The NG prototypes instead collect the relevant typed population once and assert:

```text
every item satisfies condition
```

or:

```text
no item satisfies violation predicate
```

This is substantially easier to explain.

However, iteration 001 should **not yet conclude that general set algebra is unnecessary**. The corpus mining must continue until we find or fail to find operational content whose semantics cannot be represented cleanly through collection scopes, quantifiers, predicates, and derivations.

## Finding 3 — existence and universal quantification are independent

RHEL 8 SV-230385 is an important example.

Each required file must:

1. contain at least one active `umask` statement; and
2. have every active `umask` statement satisfy the expected value.

A simple `every matching item is compliant` expression would incorrectly pass an empty population unless non-emptiness is also required.

The NG language therefore needs explicit cardinality/existence semantics that compose with quantifiers.

## Finding 4 — applicability must be separable during migration

Windows Server 2012 SV-226208 expresses:

```text
WinStore absent
OR
(WinStore present AND registry policy compliant)
```

because the policy treats absence as Not Applicable.

The NG prototype separates:

- `applies_when: WinStore exists`
- compliance assertion on the registry value.

This produces the policy result directly:

- path absent -> Not Applicable;
- path present + correct value -> Pass;
- path present + wrong value -> Fail;
- cannot determine path presence -> Error/Indeterminate.

Migration tooling therefore needs permission to normalize Boolean OVAL structures into explicit applicability only when policy semantics establish that equivalence.

## Finding 5 — external variables need typed collection parameters

PostgreSQL SV-261875 uses an OVAL external variable containing one or more target file paths.

The NG prototype represents this as an array parameter with item type, path format, and minimum cardinality.

This is preferable to treating all external values as scalar string substitutions.

Parameter definitions need:

- scalar versus collection cardinality;
- datatype;
- validation constraints;
- required/default semantics;
- provenance of supplied values;
- deterministic expansion behavior.

## Finding 6 — native semantic collectors can replace opaque shell commands

The PostgreSQL connection-audit definitions currently discover instances, inspect PID files, derive connection endpoints, change execution identity, execute SQL, and collapse everything into one shell-command verdict.

The NG prototype decomposes that into:

1. `postgresql.instances.running`;
2. `postgresql.settings` for each instance;
3. a universal assertion over returned structured settings.

The RHEL audit-syscall family similarly becomes:

1. collect normalized effective runtime audit rules once;
2. derive a required coverage matrix;
3. assert every required matrix entry is covered.

This allows scanners to optimize collection and results to identify the exact instance/syscall/architecture condition that failed.

## Finding 7 — semantic reuse becomes visible in real content

Two PostgreSQL rules that were separate shell commands now use one parameterized assessment with different required `log_line_prefix` tokens.

Four large RHEL syscall definitions use one parameterized audit-rule assessment.

This is stronger evidence for reuse than hand-created examples because the repeated logic already exists in current OVAL content.

## Finding 8 — negative/existence assertions require scope completeness

A `none` or absent-object result is only trustworthy if collection covered the required scope.

Examples include:

- no prohibited package-verification discrepancy;
- no prohibited filesystem permission state;
- application path absent for Not Applicable.

The evidence contract must therefore state collection scope and completeness. Absence observed in an incomplete search cannot silently become Pass or Not Applicable.

## Finding 9 — decisive explanations scale better than source graph traces

The migrated cases demonstrate why the result explanation should follow policy logic rather than the OVAL implementation graph.

Examples:

- SV-281055 can report "group write bit is set on /var/log/audit" rather than 20+ test/object/state nodes.
- SV-230385 can report the exact bad `umask` line or missing required statement.
- PostgreSQL multi-instance checks can name the one instance and missing token.
- syscall coverage can report the exact missing architecture/syscall/subject/result tuple.

A forensic profile may retain translation/evaluation trace data, but ordinary troubleshooting does not need the full source graph.

## Finding 10 — semantic capabilities must be standardized, not magical

The prototypes currently introduce capability concepts such as:

- `linux.config.directives`;
- `package.verify`;
- `linux.audit.effective-rules`;
- `linux.crypto-policy.effective`;
- `postgresql.instances.running`;
- `postgresql.settings`.

These are hypotheses for capability contracts, not settled names.

For each capability the standard would need to define:

- request schema;
- returned evidence schema;
- completeness/error semantics;
- normalization rules;
- version compatibility;
- privacy/sensitivity concerns where applicable;
- conformance fixtures.

A capability that different scanners interpret differently would recreate interoperability problems in a new form.

## Next validation step

The most important next step for these examples is **differential fixtures**:

```text
same target state
     ├── original OVAL evaluation
     └── native NG evaluation
             ↓
compare outcome, applicability, errors, and decisive evidence
```

Only after that should a translation be promoted from `prototype_native_translation` toward `exact_native` or `exact_normalized`.
