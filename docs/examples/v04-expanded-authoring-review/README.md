# SCAP-NG 0.4.0 — expanded Windows 11 and RHEL 9 authoring review

> **WARNING — CURRENT GENERATED OUTPUT, NOT CANONICAL AUTHORING EXAMPLES.**
> These files show the exact known-problem baseline so we can audit it; do not copy
> their field-matching style into new Assessments. In particular,
> [Windows 11 SV-253475](ms_windows_11/assessments/automated/SV-253475.automated.yaml)
> needlessly repeats `values_found`/`values_matching` inside two `and` groups.
> **[Use the proposed compact SV-253475 Assessment instead](../v04-two-sample-review/ms_windows_11/assessments/automated/SV-253475.automated.yaml)**
> with one Test-wide `field_requirement` and a single `fields` mapping.
> The latest owner decision also favors Test-wide field policy for single-field
> checks, using per-field settings only as explicit overrides; this policy has
> **not** yet been applied to this expanded gallery or the 65-stream archive.

**October 30, 2026. Non-release, source-faithful review excerpts.**

These examples preserve the original native Rule and Assessment YAML bytes from
the immutable 65-stream human-v2 package. **They deliberately retain current
authoring problems** so the owner can review more than one favorable sample.
In particular, the samples have not yet adopted the proposed single-field
Test-wide `field_requirement` convention or the approved removal of
Assessment-root `purpose` ([#264](https://github.com/vanderpol/scap-ng/issues/264),
[#266](https://github.com/vanderpol/scap-ng/issues/266)).

Each scope includes 20 exact source-derived Rule/Assessment pairs, a synthetic
single-scope review Benchmark, and the original empty applicability placeholder.
The Benchmark wrapper is **not a complete STIG**, its Profiles were deliberately
omitted, and **it is not suitable for scanner deployment**. See
[#265](https://github.com/vanderpol/scap-ng/issues/265) for identity,
applicability, manual-coverage, and source-metadata blockers.

**Validation:** All 84 YAML documents are schema-valid; both separate
20-Rule sample packages compiled. This is **not** independent OVAL equivalence
or a scanner result. **NOT SCANNER-VERIFIED — RESULT UNAVAILABLE.**
The original 65-stream ZIP, full-library proofs and hashes are unchanged.

For the [two-rule *proposed compact* examples](../v04-two-sample-review/README.md),
see the earlier focused design preview. These expanded samples show the current
as-generated 0.4 baseline instead of silently normalizing it.

## Browse the samples

### Windows 11 — 20 Rules

Capabilities represented (14): `independent.shellcommand`, `variable.value`, `windows.auditeventpolicysubcategories`, `windows.cmdlet`, `windows.fileeffectiverights53`, `windows.lockoutpolicy`, `windows.ntuser`, `windows.passwordpolicy`, `windows.registry`, `windows.service`, `windows.sid_sid`, `windows.user_sid55`, `windows.userright`, `windows.wmi.query`

[Review Benchmark](ms_windows_11/benchmark.yaml) · [Applicability placeholder](ms_windows_11/applicability.yaml)

| SV-ID | Assessment | Rule | Capabilities | Features | Original proof status |
| --- | --- | --- | --- | --- | --- |
| SV-253475 | [YAML](ms_windows_11/assessments/automated/SV-253475.automated.yaml) | [Rule](ms_windows_11/rules/SV-253475.rule.yaml) | `windows.registry` | `and` | CONVERTED_VERIFIED |
| SV-253276 | [YAML](ms_windows_11/assessments/automated/SV-253276.automated.yaml) | [Rule](ms_windows_11/rules/SV-253276.rule.yaml) | `windows.service` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-253433 | [YAML](ms_windows_11/assessments/automated/SV-253433.automated.yaml) | [Rule](ms_windows_11/rules/SV-253433.rule.yaml) | `windows.user_sid55` | `value_match`, `variables` | CONVERTED_VERIFIED |
| SV-253363 | [YAML](ms_windows_11/assessments/automated/SV-253363.automated.yaml) | [Rule](ms_windows_11/rules/SV-253363.rule.yaml) | `variable.value` | `variables` | CONVERTED_VERIFIED |
| SV-268318 | [YAML](ms_windows_11/assessments/automated/SV-268318.automated.yaml) | [Rule](ms_windows_11/rules/SV-268318.rule.yaml) | `independent.shellcommand`, `windows.cmdlet` | `multiple-tests`, `or`, `record` | CONVERTED_VERIFIED |
| SV-253435 | [YAML](ms_windows_11/assessments/automated/SV-253435.automated.yaml) | [Rule](ms_windows_11/rules/SV-253435.rule.yaml) | `windows.sid_sid` | `and`, `shared_objects`, `value_match`, `variables` | CONVERTED_VERIFIED |
| SV-253340 | [YAML](ms_windows_11/assessments/automated/SV-253340.automated.yaml) | [Rule](ms_windows_11/rules/SV-253340.rule.yaml) | `windows.fileeffectiverights53`, `windows.registry` | `and`, `filters`, `multiple-tests`, `not`, `or`, `set`, `shared_objects`, `value_match`, `variables` | CONVERTED_VERIFIED |
| SV-253298 | [YAML](ms_windows_11/assessments/automated/SV-253298.automated.yaml) | [Rule](ms_windows_11/rules/SV-253298.rule.yaml) | `windows.lockoutpolicy` | `and`, `multiple-tests` | CONVERTED_VERIFIED |
| SV-253491 | [YAML](ms_windows_11/assessments/automated/SV-253491.automated.yaml) | [Rule](ms_windows_11/rules/SV-253491.rule.yaml) | `windows.userright`, `windows.wmi.query` | `and`, `multiple-tests`, `or`, `record`, `shared_objects` | CONVERTED_VERIFIED |
| SV-253293 | [YAML](ms_windows_11/assessments/automated/SV-253293.automated.yaml) | [Rule](ms_windows_11/rules/SV-253293.rule.yaml) | `windows.ntuser` | `simple-one-test` | CONVERTED_UNVERIFIED |
| SV-253302 | [YAML](ms_windows_11/assessments/automated/SV-253302.automated.yaml) | [Rule](ms_windows_11/rules/SV-253302.rule.yaml) | `windows.passwordpolicy` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-253308 | [YAML](ms_windows_11/assessments/automated/SV-253308.automated.yaml) | [Rule](ms_windows_11/rules/SV-253308.rule.yaml) | `windows.auditeventpolicysubcategories` | `or` | CONVERTED_VERIFIED |
| SV-253265 | [YAML](ms_windows_11/assessments/automated/SV-253265.automated.yaml) | [Rule](ms_windows_11/rules/SV-253265.rule.yaml) | `windows.wmi.query` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-253479 | [YAML](ms_windows_11/assessments/automated/SV-253479.automated.yaml) | [Rule](ms_windows_11/rules/SV-253479.rule.yaml) | `windows.userright` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-253301 | [YAML](ms_windows_11/assessments/automated/SV-253301.automated.yaml) | [Rule](ms_windows_11/rules/SV-253301.rule.yaml) | `windows.passwordpolicy` | `and` | CONVERTED_VERIFIED |
| SV-253257 | [YAML](ms_windows_11/assessments/automated/SV-253257.automated.yaml) | [Rule](ms_windows_11/rules/SV-253257.rule.yaml) | `independent.shellcommand` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-253273 | [YAML](ms_windows_11/assessments/automated/SV-253273.automated.yaml) | [Rule](ms_windows_11/rules/SV-253273.rule.yaml) | `windows.cmdlet` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-253306 | [YAML](ms_windows_11/assessments/automated/SV-253306.automated.yaml) | [Rule](ms_windows_11/rules/SV-253306.rule.yaml) | `windows.auditeventpolicysubcategories` | `multiple-tests`, `or` | CONVERTED_VERIFIED |
| SV-253297 | [YAML](ms_windows_11/assessments/automated/SV-253297.automated.yaml) | [Rule](ms_windows_11/rules/SV-253297.rule.yaml) | `windows.lockoutpolicy` | `and`, `multiple-tests`, `or` | CONVERTED_VERIFIED |
| SV-253291 | [YAML](ms_windows_11/assessments/automated/SV-253291.automated.yaml) | [Rule](ms_windows_11/rules/SV-253291.rule.yaml) | `windows.registry` | `simple-one-test` | CONVERTED_VERIFIED |


### RHEL 9 — 20 Rules

Capabilities represented (13): `independent.shellcommand`, `independent.textfilecontent54`, `linux.partition`, `linux.rpminfo`, `linux.selinuxsecuritycontext`, `linux.systemdunitproperty`, `unix.file`, `unix.interface`, `unix.password`, `unix.shadow`, `unix.symlink`, `unix.sysctl`, `variable.value`

[Review Benchmark](rhel_9/benchmark.yaml) · [Applicability placeholder](rhel_9/applicability.yaml)

| SV-ID | Assessment | Rule | Capabilities | Features | Original proof status |
| --- | --- | --- | --- | --- | --- |
| SV-257851 | [YAML](rhel_9/assessments/automated/SV-257851.automated.yaml) | [Rule](rhel_9/rules/SV-257851.rule.yaml) | `linux.partition` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-258080 | [YAML](rhel_9/assessments/automated/SV-258080.automated.yaml) | [Rule](rhel_9/rules/SV-258080.rule.yaml) | `independent.textfilecontent54`, `linux.selinuxsecuritycontext` | `and`, `multiple-tests`, `shared_objects`, `value_match`, `variables` | CONVERTED_VERIFIED |
| SV-258042 | [YAML](rhel_9/assessments/automated/SV-258042.automated.yaml) | [Rule](rhel_9/rules/SV-258042.rule.yaml) | `unix.shadow` | `and`, `filters`, `multiple-tests`, `value_match`, `variables` | CONVERTED_UNVERIFIED |
| SV-257941 | [YAML](rhel_9/assessments/automated/SV-257941.automated.yaml) | [Rule](rhel_9/rules/SV-257941.rule.yaml) | `unix.interface` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-258236 | [YAML](rhel_9/assessments/automated/SV-258236.automated.yaml) | [Rule](rhel_9/rules/SV-258236.rule.yaml) | `unix.file`, `unix.symlink` | `and`, `multiple-tests` | CONVERTED_VERIFIED |
| SV-258046 | [YAML](rhel_9/assessments/automated/SV-258046.automated.yaml) | [Rule](rhel_9/rules/SV-258046.rule.yaml) | `unix.password` | `filters`, `set` | CONVERTED_VERIFIED |
| SV-257948 | [YAML](rhel_9/assessments/automated/SV-257948.automated.yaml) | [Rule](rhel_9/rules/SV-257948.rule.yaml) | `independent.textfilecontent54`, `variable.value` | `and`, `multiple-tests`, `not`, `or`, `shared_objects`, `variables` | CONVERTED_UNVERIFIED |
| SV-257782 | [YAML](rhel_9/assessments/automated/SV-257782.automated.yaml) | [Rule](rhel_9/rules/SV-257782.rule.yaml) | `linux.systemdunitproperty` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-257823 | [YAML](rhel_9/assessments/automated/SV-257823.automated.yaml) | [Rule](rhel_9/rules/SV-257823.rule.yaml) | `independent.shellcommand` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-257800 | [YAML](rhel_9/assessments/automated/SV-257800.automated.yaml) | [Rule](rhel_9/rules/SV-257800.rule.yaml) | `unix.sysctl` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-257825 | [YAML](rhel_9/assessments/automated/SV-257825.automated.yaml) | [Rule](rhel_9/rules/SV-257825.rule.yaml) | `linux.rpminfo` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-257848 | [YAML](rhel_9/assessments/automated/SV-257848.automated.yaml) | [Rule](rhel_9/rules/SV-257848.rule.yaml) | `linux.partition` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-257828 | [YAML](rhel_9/assessments/automated/SV-257828.automated.yaml) | [Rule](rhel_9/rules/SV-257828.rule.yaml) | `linux.rpminfo` | `not` | CONVERTED_VERIFIED |
| SV-257785 | [YAML](rhel_9/assessments/automated/SV-257785.automated.yaml) | [Rule](rhel_9/rules/SV-257785.rule.yaml) | `unix.symlink` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-257790 | [YAML](rhel_9/assessments/automated/SV-257790.automated.yaml) | [Rule](rhel_9/rules/SV-257790.rule.yaml) | `unix.file` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-258059 | [YAML](rhel_9/assessments/automated/SV-258059.automated.yaml) | [Rule](rhel_9/rules/SV-258059.rule.yaml) | `unix.password` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-258021 | [YAML](rhel_9/assessments/automated/SV-258021.automated.yaml) | [Rule](rhel_9/rules/SV-258021.rule.yaml) | `independent.shellcommand` | `simple-one-test` | CONVERTED_VERIFIED |
| SV-257786 | [YAML](rhel_9/assessments/automated/SV-257786.automated.yaml) | [Rule](rhel_9/rules/SV-257786.rule.yaml) | `linux.systemdunitproperty` | `and`, `multiple-tests` | CONVERTED_VERIFIED |
| SV-258045 | [YAML](rhel_9/assessments/automated/SV-258045.automated.yaml) | [Rule](rhel_9/rules/SV-258045.rule.yaml) | `variable.value` | `filters`, `shared_objects`, `value_match`, `variables` | CONVERTED_UNVERIFIED |
| SV-257955 | [YAML](rhel_9/assessments/automated/SV-257955.automated.yaml) | [Rule](rhel_9/rules/SV-257955.rule.yaml) | `unix.file` | `simple-one-test` | CONVERTED_VERIFIED |


## Review points

- Are Objects, Tests, `require`, Variables, `evaluate`, records and alternatives readable?
- Do you see repeated or unhelpful metadata? Rule XML markup and long IDs are still present.
- Are the `values_found` / `values_matching` controls and their inheritance understandable?
- Which cases need a native capability instead of a shell command?
- Which source behaviors need independent semantic checks?

The [source provenance ledger](REVIEW-RECEIPT.json) preserves the original
source ZIP hash, source Rule IDs, file hashes, original program hashes and
historical proof statuses **as labels**, not as newly established claims.
Do not interpret the subset as a full Benchmark or its historical proofs
as scanner execution.

Reproduce out-of-place with:

```bash
python tools/build_v04_expanded_authoring_review.py \
  --source-root <extracted-human-v2-root> \
  --output <new-nonexistent-directory>
```
