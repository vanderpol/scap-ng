# SCAP-NG package and manifest decision

Status: **iteration-003 pre-alpha design decision**

## Decision

SCAP-NG packages SHALL be defined first as a **manifest-authoritative logical
object graph**. The archive/container is a transport serialization of that graph
and SHALL NOT define object identity, references, or execution semantics.

For the current design, the preferred container is **ZIP** with the
`.scapng` extension.

TAR remains a permitted research/alternative serialization, but there is not
currently enough benefit to make TAR the normative/default SCAP-NG package
container.

This decision is intentionally separable from the manifest design. A future
container change SHALL NOT require changing Benchmark, Rule, Assessment,
applicability, Profile/Tailoring, or result semantics.

## Why ZIP remains the preferred default

ZIP provides several practical advantages for the expected SCAP-NG package:

- direct per-member lookup through the central directory;
- per-member compression instead of whole-archive compression;
- mature read/write support on Windows, Linux, macOS, Java, .NET, Python, Go,
  Rust and common enterprise tooling;
- easy inspection by ordinary users without requiring a specialized SCAP tool;
- simple extraction of one object without decompressing all preceding content;
- deterministic output is achievable by fixing timestamps, permissions,
  member ordering and compression settings;
- detached signature material and a manifest fit naturally as ordinary members;
- the current compiler already proves deterministic member construction,
  manifest digesting and CMS signing/verification.

The recent Windows extraction problem was caused by **long generated directory
names**, not by ZIP itself. SCAP-NG generators now use short stable Benchmark
bases for generated/intermediate paths while preserving long upstream artifact
names only in provenance.

## TAR comparison

### TAR strengths

TAR is simple and naturally stream-oriented. It is attractive when a producer
or consumer wants to process a package sequentially without random seeks.
Uncompressed TAR also has straightforward deterministic byte layout when all
header metadata is controlled.

A TAR stream could be useful for very large packages, constrained streaming
transports, or pipe-oriented Unix workflows.

### TAR weaknesses for the SCAP-NG default

Plain TAR provides no compression. In practice it is normally combined with
gzip, zstd or another compressor. Whole-stream compression creates important
tradeoffs for SCAP-NG:

- arbitrary member lookup generally requires reading/decompressing earlier
  archive data unless a separate index or seekable compression profile is
  introduced;
- ordinary Windows desktop support is less uniform than ZIP;
- `.tar.gz`, `.tar.zst`, etc. create a second standards choice: TAR alone no
  longer completely defines the package encoding;
- deterministic TAR requires defining header details such as uid/gid, uname,
  gname, mode, mtime, format variant and extension-record behavior;
- PAX/GNU extension behavior and long-name handling increase interoperability
  requirements;
- signing only the manifest remains simple, but verifying individual members on
  demand is less convenient when the entire payload is one compressed stream;
- using TAR does not simplify the Benchmark/Rule/Assessment binding model.

For SCAP-NG's expected content size and scanner use, random member access and
cross-platform inspection are more useful than TAR's sequential-stream
advantage.

## Container-independent package contract

The package SHALL have exactly one scanner-authoritative manifest.

The manifest SHALL identify:

- package format and manifest schema version;
- package/Benchmark identity and version;
- one or more entrypoints if multi-Benchmark packages are later supported;
- every packaged logical object;
- each object's object type;
- each object's logical ID and version where applicable;
- the immutable package-member path;
- exact byte size;
- content digest and digest algorithm;
- schema/capability requirements needed to consume the object;
- integrity policy for missing, substituted and unexpected members;
- package signature metadata;
- build provenance that does not become semantic identity.

Member paths are storage locations only. They SHALL NOT be semantic identity and
SHALL NOT be inferred from logical IDs by scanners.

## Runtime resolution model

Compilation changes references from **authoring locations** into **logical
package references**.

### Authoring

A Rule may contain:

```yaml
assessment_choices:
  automated:
    assessment: ../assessments/automated/example.assessment.yaml
```

That relative path is an authoring concern. The compiler SHALL resolve the
target, validate its object type and logical identity, and package the
Assessment.

### Compiled Rule

The packaged Rule SHALL reference the Assessment's logical ID, for example:

```json
{
  "assessment_choices": {
    "automated": {
      "assessment": "ng.example.assessment"
    }
  }
}
```

The scanner SHALL resolve `ng.example.assessment` through the manifest object
index. It SHALL NOT construct a filename such as
`objects/assessments/ng.example.assessment.json`.

### Benchmark → Rule

Benchmark Rule membership SHALL likewise be logical. The Benchmark identifies
Rule IDs; the manifest resolves those IDs to packaged Rule objects.

The Benchmark object itself is identified by the manifest entrypoint. A scanner
therefore performs:

```text
package
  -> manifest
  -> entrypoint Benchmark ID
  -> manifest object record
  -> Benchmark bytes
  -> Rule IDs from Benchmark membership
  -> manifest object records
  -> Rule bytes
  -> selected Assessment ID
  -> manifest object record
  -> Assessment bytes
```

### Applicability

The Benchmark SHALL reference a logical applicability-catalog ID in the
compiled package.

Applicability conditions SHALL reference logical Assessment IDs. Those
Assessment IDs are resolved through the same manifest object index as Rule
Assessment selections.

There SHALL NOT be a separate hidden applicability lookup mechanism.

### Profiles and Tailoring

Publisher Profiles embedded in the Benchmark operate on Rule logical IDs.

