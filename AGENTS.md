## Full-corpus execution invariant

- The full 65-benchmark NIWC corpus is a deliverable/checkpoint gate only.
- It SHALL NOT run as a routine development, pull-request, branch, or ordinary `main` regression.
- Run it only when intentionally producing a durable content deliverable, release/freeze candidate, or OVAL Board review checkpoint.
- Normal development SHALL use focused tests and the maintained fast regression set.

## Human-auditable maintenance invariant

- At the start of every repository task, read `MAINTAINING.md` in addition to the normal repository preflight files.
- Passing automated tests SHALL NOT by itself establish that a semantic language change is accepted.
- Any change to language/schema meaning, result semantics, capability semantics, or conversion semantics SHALL have the human review packet defined in `MAINTAINING.md` before it is treated as accepted current design.
- Agents may investigate, implement already accepted behavior, add focused tests, and prepare review material, but SHALL NOT silently resolve a materially ambiguous semantic choice through implementation alone.

## Branch management invariant

Branch state is part of the durable repository record.

- At the start of every repository task, read `BRANCH-MANAGEMENT.md` during preflight, even when no branch work is planned. Branch state is always part of the repository context.
- Do not create a non-`main` branch without immediately recording its purpose, status, relationship to `main`, and intended disposition in `BRANCH-MANAGEMENT.md`.
- Update that entry when the branch is merged, held/deferred, superseded, abandoned, or becomes ready to merge.
- Before a freeze, handoff, release, or major review build, audit all non-`main` branches against `main` and resolve or explicitly classify every branch that is ahead/diverged.
- A branch name, old green workflow, or ahead/diverged count is not proof that work belongs on `main`; inspect the actual commits/files and current project decisions.
- Accepted work SHALL NOT be left only on an untracked branch. Deferred/historical branches SHALL NOT be merged wholesale merely to eliminate divergence.

## Repository boundary and preservation preflight

Read START-HERE.md, docs/repository-policy.json, docs/repository-map.md and the current design below. Only current entry points/workflows are current generation authority. Do not select a tool merely because it is under tools/ or contains v003 in its name. Historical generation requires an explicit reproduction task and allow_historical workflow opt-in; held workflows remain held.

The rebaseline preserves every removed baseline payload through the pinned pre-rebaseline tag/history and explicit removal manifests. Do not rewrite Git history or transfer ownership under cleanup authorization. Before future removal, follow docs/lossless-rebaseline.md with an explicit reviewed removal set and verified restoration evidence. Preserve all lessons and original Board questions. Board decision candidates belong in separate versioned yes/no GitHub Discussions with reactions; do not silently rewrite a published vote or infer ratification from public counts.

Historical sections titled Iteration 002 source-only checkpoint, OVAL-aligned NG capability taxonomy and Native source design checkpoint below record earlier phase restrictions. They do not override current fresh-source corpus authorization, reviewed native mappings, authored Object vocabulary or latest CURRENT-DESIGN. Maintain shared parser/data dependencies even where their paths look historical; exceptions are in docs/repository-policy.json.



## Continuous task execution invariant

This is a hard repository operating rule for ChatGPT, Codex, and other autonomous agents working an active task.

- Once an agent begins an approved task, it SHALL continue executing the task through all safe, available, in-scope next steps until the task is complete or a genuine project-owner decision is required.
- A progress/status update SHALL NOT terminate execution. After giving an update, the agent SHALL immediately continue with the next safe step.
- A long-running CI job, external workflow, build, validation, or other wait state SHALL NOT by itself justify stopping. The agent SHALL continue useful independent or preparatory work in parallel when doing so is safe and cannot invalidate the running work, and SHALL return to the waiting gate when its result becomes available.
- The agent SHALL NOT stop merely because a subtask completed, a checkpoint was reached, the next step is obvious, a tool call returned successfully, or additional verification remains.
- The agent MAY stop before task completion only when a required decision, authorization, missing prerequisite, ambiguous requirement with materially different consequences, or other genuine blocker requires project-owner input. When stopping for such a blocker, the agent SHALL state the exact decision or information required.
- If no owner decision is required, the default action is **continue executing**.
- Completion claims SHALL describe the actual completed task and its verification state; partial progress SHALL be labeled as partial and SHALL NOT be used as a reason to end execution.

## Versioned schema snapshot invariant

This is a hard repository rule for every SCAP-NG schema version.

