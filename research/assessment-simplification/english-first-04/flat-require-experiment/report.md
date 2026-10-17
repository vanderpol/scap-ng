# Removing `condition` and record `: true` — six-STIG research proof

**Experimental authoring only; not an adopted 0.4 schema or independent scanner proof.**

- Corpus **872 automated Assessments / 1375 Tests**.
- Flat direct-field requirement: **871/872 Assessments**, **1374/1375 Tests** reconstructed exactly.
- Redundant `at_least_one_record_exists: true` flags replaced: **86**.
- Fail-closed malformed `condition` wrapper probes: **871**.
- Reserved Item/match predicate name collisions: **0** Assessments.

## Real RHEL nosuid check (same original source meaning)

```yaml
require:
  items: at_least_one
  match: all
  mount_options: {at_least_one_value_is: nosuid}
```

## Windows WMI record-group example (whole States must stay separate)

```yaml
require:
  items: at_least_one
  match: all
  scope: states
  or:
    - result:
        records: at_least_one
        match: all
        domainrole: {is: "1"}
    - result:
        records: at_least_one
        match: all
        domainrole: {is: "3"}
```

This is **not** equivalent to flattening entire States into `domainrole: {in: [1, 3]}`.

## Requirements and boundaries

The source structure, Item/cardinality requirements and all nested record semantics are source-exact for admitted Assessments. Missing/error/incomplete results have **not** been independently executed.
Literal field-level Boolean checks (`is: true`, `is: false`) are untouched: these are **meaningful data comparisons**, not meaningless marker flags.
Other Boolean control fields (such as inherited field-presence rules) need separately verified elimination if they affect semantics.

## Failures

- `authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml` — unproven output or Item scope

## Complete examples

The adjacent five `*.flat.research.yaml` files contain complete authoring research Assessments. Each was reconstructed against the pinned source when admitted.
