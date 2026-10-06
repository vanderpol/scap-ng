# Branch Management

This file is the durable registry for every non-`main` branch in `vanderpol/scap-ng`.

## Operating rule

- `main` is the authoritative current project state.
- Do not create a branch without immediately adding or updating its entry here.
- Every branch entry SHALL record: purpose, status, relationship to `main`, intended disposition, and any pull request or decision that controls it.
- Allowed statuses are:
  - **active** — approved work is still being developed;
  - **ready-to-merge** — complete and awaiting merge/validation;
  - **hold/deferred** — intentionally preserved but must not be merged without the stated decision;
  - **merged/stale** — accepted work is already on `main`; the branch is retained only until cleanup;
  - **historical/superseded** — evidence only; SHALL NOT be merged as a branch;
  - **abandoned** — rejected/obsolete work retained only if there is an audit reason.
- A diverged branch is never evidence that work is missing from `main` by itself. Compare its commits/files and classify it here.
- Before a freeze, handoff, release, or major review build, audit all branches against `main` and update this file.
- Before deleting a branch, confirm that any accepted work is present on `main` and that useful history remains recoverable from Git.
- ChatGPT, Codex, and other agents SHALL read this file during repository preflight whenever branch state could affect the task.

## Current branch register

Snapshot taken during the SCAP-NG 0.2.0 freeze/handoff reconciliation on 2026-10-04.