- Every `schema/vX.Y.Z/` SHALL be a complete, self-contained snapshot. It SHALL NOT resolve normative schemas, capability mappings, registries, or support data from another SCAP-NG version directory.
- Starting a new schema version SHALL copy forward the complete preceding schema surface. Unchanged files still belong physically to the new version.
- Every JSON Schema file in a versioned schema directory SHALL carry explicit human-visible SCAP-NG version metadata matching its directory and explicit last-modified metadata. Its `$id`, where present, SHALL identify the same version.
- Last-modified records the individual schema's last substantive modification; copy-forward alone changes version identity, not that semantic-modification date. Release/incorporation dates, when needed, are separate metadata.
- Local `$ref` and equivalent generated references SHALL remain within the same version. Truly external standards are allowed; another `schema/vX.Y.Z/` is never an external/shared dependency.
- Capability mappings, scope/registry data, and normative schema-support files SHALL be version-local even when byte-identical to the previous version.
- CI SHALL recursively enforce version identity, required metadata, complete version-local dependencies, and absence of cross-version references. A version is not freeze-ready while any violation exists.
- Version directories SHALL be directly and meaningfully diffable without hidden inheritance.

## Review-surface lifecycle invariant

This is a hard repository rule.

- `review/current/` is the only active external review target.
- Completed review cycles are frozen immutably as `review/iterations/NNN/`.
- Never revise a frozen iteration to reflect later design work; start a new current review cycle instead.
- Review iteration numbers are provenance checkpoints and are independent of product/release version numbers.
- Alpha, beta, RC, and stable releases must be promoted from a specific completed review iteration and record that source iteration plus commit/tag.
- Do not create parallel active review trees under `research/`, `docs/`, `board/`, or another directory.
- Development infrastructure such as tools, tests, CI, conversion scratch data, transition notes, and bulk source corpora stays outside `review/`.

## Mandatory current-design preflight

Before selecting or running authoring generation tools, read
`research/iterations/003/design/CURRENT-DESIGN.md`. It separates latest owner
decisions, implementation gaps and pending Board ratification. Older generated
trees are evidence, not architecture authority. Do not interpret a pending Board
vote as permission to drop owner-agreed working features. Variables support both
existing named Objects and private embedded Objects. Before describing
review output as ready, run `tools/check_current_authoring_contract.py` and
feature-specific regressions. A vocabulary pass is not semantic equivalence.

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

## Iteration 002 source-only checkpoint

Iteration 002 is source-design only until the project owner explicitly says the source model is ready.

- Do not spend compute on final package generation, signing, complete benchmark regeneration, reference-scanner work, or broad corpus expansion.
- Use the four anchors only to select and validate representative authoring examples, applicability cases, and shared-assessment mappings.
- Optimize for concise, understandable native source that an experienced SCAP/OVAL author can review directly.
- Treat packaging and runtime implementation as downstream work after source syntax/semantics are agreed.

## OVAL-aligned NG capability taxonomy

Iteration 002 uses OVAL's supported platform-family/test vocabulary as the default SCAP-NG capability taxonomy.

- Canonical default naming starts from `<oval-family>.<oval-test-basename>`, removing only the trailing `_test`; unversioned examples include `unix.file`, `windows.registry`, `linux.rpminfo`, and `solaris.package`.
- Historical numeric/version suffixes such as `53`, `54`, `55`, and `511` are an explicit OVAL Board design decision. Preserve the supported source basename in migration prototypes until the Board decides whether NG retains those suffixes or rebases corrected semantics to unsuffixed names.
- Reuse OVAL's family boundaries as accumulated design evidence, especially where collected data models differ by platform.
- Reusing OVAL capability vocabulary does not require retaining OVAL XML definition/test/object/state authoring structure.
- Effectively deprecated OVAL tests do not become NG capabilities unless governance has reinstated them.

## Native source design checkpoint

Broad benchmark expansion is paused while the native SCAP-NG authoring model is reviewed.

- Treat current fidelity-first YAML as migration evidence, not normative native syntax.
- Before adding more benchmark families, use the current review surface and current design; the historical iteration-001 native-source review remains recoverable from tag `pre-rebaseline-2026-10-02`.
- Keep XCCDF/OVAL/OCIL/CPE XML identifiers, namespaces, hrefs, and source trees in migration provenance rather than executable native source.
- Prefer meaningful NG-local names and concise typed collect/derive/evaluate syntax.
- Preserve established OVAL platform-family boundaries when collected data or evaluation semantics materially differ; for example, keep `unix.file` distinct from `windows.file` unless evidence supports a lossless common model.
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
- The historical up-conversion roadmap remains recoverable from tag `pre-rebaseline-2026-10-02`; current direction is recorded in the maintained tools/docs and roadmap.

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


## Iteration 003 native-output cleanliness

Iteration 003 restarts SCAP 1.4 up-conversion from the accepted native design.

