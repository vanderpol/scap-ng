# Full-corpus 0.3 modernization census plan

**Status:** research execution plan; no accepted schema change.

## Trigger

Run the 65-package NIWC Current modernization census after these two prerequisites:

1. the Object/Variable locality pass has a stable bounded transform with exact
   re-expansion; and
2. the Apache proving case has an executable Observation artifact prototype
   with typed exports and exact flatten/re-expansion proof.

Do not wait for every 0.3 feature to be normative. The purpose of this run is
to decide what belongs in 0.3.

## Two output views

Generate both from the same pinned source revision.

### Faithful baseline

Preserve the current lossless conversion graph. This remains the semantic oracle.

### Modernized research view

Apply only transformations in one of these categories:

- exact structural/presentation equivalence:
  - consumer-local State;
  - consumer-local/private Object locality;
  - bounded Set-operand locality;
- exact graph-desugared authoring shorthand:
  - approved bounded foreach proof classes;
- exact reusable-subgraph extraction:
  - Observation artifacts whose flattening restores the faithful graph.

Do **not** automatically rewrite features whose semantics are intentionally
different or not losslessly proven. Report them as opportunities instead:

- procedural conditionals derived from legacy Boolean criteria;
- typed linux.fstab replacement of legacy split/error graph;
- ordinary positive rewrite of violation-query forms;
- general concat / multi-source foreach;
- domain-specific semantic corrections.

## Required corpus accounting

The existing full-current pipeline accounts for all 65 pinned packages:

- 61 currently generate native content;
- 4 SQL Server packages are known blockers because of independent.sqlext.

The modernization census should preserve the same source-accounting discipline.
A source blocker is not silently omitted from denominators.

## Statistics

Report corpus-wide and per benchmark:

- Rules and automated Assessments;
- faithful Objects / States / Variables / Tests;
- modernized local Objects / States;
- named Objects / States / Variables remaining;
- Object/State cross-reference reduction;
- Variables removed by foreach;
- Variables/Objects moved into Observations;
- Observation artifacts created;
- consumer references per Observation;
- exact duplicated subgraphs avoided;
- normalized lines/bytes as secondary metrics;
- Assessments with no residual complex graph;
- Assessments still complex after modernization;
- residual complexity by reason:
  - shared acquisition;
  - nontrivial Variable graph;
  - Set/Filter semantics;
  - multiple Tests/evaluate composition;
  - nested Boolean logic;
  - unsupported/deprecated capability;
  - native-only modernization opportunity;
- counts for each modernization:
  - applied exactly;
  - eligible but left faithful by policy;
  - rejected by proof boundary;
  - not applicable.

## Complexity outcome

The most useful final number is not merely file-size reduction.

Classify every automated Assessment after modernization into:

1. **local/simple** — Test-local acquisition/expectation, no named dataflow;
2. **bounded dataflow** — foreach or small explicit Variable flow;
3. **shared observation consumer** — complexity factored into an Observation;
4. **meaningfully complex** — graph complexity still required by semantics;
5. **migration blocker / unsupported source**.

For category 4, emit the exact residual features so 0.3 decisions are driven by
measured remaining complexity rather than anecdotal examples.

## Evidence policy

The exhaustive generated corpus and detailed reports belong in
`vanderpol/scap-ng-evidence` or CI artifacts. Keep only a compact summary,
source pins, workflow URL, hashes, and representative examples in `scap-ng`.

## Milestone interpretation

This run is a **0.3 design checkpoint**, not proof that every modernization is
accepted. Its purpose is to answer:

> After all currently proven safe simplifications, how much real-world
> complexity remains, what causes it, and which proposed 0.3 features have
> enough production value to justify standardization?
