# Complex Published OVAL Prototype Backlog

**Iteration:** 001  
**Status:** Active research backlog  
**Evidence source:** NIWC Atlantic `scap-content-library/Current` at pinned revision `8c8e5dff860af6b1290ee9273a282db24278f8d5`

## Priority platforms

Iteration 001 will mine and prototype difficult published SCAP 1.4 definitions first from:

1. RHEL 9
2. Oracle Linux 9
3. Windows 11
4. Windows Server 2025

These four provide two useful dimensions:

- Linux cross-distribution reuse: RHEL 9 ↔ Oracle Linux 9
- Windows client/server reuse: Windows 11 ↔ Windows Server 2025

The eventual conversion gate still covers all 65 individual published benchmarks in the pinned NIWC `Current/` tree.

## Selection rule

A definition is promoted into a migration prototype when it exercises a semantic capability not already adequately covered.

Priority is given to published cases containing:

- deeply nested mixed AND/OR criteria;
- set union/intersection/complement;
- filters and object-set construction;
- local variables and object components;
- regex capture and string derivation;
- external variables, especially multi-valued;
- arithmetic/date/time functions;
- `check`, `check_existence`, `var_check`, and `entity_check` combinations;
- record datatypes;
- recursive filesystem behaviors;
- `extend_definition` graphs;
- negated criteria;
- zero/one/many item behavior;
- error/unknown/not-evaluated propagation;
- command/shell tests that might be replaced by semantic capabilities;
- repeated OVAL logic across RHEL 9 and Oracle Linux 9;
- repeated Windows logic across Windows 11 and Server 2025.

## Evidence requirement

Every admitted case must trace back to an exact published NIWC ZIP and include:

- repository revision;
- ZIP path and SHA-256;
- internal datastream/component identity;
- XCCDF rule ID;
- OVAL definition ID;
- source-component digest where practical.

Development or experimental repository files are not evidence for this backlog.

## Cross-platform reuse analysis

For RHEL 9 and Oracle Linux 9, measure several increasingly strong notions of overlap rather than one headline percentage:

1. rules sharing CCI/reference sets;
2. normalized policy/title similarity;
3. equivalent Check Content intent;
4. structurally/semantically equivalent OVAL logic;
5. assessments that can be exactly reused;
6. assessments that can be reused only with typed parameters;
7. superficially similar rules that must remain separate.

Only levels 4–6 should influence automated-assessment reuse claims.

## Result fixtures for each selected case

Each translated case should eventually include, where applicable:

- compliant;
- one decisive failure;
- multiple independent failures;
- missing required object/value;
- collection/read/permission error;
- partial collection;
- applicability variation;
- short-circuit result with complete outcome but incomplete diagnostics;
- exhaustive diagnostic result.

The goal is semantic coverage and conversion evidence, not benchmark-volume coverage.
