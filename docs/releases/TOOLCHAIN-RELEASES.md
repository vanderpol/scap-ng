# Versioned SCAP-NG toolchain releases

Current preparation instructions: [0.4.0 candidate guide](0.4.0-rc.md). Find the [complete 0.4.0 downloads and sample-Assessment index](0.4.0-downloads-and-samples.md), including the separate normalized editable library and maintenance toolchain.
The signed-SCAP entry point is `tools/v04_direct_converter.py`; independent
source proof and package verification are separate entry points. The candidate
includes a hash-pinned dependency lock and published matching offline wheels.
See [license inventory](0.4.0-LICENSE-INVENTORY.md). Descriptions of the shared
0.3-derived leaf converter below refer to that narrower retained tool, not to
the newer direct converter's coverage. No final release/tag before owner approval.

This is the release-process contract for **tools and their documentation**,
separate from releases of authoring samples and compiled `.scapng` content.
The [maintenance process](../../MAINTAINING.md) continues to govern review,
version promotion and issue-linked changes.

## One development source, historical reproducibility

- `main` is the only actively maintained converter/compiler/schema source tree.
  Version-neutral OVAL parsing, dependency resolution and semantic comparison
  are shared libraries, not new implementations for each NG revision.
- `0.4.0` is the active native conversion target. The `0.3.0` converter and
  round-trip code remain valuable conversion infrastructure, but producing new
  0.3 content is not a routine development target. Do not remove historical
  modules until corresponding 0.4 regression coverage is demonstrated.
- Exact historical toolchains are retained under immutable Git refs and
  versioned release assets. A `vX.Y.Z` release is an immutable snapshot,
  not a maintained release branch. Prior releases must never be rebuilt in
  place from moving `main` or overwritten with newer scripts.
- Short-lived branches are permitted for bounded, isolated research, under
  [branch-management rules](../../BRANCH-MANAGEMENT.md). Accepted work is
  integrated into `main`; no long-lived parallel version source trees.

## Required source toolchain contents

Every release archive must contain the exact tagged, committed versions of:

1. Full normative `specification/`, including migration, packaging, results,
   security and conformance rules.
2. Complete, self-contained `schema/vX.Y.Z/` and all needed registries and
   capability contracts.
3. Developer implementation guides, authoring examples and operator commands.
   Schemas validate structure; they are not substitutes for semantic guidance.
4. SCAP 1.4/OVAL converter, SCAP-NG compiler, validators, signature/integrity
   verifier, and any reusable libraries actually imported by those tools.
5. Focused and representative regression/conformance fixtures, known expected
   failures, pinned sources, and precise validation instructions.
6. Dependency lock or exact environment bill of materials, tool versions,
   license notices, source commit/tag, checksums and manifest.

The release should provide a readable **entry-point index** and one command
to verify archive integrity. The machine-readable file inventory must identify
every included file with SHA-256 and size. No dependency on expiring GitHub
Actions artifacts, live mutable `main` URLs or implicit local working state.

For the current 0.4 source snapshot, the required entry points include the
[shared OVAL converter](../../tools/scap_converter_core.py),
[native bundle compiler](../../tools/v04_native_bundle_compiler.py) and
[developer runbook](../developer/CONVERTER-COMPILER-RUNBOOK.md). The converter
currently accepts a **source-proven subset** of OVAL through mature 0.3
lowering and native 0.4 projection. See the current
[converter coverage audit](../developer/CONVERTER-COMPILER-RUNBOOK.md) for
exact accepted constructs and blocked definitions. Packaging a source
snapshot cannot upgrade partial conversion coverage into a full migration
claim.

## Archive builder and gates

`tools/build_versioned_toolchain.py` creates a deterministic ZIP from the
*committed Git tree* at an exact ref, with a `TOOLCHAIN-MANIFEST.json` covering
every tracked file. Building from a commit rather than a working directory
excludes uncommitted edits and keeps the source, specification, schemas, guides,
tests and release metadata on the same SHA.

For the current development checkout (a **candidate snapshot**, not a release):

```bash
python tools/build_versioned_toolchain.py --repo . --version 0.4.0 \
  --ref HEAD --output-dir work/toolchain
```

For a frozen release, use the exact final tag and require a version match:

```bash
python tools/build_versioned_toolchain.py --repo . --version 0.4.0 \
  --ref v0.4.0 --require-tag --output-dir work/toolchain
```

The existing 0.3.0 checkpoints use **descriptive version tags**, not a plain
`v0.3.0` final release tag. For example, the actual tag
`v0.3.0-verified-authoring-and-bundles-38422154466` identifies a preserved
historical source tree. To reconstruct a complete, unchanged source snapshot
from that tag using the current archival packager:

```bash
python tools/build_versioned_toolchain.py --repo . --version 0.3.0 \
  --ref v0.3.0-verified-authoring-and-bundles-38422154466 \
  --historical --require-tag --output-dir work/historical-toolchain
```

The `--historical` mode requires a real, version-matched descriptive Git tag
and preserves only what existed at the time. It deliberately does **not**
inject modern implementation guides or 0.4 tools into old source. This
reconstructs historical *source*, not necessarily the exact previously
published 0.3 ZIP, its dependency environment or executable behavior.

Any downloaded ZIP can be independently checked without a Git checkout using
`python tools/build_versioned_toolchain.py --verify PATH_TO_TOOLCHAIN.zip`.
Its companion `SHA256SUMS.txt` verifies the complete archive bytes.

This source-archive gate **does not** certify that all tools run correctly:
before publishing a version as complete, a separate release workflow must
also demonstrate the following, with issue-linked logs and pinned inputs:

- Executable commands from a freshly extracted archive in a clean environment.
- Fully pinned dependencies and a verified offline/repeatable install plan.
- SCAP 1.4 source → version-correct native authoring → `.scapng` compile →
  independent bundle verification, including negative/deprecated cases.
- Exact schema/specification/guide/examples correspondence; no references to
  another NG version as normative definitions.
- Historical OVAL regression retention and explicit semantic gaps, with
  source-corpus conversion distinguished from scanner execution parity.
- Publisher signing and external trust policy only when the release claims a
  signed/publisher-authenticated artifact.

The 0.4.0 pre-alpha work has **not yet satisfied** those final gates. Historical
0.3 release assets and tags remain preserved; do not represent them as newly
verified under this process until their reproduction has been checked.