| Branch | Status | Purpose / relationship to main | Disposition |
| --- | --- | --- | --- |
| `feature/optional-auto-map-groups` | merged/stale | Add opt-in `--auto-map-groups` normalization to conversion tools; default conversion remains faithful and does not invent grouping. Merged through PR #163 after focused, RHEL9 full-review, current-design, repository-boundary, and representative conversion gates passed. | Safe cleanup candidate after merge verification. |
| `feature/stig-manual-conversion-audit-161` | merged/stale | Issue #161: strict conversion-audit artifact and nested legacy-XCCDF loss guard; validated with Cyber Exchange AD Forest V3R2 and Google Chrome V2R11. Merged through PR #162. | Safe cleanup candidate after merge verification. |\n| `feature/stig-manual-audit-outputs-159` | merged/stale | Issue #159: optional native-NG HTML and XLSX manual-audit outputs; merged through PR #160. | Safe cleanup candidate after merge verification. |
| `assessment-reference-20261003` | merged/stale | Assessment reference documentation; fully behind main. | Safe cleanup candidate after freeze. |
| `assessment-results-0.2-20261003` | merged/stale | Assessment Results work; fully behind main. | Safe cleanup candidate after freeze. |
| `audit/issue-30-rhel9-selection` | historical/superseded | Old issue-30 RHEL 9 selection audit; diverged far behind current design. | Do not merge wholesale. Recover only by specific reviewed cherry-pick if ever needed. |
| `capability-audit-20261003` | merged/stale | Capability audit work; fully behind main. | Safe cleanup candidate after freeze. |
| `collected-items-0.2-20261003` | merged/stale | Collected Items 0.2.0 work; fully behind main. | Safe cleanup candidate after freeze. |
| `conditional-conformance-0.2-20261003` | merged/stale | Conditional conformance work; fully behind main. | Safe cleanup candidate after freeze. |
| `conditional-schema-0.2-20261003` | merged/stale | Conditional schema work; fully behind main. | Safe cleanup candidate after freeze. |
| `esx-host-capabilities-20261003` | merged/stale | Earlier ESX host capability draft lineage; fully behind main. | Preserve history only; ESX expansion remains deferred. |
| `esx-host-identity-software-20261003` | merged/stale | Earlier ESX identity/software draft lineage; fully behind main. | Preserve history only; ESX expansion remains deferred. |
| `fast-five-conversion-regression` | merged/stale | Five-benchmark fast conversion regression lane. Merged through PR #148. | Safe cleanup candidate after freeze. |
| `verify-fast-five-current-baseline` | historical/superseded | Temporary verification branch for the fast-five lane; PR #150 closed after the corrected lane passed directly on main. | Do not merge; safe cleanup candidate. |
| `freeze-v020-exact-main-trigger` | merged/stale | Non-semantic CI trigger used to run all required 0.2.0 freeze gates against one exact main SHA. Merged through PR #149. | Safe cleanup candidate after freeze. |
| `fix/variable-filter-dependency-validation` | historical/superseded | Old validation fix branch, diverged far behind current main. | Do not merge wholesale. |
| `freeze-v020-final-audit-fixes` | merged/stale | Final audit/comparator fixes. Merged through PR #147. | Safe cleanup candidate after freeze. |
| `freeze-v020-final-postmerge` | merged/stale | Earlier post-merge freeze work; fully behind main. | Safe cleanup candidate after freeze. |
| `freeze-v020-rhel-audit-fix` | historical/superseded | Intermediate RHEL audit/numeric comparator attempt; superseded by PR #147. | Do not merge. |
| `freeze-v020-rhel-audit-quarantine` | historical/superseded | Intermediate RHEL quarantine/comparator attempt; superseded by later accepted fixes. | Do not merge. |
| `freeze-v020-rhel-source-defect-fix` | merged/stale | Source-defect quarantine parity fix. Merged through PR #146. | Safe cleanup candidate after freeze. |
| `hold-esx-upstream-guidance-20261003` | hold/deferred | Preserves unadopted ESX host-wide draft pending upstream/community guidance. | Do not merge without explicit owner/upstream decision. |
| `item-inclusion-0.2-20261003` | merged/stale | Item inclusion/materialization work; fully behind main. | Safe cleanup candidate after freeze. |
| `iteration-002-policy-structure` | historical/superseded | Iteration-002 policy-structure history; far behind current architecture. | Historical evidence only. |
| `iteration-003-clean-conversion` | historical/superseded | Early iteration-003 clean conversion work; far behind current main. | Historical evidence only. |
| `reported-elements-0.2-20261003` | merged/stale | Reported-elements work; fully behind main. | Safe cleanup candidate after freeze. |
| `result-package-0.2-20261003` | merged/stale | Result-package work; fully behind main. | Safe cleanup candidate after freeze. |
| `roundtrip-ci-probe` | historical/superseded | Experimental round-trip CI work; diverged far behind current implementation. | Do not merge wholesale. |
| `roundtrip-conformance-003-validation` | historical/superseded | Historical iteration-003 round-trip validation branch. | Evidence only; do not merge wholesale. |
| `roundtrip-conformance-003` | historical/superseded | Historical iteration-003 round-trip implementation branch. | Evidence only; do not merge wholesale. |
| `schema-020-remaining-scope-20261003` | historical/superseded | Earlier remaining-scope note; later freeze/handoff records supersede it. | Do not merge as a branch. |
| `schema-enforcement-0.2-scope-20261003` | merged/stale | Schema enforcement scope work; fully behind main. | Safe cleanup candidate after freeze. |
| `schema-v020-self-contained-repair` | merged/stale | 0.2.0 self-contained schema repair lineage; fully behind main. | Safe cleanup candidate after freeze. |

| `research/for-each-audit-20261006` | active | 0.3.0 research on OVAL value-flow, Variable normalization, scoped Item binding/`for_each`, corpus evidence, conversion proof classes, and compact scoped results. This branch is intentionally isolated from frozen 0.2.0 and from current `main` until human semantic review. | Prepare focused review packet and proposed 0.3.0 specification; do not merge wholesale until owner review/acceptance and named focused/fast regression gates pass. |

## Branch creation template

Add a row immediately when creating a branch:

| Branch | Status | Purpose / relationship to main | Disposition |
| --- | --- | --- | --- |
| `example-branch` | active | Exact bounded task and why it cannot be done directly on main. | Merge via PR after named validation, then mark merged/stale. |

For a temporary freeze or repair branch, include the controlling issue/PR and update the row as soon as it is merged, deferred, superseded, or abandoned.
