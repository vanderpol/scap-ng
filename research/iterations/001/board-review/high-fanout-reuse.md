# High-Fan-Out Exact Assessment Reuse

The full pinned NIWC corpus survey demonstrates that exact assessment reuse is
not limited to pairs of closely related STIGs.

The survey covers 65 individual signed benchmark ZIPs, 8,892 XCCDF rules, and
7,084 supported automated assessment instances.

## Fan-out distribution

Cross-benchmark exact semantic groups are distributed as follows:

| Benchmarks sharing one exact assessment | Exact reuse groups |
| ---: | ---: |
| 2 | 899 |
| 3 | 265 |
| 4 | 220 |
| 5 | 210 |
| 6 | 66 |
| 7 | 22 |
| 8 | 8 |
| 9 | 3 |
| 11 | 1 |
| 12 | 6 |
| 13 | 1 |

There are **1,701** cross-benchmark exact-reuse groups in total.

## Thirteen-benchmark Linux example

One exact assessment enforcing a maximum of ten concurrent sessions is shared
across **13 published Linux STIG benchmarks**:

- Amazon Linux 2023;
- Ubuntu 18.04, 20.04, 22.04, and 24.04;
- Oracle Linux 7, 8, and 9;
- RHEL 7, 8, and 9;
- SLES 12 and 15.

The policy titles vary by distribution and version, but the complete normalized
OVAL technical semantics are identical.

Under an explicit reuse model, this is one technical assessment maintained once
and bound to 13 independent policy rules rather than 13 independently
maintained copies.

Several password-complexity assessments show similar exact reuse across
**12 published Linux benchmarks**, including minimum length and required
upper-case, lower-case, numeric, and special characters.

## Six-benchmark Windows examples

A single exact Secure Boot assessment is shared across:

- Windows 10;
- Windows 11;
- Windows Server 2016;
- Windows Server 2019;
- Windows Server 2022;
- Windows Server 2025.

The same six-benchmark exact reuse pattern is present for multiple Windows
controls, including:

- PowerShell script block logging;
- PowerShell transcription;
- command-line data in process creation events;
- multiple advanced audit-policy subcategories;
- machine inactivity lock;
- required legal notice.

This is useful evidence that client/server and release-to-release assessment
reuse is not theoretical.

## Architectural implication

The SCAP-NG source model should be evaluated against high fan-out, not only
two-rule demonstrations.

For an assessment shared by N policy rules:

- combined-rule reuse needs one immutable shared technical base plus N policy
  overlays;
- split policy/assessment/binding needs one shared assessment plus N explicit
  bindings;
- Ansible-inspired reuse needs one shared technical assessment plus N explicit
  bindings/typed variable sets.

All three can express the reuse. The Board should compare how clearly each
model exposes policy identity, assessment version, change impact, provenance,
and the set of affected rules when N becomes 6, 12, or 13.

## Maintenance implication

A shared assessment with fan-out 13 avoids 12 duplicate technical definitions
for that one semantic check. A single reviewed correction or collector
migration can therefore replace up to 12 repeated technical updates while all
13 policy identities remain independently reviewable.

This is the kind of multiplier represented in the full-corpus result of
**3,671 duplicate assessment-definition maintenance units avoided**.
