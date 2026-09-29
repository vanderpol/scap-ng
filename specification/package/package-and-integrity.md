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

## 5. Package manifest and object resolution

A compiled package SHOULD contain one manifest that provides both package
integrity metadata and deterministic logical-object resolution.

The manifest SHOULD map each stable logical object identity to:

- object type;
- package path;
- content digest;
- content size.

This mapping is distinct from Benchmark membership. For example, a Benchmark
Rule list identifies which Rule IDs belong to the Benchmark, while the package
manifest identifies where those Rule objects are located in the immutable
package.

A processor SHOULD be able to resolve packaged objects without relying on
filename conventions or directory scanning.

Package integrity SHOULD be computable from the canonical manifest and the
digests it contains.

The package identity SHOULD be immutable and content-derived, for example from
the canonical manifest digest.

Results SHOULD reference the immutable package identity rather than duplicate
the complete source package.

Iteration 003 previously experimented with separate `index.json` and
`manifest.json` files. Because both repeated package path and digest
information, that design was consolidated into one `manifest.json`.
This experimental manifest shape is evidence for package design and is not yet
the final normative serialization.

## 6. Signing

SCAP-NG packages SHOULD support digital signatures over the canonical package
manifest or equivalent complete logical package representation.

The final signature format, trust model, countersigning model, and certificate
requirements remain under design.

## 7. Historical authoring comments

Comments used for migration provenance or author guidance are non-semantic.

The compiler SHOULD omit authoring comments from canonical scanner packages.

A separate conversion report MAY preserve complete machine-readable legacy
lineage.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Manual Assessment](../assessment/manual-assessment.md) · [Contents](../README.md) · [Next: Results and Evidence →](../results/results.md)

<!-- spec-nav:end -->
