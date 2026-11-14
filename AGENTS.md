# Canonical schema change cascade — REQUIRED

**Owner policy, effective 2026-11-13:** there is exactly **one** supported SCAP-NG schema version in `main`, currently **0.4.1**, in the flat `schema/` directory. The converter, editor and reference implementation must support **only that same active version**, pinned to one reviewed schema commit. No `schema/v0.4.0`, `schema/v0.4.1` parallel copies, runtime version switch, compatibility shim, hidden grammar fallback, alternate editor metadata pack or dual-engine logic. Historic 0.4.0 exists only in the Git archive/history. The next version bump (0.5.0) replaces this family; never creates a second one.

## What triggers a cascade

**Every change to** `schema/**` (including Results, GUIDs, mappings, applicability, Objects/Requires, Variables, documentation descriptions, enum/defaults or datatypes), normative language contracts, schema-generating scripts, authoring vocabulary, or canonical examples **requires** a cascade. No version-number bump is needed to trigger it. Treat a documentation description as a potential editor-hover change and a Result field as an RI output change.

**Never consider a schema PR complete with only valid JSON Schema.** Its associated generated documentation, curated sample content, metadata and consumer qualifications must be fresh. Use the exact commit SHA and report different gates separately: schema-valid; source/semantic parity; editor-qualified; RI-executed; independently source-equivalent.

## Canonical regeneration and review

1. Run `python tools/generate_native_selector_schema.py` and all corresponding `--check` gates. Update all affected schemas and mappings **once**, within the existing flat `schema/` tree.
2. Run `python tools/generate_docs.py`, `python tools/generate_unix_file_reference.py`, `python tools/generate_approved_annotation_pilot.py`, `python tools/generate_review_documentation_pack.py`, `python tools/generate_documentation.py` and `python tools/check_documentation_examples.py`. Review resulting Markdown, generated schema reference, editor hover/help, field tables and release manifest. Use exact-byte `--check` CI and documentation fidelity audits; do not silently edit curated human prose.
3. Audit **every** canonical `examples/**`, `docs/examples/**`, and other current-schema teaching fixture affected by the change. Update or replace obsolete 0.4.0 version markers, schema pins and sample values with **0.4.1**. Reject stale examples in CI. For any sample with claimed pass/fail, preserve the distinction between *expected* outcome and *RI/SCC independently verified* outcome.
4. Update `tests/test_schema_integrity.py` with an independently calculated SHA-256 for the entire current flat schema family (and exact root/reference/resource counts). Run full JSON Schema Draft 2020-12 tests including invalid/negative cases. Maintain reproducibility receipts and inspect generated diffs. Never make the integrity check pass by using a placeholder digest, a moving-main pin, or reducing test coverage.
5. Update native specification and result-type documentation, semantic/provenance matrices and explicit change log. The new **0.4.1 SIEM correlation fields** (`scan_result.scan_session_guid`, `scan_result.scanner.app_guid`, `scan_result.targets[].machine_guid`) are metadata only; update the corresponding example and RI result emitter tests. Maintain machine identity per target in multi-target scans.

## Required downstream handoffs on EVERY schema change

- **Converter (Tools):** open/update [Tools #59](https://github.com/vanderpol/scap-ng-tools/issues/59). Re-pin the *single* 0.4.1 semantic/schema pack; regenerate conversion outputs and test both full 65-benchmark and 168-Definition/803-Test source accounting, provenance, blocker and semantic parity. No alternate 0.4.0 mode and no invented OVAL equivalence.
- **Editor (VS Code):** open/update [VS Code #65](https://github.com/vanderpol/scap-ng-vscode/issues/65). Regenerate the *single* offline editor pack against the exact same canonical commit. Validate YAML round-trip/CRUD, generated help, enum and operator controls, current example files, CI, and extension-host installation. Reject legacy source safely instead of silently changing it.
- **Reference implementation:** open/update [RI #66](https://github.com/vanderpol/scap-ng-ri/issues/66) and the relevant focused Result identity issue. Re-pin the same contract; adapt the compiler/evaluator or Result emitter as appropriate; qualify completeness, typed evidence, bounded performance, and positive/negative platform tests. Scan/session/app/machine GUIDs are correlation metadata, never compliance evidence.
- **Publication security is a hard gate.** The canonical CI performs read-only exact-commit pin checks against Tools, VS Code, and RI. It must not perform unapproved `git push`, `curl POST`, `gh issue comment` or cross-repository dispatch, even if a credential is present. If a consumer pin is absent or stale, fail CI and follow the linked downstream GitHub issue through an authorized reviewed PR. Only an independently qualified shared publication gate could authorize future automation; no auto-merge or writes into unrelated Codex branches.

## Completion gates

Document the triggering commit, semantic/affected-field diff, exact generator commands, hashes, changed Markdown/sample files, CI checks, downstream issues and qualified PR SHAs in the canonical PR. A passing source-only schema CI run **does not** close the downstream gates. Keep changes in linked draft PRs until a synchronized reviewed cutover is possible. Preserve historical 0.4.0 only in Git history; never reintroduce parallel active versions.

---

# Semantic implementation requirement

For every RI capability implemented or modified, the same development increment must include:

1. Research of pinned OVAL 5.12.3 evaluation rules and edge cases.
2. Mapping to the exact canonical SCAP-NG 0.4 schema, distinguishing equivalent, intentionally different, unsupported and unresolved behavior.
3. Standalone normative native documentation in this repository; OVAL must not be required reading for implementers.
4. Executable conformance fixtures with positive and negative cases, and passing RI regressions.
5. An OVAL-to-native compatibility matrix with source pointers and exact schema pins.
6. A clear separation between language requirements and RI implementation limitations.

No language behavior is complete without these four deliverables: normative documentation, compatibility mapping, executable conformance tests and passing RI regressions. Coordinate separate linked draft PRs; preserve frozen schemas and all semantic holds. Escalate genuine specification conflicts. Do not merge or promote unapproved semantics. Store implementation/performance limits separately from language requirements.


### Execution authority and incomplete evidence (permanent)

- Normative SCAP-NG contracts must distinguish acquisition status, logical Object completeness, population completeness, evidence completeness, privilege context, visibility/namespace scope, evidence trust, and evaluation outcome. A successful syscall or returned Item is not a completeness guarantee.
- Root, restricted namespace, missing, denied, partial, symlink, mount-boundary, include, and kernel-visibility behavior must be explicitly specified or held; container/namespace root must not be described as host-wide authority.
- Apparent passes that require complete population evidence must not be asserted without sufficient completeness. Observed decisive failures may remain failures only where unseen evidence cannot reverse the condition.
- Any normative change in these areas requires coordinated frozen-schema/result review, standalone canonical documentation understandable without OVAL, pinned OVAL 5.12.3 compatibility research, positive/negative conformance fixtures, and linked RI regression tests. AGENTS.md does not approve new language or schema semantics; unresolved decisions belong in an owner-review document.
