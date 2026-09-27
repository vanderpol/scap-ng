# Complex Existing OVAL Prototype Backlog

**Iteration:** 001  
**Status:** Active research backlog  
**Purpose:** Identify real OVAL definitions whose semantics could expose gaps in the SCAP-NG assessment, migration, collection, or decisive-explanation models.

## Implementation status

All Priority 1 and Priority 2 candidate families listed below now have iteration 001 native-translation prototypes under `prototypes/oval-migration-cases/`.

Their status remains `prototype_native_translation`: implementation in the research syntax is complete enough for architecture review, but differential execution against the source OVAL is still required before any equivalence claim.

This backlog is intentionally biased toward difficult constructs rather than representative easy rules.

The source paths below are from `vanderpol/scap-content`. Inclusion does not imply the source OVAL is perfect; each candidate must also be reviewed for correctness before it is treated as migration ground truth.

## Priority 1 — translate/prototype early

### 1. RHEL 10 SV-281055 — audit log directory mode

Source:

`projects/linux/rhel10/oval/U_RHEL_10_SV-281055-oval.xml`

Observed complexity:

- 7 criteria groups;
- 23 criterion references;
- 16 OVAL sets;
- 16 filters;
- 8 local variables;
- object components;
- nested AND/OR;
- `var_check`;
- pattern matching;
- record values;
- `regex_capture`.

Why it matters:

This is currently the strongest single candidate for testing whether SCAP-NG can replace a complicated OVAL dataflow graph with understandable collection + derivation + assertion semantics without losing fidelity.

It should also stress the decisive-outcome explanation model: a failure should identify the actual directory/mode condition that proves noncompliance without reproducing the entire variable/set/filter graph.

### 2. RHEL 10 SV-281050 / SV-281053 — audit log group ownership

Sources:

- `projects/linux/rhel10/oval/U_RHEL_10_SV-281050-oval.xml`
- `projects/linux/rhel10/oval/U_RHEL_10_SV-281053-oval.xml`

Observed complexity per definition:

- 8 criteria groups;
- 13–15 criterion references;
- 14 local variables;
- 6 object components;
- nested AND/OR;
- `var_check`;
- pattern matching;
- record values;
- `regex_capture`;
- `concat`.

Why they matter:

These are good tests for derived values, allowed-alternative ownership semantics, reusable derivations, and explaining a failure when an expected group is dynamically derived rather than a fixed literal.

### 3. Windows Server 2012 SV-226208 — Windows Store applicability/compliance

Source:

`projects/windows/windows2012/research/oval/U_MS_Windows_2012_SV-226208-oval.xml`

OVAL logic:

```text
WinStore absent
OR
(WinStore exists AND RemoveWindowsStore == 1)
```

Why it matters:

The original OVAL uses Boolean compliance logic to represent a policy Not Applicable condition. SCAP-NG should be able to migrate this into explicit applicability plus compliance semantics without changing the observed policy outcome.

This is also an excellent decisive-explanation case:

- absent WinStore -> Not Applicable, not Pass;
- present WinStore + bad registry value -> Fail with the registry comparison as the useful explanation;
- collection failure determining WinStore presence -> Error/Indeterminate, not Not Applicable.

### 4. RHEL 8 SV-230385 — every umask statement across required files

Source:

`projects/linux/rhel8/research/oval/U_RHEL_8_SV-230385-oval.xml`

Observed semantics:

- three required configuration files;
- each test uses `check="all"`;
- each also requires `check_existence="at_least_one_exists"`;
- object pattern finds every uncommented `umask` statement;
- every found statement must match the compliant `077` form.

Why it matters:

This tests the combination of existence and universal quantification. "No bad matches" is not sufficient because each file must contain at least one applicable statement.

The NG explanation must distinguish:

- missing required statement;
- one or more bad statements;
- incomplete collection/read error.

### 5. PostgreSQL 16 SV-261875 — external variable with one-or-more target paths

Source:

`projects/postgresql/postgresql16/research/oval/U_CD_Postgres_16_SV-261875-oval.xml`

Observed semantics:

- external variable supplies applicable target path(s);
- one OVAL file object expands over the variable values;
- test uses `check="all"`;
- at least one resulting object must exist;
- all supplied/discovered targets must satisfy file permissions.

Why it matters:

This is a strong migration case for typed external parameters that may be collections rather than scalar values, and for defining exactly how parameter expansion interacts with existence and universal assertions.

### 6. PostgreSQL 16 SV-261956 / SV-261957 — multi-instance database discovery/query

Sources:

- `projects/postgresql/postgresql16/research/oval/U_CD_Postgres_16_SV-261956-oval.xml`
- `projects/postgresql/postgresql16/research/oval/U_CD_Postgres_16_SV-261957-oval.xml`

