# SCAP-NG result-model bake-off from real OVAL Results

Status: **research / non-normative**

This directory contains pseudo-SCAP-NG result examples derived from real SCC
OVAL Results supplied for design analysis. The source corpus intentionally
includes largely out-of-box Windows Server 2025 and RHEL 9 systems so the
results contain many failures and useful edge cases.

The OVAL Results files are used as a **semantic evidence source**, not as a
serialization template.

## Corpus observations

The supplied ZIPs contain 16 OVAL Results files spanning Windows Server 2025,
Windows Updates, IIS, Defender, .NET, Edge, Windows Firewall, RHEL 9, nginx and
Firefox.

Observed result states include:

- true;
- false;
- unknown;
- not evaluated;
- not applicable.

Observed collected-Object flags include:

- complete;
- does not exist;
- not applicable.

The larger RHEL 9 and Windows Server 2025 files contain hundreds of Tests,
Objects, States and collected Items and expose the cross-section daisy-chain
required to explain an ordinary result in OVAL.

## Result-layout principle under test

One Assessment invocation produces one self-contained Assessment Result file.

A canonical Assessment Result should keep reusable data once locally while
making each Test easy to understand:

- Assessment identity/result/completeness;
- evaluated logical expression;
- Test results;
- local Object/collection-execution records;
- local collected/imported Items;
- State evaluation information where needed for explanation;
- Variable bindings;
- deterministic diagnostics/evidence.

Tests may reference local Object/Item/State records instead of embedding
duplicate copies. A compact decisive explanation should still make the common
"why did this pass/fail?" path obvious.

This deliberately differs from OVAL Results + System Characteristics, where
Definition results, Test results, authored Tests/Objects/States, collected
Objects and Items are stored in separate sections that must be joined by IDs.

## Worked examples

- `rhel9-kdump.assessment-result.yaml`:
  one failed compliance Assessment with three systemd property Tests. The
  source OVAL result requires joins across Definition Result, Test Results,
  authored Tests/Objects/States, collected Objects, and System Characteristics
  Items. The NG sketch stores each observation once and links it directly to
  its Test explanation.

- `windows2025-tpm.assessment-result.yaml`:
  three WMI Tests fail their existence requirement because TPM query Objects
  report `does not exist`. The example preserves the distinction between
  Object collection status, Item status, per-Test result, and overall
  Assessment result.

## Important unresolved items

These examples are not final schemas. They are intended to pressure-test:

1. whether Object/State nodes require stable authored IDs in native Assessment
   source;
2. exact typed Item/entity representation;
3. how much State comparison detail belongs in every result versus debug mode;
4. imported Item provenance for future shared collection execution;
5. evidence caps and incomplete population semantics;
6. whether Test results should reference local normalized nodes or embed small
   explanatory projections;
7. canonical execution IDs and file naming;
8. how the Benchmark Result links one Rule outcome to one Assessment Result
   invocation.

The result model should preserve OVAL semantics where useful without preserving
OVAL's historical stovepiped serialization.
