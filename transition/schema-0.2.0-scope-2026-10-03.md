# Schema 0.2.0 scope and prerequisite issue review

Date: 2026-10-03. Baseline reviewed: `cc1ce5168e03179be42e2f79c7b4a21b7ccefe94`, branch `main`, repository `vanderpol/scap-ng`.

Provenance: **Evidence/Audit** for repository inspection and validation; **owner direction** for the three requested work areas below. This is a continuity/design checkpoint, not a released schema, Board ratification, or an implementation claim.

## Owner-requested scope before editor R&D

The owner requests conditional Test support and confirmation of include-collected-Item support before editor research. The owner additionally requests review of **all collected Item schemas** for attributes that make results more intuitive, with Unix file user/group names as the concrete example. Treat these as the next 0.2.0 design workstream; exact syntax and execution semantics still require specification and tests.

1. **Conditional evaluation:** support decisions using local Test results and statically declared dependent Assessment results. Specify all six technical outcomes, branch selection, unevaluated branches, dependency cycles, and explanatory results. Do not treat existing `all`/`any` expressions or JSON Schema `if` validation as runtime conditional execution. Organizational Input remains constrained to values and SHALL NOT supply Test references or dynamically alter the declared graph. Reconcile any input-dependent branching proposal explicitly with that invariant.
2. **Collected Item inclusion/materialization:** distinguish Item representation from imported observations and shared collection execution. Current Assessment Results already embed `items`, and collected Items expose `imported`; these fields alone do not establish a complete import contract. Settle consumed versus available Item scope, invocation/binding identity, local references, originating execution provenance, completeness/caps, redaction, and standalone result resolution. Confirm the intended inclusion control against worked examples before choosing field names; do not assume it means a toggle that removes decisive evidence. Keep this aligned with the self-contained Assessment Result requirement.
3. **Collected Item readability audit:** inventory every capability's collected fields, including generated capability schemas and their mapping inputs. Record current fields, candidate additions, acquisition or derivation method, datatype/status, implementation cost, privacy implications, and validation cases. Include result-only fields that are absent from authored State mappings; the current generator must not silently make every explanatory field a comparable State predicate.

For `unix.file`, evaluate resolved owner user/group names alongside `owner_uid` and `owner_gid`. Keep observed numeric identities. Specify target identity-resolution context and observation timing; distinguish absent identities, unavailable lookup services, denied lookup, and lookup errors. Candidate names are not yet standardized field names. Decide whether they are optional explanatory enrichment or supported assessment operands. Optional enrichment failure SHOULD NOT change a numeric ownership Test's technical outcome. If a Test explicitly depends on a resolved name, its collection/error semantics must be specified separately. Cover unmapped IDs, aliases, renamed accounts, remote identity services, namespaces/containers, and redaction. Do not fabricate a name from an ID or use the scanner host's account database as target evidence.

Other capabilities may benefit from different context (for example, a resource display name accompanying an identifier), but each addition requires a concrete reader benefit and a defined source. This is an audit mandate, not blanket approval for extra collection or a completed inventory.

## Version boundary

`schema/v0.1.0/README.md` explicitly defers conditionals and reused Item materialization. `specification/assessment/draft-future-assessment-features.md` already outlines these topics. Extend those semantics into 0.2.0 only after outcome/error rules and distinguishing tests are agreed. Content, result and package versions are independent: identify which contracts change rather than mechanically bumping every version.

The existing defects below are enforcement gaps in accepted behavior, not new 0.2.0 features. Resolve them in the 0.1.x draft/maintenance line before treating it as a stable baseline. No schema or converter was changed in this review.

## Codex issue triage