- Native SCAP-NG output SHALL NOT contain XCCDF, OVAL, OCIL, or CPE Applicability Language namespaces, IDs, hrefs, XML-shaped structures, or other legacy serialization residue.
- Legacy source identifiers and component linkage belong only in conversion provenance/evidence.
- If preserving a legacy reference appears necessary for semantics, stop that conversion path and raise a design-review blocker; do not emit it into native NG without explicit project-owner approval.
- `benchmark.yaml` owns Benchmark policy structure, including Profiles, meaningful Groups, and Parameters.
- Iteration 003 does not generate standalone `profiles.yaml`, `groups.yaml`, `values.yaml`, `platforms.yaml`, or `processing.yaml`.
- A small `applicability.yaml` registry is retained only as semantic applicability-ID -> Assessment binding indirection; it SHALL NOT contain migrated OVAL/CPE/XCCDF structures.
- Rules reference applicability IDs, not Assessment file paths.
- The clean-room converter lives under `tools/scap_upconvert_v003/` and SHALL NOT import the iteration-001/002 whole-benchmark conversion pipeline.

## Pre-alpha publication workflow

Owner direction, 2026-09-30: during the current pre-alpha phase, commit completed
and appropriately tested work directly to `main`. Do not create routine feature
branches or pull requests unless the owner explicitly requests one. Record
provenance, implementation limits and validation evidence as usual. Once the
owner identifies a stable checkpoint, reassess the branch/review workflow.

## Current Rule/Assessment architecture

The owner reconfirmed on 2026-09-30 that separate Policy objects were replaced
by Rules to support compliance and vulnerability use cases. The model is
Benchmark → Rule → selected Assessment. Rules own named selections/defaults
and explicit relative Assessment source paths. Do not restore Policy files from
older split-policy experiments or interpret those trees as the current design.
See `research/iterations/003/design/native-source-layout.md`.
Native Assessments SHALL NOT contain a `deprecated` attribute. Effective
deprecated source tests remain conversion blockers; historical deprecation
metadata belongs in provenance, never a native runtime flag.

## Assessment presentation order

For current native output, put metadata first, then `objects`, `variables`, `states`,
`tests`, `evaluate`; omit absent sections. This is presentation, not execution
order. Resolve forward references independently of mapping key order, and retain
semantically significant sequence order (for example, function arguments).
Run `tools/check_current_authoring_contract.py` on generated review source; keep
the presentation-order guard in the converter and CI. See `CURRENT-DESIGN.md`
under `research/iterations/003/design/` for the authoritative contract.

## ChatGPT / Codex task-routing and usage-continuity rule

GitHub is the durable system of record for work performed through ChatGPT and Codex. Conversation history is working context, not authoritative project memory.

- Prefer ChatGPT for architectural reasoning, standards interpretation, SCAP/OVAL semantics, specification decisions, competing design choices, and work where discussion/rationale is itself a material project artifact.
- Prefer Codex for bounded repository implementation after the intended behavior is sufficiently defined: schema/code changes, converter updates, refactors, regression tests, CI fixes, and well-scoped GitHub issues.
- Avoid assigning Codex broad open-ended work when the same goal can be decomposed into bounded tasks, especially when it would require repeatedly loading large repository/history context.
- When recommending a Codex task, characterize expected usage qualitatively as **small**, **moderate**, or **potentially expensive** based on scope, context size, tool use, and expected iteration. This is guidance, not a claim to know the account's live usage meter.
- Neither ChatGPT nor Codex should claim visibility into the user's live remaining allowance unless the active product explicitly exposes it. If the user supplies the current usage/allowance state, use it when deciding where to continue work.
- When Codex allowance is becoming constrained, checkpoint coherent Codex work to GitHub and continue suitable reasoning/design work in ChatGPT rather than pausing the project. Reserve remaining Codex capacity for repository-execution tasks where it adds the most value.
- Switching interfaces is a change of tool, not a change of project authority. Before switching, commit or otherwise durably record current decisions, implementation state, validation evidence, blockers, and the next bounded task.
- Any conversation that materially changes a requirement, invariant, architecture decision, semantic mapping, or accepted workflow should result in a GitHub update before that decision is treated as settled.
- One interface/session should own a technical workstream at a time. Do not make concurrent overlapping edits from ChatGPT and Codex without an explicit coordination plan.
- These routing rules optimize continuity and efficient use of agentic allowance; they do not weaken validation, provenance, testing, or current-design requirements.

## Cross-interface continuity

For ChatGPT/web Codex handoffs, read transition/README.md and transition/decisions.md after CURRENT-DESIGN. Treat archived issue/conversation summaries and pinned historical documents as evidence, not current implementation proof. Recover latest owner corrections before restoring an older feature. Owner Oct 1 correction: Tailoring cannot override publisher Parameter values; delegated values use Organizational Input and changed requirements need distinct policy identity. Preserve Rule role as the working informational policy control pending an agreed replacement. Update the handoff with exact commit, validation evidence, blockers and next step when changing interfaces.

