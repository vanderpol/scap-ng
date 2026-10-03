# Current 0.2.0 handoff status

The active handoff is now [SCAP-NG 0.2.0 content-development handoff](handoff-0.2.0-content-development-2026-10-03.md).

Broad Codex content development should begin only after the five bounded 0.2.0 closure items in that checkpoint are resolved and an exact-head validation checkpoint is recorded. VMware ESX new-Test expansion is deferred pending upstream guidance and is not a 0.2.0 blocker. Content development precedes editor development.

The maintained ready-to-use Codex task is [codex-test-content-0.2.0-task.md](codex-test-content-0.2.0-task.md). The intended authority order is specification → implementation/reference guidance → conformance content → editor.

The handoff has also been audited against the draft specification in [spec-coverage-audit-0.2.0-2026-10-03.md](spec-coverage-audit-0.2.0-2026-10-03.md). Universal author/processor requirements found during that audit belong in the specification; workflow-only Codex guidance remains outside the normative core.

The historical transition material below remains useful provenance. Statements below that describe Codex handoff as merely “preparation only” or identify older repository tasks should be read as dated history rather than the current 0.2.0 handoff state.

# Latest completed checkpoint

The 2026-10-02 bounded repository rebaseline and publication are complete; the final preservation and schema Actions passed. Start with [the completed checkpoint and receiving-session prompt](rebaseline-checkpoint-2026-10-02.md), [START-HERE](../START-HERE.md), and [58 live Board votes](../board/VOTES.md). This is suitable for a bounded receiving-session access/test acceptance. Complete chat-history recovery and a wholesale migration are not claimed. The dated preparation observations below remain preserved as history.

# Current task checkpoint — repository rebaseline and Board votes

2026-10-02: schema validation is resolved at technical commit `564d1ed8924f3265da5601874d6429f4b7db3572`; full fresh corpus run 37004465863 passed. The next active task is a lossless repository rebaseline, novice/Board navigation, complete path/dependency inventory, historical workflow gating, and publication of individual versioned yes/no Board Discussions. Follow docs/repository-map.md, docs/lossless-rebaseline.md and board/README.md. No historical payload deletion or ownership transfer is authorized. Read the latest repository-audit/publication Actions and board/discussion-index.json before claiming publication or preservation complete.

The owner is switching back to the phone ChatGPT app and requested uninterrupted work; a new chat should recover this task from GitHub, not start a competing architecture or generator. Original history coverage limits below still apply. Web Codex handoff remains preparation until a final checkpoint and receiving-session access/test acceptance.

# ChatGPT ↔ web Codex transition

Status: **PREPARATION ONLY — NOT A STABLE HANDOFF OR AN EXHAUSTIVE HISTORY ARCHIVE.**

Owner authorization: 2026-10-02, “When you think your current work is at a stable point, do everything you can, saving as much history as possible … in some github transition directory … scan ALL of our conversations and ensure that every key decision point is captured.”

This directory preserves project continuity in either interface. Moving to web Codex does not authorize a replacement architecture or abandonment of existing research. Returning to ChatGPT is supported by updating these same repository records. Do not rely on either interface automatically receiving the other interface's conversation history, memory, files, connections, or credentials.

## Read first

1. [Repository instructions](../AGENTS.md).
2. [Current design](../research/iterations/003/design/CURRENT-DESIGN.md).
3. [Recovered decisions and coverage limits](decisions.md).
4. [Retrieved conversation evidence](recovered-notes.md).
5. [Earlier decision reconciliation](../research/iterations/003/evidence/decision-recovery-2026-09-30.md).
6. [Specification index](../specification/README.md) and [requirements index](../specification/requirements-index.md).
7. [Pinned source index](source-index.json), [issue/comment snapshot](issues-2026-10-02.json), relevant live issues, pinned original sources, and actual validation evidence.

Latest explicit owner instructions take precedence. Historical generated source, earlier assistant summaries, proposals, implementation behavior, and passing narrow tests SHALL NOT override accepted current decisions. Owner working acceptance, Board ratification, implementation, schema validation, round-trip equivalence, and runtime conformance are distinct statuses.

## Current observation, not a release checkpoint

Conditional research checkpoint: [known-result suite and owner requests, 2026-10-03](conditional-suite-2026-10-03.md). Proposed conditional/N/A semantics remain experimental; this is separate from completed 0.1.0 enforcement fixes.

Latest scope/triage checkpoint: [0.2.0 owner requests and independently reproduced schema issues, 2026-10-03](schema-0.2.0-scope-2026-10-03.md). This records conditional evaluation, collected Item inclusion, and an all-capability collected-field readability audit before editor R&D. It does not claim implementation or a stable release.

