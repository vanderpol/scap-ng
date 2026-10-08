# SCAP-NG 0.3 validation evidence — 2026-10-08

This page records **verified CI results**, not projected compliance improvements.
Each number includes its denominator and provenance. Do not substitute these
checks for live scanner execution or a lossless SCAP 1.4 runtime-equivalence proof.

| Gate / measure | Verified result | Evidence |
| --- | --- | --- |
| OVAL-derived source mapping parity | 100/100 current 0.3 mappings passed | [Datatype-fidelity CI run 37813630343](https://github.com/vanderpol/scap-ng/actions/runs/37813630343), `capability-state-item-parity-v03.json` |
| Legacy parity control | 100/100 passed | Same CI run, `capability-state-item-parity.json` |
| Schema generation/meta-validation | 200/200 (100 historical + 100 current) passed | Same CI run, `generated-capability-schema-validation.json` |
| Polymorphic datatype inventory | 100 mappings processed, zero structural errors, **53 fields flagged for further semantic review**, not 53 failures | Same CI run, `v03-polymorphic-fields.json` |
| OVAL collected Item cardinality inventory | 99 OVAL source Item families checked, 47 repeatable-field instances flagged for representation review, zero audit failures | Same CI run, `v03-item-cardinality.json` |
| Deprecated OVAL mapping gate | 100 supported mappings checked, no mapped deprecated State/Item fields | Same CI run, `v03-deprecated-mappings.json` |
| Focused semantic/Registry/expansion regression | **50/50** tests pass | Same CI run, job logs |
| Representative benchmark build | **6/6 source conversions**, plus 0.3 schema/semantics/package-graph validation, exact normalization, post-normalization validation and compilation | [Six-anchor run 37809832500](https://github.com/vanderpol/scap-ng/actions/runs/37809832500), reviewed commit `fb4e9fcc6036944e4727adf6bed993647f8a6efe` |

## What was fixed in the gate

- Removed nine deprecated OVAL fields from current 0.3 mappings (not from the historical pinned schemas).
- Preserved **collected Item** datatype separately from the authored **State comparison** datatype. OVAL can cast REG_SZ text to integer for numeric State comparisons; inability to cast is an evaluation error, not a reason to prohibit the source State.
- Added source-backed cardinality checks, including repeated OVAL Registry `REG_MULTI_SZ` value entities.
- Added nested-State validation for type-sensitive Registry logic and independent Windows policy/date checks.

## Full-corpus first-run findings and correction

[Initial active-0.3 full-corpus run 37811009793](https://github.com/vanderpol/scap-ng/actions/runs/37811009793)
accounted for all **65 pinned packages** and rendered all **61 supported** 0.3
candidate benchmarks. Of **24,653** YAML documents validated, **24,648**
passed and **five** revealed source-compatibility gaps. Three IIS Assessments
used a legacy `none exist` Test form with explicit `existence:none` and no
States; two Windows NTUSER filters used the OVAL-permitted empty State type
comparison. These have source-backed, guarded normalization/schema fixes and
focused CI regression tests. The **full-corpus rerun remains a separate
required gate**; do not treat unit tests alone as proving all 24,653 documents
pass.

## Remaining limits

The validated six-anchor workflow covers RHEL 9, Oracle Linux 9, Windows 11,
Windows Server 2025, Windows Server DNS, and Apache 2.4 UNIX. It is a
**conversion + static validation + packaging** gate; it does not execute
scanner-specific evidence collection or end-to-end item/state casting on hosts.

The separate **65-source 0.3 release checkpoint** uses pinned NIWC source
revision `8c8e5dff860af6b1290ee9273a282db24278f8d5` and must account for
61 supported source conversions plus four known excluded `independent.sqlext`
packages. The run and actual outcomes are tracked in
[Issue #202](https://github.com/vanderpol/scap-ng/issues/202). **Do not
replace this statement with a passing full-corpus claim until the actual run
finishes green.** The older 0.2.0 full-corpus run remains historical evidence,
not proof of 0.3 success.

See [Issue #201](https://github.com/vanderpol/scap-ng/issues/201) for mapping
fidelity issues and [Issue #202](https://github.com/vanderpol/scap-ng/issues/202)
for the corpus release gate.
