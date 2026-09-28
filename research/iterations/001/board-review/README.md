# OVAL Board Review Package — SCAP-NG Iteration 001

**Status:** Internal review package; not a draft specification  
**Evidence basis:** pinned published NIWC SCAP 1.4 content plus the separate OVAL Self-Assertion conformance corpus

## Purpose

This package gives reviewers concrete evidence for choosing a SCAP-NG authoring
and source-organization direction without relying on hand-written toy examples.

The same published benchmark semantics are rendered in all three candidate YAML
forms:

1. combined rule with shared technical rule bases and policy overlays;
2. split policy / assessment / binding;
3. Ansible-inspired authoring with no Ansible runtime dependency.

All three originate from the same canonical SCAP-NG semantic model.

## Four production anchors

| Benchmark | XCCDF rules | Supported automated assessments | Manual/external | SCAP-NG blockers |
| --- | ---: | ---: | ---: | ---: |
| RHEL 9 | 445 | 418 | 27 | 0 |
| Oracle Linux 9 | 448 | 408 | 40 | 0 |
| Windows 11 | 257 | 245 | 11 | 1 rule plus applicability |
| Windows Server 2025 | 291 | 260 | 30 | 1 rule |

All four benchmarks pass the same three-format conversion and renderer
equivalence checks. Windows source-remediation blockers remain explicit rather
than being silently carried into SCAP-NG.

## Measured exact assessment reuse

Across the four anchors:

- automated assessment instances: **1,331**
- unique exact technical assessments: **804**
- duplicated assessment definitions avoidable through exact reuse: **527**
- exact maintenance-unit reduction: **39.59%**
- cross-benchmark exact-reuse groups: **525**

The result is based on normalized complete OVAL assessment semantics, not titles,
CCI identifiers, or shared test-family names.

### Linux pair

RHEL 9 and Oracle Linux 9 contain **826** supported automated assessment
instances in total.

- Oracle Linux 9 assessments with an exact reusable RHEL 9 assessment:
  **368 / 408 = 90.2%**
- RHEL 9 assessments with an exact reusable Oracle Linux 9 assessment:
  **368 / 418 = 88.04%**
- duplicate assessment definitions avoidable across the pair: **369**

### Windows pair

Windows 11 and Windows Server 2025 contain **505** supported automated
assessment instances in total.

- Windows 11 assessments with an exact reusable Server 2025 assessment:
  **158 / 245 = 64.49%**
- Server 2025 assessments with an exact reusable Windows 11 assessment:
  **158 / 260 = 60.77%**
- duplicate assessment definitions avoidable across the pair: **158**

## Rule mapping evidence

Two independent signals are retained:

- identical normalized XCCDF Check Text;
- equivalent complete normalized OVAL semantics.

Across the four anchors:

- rule pairs aligned by either signal: **529**
- exact OVAL-equivalent groups: **525**
- identical-Check-Text groups: **8**
- pairs supported by both signals: **7**
- Check-Text-only pairs: **1**
- OVAL-equivalence-only pairs: **521**

The Check-Text-only case is important: RHEL 9 and Oracle Linux 9 contain a
"library files must be owned by root" pair with identical Check Text but
different OVAL filename/filter semantics. The rules align as policy, but their
automation is **not** counted as exact reuse.

## Representative reuse examples

The generated reuse views intentionally retain six exact groups rather than all
525, while the numeric report covers the complete four-benchmark set.

Linux examples:

- hardware random number generator service — simple service-state reuse;
- systemd-journald enabled — simple service-state reuse;
- xattr audit syscall coverage — complex reuse with 24 tests and 17 variables.

Windows examples:

- Secure Boot — simple platform/security-state reuse;
- account lockout duration — multi-test policy reuse;
- DoW Root CA certificates — larger certificate assessment with 15 collected objects.

Each example is rendered in all three candidate YAML designs from the same
measured semantic reuse group.

## Windows migration-readiness evidence

The Windows 11 benchmark contains one rule using deprecated Windows
`user_test`; the same deprecated family is also used by a CPE applicability
definition. The converter reports `user_sid55_test` as the supported
replacement.

Windows Server 2025 contains one ordinary-rule deprecated-test blocker, while
its applicability assessment converts successfully.

This demonstrates the intended SCAP-NG migration boundary: obsolete source
semantics are repaired in SCAP 1.4 first rather than becoming permanent
requirements on every future SCAP-NG scanner.

## What reviewers should compare

The reuse set is intentionally identical across the formats. Reviewers can
therefore focus on the actual architectural tradeoffs:

- clarity when reading one complete rule;
- ease of seeing policy-to-assessment relationships;
- simplicity of cross-STIG assessment reuse;
- provenance/versioning of shared automation;
- safety and transparency of overlays;
- parameter passing;
- Git review/change impact;
- packaging/build complexity;
- scanner implementation complexity;
- ease of migration from existing SCAP 1.4 content.

No architecture should receive credit merely because its example set was
written differently or allowed more reuse than another.

## Supporting evidence

- `../four-anchor-reuse-methodology.md` — mapping/reuse/cost methodology.
- `../generated/four-anchor-reuse/assessment-reuse.json` — complete machine-readable reuse analysis.
- `../generated/four-anchor-reuse/reuse-views/` — six exact reuse groups rendered in all three YAML designs.
- `../generated/windows11-full-conversion/` — complete Windows 11 conversion evidence and source-remediation blockers.
- `../generated/rhel9-full-conversion/` — complete RHEL 9 conversion evidence.
- `../scap14-public-corpus-conversion-requirement.md` — required migration gates before specification finalization.
