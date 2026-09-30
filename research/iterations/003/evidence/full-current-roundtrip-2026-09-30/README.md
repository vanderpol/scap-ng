# Complete current-design round-trip regression — 2026-09-30

This checkpoint tests the current named Collection/Variable/Test representation against the pinned input corpus. It does not use the superseded Policy layout or historical native-output mode.

## Result and coverage

The complete regression finished with confirmed source blockers; it is **not an all-green conversion result**. The converter/validator defects identified during this run are fixed on main.

| Evidence | Result |
| --- | --- |
| All NIWC Current packages | 65 expected, 65 reported; zero missing or duplicate reports |
| OVAL definition occurrences | 11,973 accounted for: 11,628 comparator-equal; 204 deprecated-Test blockers; 132 publisher-extension blockers; 9 source type-binding failures |
| Regenerated OVAL validation | All 65 package XSD and source-relative Schematron steps passed |
| Windows 11 package | 475 of 477 occurrences equal; 2 deprecated-Test blockers; no other failure |
| RHEL9 package OVAL census | All 828 occurrences equal |
| Self-Assertion language corpus | 165 of 167 definitions equal; only 2 expected deprecated-Test blockers; regenerated XSD passed and no introduced Schematron findings |
| Full RHEL9 source generation | Windows and Linux passed: 445 Rules, 11 Profiles, 418 automated + 445 manual Assessments, 18 applicability conditions, 1,328 YAML files; all 4,895 Rule/Profile selection comparisons match |
| Current-design contract suite | Passed on Windows and Linux, including the latest Tailoring provenance tests |

See [machine-readable checkpoint](checkpoint.json) and [all 65 package results](niwc-census.md). Source evidence: [NIWC census run 36785610344](https://github.com/vanderpol/scap-ng/actions/runs/36785610344), [Self-Assertion run 36785610433](https://github.com/vanderpol/scap-ng/actions/runs/36785610433), and [fresh full RHEL9 run 36786162246](https://github.com/vanderpol/scap-ng/actions/runs/36786162246).

The census remains red because its classifier treats the nine confirmed source type errors as unexpected failures. There are no remaining semantic-difference, reverse-conversion, current-authoring-contract, XSD or introduced-Schematron failures in this completed run.

## Defects fixed during the run

- The broad corpus CLI still invoked the historical lowerer. It now defaults to `collection_graph=True`, records `native_layout: current`, validates the current authoring contract and preserves generated section order. `--layout historical` is an explicit comparison-only option.
- The legacy-residue guard recognized `object_title` as documentary metadata but omitted the renamed `collection_title`. Both now have the same documentary contract. Legacy identifiers in executable selectors remain prohibited; a negative regression checks that boundary.
- Schematron diagnostics differed only in the lexical namespace prefix on a deprecated element. The comparator now normalizes that prefix while preserving distinct element findings.
- A Self-Assertion shell pipeline could conceal a failed Schematron comparison. It now uses `set -euo pipefail`.
- NIWC schema and Schematron checks now continue after blocker classification fails, so a known source blocker does not conceal validation of the successfully regenerated definitions. Parse failures are also included in aggregate enforcement.
- Current-graph cardinality tests exercise 42 combinations across independent Test existence/item checks, State entity quantifiers and multiple-State operators. Historical regression cases remain separate from these current-grammar checks.

The focused contract suite passed on Windows and Linux in [run 36785610368](https://github.com/vanderpol/scap-ng/actions/runs/36785610368). Coverage includes shared Collection identity, distinct equal source Objects, named and private embedded Collections, Variable chains/depth/sets/Filters, reference and cycle rejection, defaults, State entities, section order, Rule bindings, subtractive Profiles including explicit empty disabled lists, Tailoring layering/values/selectors, and creator/authorizer/purpose preservation.

## Remaining type-binding blockers

Nine definition occurrences in three source packages fail type binding. These are not silently repaired or counted as successful conversion.

| Source | Definition suffixes | Binding rejected | Historical comparison |
| --- | --- | --- | --- |
| F5 NGINX | 278400 | `unix.file` Test → `independent.shellcommand` Object/State | Already rejected |
| IIS 10 Site | 218741, 218742 | `windows.appcmd` Test → `independent.variable` Object/State | Already rejected |
| IIS 8.5 Site | 80, 90 | `windows.appcmd` Test → `independent.variable` Object/State | Already rejected |
| IIS 10 Site | 218752, 218781 | `appcmd_object` Filter → `appcmdlistconfig_state` | Old mode accepted; current mode rejects |
| IIS 8.5 Site | 180, 470 | `appcmd_object` Filter → `appcmdlistconfig_state` | Old mode accepted; current mode rejects |

The original pinned packages were inspected in [diagnostic run 36786500144](https://github.com/vanderpol/scap-ng/actions/runs/36786500144). [Source binding evidence](type-binding-blockers.json) records the actual qualified types, references and old/current diagnostics.

The pinned [OVAL 5.12.3 Windows schema](https://github.com/OVAL-Community/OVAL/blob/v5.12.3/oval-schemas/windows-definitions-schema.xsd), pattern `win-def_appcmd_object_verify_filter_state`, requires an `appcmd_object` Filter to reference a Windows `appcmd_state`. The four newly rejected Filter cases violate that source constraint. A successful XML comparator in the older path did not prove valid source typing. The current guard is retained.

The existing census classifier records these nine cases under `unexpected_failures`, so the census remains red. This report explains the exact source defects rather than broadening an allowlist to make the run green. Deprecated Tests and nonstandard publisher extensions remain independently counted blockers.

## Exact pins and reproduction

- Converter/test code: `da8a5429a82d4cc53717606f086b17da45b1c560`.
- NIWC Current: `8c8e5dff860af6b1290ee9273a282db24278f8d5`; all 65 non-Consolidated SCAP 1.4 packages selected by the workflow matrix.
- Self-Assertion: `e3538595c5083b9c34d937a81d319234df9bbfaa`, `SCAP_1.4/OVAL_Test_Content`.
- OVAL schemas: `v5.12.3`.
- RHEL9 package SHA-256: `70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5`.
- Fresh full RHEL9 generation after the guard fixes: `0e8fa31a5c0d20dc800df57c42fee41ca74f9d22`; only the design ledger and workflow trigger changed after the tested converter commit.

The maintained workflows are `.github/workflows/full-current-oval-roundtrip-census.yml`, `v003-self-assertion.yml`, `scap-ng-current-regression.yml` and `scap-ng-current-full-review.yml`. Their package reports, regenerated schema checks and source-relative Schematron reports remain available as CI artifacts.

Example current corpus command:

```text
python tools/scap_ng_roundtrip_v003/roundtrip_corpus_v003.py --corpus <original-oval-closures> --out <output> --report <report.json> --inventory-only
```

`--inventory-only` collects every outcome; it is not a passing gate. The workflows classify and enforce the report afterward.

## Limits

NIWC counts are definition occurrences across split rule dependency closures, not necessarily unique source Definitions. Self-Assertion counts are separate language-feature evidence. Broad coverage here is OVAL conversion/representation coverage across all packages; complete XCCDF Rule/Profile/manual/applicability rendering is additionally exercised for RHEL9. Tailoring fixtures are contract tests, not SCAP XML Tailoring round trips. Compiled packaging, final NG grammar and differential evaluation on assessed systems remain unproven.
