# SCAP-NG 0.4.0 — full 65-stream proposed authoring review

**2026-10-30. DRAFT review only — not an executable/scanner-verified release.**

This is a deterministic, out-of-place authoring projection of the existing
[immutable human-readable v2 source](https://github.com/vanderpol/scap-ng-evidence/releases/tag/v04-human-readable-review-20261030-ab5cddd).
It does **not** claim to be new OVAL content, to convert the five source-only
streams, or to replace the pinned original source and accepted static proofs.

The candidate uses the same bounded Test-wide field-policy transformation as
the [proposed 40-Rule gallery](../examples/v04-proposed-authoring-review/README.md).
The renderer hoists explicit, identical scalar `values_found` /
`values_matching` controls to `require.field_requirement`, retaining genuine
field-level overrides. A flat scalar conjunction is collapsed only when a
single original State is unambiguously source-pinned. Boolean branches, record
counts, absence-only checks, datatypes, and Object selectors are otherwise
preserved.

## Completed local review results

| Check | Result |
| --- | ---: |
| Original streams represented | 65 |
| Streams with native YAML | 60 |
| Source-only streams | 5 |
| Automated Assessments | 6,817 |
| Assessments changed | **5,203** |
| Assessments unchanged | 1,614 |
| Refactored Test field policies | **7,336** |
| Uniquely source-pinned scalar State conjunctions folded | 1,332 |
| Rewrite holds and validation errors | **0** |
| YAML documents validated against 0.4.0 schema | **13,754** |
| Native streams independently compiled | **60 / 60** |

Generated review ZIP: `scap-ng-0.4.0-proposed-authoring-review-65.zip`

SHA-256:

`da559a00f18867be28baa985e3fbeabd7dbeafad0a4e4749b028dd09fb85a65a`

Size: 13,370,627 bytes. The archive's 13,756 entries (13,754 native YAML
files plus the README and exact edit receipt) passed `unzip -t`.

**Publication state:** The new ZIP is retained as a review download; it has
**not** been uploaded to a public GitHub release asset or designated as the
official 0.4.0 release. Do not replace existing published archives based on
this report. Once a publishing environment with evidence-repository asset
access is available, publish the ZIP **immutably** and link it here after
verifying its exact SHA-256.

## Reproduce independently

Start from an extraction of the pinned human-v2 ZIP containing the
`authoring/` and `records/streams/` directories.

```bash
python tools/build_v04_full_proposed_authoring_draft.py \\
  --source-root <extracted-human-v2-root> \\
  --output <new-nonexistent-directory> \\
  --zip-path <new-nonexistent-zip-path>
```

The script refuses to overwrite an existing output, validates each native
document, compiles each scope in isolation, and records original/candidate
Assessment hashes and exact preimages for changed Tests. The output names
and input sorting are deterministic; proof claims are not transferred to the
changed programs.

## Remaining acceptance gates

1. `field_requirement` is still optional in the shipped JSON Schema.
   Proposed mandating, record-member inheritance and canonical style linting
   are tracked in [#264](https://github.com/vanderpol/scap-ng/issues/264).
2. Datatype inference and conflicts remain under
   [#255](https://github.com/vanderpol/scap-ng/issues/255). This pass does not
   remove explicit datatypes.
3. Assessment-root `purpose`, generated logical IDs, source metadata, manual
   coverage and complete Benchmark applicability remain separate work. The
   60 source-derived Benchmark shells retain their `direct-slice` and
   `fixture-platform` / `fixture-applicability` placeholders.
   See [#265](https://github.com/vanderpol/scap-ng/issues/265).
4. Existing original-source proof status and scanner execution claims remain
   independent of this presentation rewrite. No changed program is automatically
   accepted as source-equivalent or scanner-verified.

For reviewer convenience, first inspect the
[40-Rule proposed gallery](../examples/v04-proposed-authoring-review/README.md)
and its before/after links. The 65-stream ZIP is a broad draft acceptance
exercise, not evidence that the language or content has been finalized.
