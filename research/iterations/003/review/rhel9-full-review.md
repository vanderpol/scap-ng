# RHEL 9 — complete native SCAP-NG iteration 003 review

**Current authoring review:** [full source-driven RHEL9 review](rhel9-current-full/README.md).
The current build uses **Benchmark → Rule → Assessment**, named Collections,
Variables and Tests, and direct relative Assessment paths on all 445 Rules.
This document below describes the historical baseline and is not its current
validation evidence. The earlier two-rule vocabulary slice is incomplete.

**Status:** HISTORICAL BASELINE — superseded as the current authoring review.  
**Audience:** SCAP-NG model and authoring review before reference-scanner implementation.  
**Generated from:** NIWC enhanced RHEL 9 STIG 002.009.013 / SCAP 1.4 ZIP, source archive SHA-256 `70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5`. Source archive provenance is in `../evidence/rhel9-full/source-package.json`.

## Superseded split-policy variant

The `source/split-policy-assessment/rhel9-full` tree and its structural validation
are historical experiments. They reintroduced a separate Policy object and
SHALL NOT serve as the current architecture or as input for new native examples.
Current authoring review uses the Rule/Assessment slice linked above.

## Start here

This is a **complete 445-Rule native benchmark**, not a small example. It is the first review of the end-to-end authoring model:

1. [Benchmark](../source/split-rule-assessment/rhel9-full/benchmark.yaml): identity, publication, platform, applicability catalog, all Groups, all Rule membership and Profiles.
2. [Typical automated Rule](../source/split-rule-assessment/rhel9-full/rules/SV-257777.rule.yaml): policy statement, identifiers, remediation, named selectors and default.
3. [Automated Assessment](../source/split-rule-assessment/rhel9-full/assessments/automated/SV-257777.automated.assessment.yaml): native collector/expected-State form. This assessment has multiple States and is worth close authoring review.
4. [Manual-only Rule](../source/split-rule-assessment/rhel9-full/rules/SV-257778.rule.yaml) and [Manual Assessment](../source/split-rule-assessment/rhel9-full/assessments/manual/SV-257778.manual.assessment.yaml): authoritative human procedure and selection.
5. [Applicability catalog](../source/split-rule-assessment/rhel9-full/applicability.yaml): named, explicitly referenced runtime applicability assessments.
6. [Package manifest](../packages/rhel9-full.manifest.json) and [archive](../packages/rhel9-full.scap-ng.zip): compiled, self-contained transport view.
7. [Rule source mapping](../evidence/rhel9-full/rule-mapping.json), [group provenance](../evidence/rhel9-full/grouping.json) and [conversion diagnostics](../evidence/rhel9-full/diagnostics.json): migration lineage and outstanding findings.

Relative links above assume the review file is located at `research/iterations/003/review/rhel9-full-review.md`.

## Proven baseline from generated artifacts

- Benchmark Rules: **445**.
- Native Assessment files: **879**, including automated, manual and applicability assessments.
- Package manifest logical objects: **1,326**, with **1,327** archive members.
- Existing generator CI checks: native-source legacy-residue clean, manifest object references/digests, Benchmark Rule and applicability reference resolution.
- Conversion diagnostics: **0 error**, **0 fatal**, **736 warnings**, primarily source OVAL descriptions/comments missing and emitted as null, not invented.
- Generated grouping is a **heuristic**, with a `needs-grouping` category. Functional labels must not be confused with source STIG-authored Groups.
- Profile names/selection derive from SCAP source; check whether they are authoring-friendly and whether disabled Rules are easy to audit.
- Stage-1 conversion is expected to preserve behavior and source defects. This is **not** a scan-tested or OVAL-runtime-equivalent release.

**Important limitation:** The full package remains a transitional Rule/Assessment prototype. The current architecture is Benchmark/Rule/Assessment, with Rule-owned selections and explicit relative Assessment source paths. The vocabulary slice must be reviewed before complete regeneration.

## Review prompts (structural rather than individual rule correctness)

### Benchmark

- Does a reader immediately recognize Benchmark identity, publication/version, platform applicability, Profiles and all 445 Rules?
- Are publication front/rear matter and old XCCDF artifacts kept out of authoring-critical fields?
- Is the grouped organization usable at full scale? Which rules still fall in `needs-grouping` and is the automated/manual distinction best handled as metadata rather than top-level hierarchy?
- Are external identifiers and scoring intelligible without decoding legacy IDs?

### Rule versus Policy

- Which fields belong to the Benchmark Rule (membership, identifiers, selection, applicability, references), and which belong in a separate shared Policy (discussion, remediation, requirements, named checks, defaults, check input binding)?
- Can multiple Rules in RHEL 9 and Oracle Linux 9 reference one shared Policy without duplicating assessment implementation or overriding source-specific titles?
- Can a reader see a named check selector and find its default/automated/manual options with one navigation step?
- **The generated `checks` field currently lives under Rule:** this is a transitional representation requiring migration to the agreed Policy authority.

### Assessment

- Is the collection/select vs expected-state/assertion representation understandable to an experienced OVAL author without requiring OVAL terminology?
- Are nested variables, multiple States, set/filters, behavior defaults and existence checks reviewable?
- Are missing source comments represented honestly, with space for native author-supplied explanations later?
- Is any XML/XCCDF/OVAL serialization structure leaking into native Assessment logic?

### Applicability and manual content

- Can a reader tell that platform applicability is an executable Assessment, not a magic CPE-only check?
- Are manual procedures easy to find and correctly distinct from automatic checks?
- Could a scan operator supply organization-defined values without changing command/collector execution?

### Results (design review only)

- Which Rule/Policy/Assessment identifiers, check-selector identities, expected vs observed values and existence failures must appear in a scanner result to be useful in SIEM?
- Which evidence should be bounded vs always present?

## Known exceptions and follow-on work

1. **Separate Policy layer:** complete the agreed split architecture, not merely rename `rules/` to `policies/`. Preserve independent check-selector resolution and benchmark Rule ownership. Demonstrate RHEL 9/Oracle Linux 9 reuse.
2. **Source comments:** 736 warning records do not establish 736 broken checks. Do not invent titles from unrelated Rule text solely to suppress warnings; human authored titles may be added later.
3. **Heuristic Group organization:** review/resolve `needs-grouping` with user-facing categories. Grouping must not accidentally change rule selection or scoring.
4. **Proof boundary:** OVAL semantic round trip and XSD/Schematron validation do not prove scanner runtime behavior; executable differential tests remain for the reference scanner.
5. **SCAP 1.4 SQL extension:** `sqlext` is out of scope for this effort, unrelated to this RHEL 9 benchmark.
6. **Source authority:** verify that archive hashes and date-bound provenance remain pinned if the generator downloads from moving `main` URL.
7. **Census:** the complete public-corpus sweep remains a parallel compatibility gate and need not delay the benchmark format review.

## Review decisions to record

When reviewing, note each specific change under one of these categories:
**Benchmark**, **Policy**, **Assessment**, **Applicability**, **Parameters**, **Manual**, **Results**, **Package**, or **Provenance**. Record the Rule/Assessment example when possible, the desired author-facing form, and whether the change alters semantics or only usability. Do not silently edit generated Stage-1 assessment semantics to make YAML look prettier.

## Next production milestone

The complete 445-Rule split-policy source and reference validation are now available (see above). Next: review Policy ownership and authoring clarity, then implement a compiled self-contained split-policy package and prove its semantic parity with the original Rule/Assessment baseline. Keep both source forms for comparison.
