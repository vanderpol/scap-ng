# Repository rebaseline checkpoint — 2026-10-02

Status: the bounded repository audit, visitor navigation and Board proposal publication are complete. This is a suitable checkpoint for a receiving session to verify access and reproduce checks. It is not a release, Board ratification, runtime conformance claim, or exhaustive chat-history archive.

## Exact checkpoints

| Purpose | Commit / reference |
| --- | --- |
| Preserved before-cleanup tree | `9751ef0e5ae43ab728876969ff59dad538a101f0` |
| Preservation tag | `pre-rebaseline-2026-10-02`, verified at the before-cleanup commit |
| Navigation, inventory, historical workflow gates, 58 proposal sources | `1752740bb2fa6f9abe5e0080e2afbac956c8d561` |
| Actual Discussion publication index | `15bd33c32ace3586829c5e3a9e0ea6ec2e7f0dd7` |
| Active schema utility promotion and archived-code CI guard | `f9762b4ec08c68ea69f491d0d019c126483e67f2` |
| Earlier authored unknown-Test fix | `564d1ed8924f3265da5601874d6429f4b7db3572` |

The other session's hybrid ChatGPT/Codex operating-model commit `aa654781aac304ba6bf7df3db2e981860e30d0d6` was preserved when publishing the audit. Start from current main and inspect later changes; do not reset main to a checkpoint or overwrite concurrent work.

## What changed and what was preserved

- Every one of the baseline's 34,242 tracked paths remains. Original iteration-001/002 payload byte hashes match the baseline. No payload deletion, relocation, history rewrite, ownership transfer or community release was performed.
- The complete baseline inventory identifies path, mode, original Git blob, role and classification basis. 28,267 files (82.6%) are classified as historical artifacts; 5,302 are current generated review files. Classification does not prove individual semantic correctness or authorize deletion.
- START-HERE, the repository map and the maintained RHEL9 review guide give visitors a current route. Historical instructions retain provenance and are marked accordingly. Twelve historical workflows require explicit manual opt-in; three held workflows remain held.
- Current CI is prohibited from executing code under iteration-001/002. The still-used SCAP 1.4 schema validator was copied byte-for-byte to `tools/validate_scap14_schema_bundle.py`; its original remains intact. Two historical data inputs remain explicitly used and accounted for.
- 130 historical decision/design/specification/topic records were indexed from the exact baseline tree, with headings, original question sections and hashes. The reconciliation preserves unresolved exact weight mappings, algorithm suites and other detailed contracts; a broad direction vote does not close those details.
- All 58 versioned yes/no proposal Discussions were published successfully. See [the vote index](../board/VOTES.md) and [machine-readable publication record](../board/discussion-index.json). Use 👍 Yes / 👎 No on the opening post. Publication and public reaction totals are not Board ratification; electorate, quorum, voting window and formal disposition remain governance matters.

## Validation evidence

- [Initial preservation and tag run 37009025649](https://github.com/vanderpol/scap-ng/actions/runs/37009025649): success at `1752740`.
- [Discussion publication run 37009025764](https://github.com/vanderpol/scap-ng/actions/runs/37009025764): success, 58 indexed proposals, zero publication failures.
- [Current-design regression run 37009025580](https://github.com/vanderpol/scap-ng/actions/runs/37009025580): success on Windows and Linux at `1752740`.
- Self-Assertion, Linux, Windows, diverse-platform and previously blocked-package workflows passed at `1752740` (runs 37009025751, 37009025676, 37009025635, 37009025656 and 37009025567).
- Local final boundary check: 34,242 baseline paths, zero failures. The promoted schema utility verified 108 pinned schema files and compiled the Omni schema. The copy changes no validator behavior.
- Final follow-up checks at `f9762b4`: [preservation run 37009814822](https://github.com/vanderpol/scap-ng/actions/runs/37009814822) and [schema run 37009814838](https://github.com/vanderpol/scap-ng/actions/runs/37009814838) both completed successfully.
- Earlier fresh full corpus run [37004465863](https://github.com/vanderpol/scap-ng/actions/runs/37004465863) passed after the unknown-Test fix: 25,147 valid Assessments before normalization, 19,655 after, 65 compiled baseline/normalized/signed-test bundles. Retained evidence: [unknown-Test fix report](../research/iterations/003/evidence/unknown-test-authored-result-fix-2026-10-02.json).
- Cleanup-triggered duplicate full census 37009025866 and native experiment 37009025594 were still queued/running when this checkpoint was prepared. Do not treat them as passed. Check live outcomes; preserve new substantive failures or evidence. Cleanup changed no converter/capability semantics.

Schema validation, round-trip preservation and bundle compilation do not establish full runtime equivalence, target execution coverage or publisher trust. Self-signed CMS fixtures are signing-path experiments.

## Receiving session: bounded first task

Expected usage: small to moderate for access verification and baseline checks; potentially expensive if rerunning the full corpus. Only one session should own an overlapping technical workstream.

Ready-to-paste prompt:

> Resume vanderpol/scap-ng from current main. First read AGENTS.md, START-HERE.md, research/iterations/003/design/CURRENT-DESIGN.md, docs/repository-map.md, docs/decision-reconciliation.md and transition/rebaseline-checkpoint-2026-10-02.md. Do not change the architecture or run old iteration generators. Report the exact checkout commit and changes since f9762b4ec08c68ea69f491d0d019c126483e67f2. Verify repository/source access, the preservation tag, 58 Discussion links, and the two final follow-up Actions. Reproduce `python tools/audit_repository_layout.py --check` and `python tools/validate_scap14_schema_bundle.py third_party/scap-1.4-schemas` with the documented dependencies. Report discrepancies and unresolved Board/detail questions before selecting a new bounded implementation task. Do not infer exhaustive chat recovery, Board approval or runtime conformance.

Dependencies for the bounded checks: Python 3.12, PyYAML 6.0.3 and lxml. Read the repository's dependency files for converter/regression/full-corpus work.

## Limits and next work

The accessible conversation summaries and repository evidence were reconciled; complete enumeration or verbatim recovery of all prior chats was unavailable. Original uploads and expired Actions artifacts are not automatically accessible to a new Codex environment. See transition/decisions.md, recovered-notes.md and source-index.json. A missing historical source remains a coverage gap, never permission to invent a decision.

No need to move the whole project into one interface. Continue standards/design reasoning in ChatGPT and give Codex bounded repository tasks after its acceptance check. A return to ChatGPT uses the same GitHub checkpoint plus any later committed work. Verify actual account/repository connections in the receiving environment; this session's authorization does not create access there.

Before any future physical removal, follow [the lossless method](../docs/lossless-rebaseline.md): independent verified bundle/archive, restore check, dependency review, concrete removal manifest, explicit owner authorization. The tag and inventory alone are not an independent backup. Formal community transfer and broad release readiness remain separate tasks.