Repository sampled at commit `56a65e1f3431ff4ac0fa0a893a920fc5aa726188`:
Load only reviewed post-alignment capability mappings.

The repository was receiving additional commits during preparation. No stable technical checkpoint has been declared. The sampled current-commit Actions included queued/in-progress normalization, regression, Self-Assertion, census, and platform runs. Skipped or cancelled runs are not passing evidence. Older green runs cannot validate later capability or grammar changes.

Before transition, record a new exact technical commit, source pins, commands, completed run/job URLs, retained artifacts/hashes, known failures, exclusions and next task. Keep previous observations as history instead of overwriting their dates or pretending they describe current HEAD.

## Stable handoff gates

- Finish the current bounded technical slice; account for all changes and applicable validations on the exact technical commit.
- Record unresolved defects and semantic limitations explicitly. A stable checkpoint can have documented open work; it need not mean the whole research project is complete.
- Reconcile accepted decisions with CURRENT-DESIGN, AGENTS, specification, examples, tools and consumers. Do not revive superseded Policy/Collection terminology.
- Recover accessible project conversations in topical/date passes, then reconcile each material decision with dated owner evidence and repository authority.
- Inventory original transcripts/export coverage separately from retrieved summaries. Preserve source exports where available without publishing unrelated personal/account information.
- Inventory uploaded reference documents, result packages and checklists. Retain their original files where permitted and appropriate; a Library identifier alone is not proof Codex can retrieve the file.
- Preserve important CI evidence beyond temporary Actions retention: source pins, compact reports, commands, versions, hashes and representative fixtures in git; retain required large original artifacts through durable accessible storage.
- Resolve conflicting or missing history explicitly; do not ask the owner to redesign a settled requirement merely because retrieval is incomplete.
- Verify Codex's repository access, source availability, dependencies and baseline tests before allowing it to continue implementation.
- Supply a ready-to-paste starting prompt and a completed checkpoint report.

## Hybrid ChatGPT / Codex operating model

Use the two interfaces as complementary tools rather than treating transition as one-way migration.

- ChatGPT is normally the better venue for architecture, standards interpretation, semantic analysis, requirements, specification work, and decisions whose rationale must be discussed.
- Codex is normally the better venue for bounded repository execution once the intended behavior is defined, including implementation, refactoring, regression tests, CI repair, and focused GitHub issues.
- Broad open-ended Codex tasks should be decomposed when practical to limit repeated large-context loading and preserve agentic usage for work that benefits from repository execution.
- Before sending work to Codex, label the expected usage qualitatively as small, moderate, or potentially expensive. No interface should infer or claim the user's live remaining allowance unless it is explicitly exposed or supplied by the user.
- If available Codex allowance becomes constrained, checkpoint coherent work to GitHub and continue appropriate design/reasoning work in ChatGPT. The project should not stall solely because one interface's agentic allowance is low.
- GitHub remains authoritative across switches. Record material requirement/architecture changes, validation evidence, blockers, and next steps before treating a conversational decision as settled.
- Only one interface/session should own an overlapping technical workstream at a time.

The detailed normative rule is in [AGENTS.md](../AGENTS.md) under **ChatGPT / Codex task-routing and usage-continuity rule**.

## Receiving-session acceptance task

Read AGENTS.md, CURRENT-DESIGN.md and transition/. Do not change code yet. Report the exact checkout commit, current architecture, superseded designs, constraints, Board questions, proven tests versus unproven runtime semantics, history coverage limits and next task. Verify source input and required repository/service access. Reproduce the documented baseline check at the pinned checkpoint. Report discrepancies before continuing; do not reinterpret missing records as permission to change architecture.

Only one interface/session should own a given technical workstream at a time. If returning to ChatGPT, first commit/save coherent Codex work and update the checkpoint, decisions, open blockers, validation evidence and next step. Resume from the current repository rather than replaying older chat instructions.

## Access scope

Primary repository: vanderpol/scap-ng. Previously authorized related repositories are vanderpol/scap-content and vanderpol/stig-automation; access them only when needed for the task. AGENTS also identifies public pinned NIWC production and OVAL Self-Assertion evidence sources. Verify the receiving environment's actual access; authorization in this conversation does not create a connector connection.

## Provenance and coverage

Classification: **Evidence/Audit**. Prepared from directly visible owner instructions, supplied conversation summaries, targeted history retrieval and inspected repository files. No external redesign draft establishes owner acceptance. This directory is not a verbatim archive, and complete conversation enumeration is unavailable through the retrieval used so far. See decisions.md and recovered-notes.md for limits. No completeness guarantee or transition-ready claim is made.
