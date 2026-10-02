# Repository cleanup before web Codex handoff

Status: requested by owner 2026-10-02; audit pending. Finish the native-corpus
schema-validation defect first. This file records the next task, not a completed
review or approval of a particular layout.

The owner reports repeated accidental execution of obsolete iteration code and
requests a safer repository layout before handoff. Review **all three iteration
directories**, retaining lessons learned, decisions, evidence, and unresolved
questions that may need OVAL Board action. Do not treat historical successful
experiments as current implementation proof or delete their evidence to reduce
confusion.

Required audit outputs:

- Inventory each iteration's code, design records, decision registers, Board
  questions, fixtures, generated trees and evidence; pin every source used.
- Reconcile adopted working decisions, superseded proposals, implementation
  gaps and unresolved Board questions against latest owner instructions and
  current GitHub issues. Historical questions require reconciliation, not
  automatic reopening or closure.
- Establish one clear current entry point, explicit archived-code boundaries,
  and reproducible current validation commands. Inspect CI/import/path
  dependencies before moving maintained material.
- Preserve source links and a relocation map for any moved documents. Historical
  generated trees remain evidence and must not become generator input.
- Verify current converter, validators, regression suites and CI after any
  structural change; record remaining risks before recommending handoff.

Existing safeguards: root AGENTS.md requires CURRENT-DESIGN preflight; maintained
converter is tools/scap_upconvert_v003/ and must not import 001/002 pipelines.
These safeguards have not yet been audited for consistent enforcement across
the entire repository. Personal-context recovery for this request is partial
and is not an exhaustive transcript export. Older working instructions and
earlier Board proposals must be compared with current decisions, especially
Benchmark → Rule → Assessment, authored Object terminology, native capability
semantics, Tailoring Parameter limits and retained Rule role.
