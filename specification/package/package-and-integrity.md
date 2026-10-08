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

SCAP-NG source MAY use any supported serialization that represents the same
object model. A repository SHOULD use one authoring serialization consistently.

The supported serialization set is defined by the applicable SCAP-NG version
or conformance profile.

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

Authors need direct, readable source references. Scanners need immutable,
validated object lookup independent of source-directory layout. The compiled
package manifest provides runtime resolution and integrity; authors do not
maintain a separate runtime index.

### 5.1 Authoring and compilation

For native 0.3 authoring, each Rule SHALL identify its selected Assessment by
**logical ID**, optionally specifying `expected_version` where multiple
eligible versions exist. The compiler uses the supplied source scope (the
Benchmark and eligible shared content), indexes actual Assessment identities,
and rejects missing, ambiguous, incompatible, wrong-kind, or out-of-scope
references. An author SHALL NOT maintain a separate Policy/Assessment index or
write filesystem traversal paths.

Legacy converted source MAY use relative paths temporarily. The compiler
verifies these within the declared source boundary and replaces them with
logical identities before packaging. Filename and directory placement SHALL
NOT determine semantic identity.

Illustrative source:

```yaml
# rules/SV-257777.rule.yaml
rule:
  id: SV-257777
  assessment_choices:
    automated:
      assessment: rhel9.sv-257777.automated
    manual:
      assessment: rhel9.sv-257777.manual
  default_assessment_choice: automated
```

### 5.2 Compilation output and runtime

A compiled package SHALL contain an authoritative **object-resolution
manifest** that also carries package-integrity metadata. It SHALL map each
packaged logical object identity (and version when required to disambiguate)
to the object's declared type and exact immutable package member. The entry
SHALL include sufficient integrity information, including a content digest,
to detect modification or substitution. Content size SHOULD also be recorded.

The compiler SHALL resolve authored logical references (and transitional
converter source paths) into exact packaged objects and construct the manifest
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

### 5.3 Package identity

The package identity SHOULD be immutable and content-derived from the package
manifest or equivalent integrity material. Results SHOULD reference that
immutable package identity.

Source files may be moved or renamed without changing logical object identity.
Compiled packages resolve their own immutable members through the manifest and
do not depend on the original source layout.

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

## 7. Migration and authoring metadata

Authoring comments and migration evidence are non-semantic.

The compiler SHOULD omit authoring comments from scanner packages. Conversion,
normalization, source-defect, round-trip, and migration-audit evidence SHALL
remain separate from the executable content graph. Such evidence MAY reference
native logical identities for traceability, but executable Benchmark, Rule,
Assessment, and applicability content SHALL NOT depend on it.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Manual Assessment](../assessment/manual-assessment.md) · [Contents](../README.md) · [Next: Results and Evidence →](../results/results.md)

<!-- spec-nav:end -->