| Issue | Independently observed behavior at baseline | Disposition |
| --- | --- | --- |
| [#118](https://github.com/vanderpol/scap-ng/issues/118) | Both input-binding record schemas accept `redacted: true` with a `value` | Confirmed structural defect; reject any present value, including null; audit other redaction shapes |
| [#119](https://github.com/vanderpol/scap-ng/issues/119) | Filename changes validator selection; manual schema accepts response while generic schema rejects it; generic schema accepts a missing response | Confirmed dispatch/contract defect; validate mode consistently, with cross-mode negative tests |
| [#120](https://github.com/vanderpol/scap-ng/issues/120) | Publisher Profile subschema accepts `enabled_rules` with no `disabled_rules` | Confirmed structural defect against CURRENT-DESIGN; preserve different Tailoring permissions |
| [#121](https://github.com/vanderpol/scap-ng/issues/121) | Manual schema accepts duplicate `yes` choices mapped to opposing outcomes | Confirmed semantic uniqueness gap; uniqueness by value needs a semantic check or reviewed representation; object `uniqueItems` alone is insufficient |

Issues #122 (DNS target experiment) and #123 (published root xattr audit coverage) are research/source-content investigations, not these schema defects. Do not repair converter output silently to hide source anomalies.

## Validation actually performed

Python 3.12, jsonschema 4.26.0, PyYAML 6.0.3. All 21 top-level v0.1.0 schemas passed Draft 2020-12 meta-validation. Focused probes reproduced #118 and #120 against the exact embedded record/Profile subschemas; #119 and #121 used complete Manual Assessment documents and the maintained validator factory/filename classifier.

Command: `python -m unittest tools.test_result_schema_scope tools.test_benchmark_result_instances tools.test_package_manifest_schema -q`.

Result: **30 tests passed**. These tests do not detect the four reproduced defects. No full corpus rebuild, target scanner comparison, conditional evaluator, imported Item implementation, or completed all-capability readability audit was executed. Initial attempts could not import jsonschema; after installing it, the above probes and tests completed successfully.

## Next bounded work

First fix #118–#121 with regression cases and current validation-workflow integration. Then specify 0.2.0 conditional/result semantics and Item inclusion, and perform the complete collected-field audit. Produce readable examples and semantic fixtures before editor R&D. Keep experimental syntax separate from the 0.1.0 executable contract until promotion criteria are met. Board proposals remain separate versioned yes/no Discussion candidates; no vote or ratification is implied here.

## Subsequent bounded implementation in this session

Implemented enforcement fixes for #118–#121 after the owner directed continued work. The redaction audit also found and corrected the same leak in the Benchmark Result Organizational Input registry: redacted entries now omit value; unredacted entries still require it. Generic Assessment validation delegates manual mode to the existing Manual Assessment contract and rejects manual-only fields in automated mode. Filename classification uses the generic mode-aware schema consistently. Publisher Profiles now have a closed supported record (`id`, optional title/description/extends/parameters, required `disabled_rules`); reference/inheritance checks remain semantic work. Both identical and conflicting duplicate manual choice values fail the maintained validation harness, with an indexed diagnostic. Bare JSON Schema validation alone cannot enforce uniqueness by choice value; the README documents the required semantic check.

Added `tools/test_schema_issue_regressions.py` to the native-schema and current-regression CI workflows. Local validation after changes:

- New issue regressions: 8 tests passed, including actual corpus CLI invocation for duplicate answers.
- Result scope, Benchmark Result instances, package manifest, optional Assessment node families: 32 tests passed.
- Current corpus CLI: 15 tests passed.
- Full-review contract: 9 tests passed.
- Generated manual response contract: 3 tests passed.
- Tailoring examples: 15 tests passed.
- All 21 top-level schemas passed Draft 2020-12 meta-validation.

Total: **82 local tests passed**. No full 65-package rebuild or target equivalence test was run locally. CI completion must be checked on the published implementation commit before closing issues. The 0.2.0 scope above remains design work, not implemented functionality. Next: agree conditional outcome rules and Item inclusion semantics, then inventory all capability result fields and propose additions with explicit collection/lookup behavior.

The [initial all-capability collected-field review](../research/iterations/003/evidence/collected-item-readability-2026-10-03.md) now inventories all 100 mappings, 99 Item definitions, with no generation errors. It records readable-result candidates and Unix ownership acceptance cases. The full machine-readable field inventory includes hashes. This completes the initial field review, not the selection, specification or implementation of new attributes.

Publication: [PR #124](https://github.com/vanderpol/scap-ng/pull/124), branch `schema-enforcement-0.2-scope-20261003`. Automatic approval review rejected a direct push to `main`; a review branch is the safer publication path. Shell push also lacked GitHub credentials, so the connected GitHub tools published the review branch. PR-triggered schema/regression CI is enabled for this publication path; completed CI evidence must be inspected before closure.
