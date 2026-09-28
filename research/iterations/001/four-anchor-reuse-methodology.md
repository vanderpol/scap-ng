# Four-Anchor Rule Mapping and Assessment Reuse Methodology

**Status:** Iteration 001 internal research method  
**Scope:** RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025  
**Evidence source:** pinned NIWC Atlantic published SCAP 1.4 corpus

## Purpose

This experiment measures how much automation can be shared across real published
STIG benchmarks and renders that same reuse in each SCAP-NG candidate authoring
form.

It deliberately separates **policy rule alignment** from **assessment reuse**.
Two policy rules may correspond even when their automated implementations are
not identical.

## Benchmark pairs

The primary comparisons are:

- RHEL 9 <-> Oracle Linux 9
- Windows 11 <-> Windows Server 2025

The analyzer may also discover exact technical reuse across any of the four
benchmarks.

## Rule alignment

A pair of rules is treated as aligned when either of these independent signals
is present.

### 1. Same normalized Check Text

XCCDF Check Text is normalized only for presentation whitespace. Wording,
punctuation, commands, paths, thresholds, and other substantive content remain
significant.

Identical normalized Check Text is evidence that two policy rules describe the
same checking procedure.

It does **not** by itself prove that their automated implementations are
equivalent.

### 2. Equivalent complete OVAL semantics

The entire OVAL assessment graph is normalized independent of publisher-local
OVAL identifiers and provenance. Comparison includes the effective definition
criteria, tests, objects, states, variables, collection semantics, predicates,
existence/check operators, and referenced logic.

Using the same OVAL test family is not sufficient. Two rules that both contain
a Windows registry test, for example, are not considered equivalent unless the
complete normalized technical assessment is equivalent.

Equivalent full OVAL semantics is evidence for both rule alignment and exact
technical assessment reuse.

## Reuse classes

### Exact reuse

Two or more rules have the same normalized technical assessment semantics.

These groups may be rendered automatically as one shared assessment because no
technical behavior is intentionally changed.

### Parameterization candidate

Two or more normalized assessments have the same semantic shape after literal
values are abstracted.

This is an **upper-bound candidate classification**, not a reuse claim. A
candidate must be reviewed to establish that the differing literals are valid
typed parameters and that parameterization does not alter policy meaning,
applicability, error handling, or result semantics.

## Source-remediation blockers

Rules that depend on effectively deprecated OVAL tests remain visible in
mapping reports but are not reusable SCAP-NG automated assessments.

The SCAP 1.4 source must first be updated to supported OVAL semantics. This
keeps obsolete collectors out of the SCAP-NG runtime while making the
migration debt explicit to content authors.

## Rendering exact reuse in the candidate designs

Every measured exact-reuse group is rendered three ways from the same
canonical semantics:

1. **Combined rule** — one shared technical rule base plus policy-specific
   overlays. The overlay may carry policy identity/content but may not mutate
   the shared assessment logic.
2. **Split policy / assessment / binding** — one shared assessment plus
   explicit bindings from each policy rule.
3. **Ansible-inspired** — one shared Ansible-like assessment plus explicit
   bindings/variables. There is no Ansible runtime dependency.

The goal is not to give one design a reuse advantage. Each design must
represent the same measured reuse set so reviewers can compare authoring,
review, provenance, and maintenance ergonomics fairly.

## Maintenance and cost measurements

The primary economic measurements are observable maintenance units:

- total automated assessment instances;
- unique exact assessments;
- duplicated assessment definitions avoided;
- cross-benchmark reuse-group count;
- reuse fan-out;
- exact maintenance-unit reduction percentage;
- source bytes required by each reuse representation.

No universal labor rate or review-time assumption is embedded.

Organizations may apply their own values using:

    one-time migration/review hours avoided
      = duplicate assessment definitions avoided
        * average review hours per assessment

    annual maintenance hours avoided
      = duplicate assessment definitions avoided
        * average assessment change events per year
        * average review/test hours per change

    annual labor cost avoided
      = annual maintenance hours avoided
        * loaded hourly labor rate

This permits a defensible cost estimate without presenting speculative dollar
values as measured evidence.

## Evidence interpretation

The four-anchor result is a measured demonstration, not a projection of the
entire SCAP ecosystem.

After the mapping/fingerprinting method is stable, the same analyzer can run
across every individual benchmark in the pinned NIWC Current corpus. That
larger run is the appropriate basis for an at-scale reuse estimate.
