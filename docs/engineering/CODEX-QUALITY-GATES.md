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


## Claim-before-conclusion gate (mandatory for every task)

Codex must verify the following **before** stating that a feature is missing, unsupported, completed, untested, deprecated, or blocked. A generic instruction to "self-audit" or a passing test suite is not enough.

1. **Identify exact source-of-truth bytes.** Record the current merged contract commit, file and JSON Pointer/section, consumer pin, and active version. Consult the authoritative schema, relevant prose semantics, and source grammar where conversion is involved. Never infer feature absence from an error, a mapping inventory, a search result, or an outdated README.
2. **Trace the complete execution path.** Inspect the parser/importer, schema validation, semantic type checker, lowering, serializer, runtime/evaluator, editor, and generated mapping as applicable. Make a compact *contract-versus-consumer* table: supported in canonical? emitted? structurally accepted? semantically accepted? executable? Tested? Treat disagreement as a defect in the mismatching stage until disproved.
3. **Challenge the diagnosis with a minimal witness.** For a proposed canonical-language gap: provide a source-valid nondeprecated minimal input, exact attempted native Assessment, and actual canonical schema rejection or a documented missing semantic contract. **If canonical accepts the construct but any consumer rejects it, classify a consumer implementation/validation gap, not a canonical gap.** If schema accepts but semantics are unclear, classify as normative ambiguity, not proven absence. Verify deprecation directly from the pinned source XSD/Schematron.
4. **Generate an independent falsification case.** Use an expected-result oracle based on contract text, not conversion output or test labels. At minimum test one valid input, one invalid or negative case, and one boundary or status case per distinct behavior. Mutate the input or a dependency to make a formerly green test fail. When a semantic gate is changed, verify both focused and bulk production paths reject the same prohibited case.
5. **Repair and rerun.** Fix the earliest mismatching stage, add a permanent regression keyed to the canonical operation and original bug, rebuild/repin deterministic artifacts, check local and exact-head hosted CI, and re-evaluate every affected ledger/disposition. Do not "fix" a failure by renaming its category.
6. **Ask an independent adversarial reviewer.** On material code/contract changes, run a distinct reviewer context/subagent when supported, with a read-only brief: "Find one reason the implementation or its gap classification is wrong; check authoritative source and all consumers; compare raw examples; report counterevidence." If unavailable, perform a visibly separate diff/source review and say it was same-agent. A reviewer must not use the author's implementation as its expected-results oracle.

### Machine-enforced requirements to add and maintain

- **Schema→consumer coverage matrix:** enumerate active discriminators, expression operators, field types, status and cardinality tokens from the pinned JSON Schemas; compare with every applicable converter lowerer, semantic/type validator, RI evaluator and editor authoring branch. Every admitted feature needs a positive witness, a negative/boundary witness, or an explicit proof-scoped exclusion. Run a mutation that removes a handler to prove the gate fails. Do not assume a grep match proves correct execution.
- **Gap-claim guard:** any `canonical_language_gap` or `unsupported` entry in an authoritative receipt must point to a precise pinned source feature, demonstrate a rejected/undefined canonical target, and document alternative representability. A schema-accepted example that a local type validator rejects must fail this guard as a consumer defect.
- **Evidence/claim guard:** compare claimed counts with freshly generated artifacts and source identities; distinguish schema-validation, semantic-validation, scanner-executed and independently corroborated results. Reject unsupported "100% complete" or "DONE" evidence labels.

These are CI/acceptance requirements, not a claim that every repository already implements them. Codex must first inspect existing gates, build missing executable tests in bounded increments, and report any gates still advisory; do not disable required checks to merge.

### Required completion receipt (per material task)

| Claim | Evidence required |
| --- | --- |
| Feature supported | Canonical source pointer/pin, accepting witness and exact stage-by-stage result |
| Feature absent / canonical gap | Source-valid witness; canonical rejection or missing normative contract; countercheck against all known consumers |
| Source deprecated / invalid | Pinned official source-XSD/Schematron/prose evidence and exact source IDs |
| Converter/RI/editor defect | Reproduction, fixed-stage diff, negative and positive regressions, mutation proving test sensitivity |
| DONE / PARTIAL | Exact merged and consumer commits, source/digest pins, test/CI links, unresolved categories and proof levels, self-audit findings and fixes |

**Stop/continuation rule:** A blocked dependency blocks that PR's qualification, not other independent engineering work. After posting PARTIAL, continue to the next unblocked task within the actual execution budget. Claim DONE only for passed bounded gates; never imply a Codex session can continue beyond platform limits.


## Review checklist (apply to each task, not just conformance)
- **Schema/editor:** invalid forms rejected; YAML/graphical semantic roundtrip; every branch/operator, nested form, ordering, and missing-property case exercised.
- **Converter:** original XSD/Schematron/prose semantics drive a source→native crosswalk; source-valid positive and negative witnesses; lossless ID/default/type/logic/status provenance; no content-specific success masquerading as general conversion.
- **RI/scanner:** independent expected oracle; real evidence versus synthetic fixtures separated; missing/denied/error/empty distinguished; privilege, platform, concurrency, bounded resources, cancellation and deterministic results.
- **Conformance content:** fixture and expected result independently justified; selector misses are not confused with Require mismatches; generic seven-variant templates are not proof of complete semantics; verify adversarial vectors before scaling.
- **Cross-repo changes:** repin consumers, regenerate assets, check CI and provenance, document explicit unqualified gates.

**Human review remains required.** This policy is designed to catch obvious issues *before* the independent review, not to replace it.
