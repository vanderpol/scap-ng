# Source, Compilation, Packaging, and Integrity

**Status:** pre-alpha normative draft

## 1. Authoring versus execution

SCAP-NG SHALL distinguish human authoring source from scanner-facing compiled
content.

A compiler/build process SHALL:

1. parse source;
2. resolve explicit references;
3. validate schemas;
4. validate semantic constraints;
5. resolve Profiles, Tailoring, Platform, applicability, Parameters, and
   Assessment bindings as appropriate;
6. normalize objects;
7. emit canonical scanner-facing content.

## 2. Source serialization

SCAP-NG source MAY be authored using more than one supported serialization when
those serializations represent the same object model.

The current design permits JSON-compatible YAML and JSON as candidate source
serializations.

The final mandatory publisher serialization set remains under design.

A repository SHOULD use one authoring serialization consistently.

## 3. Canonical compiled form

The scanner-facing compiled representation SHOULD use canonical JSON.

Compiled content SHALL use stable logical identities rather than source file
paths as semantic references.

Authoring paths SHALL be resolved before execution.

## 4. Self-contained package

A scanner-facing Benchmark package SHALL be self-contained for the policy and
Assessment content required to execute that Benchmark.

Execution SHALL NOT depend on mutable external Assessment content whose version
can diverge from the policy package after compilation.

Reusable Assessments MAY be embedded once and referenced by stable identity
within the package.

## 5. Explicit source references versus compiled manifest resolution

**Two different operations serve different users.** Authors need a direct and
human-readable way to follow Benchmark → Rule → selected Assessment. Scanners
need immutable, validated object lookup and package integrity without depending
on the author's directory layout. The compiled package manifest serves this
*runtime* need; it is **not** an additional author-maintained Assessment index.

### 5.1 Authoring and compilation

For the current file-backed authoring model, each Rule SHALL expose its named
Assessment selections using explicit relative paths to Assessment YAML files.
Those paths SHALL resolve relative to the **referring Rule file**, not to the
process working directory or an implicitly chosen repository root.

The compiler SHALL normalize paths, enforce the declared source boundary,
verify referenced files exist and contain Assessment objects, and read their
actual logical identities and versions. It SHALL reject missing, ambiguous,
incompatible, or boundary-escaping links. Neither a filename nor a containing
directory convention SHALL determine an Assessment's semantic identity.
Authors SHALL NOT be required to maintain a separate Policy file or Assessment
lookup index.

Illustrative source (field names remain pre-alpha):

```yaml
# rules/SV-257777.rule.yaml
rule:
  id: SV-257777
  assessment_choices:
    automated:
      assessment: ../assessments/automated/SV-257777.automated.assessment.yaml
    manual:
      assessment: ../assessments/manual/SV-257777.manual.assessment.yaml
  default_assessment_choice: automated
```

### 5.2 Compilation output and runtime

A compiled package SHALL contain an authoritative **object-resolution
manifest** that also carries package-integrity metadata. It SHALL map each
packaged logical object identity (and version when required to disambiguate)
to the object's declared type and exact immutable package member. The entry
SHALL include sufficient integrity information, including a content digest,
to detect modification or substitution. Content size SHOULD also be recorded.

The compiler SHALL resolve Rule-owned source paths and named Assessment
selections into logical object references and construct the manifest
**automatically**. An author SHALL NOT create or synchronize a separate
Assessment index by hand.

On loading the package, a scanner SHALL validate applicable package integrity
and use the manifest to resolve logical Rule and Assessment references to exact
packaged members. A scanner SHALL NOT discover objects by guessing filenames
from IDs, searching directories, or reopening relative authoring paths.
Missing references, conflicting identities, wrong types and digest mismatches
SHALL cause a defined validation failure rather than fallback resolution.

The manifest lookup is distinct from Benchmark membership: the Benchmark's
Rule list says **which Rules belong** to the Benchmark; the manifest says
**where referenced packaged Rule and Assessment objects live** and how to
verify them.

Multiple named Rule selections MAY resolve to the same Assessment identity.
The manifest need only bind that Assessment once; selected-choice identity
SHALL remain available for results and provenance.

### 5.3 Why this is useful

The separation permits a source Assessment file to be moved or renamed
without changing its logical identity; authoring references must be updated,
but existing immutable packages continue to resolve their own contents.
Packages need not preserve source directory layouts, and result records can
refer to immutable package and Assessment identities instead of copying the
complete source.

The package identity SHOULD be immutable and content-derived (for example,
from a canonical manifest digest), and results SHOULD reference that immutable
identity. Package-signature specifics and the final manifest serialization
remain under design; the deterministic resolution and integrity requirements
above are the intended behavior.

Iteration 003 previously experimented with separate `index.json` and
`manifest.json` files. Because both repeated package path and digest
information, that design was consolidated into one `manifest.json`.
The current experimental shape is implementation evidence, **not** an
already-ratified final JSON schema.

## 6. Signing

