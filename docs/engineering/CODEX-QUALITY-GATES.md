# Standing Codex engineering quality gates

**Owner policy (2026-11-21). Applies to every SCAP-NG Codex task across canonical schemas, converter, reference implementation, VS Code editor, evidence, and related repos.** The objective is to prevent avoidable back-and-forth review cycles. These gates supplement, and do not override, each repository's normative source, security, CI, version, and mainline-integration requirements.

## Mandatory implement → challenge → correct cycle

1. **Confirm the actual contract before coding.** Read current `AGENTS.md`, the live issue, merged main and dependency pins. Cite the exact normative schema/semantics and acceptance criteria. Establish a baseline and note existing known failures; avoid reproducing stale work.
2. **Define truth before writing tests.** Specify input/preconditions, selected population and evidence, operation/logic, expected typed results, decisive reason, and source of authority. **Do not derive test expectations from the implementation under test**, generic labels such as “negative,” or the same generator that creates the fixtures.
3. **Implement in bounded increments.** Preserve the real production path and source identities. Test schema, semantics and negative paths; do not weaken validators or alter expected outcomes merely to obtain green tests.
4. **Perform a separate adversarial self-review before reporting completion.** Read the actual diff and representative raw inputs/outputs, not just test summaries. Deliberately search for a conforming counterexample, hidden assumptions, selector-versus-Require confusion, identical inputs with conflicting outcomes, datatype/case/cardinality/status boundaries, incomplete evidence, unsupported hosts, and dependency/CI drift. Correct findings and repeat the audit. Prefer an independent test module, different reasoning approach or separate Codex context for this phase.
5. **Require mutation/metamorphic checks where applicable.** Demonstrate that changing a decisive input changes the predicted result; irrelevant changes do not; removing evidence does not silently yield FALSE/TRUE; UNKNOWN/ERROR/NOT_APPLICABLE propagate as specified. Tests of the validators and oracle must fail on intentionally corrupted manifests, fixtures, hashes, status values, or semantics.
6. **Independently reconcile claims with actual evidence.** Verify commands really ran, CI current-head statuses, pinned versions, source hashes, and complete ledgers. Distinguish schema-valid, structurally converted, semantically proved, runtime executed, and independently equivalent. No blanket “all covered” claims based on counts or matching generated files.
7. **Fix known problems before claiming done.** If a gate is failing, report “implemented but unqualified” with exact blockers and a next action. Do not silently waive failures, relabel tests, fabricate evidence, or hide regressions. Escalate only genuinely unresolved normative/security/privilege or owner decisions.
8. **Report a compact falsifiable receipt.** State issue/PR/commit and canonical pins; feature and exception coverage; independent challenges and defects **found and fixed**; mutation results; local and hosted tests; remaining holds; and what has **not** been proved. Keep reviewable code merged promptly per repository integration policy; do not conflate a pre-alpha merge with release readiness.

## Review checklist (apply to each task, not just conformance)
- **Schema/editor:** invalid forms rejected; YAML/graphical semantic roundtrip; every branch/operator, nested form, ordering, and missing-property case exercised.
- **Converter:** original XSD/Schematron/prose semantics drive a source→native crosswalk; source-valid positive and negative witnesses; lossless ID/default/type/logic/status provenance; no content-specific success masquerading as general conversion.
- **RI/scanner:** independent expected oracle; real evidence versus synthetic fixtures separated; missing/denied/error/empty distinguished; privilege, platform, concurrency, bounded resources, cancellation and deterministic results.
- **Conformance content:** fixture and expected result independently justified; selector misses are not confused with Require mismatches; generic seven-variant templates are not proof of complete semantics; verify adversarial vectors before scaling.
- **Cross-repo changes:** repin consumers, regenerate assets, check CI and provenance, document explicit unqualified gates.

**Human review remains required.** This policy is designed to catch obvious issues *before* the independent review, not to replace it.
