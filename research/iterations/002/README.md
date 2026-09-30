# SCAP-NG Research Iteration 002

**Status:** active native-source design iteration

Iteration 001 is the fidelity/migration research archive. Iteration 002 starts
from the lessons learned there and focuses on a clean, concise, OVAL-aligned
native SCAP-NG authoring model suitable for review by existing SCAP/OVAL
content authors.

## Primary objective

Design source files that are:

- small enough to understand quickly;
- expressive enough to preserve SCAP 1.4/OVAL semantics;
- familiar to experienced OVAL authors;
- free of XCCDF/OVAL/OCIL runtime dependencies;
- explicit about applicability, reuse, and error semantics;
- suitable for later deterministic up-conversion from SCAP 1.4.

## Ground rules

1. **Reuse OVAL's platform-family taxonomy.**
   The default NG capability namespace is the OVAL family namespace plus the
   OVAL test basename.

   Examples with unversioned OVAL names map naturally:

       unix.file
       windows.registry
       linux.rpminfo
       solaris.package

   Historical suffixes such as `53`, `54`, `55`, and `511` remain an
   explicit OVAL Board naming decision. Until that decision, conversion
   prototypes preserve the supported source basename rather than silently
   rebasing it.

   Do not invent a parallel taxonomy without a demonstrated semantic reason.

2. **Preserve family boundaries that OVAL learned through operational use.**
   A Windows file and a Unix file are not the same data model merely because
   both concern files.

3. **Simplify authoring structure, not collection semantics.**
   NG does not need to reproduce OVAL's XML definition/test/object/state
   layering when a smaller native form can express the same behavior exactly.

4. **Applicability uses the full assessment language.**
   Any NG assessment capability may be used to determine applicability.
   Content authors define applicability; scanners do not provide an opinionated
   platform oracle.

5. **Legacy standards are provenance, not runtime dependencies.**
   XCCDF, OVAL, OCIL, CPE language, source IDs, namespaces, and hrefs may be
   retained in migration provenance but are not required for native execution.

6. **Simple rules must stay simple.**
   Complexity belongs only where the underlying assessment really requires it.

7. **OVAL experience is design evidence.**
   OVAL is old, but its collector families, defaults, edge cases, and platform
   distinctions reflect years of deployed content. Reuse those lessons
   intentionally.

8. **Profiles describe differences, not snapshots.**
   Benchmark membership enables Rules by default. Native Profile Rule selection
   is subtractive only and serializes only actual disable deltas. See
   `decisions/profile-rule-selection.md`.

## Working areas

- `design-principles.md` — normative direction for this iteration.
- `examples/` — native source examples, including complete benchmark-layer
  conversions for the four anchor STIGs.
- `decisions/` — design decisions as they stabilize.
- `provenance/` — migration/source linkage for review examples only.
- `schema-creation-research.md` — research-only schema strategy and Board-review boundary; no schema approved or created yet.

Nothing enters iteration 002 merely because a converter can generate it.
Every example should be understandable and defensible as potential native
SCAP-NG source.

## Source-only checkpoint

Iteration 002 remains limited to native source-language design.

The project owner has explicitly expanded this checkpoint to include complete
**XCCDF benchmark/policy-layer conversions** of the four anchor STIGs so that
Benchmark, Rule identity, Profile, Group, Parameter, platform, and applicability
design can be reviewed against realistic full content.

During this checkpoint:

- do not build final SCAP-NG distribution packages;
- do not add signing/release work;
- do not build the reference scanner;
- do not convert compliance Assessment Methods merely to complete the anchor
  benchmarks;
- do convert the complete XCCDF benchmark layer for RHEL 9, Oracle Linux 9,
  Windows 11, and Windows Server 2025;
- preserve required platform and rule applicability information, while
  deferring the executable NG implementation of those conditions until the
  assessment-language work;
- use the complete anchor conversions to expose unnecessary duplication and
  validate canonical native-source rules;
- do not run broader corpus conversions merely to increase coverage.

The current goal remains agreement on what authors should write, not production
of the final distributable form.


## Source-style five-rule examples

Current source-layout review examples:

- `examples/source/rhel9/` — five RHEL 9 Rules with policy, Manual Assessments,
  lossless Automated Assessments, and Platform Assessments.
- `examples/source/windows11/` — five Windows 11 Rules with policy, Manual
  Assessments, lossless Automated Assessments, Platform Assessment, and
  applicability catalog/Assessments.

These trees are intended to show how the current split policy/assessment model
looks as a coherent authoring source layout. They are design-review examples,
not frozen schema.


## Current implementation checkpoint

The 2026-09-28 reconciliation of current design decisions against reused
migration tooling is recorded in
[`2026-09-28-design-reconciliation.md`](2026-09-28-design-reconciliation.md).

That checkpoint is the guard against treating iteration-001 or earlier
iteration-002 generated behavior as authoritative when it conflicts with the
current split policy/assessment architecture, lossless-conversion requirement,
check-selector semantics, result/evidence model, or authoring decisions.

## Medium-range backlog

- [Content-authoring prototype](BACKLOG_CONTENT_AUTHORING_PROTOTYPE.md) — author workflow prototype, scheduled after effective-default auditing and substantial semantic round-trip verification; not part of the current validation milestone.
