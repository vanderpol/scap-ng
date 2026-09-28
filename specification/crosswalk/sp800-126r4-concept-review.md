# SP 800-126r4 Concept Review for SCAP-NG

**Status:** informative design cross-check  
**Reference:** NIST SP 800-126 Revision 4, SCAP Version 1.4, June 2026

This document records high-level SCAP 1.4 concepts that SCAP-NG should either
preserve, replace deliberately, or review explicitly.

It is not a requirement to reproduce SCAP 1.4 component architecture.

## Concepts clearly retained in NG

| SCAP 1.4 concept | SCAP-NG direction |
| --- | --- |
| checklist / Benchmark | retained as Benchmark policy container |
| Rule | retained as stable policy requirement |
| Profile | retained, simplified to publisher policy delta |
| Tailoring | retained as external policy modification |
| Value | replaced by typed Parameter + Organizational Input distinction |
| platform applicability | retained, redesigned as explicit Platform Assessment plus applicability conditions |
| automated checking | retained as automated Assessment Methods |
| manual checking | retained as Manual Assessment Methods with a default interaction contract |
| asset identity | retained in normalized result target identity |
| result stream | replaced by normalized NG result package plus consumer projections |
| globally unique/stable identity | retained as stable logical identity separate from revision |
| validation | retained and expanded to schema + semantic validation |
| integrity/signing | retained conceptually; NG wire profile remains under design |

## Concepts deliberately replaced or simplified

| SCAP 1.4 mechanism | SCAP-NG direction |
| --- | --- |
| XCCDF/OVAL/OCIL stovepipes | one policy model plus common Assessment model |
| CPE-only platform machinery | explicit Platform identity bound to an Assessment; external identifiers may still be preserved |
| XCCDF check-system indirection | explicit Rule-to-Assessment relationship |
| OCIL questionnaire hierarchy | procedure-only Manual Assessment by default; optional richer human interaction later |
| XCCDF/OVAL variable export stovepipe | typed Parameters and Assessment input bindings |
| Profile positive-selection snapshots | Benchmark-enabled baseline plus subtractive Profile deltas |
| monolithic XML source data stream | self-contained compiled package of normalized objects |
| ARF component-report nesting | normalized NG run/target/Rule result model |
| embedded historical source definitions in results | immutable package reference plus selected self-describing Rule result metadata |

## SP 800-126r4 concepts requiring explicit NG decisions

The following high-level SCAP concepts remain important completeness checks but
are not yet fully resolved for NG:

- formal product/content conformance profiles;
- formal NG use cases;
- vulnerability-scanning and inventory-specific policy semantics;
- severity/scoring standards and version precedence;
- exact digital-signature/trust profile;
- confidentiality/redaction requirements;
- extension preservation rules in compiled packages;
- remote content/reference policy, if any;
- final result-state vocabulary across automated and manual modes.

## Use-case review

SCAP 1.4 formally defines compliance checking, vulnerability scanning, and
inventory scanning as use cases.

SCAP-NG is currently being designed primarily from compliance-policy and STIG
requirements. The specification SHOULD NOT silently assume that the legacy
three-use-case taxonomy is either mandatory or obsolete.

Before v1.0, the project SHOULD explicitly decide:

1. which use cases are normative in SCAP-NG;
2. whether the same Benchmark/Rule/Assessment model covers all of them;
3. whether vulnerability/inventory content requires different result semantics;
4. whether use-case declaration belongs at package, Benchmark, or Assessment
   scope.

## Packaging/reference review

SCAP 1.4 data streams provide component bundling, reference resolution, reuse,
validation context, and future transport adaptability.

SCAP-NG should preserve those *capabilities* without preserving the XML data
stream architecture.

The current NG direction is:

- human-friendly normalized source objects;
- explicit author-controlled references;
- build-time resolution;
- self-contained compiled packages;
- stable logical identities in compiled form;
- manifest/digest/signature support.

## Result review

SCAP 1.4 uses ARF plus component-specific result documents and includes explicit
target identification.

SCAP-NG should preserve the operational goals while eliminating component
result duplication:

- identify the actual target;
- identify the exact policy/package executed;
- preserve the effective Profile/Tailoring/Input state;
- retain Rule result identity and useful policy metadata;
- distinguish result truth from evidence completeness;
- support compact and rich result projections.

## Security review

SP 800-126r4 highlights confidentiality, malicious content, content integrity,
and the fact that format conformance does not establish the security value of a
checklist.

SCAP-NG should retain those concerns and additionally treat active Assessment
capabilities and policy-data injection boundaries as first-class security
topics.
