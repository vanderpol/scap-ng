# Complete all-65 DRAFT first; independent verification second

**Current download navigation (October 30):** [0.4.0 downloads and Assessment samples](../releases/0.4.0-downloads-and-samples.md) separates the revised original-source DRAFT from the newer normalized 13,754-file editable YAML review package. This document also retains older stage-one DRAFT reproduction instructions; do not mistake them for the final normalized authoring layout.

Current revision authority: [#260 owner tasking](https://github.com/vanderpol/scap-ng/issues/260#issuecomment-6510844015).
The revised candidate builder enables bounded warning-based drafting without
changing strict independent proof. Ledgers now add disjoint `conversion_status`
values and overlapping warning counts while retaining historical `draft_status`
fields for comparison. Exact 4,258 accepted source/authoring/program hash pairs
are preserved. Earlier archives remain immutable. The revised candidate's
download/checksum/cohort recovery ledger is linked from #251/#260; the original
stage-one description below remains historical reproduction evidence.

Owner direction, 2026-10-29, under [#251](https://github.com/vanderpol/scap-ng/issues/251):
publish a complete, reviewable DRAFT before completing proof coverage. Attempt
every automated conversion irrespective of proof availability. Preserve every
original Rule and manual content. Include structurally valid unverified native
authoring with explicit labels; unsupported and invalid cases remain blockers.
Never create a fictional executable Assessment to fill a coverage gap.

## Stage one deliverable

`tools/build_v04_full_draft.py` is an explicitly requested deliverable builder,
not a routine regression. It uses the existing generic converter and all
**existing approved supported mappings** diagnostically. It does not activate
those capabilities in production admission, change mappings/schemas, or alter
the strict verified-upgrade path. Unsupported #255 contracts stay unsupported.

For each of the 65 pinned ZIPs it checks byte count, SHA-256 and Git blob identity,
attempts every OVAL-bearing Rule, validates emitted native authoring, attempts
compilation and checks compiled operands. No independent source reader is
required to admit a structurally valid **unverified DRAFT candidate**. Known
invalid original closures, effectively deprecated Tests and nonstandard sqlext
packages remain explicitly rejected. Original validity not previously checked
is labeled NOT RUN, never inferred from native schema validity.

The deliverable includes:

- An HTML index and one source-review page per benchmark, plus complete JSON/CSV
  Rule ledgers with conversion, validation, proof, compilation and blocker status.
- Exact original ZIPs, every original Rule as inspectable XML, and every original
  component, including manual/OCIL questions, policy metadata, Profiles and CPE.
- Actual candidate native JSON/YAML and diagnostic compiled packages only where
  compilation succeeds. A valid but uncompilable candidate has a compile blocker
  and is not included in an executable package.
- Exact retained-proof authoring/program hashes, original pins, toolchain-input
  hashes, reproduction instructions, environment and artifact checksums.

Original preservation and complete Rule accounting do **not** mean all Rule
policy, applicability or manual methods have been natively translated. The
current native Rule/Benchmark wrappers still describe a primary automated subset.
The preserved originals are the complete review source for fields not translated;
manual content is never replaced by a synthetic automated Assessment.

## DRAFT status meanings

| Status | Meaning |
| --- | --- |
| RETAINED_PUBLISHED_STATIC_PRIMARY_PROOF | Exact pinned original and unchanged previously proved authoring/program hashes; no runtime claim |
| CONVERTED_SCHEMA_VALID_UNVERIFIED | Native structural checks passed; original validity/proof may be unrun; consult compile_status |
| BLOCKED_EXPLICIT | Unsupported, excluded or invalid conversion; original retained, no fabricated native execution |
| MANUAL_OCIL_ONLY_PRESERVED | Complete original manual content preserved; native manual execution not claimed |

`compile_status` distinguishes actual checked compilation from a compile blocker.
The `UNVERIFIED-diagnostic-candidates.scapng` filename does not promote its
contents into accepted production packages. Readers should download the review
archive and open `index.html`; all original and native links are local to it.

## Reproduction and boundaries

Use the manifest's exact toolchain and input digests. The baseline is a complete
snapshot of the previously published proof identities/hashes; known exclusions
come from recorded original-source validation. A mismatch or lost baseline is a
fatal deliverable error, not an opportunity to relabel an old proof.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/build_v04_full_draft.py \
  --source-pins SOURCE_PINS.json --inputs ORIGINAL_ZIPS \
  --baseline PUBLISHED_PROOF_BASELINE.json --known-invalid KNOWN_INVALID.json \
  --output NEW_UNIQUE_DRAFT_DIRECTORY --workers 3 \
  --acknowledge-full-corpus-deliverable
```

Preserve the earlier frozen all-65 archive unchanged. This command creates a new
unique deliverable revision; it is not a request to rerun old frozen generation.
The focused regression module uses only bounded fixture views and never the 65
sources. No normal workflow may invoke this builder as a routine corpus test.

## Stage two and final release

Continue original XSD/Schematron/reference/deprecation checks and independent
source/native/compiled/package comparisons after DRAFT publication, in bounded
batches. Retain all existing proofs and hashes, report unresolved cases and
publish separate verified checkpoints. Do not retrofit an unverified label into
a verified claim without the required evidence.

The strict `verify_v04_direct_scope.accept_source` path and final verified-release
validation requirements are unchanged. Runtime equivalence, complete policy/CPE/
manual migration, toolchain reproducibility, signing/trust when claimed, and
human acceptance remain distinct gates. DRAFT publication does not resolve
#255, authorize schema changes, or expand into scanner/editor/0.5 work.
