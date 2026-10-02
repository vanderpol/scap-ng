# SCAP-NG evidence-repository migration

Target evidence repository: `vanderpol/scap-ng-evidence`.

## Boundary

The main `scap-ng` repository retains material that people maintain and review:

- `review/` and current review navigation;
- specification/schema source;
- Board proposals/discussion indexes;
- maintained implementation tools and tests;
- small representative examples;
- compact evidence summaries needed to understand review claims.

The evidence repository is the destination for large or exhaustive generated proof:

- corpus conversion outputs;
- OVAL/SCAP round-trip outputs;
- generated native normalization/compiler trees;
- exhaustive per-package/per-rule validation records;
- repository inventory snapshots;
- large generated result sets and machine-readable comparison reports.

Evidence remains non-normative and directionally separate from native SCAP-NG content.

## Migration rule

No source tree is deleted from this repository merely because it looks generated.

For each candidate set:

1. record source commit, path and blob/tree identity;
2. classify whether it is evidence, current review material, maintained source/tooling, or history;
3. copy it to `scap-ng-evidence` under a stable evidence-run ID;
4. write a manifest recording source pins, generating tool/command, validation state and limitations;
5. verify copied bytes/hashes and path accounting;
6. update compact summaries and links in `scap-ng`;
7. run current dependency/link/regression checks;
8. remove the main-repository payload only after the concrete removal set is reviewable and authorized.

The original Git history and the pre-rebaseline tag remain recovery sources.

## Initial strong evidence candidates

The following are strong candidates for staged evidence migration, subject to dependency verification:

- `research/iterations/003/evidence/full-current-native-normalize-compile/`
- `research/iterations/003/evidence/full-current-roundtrip-2026-09-30/`
- `research/iterations/003/evidence/rhel9-full/`
- `research/iterations/003/evidence/rhel9-review-slice/`
- `research/iterations/003/evidence/roundtrip-source-oval/`
- `research/iterations/003/evidence/xccdf-valid-gap-inventory/`
- large generated portions of `research/iterations/003/review/full-current-native-normalized/`
- large generated portions of complete RHEL 9 / Windows 11 review outputs once small reviewer-facing examples and summaries are separated;
- `docs/audit/repository-inventory.tsv.gz` and future bulky repository-audit snapshots.

## Keep in the main repository

The following should not be moved merely for size reduction:

- design/specification decisions;
- current schemas;
- Board proposals, vote manifests and Discussion links;
- maintained tools/tests/workflows;
- source manifests or governance inputs required by active tools;
- representative examples needed to understand the standard;
- compact human-readable summaries;
- provenance maps that are required to locate evidence.

## Repository-transfer goal

Before OVAL Community transfer, the intended shape is:

- `scap-ng`: compact standards/design/tooling repository;
- `scap-ng-evidence`: reproducible bulk proof and generated datasets;
- existing `vanderpol/scap-ng` history/tag/archive: full R&D provenance.

This split is intended to reduce repository clutter without discarding evidence.