SCAP-NG packages SHOULD support digital signatures over the canonical package
manifest or equivalent complete logical package representation.

The final signature format, trust model, countersigning model, and certificate
requirements remain under design.


### Result-package signing relationship

Benchmark content-package signing and Benchmark Result-package signing use the
same architectural pattern: an immutable manifest integrity-binds package
members and a signature authenticates that manifest.

The two signatures serve different purposes and SHALL remain distinct:

- a **Benchmark package signature** authenticates the policy/Assessment content
  that was distributed for execution;
- a **Benchmark Result package signature** authenticates the completed result
  artifact produced for a particular run/target.

A Benchmark Result SHOULD reference the immutable identity/digest of the
Benchmark package that was executed. A signed result therefore provides a
cryptographic chain from the completed result to the exact signed/identified
content package without embedding the entire source Benchmark in the result.

Implementations SHOULD reuse the same signature envelope, key-identification,
algorithm, and trust-validation machinery for both package types where
practical. SCAP-NG SHOULD NOT define two unrelated cryptographic frameworks for
content and results.

### Migration of legacy XML signatures

SCAP 1.4 source content may contain XML Digital Signature elements on OVAL,
XCCDF, or related source nodes. Those signatures authenticate the **legacy XML
representation**, not the semantically converted SCAP-NG representation.

A converter that supports signature-aware migration SHALL verify a legacy XML
signature against the original, unmodified source bytes/node set **before**
normalization or conversion. Verification results SHOULD record, in migration
evidence as available:

- source artifact identity and cryptographic digest;
- signed source node/document identity;
- verification status;
- signer/key or certificate identity;
- signature and digest algorithms;
- trust-chain status separately from cryptographic signature validity;
- verification time and verifier implementation/version.

A valid legacy XML signature SHALL NOT be copied into native SCAP-NG executable
content as though it authenticates the converted object. Conversion changes the
representation and may change object boundaries, so the original signature no
longer covers the resulting package members.

The compiled SCAP-NG package SHALL establish its own integrity and, when signed,
its own package signature over the canonical NG package manifest or equivalent
complete logical representation. Migration evidence MAY link that new package
identity to the verified legacy source digest/signature result.

If a source signature is present but cryptographic verification fails, a
signature-aware converter SHALL fail closed or quarantine the affected source;
it SHALL NOT silently convert the content while claiming authenticated legacy
provenance. Lack of a legacy signature is not itself a migration failure unless
a deployment policy requires signed source.

Legacy source-signature verification, SCAP-NG content-package signing, and
SCAP-NG result-package signing are therefore three distinct trust events. A
successful event at one layer SHALL NOT be treated as proof of another.

## 7. Historical authoring comments

Comments used for migration provenance or author guidance are non-semantic.

The compiler SHOULD omit authoring comments from canonical scanner packages.

A separate conversion report MAY preserve complete machine-readable legacy
lineage.

Conversion, normalization, source-defect, round-trip, and migration-audit
evidence SHALL remain logically separate from the native executable content
graph. Such evidence MAY reference native logical identities for traceability,
but Benchmark, Rule, Assessment, Collection, and applicability objects SHALL
NOT require that evidence in order to resolve or execute.

The compiler SHALL NOT include detailed migration or repository-normalization
evidence in a scanner package by default. If a future specification defines an
optional provenance/audit package member, it SHALL be separately typed and
SHALL NOT alter Assessment truth, collection semantics, or runtime reference
resolution.

Migration, conversion, and repository-normalization evidence SHALL remain outside the native scanner-facing content graph. Such evidence MAY reference native logical identities for traceability, but native Benchmark, Rule, Assessment, Collection, and applicability objects SHALL NOT depend on conversion evidence to execute. A compiler SHALL NOT include migration diagnostics, source-defect reports, round-trip traces, or normalization lineage in a scanner package by default. Any future standardized provenance package member SHALL be explicitly typed and separable from Assessment evaluation semantics.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Manual Assessment](../assessment/manual-assessment.md) · [Contents](../README.md) · [Next: Results and Evidence →](../results/results.md)

<!-- spec-nav:end -->


## Candidate: schema-contract propagation into scanner packages

**Status: pre-schema research placeholder.**

The Benchmark is the authority for the authoring schema contract. A compiler
SHOULD validate the full closed reference graph using that contract, then stamp
its *resolved* NG content schema identifier/version into the compiled package
manifest. The manifest's own `format_version` describes the **manifest layout**;
it is not interchangeable with `ng_schema_version` (the SCAP-NG content model).

Iteration-003 uses `ng_schema_version: null` in both the Benchmark and its
review package manifest because no published NG assessment/JSON Schema is
available. Such packages remain research artifacts and SHALL NOT be accepted
by a production scanner as version-compatible merely because their JSON is
parseable. An implementation SHALL reject unsupported or unresolved schema
versions and conflicting nested declarations. A normalized scanner package
SHALL NOT rely on unspecified or silently inherited execution semantics.
