# Assessment References, Reuse, and Source Organization

**Status:** working design decision  
**Iteration:** 002  
**Scope:** native SCAP-NG Rule-to-Assessment binding, shared Assessment naming, repository organization, and generated reuse views

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Authoritative relationship

A Rule policy object SHALL explicitly reference the Assessment Method used to
evaluate that Rule.

Example:

    rule:
      id: RHEL-09-255040
      assessment: ../../shared/linux/sshd/root-login-disabled.yaml

The Rule-to-Assessment reference is the authoritative source relationship.

An Assessment Method SHALL NOT maintain an authoritative hand-edited `used_by`
list. Doing so would duplicate relationship state and create synchronization
risk.

The same principle applies to Platform and reusable applicability assessments:
the policy object that consumes an Assessment owns the forward reference.

## Generated reverse usage index

SCAP-NG authoring/build tooling SHOULD derive the reverse relationship
automatically from authoritative forward references.

At minimum, tooling SHOULD be able to answer:

- which Rules consume an Assessment;
- which Benchmarks transitively consume an Assessment;
- how many Rules and Benchmarks depend on an Assessment;
- which shared Assessments have the largest change/test blast radius;
- which benchmark-specific Assessments may be candidates for promotion into a
  shared library;
- which duplicate or near-duplicate Assessments may warrant review.

A generated machine-readable view SHOULD be produced, for example:

    generated/assessment-usage.json

A human-readable view MAY also be produced, for example:

    generated/assessment-usage.md

These files are derived artifacts and SHALL NOT be treated as authoritative
policy source.

Example derived view:

    linux.sshd.root-login-disabled:
      consumers:
        - benchmark: disa.rhel9.stig
          rule: RHEL-09-255040
        - benchmark: disa.oracle-linux9.stig
          rule: OL09-00-000000

The build system MAY include equivalent reverse-reference information in a
compiled package or development report when useful, but source authors SHALL
not be required to maintain it manually.

## Assessment naming

A reusable Assessment SHOULD be named for the semantic fact or condition it
establishes, rather than:

- the first Benchmark that used it;
- the first Rule that used it;
- the collector or implementation mechanism;
- an opaque migration identifier.

Examples of preferred reusable logical identities:

    linux.sshd.root-login-disabled
    linux.auditd.service-enabled
    linux.crypto.fips-enabled
    unix.file.owner-root
    windows.account.guest-disabled

A benchmark-specific Assessment MAY initially use a Rule-oriented identity when
reuse has not yet been established.

Example:

    rhel9.RHEL-09-255040

When later analysis proves that the Assessment is semantically reusable, the
content SHOULD be promoted to a shared semantic identity and source location.

Promotion SHALL occur only when equivalence has been established. Similar
syntax or similar intent alone is not sufficient evidence that two Assessments
are interchangeable.

## Source organization

Shared Assessment files SHOULD use a hierarchical organization that communicates
scope and purpose instead of a large flat directory.

The preferred pattern is:

    assessments/
      shared/
        <platform-or-family>/
          <application-or-subsystem>/
            <function>.yaml

Representative examples:

    assessments/shared/linux/sshd/root-login-disabled.yaml
    assessments/shared/linux/auditd/service-enabled.yaml
    assessments/shared/linux/crypto/fips-enabled.yaml
    assessments/shared/unix/file/owner-root.yaml
    assessments/shared/windows/account/guest-disabled.yaml
    assessments/shared/windows/registry/password-policy.yaml

Benchmark-specific Assessments SHOULD remain under a clearly scoped location
until reuse is demonstrated, for example:

    assessments/
      rhel9/
        RHEL-09-255040.yaml
      oracle-linux9/
        OL09-00-000000.yaml

The directory hierarchy is an authoring and maintenance aid. File paths SHALL
NOT define the stable logical identity of an Assessment.

Moving an Assessment file SHALL NOT, by itself, create a new Assessment
identity.

## Capability versus Assessment identity

A capability name describes a scanner/collector primitive, for example:

    unix.file
    linux.rpminfo
    windows.registry

A reusable Assessment describes a semantic condition established using one or
more capabilities, for example:

    unix.file.owner-root
    linux.sshd.root-login-disabled

Assessment identities SHOULD NOT merely repeat the underlying capability name.

## Exact duplicate promotion

When two or more Assessment Methods have been shown to have identical complete
technical semantics after removing source identifiers, provenance, comments,
metadata, and version-only noise, they SHOULD be represented by one shared
Assessment definition with multiple policy bindings.

For automated SCAP 1.4 migration, exact equivalence SHALL be established from
the complete normalized Assessment graph. Matching capability names, matching
Rule titles, matching Check Text, or similar-looking YAML alone is not
sufficient.

Automatic exact-reuse promotion MAY therefore:

- replace duplicate automated Assessment definitions with one shared Assessment;
- preserve each Benchmark's Rule and policy identity;
- preserve each Rule's check-selector identities;
- allow multiple selectors to resolve to the same shared Assessment when that
  matches source semantics; and
- generate reverse consumer/provenance information from the bindings.

Automatic exact-reuse promotion SHALL NOT alter the Rule's policy meaning,
applicability, selector behavior, or result semantics.

Assessments that have the same normalized semantic **shape** only after
abstracting literal values are parameterization candidates, not proven exact
duplicates. Such candidates SHALL NOT be automatically shared until the
parameterization contract has been reviewed and shown to preserve policy and
Assessment semantics.

## Reuse discovery and promotion workflow

A practical development workflow is:

1. create a Rule-specific Assessment when only one consumer is known;
2. add additional Rule references when exact reuse is established;
3. promote the Assessment to a shared semantic name/location when reuse becomes
   meaningful;
4. regenerate the reverse usage index;
5. use the generated consumer list to review change impact and regression-test
   coverage.

Tooling SHOULD make this promotion inexpensive and SHOULD update source
references deterministically.

## Build and validation behavior

The SCAP-NG build process SHALL resolve every Assessment source reference and
verify that it identifies a valid Assessment object.

The build SHOULD fail when:

- a referenced Assessment file is missing;
- the referenced file is not an Assessment object;
- an Assessment identity collides with another distinct object;
- a source reference resolves ambiguously.

The build SHOULD generate reverse-consumer information after successful
resolution.

## Design rationale

This model preserves one authoritative relationship:

    Rule -> Assessment

while providing the equally valuable maintenance view:

    Assessment -> all consuming Rules and Benchmarks

without duplicating hand-maintained state.

It also prevents the maintenance problems associated with large flat
Assessment directories and makes shared implementation visibly reusable across
Benchmark families.

## Future specification direction

A future SCAP-NG specification SHOULD standardize:

- explicit author-controlled policy-to-Assessment references;
- stable logical Assessment identity independent of source path;
- requirements for deterministic reference resolution;
- validation of Assessment references.

The exact repository directory layout and generated reverse-index presentation
SHOULD remain authoring-tool conventions rather than runtime requirements,
unless interoperability experience demonstrates a need to standardize them.
