# AGENTS.md

## SCAP-NG research evidence rules

SCAP-NG uses two deliberately separate classes of OVAL/SCAP evidence. Do not mix their roles or conclusions.

### 1. Published NIWC STIG corpus — production migration evidence

Repository: `niwc-atlantic/scap-content-library`

Purpose:
- Validate faithful forward conversion of real published SCAP 1.4/STIG content.
- Measure real-world construct usage, dependency closure, rule complexity, and cross-platform reuse.
- Provide production migration/conversion evidence for SCAP-NG architecture decisions.

Requirements:
- Use pinned published artifacts/revisions from the iteration corpus manifest.
- Preserve source behavior before proposing normalization, cleanup, or semantic repair.
- Record anomalies in the source rather than silently correcting them.
- Treat successful conversion of this corpus as evidence of practical migration coverage, not proof of complete OVAL language conformance.

### 2. OVAL Community Self-Assertion corpus — language-conformance evidence

Repository: `OVAL-Community/SCAP-Self-Assertion`
Path: `SCAP_1.4/OVAL_Test_Content`

Purpose:
- Unit-test OVAL Definition Evaluator semantics.
- Exercise OVAL 5.12.3 constructs that production STIG content may not use.
- Validate variables, functions, object components, sets, filters, datatypes, checks, existence semantics, result propagation, records, and platform-specific constructs.

Requirements:
- Keep this corpus logically and statistically separate from the published STIG corpus.
- Do not cite Self-Assertion content as production STIG migration evidence.
- Use expected evaluator behavior from the test content and OVAL 5.12.3 schema/documentation as the semantic contract.
- Prefer small focused Self-Assertion cases when implementing or debugging individual OVAL language features.
- Add regression tests when a Self-Assertion case exposes an importer/evaluator defect or ambiguity.

## Deprecated OVAL test exclusion rule

SCAP-NG contains **no effectively deprecated OVAL tests from SCAP 1.4 / OVAL 5.12.x**.

Raw `oval:deprecated_info` in a historical 5.12 schema is not sufficient by itself to determine current support. OVAL Community governance may later reinstate a test. The checked-in `oval-test-support-overrides.json` records those explicit reinstatement decisions.

- A definition that references an OVAL test whose **effective** status remains deprecated is not convertible to SCAP-NG.
- The converter may ingest and source-account the definition so it can produce a precise diagnostic, but it must mark conversion `unsupported` with reason `deprecated_oval_test`.
- Effectively deprecated tests are not eligible for `legacy_compatible`, `exact_normalized`, or silent automatic replacement.
- A test explicitly reinstated by later OVAL Community governance is treated as supported even if the source 5.12 schema still contains historical `deprecated_info`.
- The diagnostic should identify the deprecated test and, when the schema provides one, its supported replacement.
- The SCAP 1.4 content author must update and validate the source content using supported OVAL tests before SCAP-NG conversion can succeed.
- Deprecated objects/states that are reachable only through a deprecated test therefore do not create SCAP-NG runtime requirements.
- Production use of deprecated tests is measured as source-remediation debt, not as evidence that SCAP-NG must implement the deprecated collector.
- Example: Windows `accesstoken_test` is deprecated as of OVAL 5.11 and replaced by `userright_test`; SCAP-NG accepts the supported `userright_test` model, not `accesstoken_test`.
- Counterexample: Solaris `package_test` and `package511_test` were marked deprecated in OVAL 5.12, but OVAL Community issue #225 / PR #226 restored them to OVAL 6.0 and issue #300 records that their restoration to the 5.x line was intended but overlooked. They are therefore supported, not SCAP-NG blockers.

## Full-datastream conversion workflow

Whole-benchmark migration work must be automated and reproducible.

- Start from a pinned published SCAP 1.4 datastream/package, not hand-copied rule fragments.
- Build one unified XCCDF + OVAL benchmark IR before rendering any SCAP-NG source organization.
- Render combined-rule and split policy/assessment/binding candidates from that same benchmark IR.
- Verify policy and assessment equivalence between renderings rule-by-rule.
- Preserve complete source-accounting trees for constructs that do not yet have dedicated normalized NG fields.
- Treat faithful generic lowering and native normalization as separate gates. Generic migrated assessments may remain `legacy_compatible` until reviewed collector/capability mappings and differential tests justify `exact_native` or `exact_normalized`.
- Reusable conversion/parser/validation/package utilities belong under repository-level `tools/`. Iteration directories may contain experiments, regression fixtures, reports, and generated evidence but should not become the only home of reusable infrastructure.
- Large complete generated conversion trees may be retained as reproducible CI artifacts when committing every duplicated rendering would add unnecessary repository weight. Commit the tools, workflow, compact counts/blockers/hashes, representative conversions, and lessons learned.

## Cross-benchmark mapping and assessment reuse

Benchmark-to-benchmark mapping and automation reuse must be evidence-based.

