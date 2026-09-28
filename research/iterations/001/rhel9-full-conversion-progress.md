# RHEL 9 Full SCAP 1.4 -> SCAP-NG Conversion Progress

**Iteration:** 001  
**Source:** pinned published NIWC RHEL 9 SCAP 1.4 benchmark  
**Source revision:** `8c8e5dff860af6b1290ee9273a282db24278f8d5`  
**Status:** first complete mechanically generated benchmark conversion working; semantic hardening continues

## First end-to-end milestone

The workflow `.github/workflows/convert-rhel9-scap14-to-ng.yml` now starts from the published signed RHEL 9 SCAP 1.4 ZIP and performs the complete migration pipeline automatically:

1. build the effective OVAL schema/support catalog;
2. extract one schema-valid OVAL document per XCCDF rule;
3. build faithful OVAL semantic IR for every automated rule;
4. join XCCDF policy/profile/value/check information with OVAL IR;
5. compile one canonical migrated benchmark;
6. render both candidate source organizations;
7. verify rule-by-rule equivalence between renderings;
8. build deterministic signed prototype `.scapng` packages;
9. verify package hashes and Ed25519 prototype signatures;
10. publish compact Git evidence plus the complete generated source/package artifact.

### Current RHEL 9 counts

- 445 XCCDF rules
- 418 rules with automated OVAL
- 27 rules without OVAL automation
- 445 canonical converted rules
- 445 combined-rule renderings
- 445 split-model policy rules
- 445 split-model assessment bindings
- zero conversion blockers in this RHEL 9 benchmark

The complete first-generation converted source tree contains 1,345 files and approximately 38.9 MB before compression.

## Signed package results

The first successful package pass produced four verified prototype bundles:

| Model | Package type | Approx. size | Members |
|---|---|---:|---:|
| combined rule | policy-only | 0.99 MB | 450 |
| combined rule | automated/mixed | 1.49 MB | 450 |
| split policy/assessment/binding | policy-only | 0.91 MB | 450 |
| split policy/assessment/binding | automated/mixed | 1.89 MB | 896 |

The signatures use the public RFC 8032 test key, exactly like the earlier iteration-001 package prototypes. They demonstrate deterministic integrity/signature mechanics only, not publisher trust.

## What "converted" currently means

OVAL XML is **not** copied into the NG package as opaque XML.

The converter lowers it into a structured assessment graph:

- OVAL objects -> typed collection nodes;
- local/external variables -> typed derivation/evaluation-plan nodes;
- states -> predicate nodes;
- tests -> collection/existence/state evaluation nodes;
- definitions -> explicit Boolean criteria trees;
- XCCDF check references -> root definition bindings.

Source OVAL identifiers and namespaces remain as provenance so equivalence can be audited.

These assessments are currently marked `legacy_compatible`, not `exact_native`. That status is intentional: the structured graph is faithful enough for migration research, but the native SCAP-NG capability contracts for every RHEL collector have not yet been independently specified and differential-tested.

## XCCDF hardening underway

The first package pass proved whole-benchmark flow but also made clear that policy semantics above individual rules need the same loss-accounting discipline as OVAL.

The current hardening pass adds first-class XCCDF Group representation, including:

- nested group membership;
- `selected` inheritance inputs;
- scoring weights;
- group platforms/applicability references;
- `requires` and `conflicts`;
- group-scoped Values;
- Profile selection/refinement actions.

This is required because an unselected XCCDF Group implicitly prevents all descendant rules from being processed.

## Important properties already preserved

- Complete source Rule subtrees remain attached for source accounting.
- Manual Check Content embedded by the published STIG is retained even for automated rules.
- The 27 rules without OVAL automation retain their manual/external check procedures.
- The known RHEL 9 complex OVAL cases, including the xattr audit case with the published duplicate/missing-condition anomaly, are converted without silently repairing source behavior.
- Both candidate source organizations are generated from one benchmark IR rather than independently authored.
- The conversion verifier fails if policy or assessment semantics diverge between renderings.

## Remaining gates before calling this production-grade migration

### 1. Effective XCCDF policy semantics

Complete Group/Profile/Value/check-selector handling, including profile inheritance and effective selection/applicability.

### 2. Platform applicability

Translate the datastream's CPE/platform components into the NG applicability model and verify that rule/benchmark applicability is preserved.

### 3. Native capability promotion

Define and validate native collector contracts for the RHEL 9 object/test families. Promote assessments from `legacy_compatible` to `exact_native` or `exact_normalized` only when equivalence is demonstrated.

### 4. Differential execution

Run source SCAP/OVAL and converted NG against representative system-characteristics/endpoint fixtures and compare applicability, outcomes, evidence completeness, errors, and boundary behavior.

### 5. Wider corpus

After RHEL 9 stabilizes, run the same generic pipeline against Oracle Linux 9, Windows 11, and Windows Server 2025, then the complete pinned NIWC `Current/` benchmark set.

Effectively deprecated OVAL tests are source-remediation blockers and remain outside SCAP-NG. OVAL Community reinstatement decisions recorded in `oval-test-support-overrides.json` override stale historical deprecation annotations.