If Tailoring is distributed inside a package in the future, its references
SHALL also resolve logical Benchmark/Rule/Parameter/Assessment-selection
identities through explicit manifest/package bindings. Tailoring SHALL NOT
identify an Assessment implementation by member path.

## Check/Assessment selection

A Rule owns its named Assessment selections and its default selection.

The manifest does **not** choose which Assessment runs. It only proves which
logical objects are present and where their immutable bytes live.

Selection occurs in the policy layer:

1. resolve effective Benchmark/Profile/Tailoring Rule selection;
2. resolve the Rule's effective named Assessment choice;
3. obtain the logical Assessment ID from the compiled Rule;
4. resolve that ID through the manifest;
5. load/validate/execute the Assessment.

This preserves separation between:

- policy selection;
- Assessment implementation identity;
- package storage.

The manifest SHALL NOT duplicate the Rule's complete selector/default policy
logic. Duplicating it would create two authorities that could disagree.

The compiler MAY include derived indexes or dependency summaries for efficiency,
but they SHALL be verifiable projections of packaged objects and SHALL NOT
override the native policy object.

## Manifest object index

A conceptual object record is:

```json
{
  "ng.example.assessment": {
    "type": "assessment",
    "version": 1,
    "path": "o/a/7f3c.json",
    "sha256": "...",
    "size": 1234
  }
}
```

The physical path MAY remain human-readable or become shorter/content-oriented.
Either way, consumers use the manifest record.

Short member paths are preferred for portability. The package SHALL avoid
repeating verbose Benchmark/source names through nested member paths.

## Package member layout

The current readable layout is acceptable:

```text
META-INF/
  manifest.json
  signature.p7s
  signer.pem
objects/
  benchmark.json
  applicability.json
  rules/
  assessments/
```

However, this layout is **not normative resolution logic**.

A future implementation may shorten members, for example:

```text
m/manifest.json
o/b.json
o/r/<short>.json
o/a/<short>.json
sig/signature.p7s
```

without changing logical object references.

For signed packages, the signer's certificate/chain may be carried in a
dedicated signature area. Test-only self-signed certificate naming SHALL NOT
become the final normative layout.

## Integrity and signing implications

The manifest SHALL cryptographically bind all executable/policy package
members by digest.

The package signature SHALL bind the canonical manifest bytes. This creates the
chain:

```text
signature
  -> canonical manifest
  -> logical object inventory + member paths + digests + sizes
  -> exact packaged object bytes
```

The verifier SHALL reject:

- a missing manifest-listed member;
- digest or size mismatch;
- duplicate physical members that create ambiguous lookup;
- duplicate logical IDs;
- wrong object type for a logical reference;
- unresolved logical references;
- unexpected members when the package integrity policy says to reject them;
- invalid/untrusted signature according to the selected trust policy.

Archive metadata such as ZIP timestamps SHALL NOT be part of object semantic
identity. Reproducibility rules SHALL nevertheless canonicalize container
metadata so identical unsigned inputs can produce byte-identical packages.

## Source provenance in the manifest

Authoring source paths are useful build provenance but SHALL NOT participate in
runtime object resolution or immutable logical identity.

The current experimental compiler places a `source` path on each manifest
object. That is useful for debugging but can make otherwise equivalent packages
differ after repository normalization.

Final design SHOULD separate:

- **integrity/runtime object index** — deterministic logical object/type/path/
  digest/size/version data;
- **optional build provenance** — source repository paths, source revisions,
  normalizer lineage and compiler environment.

Build provenance MAY be stored in a separate manifest section or optional
non-semantic member so source-layout changes do not unnecessarily change
package identity.

## ZIP profile requirements if finalized

If ZIP remains the final normative container, the specification SHALL define a
small deterministic ZIP profile rather than saying only "make a ZIP":

- no encrypted members;
- no duplicate member names;
- UTF-8 names;
- forward-slash member separators;
- relative member names only;
- no `..`, absolute paths, drive prefixes or path traversal;
- short portable member names;
- fixed timestamp or a specified reproducible timestamp policy;
- fixed file mode/attributes;
- deterministic member ordering;
- a specified compression method baseline;
- scanners SHALL support stored and the selected baseline compression method;
- archive comments and unnecessary extra fields SHOULD be absent;
- ZIP64 support SHALL be explicitly decided rather than accidental.

The package verifier SHALL validate the archive profile before trusting the
manifest.

## TAR research status

A TAR prototype MAY still be maintained to ensure the manifest is genuinely
container-independent. It would be useful as a conformance test:

> package the same canonical objects and manifest into ZIP and TAR; after
> container parsing, both SHALL expose the same logical object graph and
> manifest semantics.

This is a useful portability test, but it is not a reason to require scanners
to support two production package formats.

## Current conclusion

Use **one default production container**, not ZIP plus TAR as co-equal mandatory
formats.

For iteration 003, that container remains deterministic ZIP/`.scapng`.

Keep the manifest and object-reference contract deliberately independent of ZIP
so the standards body can replace or add a container later without redesigning
the Assessment or policy languages.

The next compiler work should therefore focus on:

1. making logical-ID manifest resolution fully authoritative;
2. removing source-layout dependence from immutable package identity;
3. validating the complete logical reference graph at compile and verify time;
4. defining the deterministic ZIP profile;
5. shortening package member paths;
6. adding a TAR serialization prototype only as a container-independence
   regression, not as a second normative format.