- Use normalized XCCDF Check Text equality as one policy-rule alignment signal. Normalize presentation whitespace only; do not use fuzzy title/CCI similarity as proof.
- Use equivalent **complete normalized OVAL semantics** as a second alignment signal and as evidence for exact technical-assessment reuse. Sharing an OVAL test family is not sufficient.
- Keep policy alignment separate from automation reuse. Same Check Text can align two rules even when their OVAL implementations differ.
- Exact reusable-assessment identity must be independent of source-local OVAL IDs, comments, metadata, and provenance while preserving effective technical semantics: criteria, tests, objects, states, variables, literal values, collection/filter/set behavior, check/check-existence/state operators, and referenced logic.
- Preserve independent policy identities and provenance for every binding to a shared assessment. Exact technical reuse must not erase policy wording differences or source defects.
- Treat literal-abstracted semantic-shape matches only as **parameterization candidates**. Do not count them as proven reuse until typed parameters and semantic equivalence are reviewed/tested.
- Report reuse first in observable maintenance units: assessment instances, unique exact assessments, duplicate definitions avoided, fan-out, and percentage reduction. Apply organization-specific labor/time/rate assumptions separately.
- Effectively deprecated OVAL tests remain source-remediation blockers and are excluded from reusable SCAP-NG automated-assessment counts until the SCAP 1.4 source is corrected.

## Native source design checkpoint

Broad benchmark expansion is paused while the native SCAP-NG authoring model is reviewed.

- Treat current fidelity-first YAML as migration evidence, not normative native syntax.
- Before adding more benchmark families, agree on concise native source using the review corpus in `research/iterations/001/native-source-design-review.md`.
- Keep XCCDF/OVAL/OCIL/CPE XML identifiers, namespaces, hrefs, and source trees in migration provenance rather than executable native source.
- Prefer meaningful NG-local names and concise typed collect/derive/evaluate syntax.
- Applicability is content-authored ordinary assessment logic. Anything supported by the NG assessment language may be used for applicability; do not introduce scanner-side `os_info` or other opinionated platform classification as a normative dependency.
- CPE/platform identifiers are naming/mapping metadata unless explicitly backed by an NG applicability assessment; a CPE name alone never determines applicability.
- Preserve exact canonical semantics behind the authoring source so simplification never weakens result accuracy.
- Keep the four-anchor conversion workflow manual-only during this checkpoint.

## Open-source up-conversion tool direction

The SCAP 1.4 conversion tooling is expected to evolve into a standalone open-source up-conversion tool.

- Keep reusable parsing, semantic IR, migration analysis, validation, rendering, and packaging logic general-purpose and independent of NIWC/DISA-specific filenames or benchmark IDs.
- Isolate research-only orchestration, evidence generation, and iteration-specific paths from reusable converter logic.
- Prefer importable modules with thin CLI wrappers over scripts that depend on implicit working-directory state.
- Preserve complete provenance, migration status, blocker diagnostics, and loss accounting; never silently drop or repair source semantics.
- Keep the semantic IR versioned independently from external SCAP-NG source syntax so future format changes do not require rewriting SCAP 1.4 ingestion.
- New converter functionality should be designed so it can eventually live under an installable `scap_upconvert` package and be exercised locally without GitHub Actions.
- The roadmap is documented in `research/iterations/001/upconversion-tool-roadmap.md`.

## Reference scanner sequencing

A SCAP-NG reference scanner is a post-format-stabilization milestone.

- Do not make the reference scanner the mechanism for deciding the final SCAP-NG source organization while the OVAL Board is still reviewing candidate formats.
- Keep converter IR and generated NG assessments execution-oriented so they can later be consumed by a scanner without semantic redesign.
- After the format stabilizes, build a minimal reference scanner focused on normative correctness and conformance, not production-scale product features.
- Differentially execute SCAP 1.4 and converted SCAP-NG content against the same systems and compare applicability, effective rule selection, per-rule results, error/incomplete states, and decisive evidence.
- Treat semantic mismatches as converter/specification/scanner defects until explained; presentation-only differences must not be confused with semantic equivalence.

## OVAL 5.12.3 importer expectations

The SCAP-NG importer must aim for lossless dependency and semantic representation before native lowering.

In particular:
- Follow recursive references across definitions, tests, objects, states, variables, object sets, filters, `extend_definition`, `object_component`, and `variable_component`.
- Preserve explicit versus defaulted OVAL attributes where the distinction matters for faithful round-tripping.
- Treat OVAL defaults as semantic behavior, not merely syntax. For example, a `filter` without an `action` defaults to `exclude`, and a `set` without `set_operator` defaults to `UNION`.
- Apply filters to each referenced object set before applying the enclosing set operator, per OVAL 5.12.3 semantics.
- Preserve recursive `UNION`, `INTERSECTION`, and relative `COMPLEMENT` semantics, including collection/result flag propagation.
- Do not claim arbitrary OVAL 5.12.3 semantic equivalence until the relevant Self-Assertion conformance cases and production corpus cases pass.
- When semantics are not yet implemented exactly, preserve them explicitly in the IR and mark them unresolved/requires-review rather than approximating them.

## Evidence hierarchy

Use evidence according to the question being answered:

- "Can SCAP-NG migrate real published STIG content?" -> NIWC published STIG corpus.
- "Does SCAP-NG correctly model this OVAL language feature?" -> OVAL Self-Assertion corpus plus OVAL 5.12.3 schema/documentation.
- "Can a native SCAP-NG representation replace the source behavior exactly?" -> require faithful IR plus differential/conformance testing; do not infer equivalence from syntax alone.
