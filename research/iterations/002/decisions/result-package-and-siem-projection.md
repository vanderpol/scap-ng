# SCAP-NG Result Package and SIEM Projection

**Status:** working design decision  
**Iteration:** 002  
**Scope:** canonical scan results, per-Rule result context, aggregate counters, target identity, and SIEM projection

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Motivation

Legacy SCAP result formats often embed or repeat very large portions of source
XCCDF/OVAL content. That makes results self-contained but heavy.

At the opposite extreme, emitting only Rule IDs and outcomes makes results
difficult to use outside the scanner because downstream systems may not have
the Benchmark/STIG content needed to resolve titles, severity, revisions, or
other policy context.

Operational consumers such as Splunk and Elastic also benefit from independent
events that contain enough target and Rule context to be useful when indexed
without external joins.

SCAP-NG should support both goals without requiring one serialization to serve
every use case.

## Canonical result package

The canonical SCAP-NG result artifact SHOULD be a normalized result package.

Run-, target-, Benchmark-, and scanner-level metadata SHOULD be represented once
per run.

Per-Rule results SHOULD carry the Rule-specific data needed to understand the
finding without embedding the complete Benchmark or Assessment source.

Illustrative shape:

    results:
      run:
        id: ...
        started: ...
        completed: ...

      scanner:
        name: ...
        version: ...

      target:
        id:
          type: smbios_uuid
          value: ...
        hostname: ...
        addresses: [...]
        platform: ...

      benchmark:
        id: disa.windows11.stig
        version: V2R10
        profile: MAC-1_Classified

      summary:
        ...

      rule_results:
        - rule: ...
          outcome: ...
          title: ...
          severity: ...
          message: ...
          ...

The exact schema remains provisional.

## Target identity

Hostnames and IP addresses are useful attributes but SHOULD NOT be assumed to
be globally unique or stable target identities.

A result package SHOULD support one or more typed target identifiers.

Examples include:

- SMBIOS UUID;
- cloud instance ID;
- hardware serial number;
- scanner-managed asset ID;
- organization-managed asset UUID.

Where available and trustworthy, SMBIOS UUID is a strong candidate for
physical/virtual machine correlation because it is generally more stable than
hostname or IP address.

The result model SHOULD retain hostname and all relevant addresses as
descriptive/correlation attributes even when another identifier is primary.

A target identifier SHOULD record its type so consumers do not need to infer
semantics from a generic string.

## Aggregate summary counters

A result package SHOULD contain precomputed aggregate counters.

Downstream systems SHALL NOT be required to recompute common scan-level
statistics from every Rule result merely to display or filter a scan summary.

At minimum, summary counters SHOULD consider:

- total Rules;
- passed;
- failed;
- not applicable;
- not checked / not evaluated;
- error;
- informational or equivalent non-scored result categories, if supported.

Example:

    summary:
      rules:
        total: 257
        pass: 90
        fail: 154
        not_applicable: 3
        not_checked: 10
        error: 0

## Severity aggregates

The result summary SHOULD also contain aggregate Rule-result counts by severity
when the Benchmark defines severity.

Core SCAP-NG SHOULD use generic severity identities rather than hard-code one
publisher's terminology.

Example:

    summary:
      failures_by_severity:
        high: 13
        medium: 133
        low: 8

Publisher-specific aliases MAY also be retained or projected.

For a DISA STIG, a presentation/export layer MAY expose:

    publisher_summary:
      disa:
        cat_i_failures: 13
        cat_ii_failures: 133
        cat_iii_failures: 8

or map the generic values deterministically:

    high   -> CAT I
    medium -> CAT II
    low    -> CAT III

The exact DISA mapping SHALL follow the publisher's declared severity semantics
rather than scanner-specific assumptions.

SCAP-NG core SHALL NOT require CAT I / CAT II / CAT III labels for non-DISA
content.

## Aggregate dimensions

Where operationally useful, a result package MAY provide additional precomputed
aggregates such as:

- outcome by severity;
- automated versus manual Assessment counts;
- applicable versus not-applicable counts;
- tailored versus publisher-baseline results;
- results requiring organizational input;
- failure-reason category counts.

These SHOULD remain derived summary data and SHALL NOT replace the individual
Rule results.

## Per-Rule self-description

Each Rule result SHOULD be sufficiently self-describing for common downstream
analysis without requiring the consumer to possess the original Benchmark.

A per-Rule result SHOULD consider including:

- stable Rule identity;
- publisher external identifiers needed by common consumers;
- Rule title;
- severity;
- outcome;
- concise deterministic result message;
- structured failure reason when applicable;
- bounded concrete evidence when applicable;
- Assessment mode/type;
- tailoring/input provenance where relevant.

