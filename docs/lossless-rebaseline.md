# Lossless repository rebaseline

Status: preservation and navigation changes; **no payload deletion, directory relocation or Git history rewrite**. Provenance: Evidence/Audit of owner directions, 2026-10-02.

## Baseline and verification

The baseline is commit `9751ef0e5ae43ab728876969ff59dad538a101f0`, containing 34,242 tracked paths. The inventory records each path, file mode and Git blob ID, plus its audited role and classification basis. This covers the complete tracked Git tree; it does not claim to archive untracked files, all ChatGPT transcripts, GitHub Discussions/reactions, or expired Actions artifacts.

The preservation workflow creates `refs/tags/pre-rebaseline-2026-10-02` at that exact commit and fails if an existing tag points elsewhere. Git tags can be deleted by an authorized maintainer; preserve the tag during transfer and keep an independent backup. The inventory is a verification record, not a replacement for the files.

Current cleanup changes navigation, status records and historical workflow triggers. Existing iteration-001/002 file bytes must match baseline Git blobs. Every baseline path must still exist. Current helper code and data at historical-looking locations remain explicitly accounted for. Changes to maintained instructions or workflows are recoverable from the baseline, and intentional changes remain visible in the commit diff.

From the checkout root:

```sh
python -m pip install PyYAML==6.0.3
python tools/audit_repository_layout.py --check
```

To rebuild the inventory and static dependency report:

```sh
python tools/audit_repository_layout.py --output work/repository-audit
```

The analysis follows Python imports and literal CI script paths. Dynamic imports, data paths, external consumers and scripts invoked through generated commands require review. A missing static reference is never permission to delete a file.

## Independent backup before any future removal

Use a full Git clone, including tags, and retain the backup outside the repository being reduced. These commands are suitable for Git on Windows as well as Unix; choose a writable backup directory first:

```sh
git fetch --tags origin
git bundle create pre-rebaseline-2026-10-02.bundle pre-rebaseline-2026-10-02
git bundle verify pre-rebaseline-2026-10-02.bundle
git archive --format=zip --output=pre-rebaseline-2026-10-02.zip pre-rebaseline-2026-10-02
```

The bundle retains the referenced history; the ZIP retains the exact tracked tree without Git history. Run them from a full clone, not a shallow checkout. Extract and compare the ZIP against the baseline inventory; clone the bundle into a clean directory and compare its tree. Record archive SHA-256, byte size, baseline commit, retained paths, storage location and a successful restoration check. An untested export or temporary Actions artifact is not a durable backup.

## Later physical restructuring or removal

1. Freeze a new before-change commit and retain its ref and independent verified archive.
2. Reconcile every lesson, decision and Board question. Keep source-to-current links and original feedback verbatim.
3. Inspect imports, literal paths, workflow triggers, data references, fixtures, licenses and external links. Move dependencies with a documented relocation map and temporary compatibility entry points where needed.
4. Build an explicit candidate removal manifest. Each path needs its role, original blob ID, archive destination, dependency review and replacement/evidence retention.
5. Restore the archived candidate set into a clean checkout and verify every byte/mode. Run affected current and historical reproduction checks. Record failures rather than masking them.
6. Remove payloads only after that evidence is reviewable and the owner authorizes the concrete removal set. Removing generated files from main does not shrink prior Git history.
7. Treat a fresh reduced-history OVAL Community repository as a separate transfer/release decision. Retain this repository/verified archive and provenance links. Do not force-push rewritten history or transfer ownership under this cleanup authorization.

The new visitor layout is a front door into one maintained authority, with historical payloads indexed in place. Future promotion to top-level `design/`, `examples/` and `evidence/` can be performed after dependency relocation is verified; copying two competing “current” designs is not the rebaseline method.
