# Ansible-inspired RHEL 9 authoring research

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**
>
> Nothing in this directory changes the SCAP-NG 0.2.0 or 0.3.0 language,
> schemas, converter requirements, or Board-review baseline. The examples here
> are deliberately speculative and exist only to test whether a substantially
> simpler human authoring layer is feasible on real production content.

## Research question

Can the complete RHEL 9 STIG be represented accurately in a substantially
simpler, Ansible-inspired authoring language while preserving a rigorous typed
semantic model underneath?

The hypothesis being tested is that authors should normally read a check
top-to-bottom as:

```
collect something
expect something about it
combine checks if needed
```

rather than defining and cross-referencing OVAL-like Objects, States,
Variables, Tests, and Definition composition unless those abstractions provide
real authoring value.

## Guardrails

- Source semantics come from pinned NIWC SCAP 1.4 content, not from the
  speculative syntax.
- Existing faithful conversion/semantic IR remains the oracle.
- Inlining is an authoring convenience, not permission to change collection,
  existence, quantifier, datatype, error/status, or evidence semantics.
- Named/reusable components remain allowed where reuse is real.
- `shellcommand` is a residual strategy for command-oriented checks, not a
  universal replacement for typed collectors.
- File-system enumeration, remote/local filesystem policy, evidence capping,
  and similar scanner-aware behavior should remain native where appropriate.
- Manual checks are reviewed individually; higher automation percentage is not
  a goal if the check requires human judgment.
- No schema files outside this research directory SHALL be modified by this
  experiment.

## Production basis

Primary benchmark:

`Current/U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip`

Pinned NIWC revision:

`8c8e5dff860af6b1290ee9273a282db24278f8d5`

The broader eight-package OVAL census is documented in
[`../authoring-language-08/OVAL-USAGE-CENSUS-2026-10-06.md`](../authoring-language-08/OVAL-USAGE-CENSUS-2026-10-06.md).

## Research phases

1. Build a stratified RHEL 9 sample that includes simple, multi-Test,
   dataflow-heavy, existing shellcommand, and manual Rules.
2. Render real Rules side-by-side as current converted NG and speculative
   Ansible-inspired authoring.
3. For every simplification, document the exact semantic IR it must compile to.
4. Refine the speculative vocabulary only when multiple real Rules justify it.
5. Attempt a whole-RHEL-9 classification:
   - simple native;
   - composed native;
   - advanced structured;
   - better as shellcommand;
   - legitimate manual;
   - content redesign required.
6. Separately review all currently manual RHEL 9 Rules for safe automation,
   including shellcommand candidates.
7. Report actual coverage and unresolved semantics. Do not promote this syntax
   without DISA content-developer and OVAL Board requirements review.

## Success criteria

The experiment succeeds if it can answer, with real production evidence:

- what percentage of RHEL 9 can use simple local `collect / expect` authoring;
- what percentage needs explicit composition;
- what percentage genuinely needs richer dataflow;
- what percentage is clearer as a controlled shell command;
- which manual checks can safely become automated;
- which checks remain legitimately manual;
- how much author-visible structure, cross-reference count, and YAML size are
  reduced without changing semantics.

A high conversion percentage alone is not success. Human readability and
semantic fidelity are both required.


## Current checkpoint artifacts

- [RHEL 9 feasibility checkpoint](RHEL9-FEASIBILITY-CHECKPOINT.md) — provisional
  whole-benchmark classification of the 418 automated Rules and the 27
  default-manual Rules.
- [Manual automation review](MANUAL-AUTOMATION-REVIEW.md) — individual review
  of all 27 default-manual procedures.
- [Straw-man syntax](STRAW-MAN-SYNTAX.md) — non-normative working vocabulary.
- [Examples](examples/) — real RHEL 9 Rules rendered in the speculative local
  authoring form.
- [Manual review notes](manual-review/) — examples where a command is not
  sufficient to decide compliance.

### Current provisional counts

The 418 default-automated Rules currently classify by observed source features
as:

- 207 (49.5%) simple native;
- 106 (25.4%) composed native;
- 84 (20.1%) advanced structured/dataflow;
- 21 (5.0%) existing shellcommand.

These are research buckets, not proven syntax coverage.

The 27 default-manual Rules currently classify as:

- 5 deterministic automation candidates;
- 7 potentially automatable with a better typed domain model;
- 15 requiring organizational/external input or approved-exception knowledge.

This specifically argues against treating `shellcommand` as the universal
answer to the remaining manual population.


## Planned second platform: Windows Server 2025

After the RHEL 9 feasibility pass reaches a stable research checkpoint, repeat
the same experiment against the pinned Windows Server 2025 production package.

Why Windows Server 2025 is the required second platform:

- it tests whether the simplified authoring model is genuinely cross-platform
  rather than a Linux-friendly DSL;
- it exercises registry, user-right, audit-policy, WMI, file, service, and
  PowerShell/cmdlet-oriented capabilities;
- organizational input is likely to appear in different forms than on RHEL;
- Windows content provides a strong test of whether local inline expectations
  remain readable when the underlying collector semantics are not file/text
  oriented;
- it gives us a second real-world coverage curve before making any language
  recommendation.

The existing production census measured 261 automated OVAL-backed Rules in the
Windows Server 2025 package. Preliminary structural signals were:

- 53.6% simple single-Test/local-component candidates;
- 74.3% local-readable candidates allowing multiple Tests;
- only 8.4% dataflow-complex Rules;
- 80.1% of Rules with no Object/State reuse barrier;
- 71.7% of direct Test->Object references single-use;
- 93.0% of direct Test->State references single-use.

These figures are **not** syntax coverage. They justify using Windows Server
2025 as the next feasibility benchmark after RHEL 9.

The Windows study SHALL use the same research-only buckets and additionally
measure Windows-specific constructs, especially:

1. registry collection and expectation;
2. local/security policy and user-right assignment;
3. audit policy;
4. WMI/cmdlet/PowerShell-oriented checks;
5. services and system configuration;
6. multi-Test Boolean composition;
7. organizational input;
8. command-oriented checks versus typed native capabilities;
9. manual checks that may become deterministic with organizational input;
10. cases where the simplified syntax fails and the richer semantic IR remains
    necessary.

No Windows-derived syntax change becomes an accepted design without the same
human review and cross-platform comparison required for the RHEL study.
