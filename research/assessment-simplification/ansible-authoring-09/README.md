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