The complete discussion, remediation text, manual check procedure, and
Assessment implementation SHOULD NOT automatically be duplicated into every
Rule result.

## SIEM projection

The canonical normalized package need not be JSONL.

A SIEM exporter MAY deliberately denormalize canonical results into independent
events.

A JSONL projection may emit:

1. one scan-summary event containing run, target, Benchmark, score, and
   precomputed aggregate counters; followed by
2. one Rule-result event per Rule containing enough repeated run/target/Rule
   context to be independently indexed.

That redundancy is acceptable in a transport/projection optimized for Splunk,
Elastic, or similar event stores.

The canonical result model SHOULD make this projection deterministic and simple.

## Design principle

SCAP-NG SHOULD distinguish:

    canonical result semantics
              ↓
      normalized result package
              ↓
     consumer-specific projection
       /          |          \
    JSON       JSONL/SIEM    STIG Viewer

Consumer-specific denormalization SHALL NOT dictate the canonical source/result
object model.

## Open questions

The following remain open pending additional operational result review:

- exact minimum Rule metadata that must be embedded in canonical results;
- whether score is normative or a derived publisher/profile-specific value;
- target identifier precedence and confidence/provenance;
- final outcome vocabulary;
- final severity vocabulary and extension model;
- whether summary aggregates are mandatory or SHOULD-level requirements;
- how much Benchmark/profile metadata belongs in every standalone individual
  .result artifact versus only in a complete .results package.


## Signed result package

SCAP-NG SHOULD make cryptographic signing of scan results a normal, simple
implementation path rather than an optional XML-signature feature that is
rarely exercised.

The preferred design reuses the same manifest-and-signature model as signed
Benchmark packages:

1. serialize the canonical Benchmark Result and each referenced detailed
   Assessment Result using the required canonical representation;
2. compute a SHA-256 digest for every normative result member;
3. record those members and digests in one result manifest;
4. sign the canonical result manifest once;
5. verify the manifest signature and every listed member digest before trusting
   the result package.

Conceptual package:

    META-INF/
      result-manifest.json
      signature.cose

    benchmark-result.json
    assessment-results/
      <execution-id>.json
      ...

The signature covers the complete logical result set without depending on ZIP
compression bytes, file ordering, timestamps in an archive container, or
incidental transport representation.

### Simplicity and common implementation

Content packages and result packages SHOULD use the same signature envelope,
algorithm registry, trust-store model, certificate/key identification rules,
and verification API wherever practical.

A vendor SHOULD NOT need to implement XML Digital Signature, a separate result
signature scheme, and a package signature scheme merely to support SCAP-NG.

The initial project direction is one detached/sidecar signature over a canonical
manifest rather than embedded signatures scattered through result objects.

### What is signed

The result manifest SHALL integrity-bind, directly or by member digest, at
minimum:

- the Benchmark Result;
- every detailed Assessment Result referenced by the Benchmark Result;
- the exact Benchmark/package identity and digest used for execution;
- the result schema/specification versions needed to interpret the package.

The manifest SHOULD also carry stable run identity and creation/completion
timestamps so the signed object can be correlated without parsing every member.

### Signer identity and verification

A signed result SHOULD make the following visible to consumers:

- signing key or certificate identity;
- signature algorithm;
- signature creation time when provided by the signing mechanism;
- trust-chain or trust-anchor information needed by the deployment model;
- verification status produced by a verifier;
- the exact result-manifest digest that was verified.

Signer identity is distinct from scanner/product identity. A deployment MAY use
the same credential for both, but the data model SHALL NOT assume that the
software vendor is the party signing an operational scan result.

### Tamper evidence

Any modification to a signed Benchmark Result, Rule Result, Assessment Result,
or other normative member SHALL cause digest/signature verification to fail.

A consumer SHALL NOT present a modified result as still signed merely because
the original signature file remains present.

Non-normative transport/projection artifacts such as a generated SIEM JSONL
export MAY be unsigned derivatives. When produced from a signed canonical
result, they SHOULD carry a reference to the source signed-result package and
its verified manifest digest.

### Optional signing versus verifiability

The format SHOULD permit unsigned result packages for low-assurance/testing
workflows, but every conforming implementation SHOULD be able to verify signed
result packages.

High-assurance conformance profiles MAY require scanners to sign results.

This keeps the base format easy to implement while giving DoD/enterprise
deployments a straightforward path to require provenance and tamper evidence.

### Open cryptographic profile question

The existing package prototype uses a `signature.cose` placeholder. The final
cryptographic profile should select one small, widely implementable signature
format and algorithm set for both content and result packages rather than
supporting multiple interchangeable signature frameworks.

