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

## Receiving-session acceptance task

Read AGENTS.md, CURRENT-DESIGN.md and transition/. Do not change code yet. Report the exact checkout commit, current architecture, superseded designs, constraints, Board questions, proven tests versus unproven runtime semantics, history coverage limits and next task. Verify source input and required repository/service access. Reproduce the documented baseline check at the pinned checkpoint. Report discrepancies before continuing; do not reinterpret missing records as permission to change architecture.

Only one interface/session should own a given technical workstream at a time. If returning to ChatGPT, first commit/save coherent Codex work and update the checkpoint, decisions, open blockers, validation evidence and next step. Resume from the current repository rather than replaying older chat instructions.

## Access scope

Primary repository: vanderpol/scap-ng. Previously authorized related repositories are vanderpol/scap-content and vanderpol/stig-automation; access them only when needed for the task. AGENTS also identifies public pinned NIWC production and OVAL Self-Assertion evidence sources. Verify the receiving environment's actual access; authorization in this conversation does not create a connector connection.

## Provenance and coverage

Classification: **Evidence/Audit**. Prepared from directly visible owner instructions, supplied conversation summaries, targeted history retrieval and inspected repository files. No external redesign draft establishes owner acceptance. This directory is not a verbatim archive, and complete conversation enumeration is unavailable through the retrieval used so far. See decisions.md and recovered-notes.md for limits. No completeness guarantee or transition-ready claim is made.