Observed semantics:

- searches all local filesystems for active PostgreSQL instance PID files;
- determines whether each instance is running;
- derives port/socket connection information;
- executes a read-only SQL query as postgres;
- requires every discovered running instance to satisfy the requirement;
- current implementation uses a large `shellcommand_test`.

Why it matters:

This should not merely be transliterated into a new command block. It is a candidate for decomposing one opaque shell command into:

1. instance discovery;
2. process/running-instance validation;
3. connection endpoint derivation;
4. typed PostgreSQL query collection;
5. universal assertion over instances.

It also tests partial-instance collection errors and explanation when one of many instances fails.

## Priority 2 — important scale/structure cases

### 7. RHEL 10 SV-281063 — cron configuration permissions

Source:

`projects/linux/rhel10/oval/U_RHEL_10_SV-281063-oval.xml`

Observed complexity:

- 32 criterion references;
- 30 sets;
- 34 filters;
- numerous file/object permission checks.

Why it matters:

This is useful for determining whether the NG model can express large related file-scope requirements compactly and whether one failed path can be explained without serializing 31 successful siblings.

### 8. RHEL 10 SV-281101 — control of audit configuration permissions

Source:

`projects/linux/rhel10/oval/U_RHEL_10_SV-281101-oval.xml`

Observed complexity:

- 29 criterion references;
- 27 sets;
- 28 filters;
- recursive filesystem behavior.

Why it matters:

This stresses recursive/scope semantics, set/filter migration, and bounded failure evidence over many related files.

### 9. RHEL 10 SV-281054 — audit log file mode

Source:

`projects/linux/rhel10/oval/U_RHEL_10_SV-281054-oval.xml`

Observed complexity:

- 14 criterion references;
- 10 sets;
- 11 filters;
- 6 local variables;
- object components;
- recursion;
- `var_check`;
- regex capture.

Why it matters:

A useful intermediate case between simple file metadata and SV-281055's larger derived graph.

### 10. RHEL 10 SV-281125 / SV-281117 / SV-281165 / SV-281163 — syscall audit rules

Representative sources:

- `U_RHEL_10_SV-281125-oval.xml`
- `U_RHEL_10_SV-281117-oval.xml`
- `U_RHEL_10_SV-281165-oval.xml`
- `U_RHEL_10_SV-281163-oval.xml`

Observed complexity:

- multiple criteria groups;
- 10–26 criterion references;
- numerous pattern states;
- extensive shell-command usage in current content.

Why they matter:

These should test a semantic audit-rule collector rather than preserving repeated command execution, and test whether multiple syscall/architecture requirements can share collected audit configuration while producing rule-specific explanations.

### 11. RHEL 10 SV-281008 — FIPS system-wide crypto policy

Source:

`projects/linux/rhel10/oval/U_RHEL_10_SV-281008-oval.xml`

Observed complexity:

- multiple criteria groups;
- 12 criterion references;
- mixed pattern checks and shell-command collection.

Why it matters:

Useful for testing composition of heterogeneous evidence sources and deciding where native high-level capability semantics are justified.

## Root-cause / decisive-explanation cases to require

Every translated candidate should include at least these fixtures:

1. fully compliant;
2. one simple decisive failure;
3. multiple independent failures;
4. missing required object/value;
5. collection permission/read error;
6. partial collection where applicable;
7. branch/applicability variation where applicable;
8. short-circuit result with `outcome_complete: true`, `diagnostics_complete: false`;
9. exhaustive diagnostic result where feasible.

For nested Boolean definitions, the NG result should be evaluated against the rules in `result-explanation-model.md`.

## Mining categories still required

The repository scan must continue looking for real examples of:

- OVAL set union/intersection/complement;
- filters with include/exclude behavior;
- local variables with multiple nested components;
- external variables with multi-valued expansion;
- arithmetic and time-difference functions;
- object-component chains;
- regex capture and string derivations;
- check / check_existence / var_check / entity_check combinations;
- datatype and version comparisons;
- record datatypes and field checks;
- behaviors controlling recursion/filesystem scope;
- extend_definition graphs;
- negated criteria;
- deeply nested mixed AND/OR trees;
- multiple equivalent minimal failure proofs;
- objects yielding zero, one, or many items;
- error/unknown/not-evaluated propagation;
- platform tests beyond Linux and Windows;
- tests deprecated in OVAL but still present in trusted content.

## Selection rule

A candidate should be promoted into an NG prototype when it tests a semantic capability not already adequately exercised. We should avoid creating dozens of examples that differ only in product name or literal value.

The goal is semantic coverage, not benchmark-volume coverage.
