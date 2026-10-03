# Conditional content checkpoint — 2026-10-03

Source baseline: `ab6e9fb1b291fab389157990e5a66f4d29ed1a97`, merged main after PR #124. Workstream: new experimental 0.2.0 conditional known-result suite; established schemas/converter/normalizer are unchanged.

Owner requests: prepare explanatory content with known results, in the style of OVAL Self-Assertion; investigate a way for conditional evaluation to return not applicable, considering a better option than a synthetic Test; track possible future normalizer upgrades only after conditional 0.2.0 is implemented, tested and merged.

The [suite README](../tests/conditional-0.2.0/README.md) is the development entry point. It includes 14 example Assessments, 33 curated cases, complete 216-case local and 216-case dependent guard matrices, 10 invalid-content fixtures, and a bounded executable model. The regression tests add a 1296-case applicability matrix and a 36-case explicit-N/A matrix. Every expected result is either a curated fixture value or comes from an explicit, independently visible contract table/staging rule. The model does not read expected results to determine its output.

Proposed guard behavior: true selects then, false selects else, and the other four outcomes propagate without selecting either. An explicit `not_applicable: {reason: ...}` expression leaf is explored instead of a new Test capability. Existing intrinsic applicability is demonstrated as the preferable alternative when the whole Assessment is inapplicable. Neither proposed syntax nor guard propagation is ratified.

Local commands and results:

- `python tools/conditional_conformance.py --report /tmp/conditional-model-results.json`: 465 positive evaluations passed; all 10 invalid-content cases produced expected errors.
- `PYTHONPATH=tools python tools/test_conditional_conformance.py -q`: 19 unittest methods passed, including extra applicability/N/A matrices, dependency cycles/reuse/context isolation, missing results, invalid operands, current capability declaration/reference checks and normalization counterexample.
- `python tools/check_current_authoring_contract.py tests/conditional-0.2.0/content`: 14 files passed vocabulary/presentation guard.

Separate units must remain separate in reporting: 465 content/model evaluations, 10 invalid fixtures, 19 regression methods. An additional 60 existing OVAL truth-table tests and 8 existing schema-issue regression tests passed (87 unittest methods in total across these three commands). This is not target collection/evaluator/scanner conformance. Metadata uses familiar native Test/State/Variable terminology, but the model consumes supplied terminal Test outcomes and its trace is not a canonical Assessment Result. A private experimental expression schema validates the proposed grammar; there is no new production 0.2.0 schema.

Provenance: new project-authored examples/model plus **Evidence/Audit**; the inherited maintained OVAL aggregation helper and inspected current-design files are pinned in `tests/conditional-0.2.0/provenance.json`. The positive/negative evidence is reproducible in CI on Windows and Ubuntu. No target accesses, signing or broad corpus builds are required for this bounded work.

Deferred [normalizer issue #126](https://github.com/vanderpol/scap-ng/issues/126) now has a concrete caution: `(G AND T) OR (NOT G AND E)` yields false for G=error/T=false/E=false, but the proposed conditional yields error. Boolean-shape matching is insufficient for an automatic lossless upgrade. This counterexample is a regression, not a complete feasibility result.

Next: review the guard table, explicit N/A node and intrinsic-applicability comparison; agree final semantics and branch/result evidence rules. Then implement the versioned 0.2.0 content/result contracts and collector-backed conformance fixtures. Keep Item materialization, `reported_elements` (#125), evidence completeness and normalizer upgrade gates visible. Do not call this suite a completed conditional schema implementation or start editor R&D on its provisional syntax.

## Published checkpoint

[PR #127](https://github.com/vanderpol/scap-ng/pull/127), branch `conditional-conformance-0.2-20261003`, technical checkpoint `cc70ed3590006d9de0b8b2a6bce339a15433a5ce`. The [Windows and Ubuntu current-regression run](https://github.com/vanderpol/scap-ng/actions/runs/37141128864) completed successfully on both platforms and uploaded the experimental known-result reports. [Repository verification](https://github.com/vanderpol/scap-ng/actions/runs/37141128912) also succeeded. Source role metadata was explicitly corrected to purpose `applicability` before this final technical run. This publication is experimental content/model work, remains unmerged at checkpoint recording, and does not promote conditional schemas into 0.2.0.

## Superseding owner direction — 2026-10-03

Automatic conditional normalization and candidate detection are removed from the planned features. Issue #126 is closed as not planned: the general Boolean-pattern rewrite is not lossless across six-state truth or collection/evidence behavior. Earlier deferred-feature wording above is historical. Preserve the counterexample regression and continue authored conditional support.
