# Iteration 002 Four-Anchor Source Review Plan

**Status:** active  
**Scope:** source design only

Iteration 002 keeps four real STIG anchors:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025

The anchors are used to design and review native SCAP-NG source. They are not
being regenerated as complete distributable benchmarks during this phase.

## Why keep all four

The anchors provide two natural reuse pairs:

    RHEL 9 <-> Oracle Linux 9
    Windows 11 <-> Windows Server 2025

They also exercise different mature OVAL families and applicability patterns.

This lets us review:

- shared assessments across related benchmarks;
- benchmark-level applicability;
- rule-level applicability;
- Unix/Linux collectors;
- Windows collectors;
- simple assertions;
- complex variable/data-flow cases;
- manual checks;
- policy-to-assessment bindings.

## Source-selection rule

Only include an example when it teaches us something about the authoring model.

Do not generate hundreds of files for completeness.

For each anchor, select a small set covering:

1. one very simple assessment;
2. one moderately complex assessment;
3. one complex OVAL variable/data-flow case where applicable;
4. benchmark-level applicability;
5. rule-level applicability;
6. at least one assessment shared with its paired benchmark;
7. one case where policy aligns but the technical assessment differs;
8. one manual assessment where useful.

## Working layout

    research/iterations/002/
      examples/
        shared/
          assessments/
          platforms/
        rhel9/
          benchmark.yaml
          policy/
          platforms/
        oracle-linux9/
          benchmark.yaml
          policy/
          platforms/
        windows11/
          benchmark.yaml
          policy/
          platforms/
        windows-server-2025/
          benchmark.yaml
          policy/
          platforms/
      provenance/
      decisions/

Shared technical assessments should live once under `examples/shared/` when
the review establishes exact semantic reuse.

## Native-source rules

- Keep executable source free of XCCDF/OVAL/OCIL runtime references.
- Use OVAL-aligned capability families such as `unix.file`,
  `windows.registry`, and `linux.rpminfo`.
- Treat historical numeric suffixes as an OVAL Board naming decision.
- Applicability uses the same assessment language as compliance checks.
- Platform/CPE names are identifiers, not scanner-side truth.
- Use meaningful local identifiers.
- Prefer concise defaults over repeating obvious mechanics.
- Preserve complex semantics only where the actual assessment requires them.
- Human provenance comments are optional.
- Machine provenance stays outside executable source.

## Explicitly out of scope for now

Until the source model is approved:

- final distribution packages;
- signing;
- package manifests;
- full benchmark regeneration;
- reference scanner implementation;
- broad-corpus generation.

## Design authority during iteration 002

The source format is intentionally open to redesign.

The working approach is:

1. start from the real semantic requirement;
2. preserve OVAL lessons that still matter;
3. remove legacy structure that does not improve clarity or correctness;
4. choose the smallest readable native syntax that remains deterministic;
5. compare simple and complex cases side by side;
6. change the syntax freely while 002 is still a design iteration.

Questions should be escalated only when a choice materially changes semantics,
authoring power, compatibility expectations, or the eventual specification.
Routine syntax and organization decisions should be made within the iteration
and demonstrated with concrete examples.
