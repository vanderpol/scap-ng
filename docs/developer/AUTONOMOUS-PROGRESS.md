# Autonomous development checkpoint

Updated: 2026-10-28. Workstream: [converter #251](https://github.com/vanderpol/scap-ng/issues/251),
with [schema dependencies #255](https://github.com/vanderpol/scap-ng/issues/255).
Follow [AGENTS.md](../../AGENTS.md), [MAINTAINING.md](../../MAINTAINING.md), and
[branch policy](../../BRANCH-MANAGEMENT.md). This is an engineering restart
record, not an external review surface or a release declaration.

## Completed and fully verified baseline

- Last completed implementation commit:
  `f789583e6bc5bebebaae6c00b7a3d790d9cefbbb` on `main`. Exactly two explicitly
  owner-authorized schema metadata annotations; no grammar change.
- Last complete maintained-suite verification: the same exact commit,
  [run 40719820070](https://github.com/vanderpol/scap-ng/actions/runs/40719820070),
  job `122927340809`: **3,253 run; 3,252 passed; 0 failures; 0 errors; 1 existing
  skip** in 853.508 seconds. All ten triggered workflows passed. Do not dispatch
  another full suite for this commit.
- Focused metadata verification: 45 passed, zero failures/errors/skips.
  The former mandatory version/date annotation failure is resolved.
- Last affected six-benchmark gate: converter commit
  `4365ffa82d7181195fd2fa012b92ea37cfb2ca05`,
  [run 40715616321](https://github.com/vanderpol/scap-ng/actions/runs/40715616321),
  passed with **1,055/1,396 original OVAL Rules proved**; all previous 1,012
  program hashes retained. The metadata-only commit did not trigger this gate;
  do not describe it as a new six-source execution.
- Delivered coverage: **49/51 approved platform-scope capabilities**, **49/100
  overall**. Pinned Self-Assertion: 521/713 configured Tests compiled and
  independently compared as typed terms; **519/803** original Tests are also
  source-valid/nondeprecated. Separate public cohorts: YAML **45/51**, RPM
  verifyfile **1/1**. These denominators and proof levels must remain separate.

## Local work after that verification

The preserved worktree has an uncommitted, schema-independent batch; it is not
part of the green commit above:

- Closed identity-domain enum selector references: generic validation of already
  representable literal/reference/unique Variable graphs, preserving names,
  graphs and quantifiers. Two original AppCmd/AppCmdListConfig Tests now pass a
  conversion/schema/compilation/independent-term probe. Full pinned corpus probe
  reports **523 compiled, 523 typed-term proofs, 0 mismatches**, out of 713
  configured/803 original Tests. Focused positive/negative regressions, old-proof
  hash retention, and affected benchmark checks remain to be completed before
  publishing or claiming this improvement verified.
- Diagnostic classification cleanup and resolved metadata-blocker bookkeeping.
  No source admission is authorized by a diagnostic category change.
- Local files: `tools/v04_direct_converter.py`,
  `tools/v04_direct_enum_variables.py`, `tools/v04_conversion_diagnostics.py`,
  `tests/fixtures/v04-converter-schema-dependencies.json`, and new
  `tests/fixtures/v04-direct-enum-selectors/`. Preserve and inspect these on
  restart; do not overwrite or reimplement them blindly.
- Workspace-only evidence/recovery location:
  `/workspace/.onboarding/scap-converter-recovery-20261028/`.
  `identity-enum-probe.json`, `enum-corpus-identity.json`,
  `enum-corpus-textfile.json`, and `status.json` retain detailed evidence.
  This path is not a portable source of truth: committed fixtures and linked
  GitHub runs must support any published result. `status.json` includes
  historical snapshots; this checkpoint is the concise current index.

## Failures, dependencies, and owner decisions

No current baseline CI failure. Local changes have not had full-suite
verification. Schema validity, compilation, independent typed-term comparison,
and scanner-runtime equivalence remain separate claims.

Pending #255 integration includes production activation of the canonical
Variable-function contract and the remaining nine function implementations;
approval of design direction does not authorize production grammar or compiler
changes. Preserve the grouped function decision packet and all source pins.
Other affected cases remain explicitly unsupported: collection population and
Variable-source Sets/Filters/external bindings, acquisition parameter multivalue
contracts, float/error profiles, SSH default/nil path and YAML record-member
projection. Consult the consolidated dependency register and exact source
counterexamples before classifying or changing any case.

No routine owner decision is required for the next independent batch. Request
direction only where the standing authorization's normative, architectural,
destructive/protected-workflow, scope, or genuine-blocker boundaries apply.
Schema/compiler/scanner/editor responsibilities remain separate from #251.

## Next actions and restart procedure

1. Inspect Git status, HEAD, local refs, latest GitHub `main`, and exact-head CI.
   Preserve newer work, recovery refs/stashes and source fixtures. Inspect the
   commit history of this file to identify its latest published checkpoint;
   do not create a duplicate documentation commit after interruption.
2. Finish positive/negative enum-reference and diagnostic tests, validate both
   original dependency closures, compilation operands and provenance, and
   compare all previous source/native/program proof hashes.
3. Run affected capability and benchmark checks plus all 100 contract parity
   checks. Document expected coverage differences individually. Publish the
   coherent passing batch directly to `main` with #251 reference.
4. Let existing workflows verify that integration commit. Do useful independent
   work locally while they run; do not supersede a full gate with a small push.
   Investigate failures automatically; never report pending checks as passing.
5. Use the [timing review](../audit/v04-regression-profile-20261028.md) for bounded
   profiling/optimization work without removing coverage or changing protected
   workflows. Update this checkpoint at the next meaningful milestone or before
   foreseeable interruption; keep large evidence in CI or workspace artifacts.
