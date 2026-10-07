# Full-corpus 0.3 modernization census

**Status:** completed research checkpoint; no schema change or design acceptance.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37632292259

Pinned NIWC revision:
`8c8e5dff860af6b1290ee9273a282db24278f8d5`

The run regenerated all 65 individual NIWC Current packages from source:

- **61** generated native content;
- **4** expected `independent.sqlext` source blockers;
- **0** unexpected blockers.

## Result

Measured automated Assessments: **7,165** total, including **6,916 Rule
Assessments** and **249 applicability Assessments**.

Exact/reversible research transforms produced:

| Measure | Faithful | Research view | Reduction |
| --- | ---: | ---: | ---: |
| Top-level Objects | 13,402 | 1,197 | **91.07%** |
| Top-level States | 9,121 | 435 | **95.23%** |
| Named Variables | 2,250 | 2,002 | **11.02%** |
| Named component references | 23,883 | 1,926 | **91.94%** |

Rule Assessment classifications:

| Class | Count | Percent |
| --- | ---: | ---: |
| local/simple | **4,736** | **68.48%** |
| bounded dataflow (`foreach`) | 22 | 0.32% |
| shared Observation consumer | 52 | 0.75% |
| meaningfully complex | **2,106** | **30.45%** |

The exact `foreach` v1 proof class is therefore useful but narrow: **22**
rewrites across 6,916 Rules.

## Shared Observation result

The census created **9 package-local Observation artifacts** with **69**
automated consumers:

- Apache discovery: 20 consumers across UNIX Server/Site content;
- Windows DomainRole: 43 consumers across Windows 10, Windows 11, and Server
  2019/2022/2025;
- RHEL/Oracle Linux dconf discovery: 6 consumers.

Those artifacts factor **129 Object occurrences** and **226 Variable
occurrences** into 15 unique Observation Objects and 24 unique Observation
Variables within their packages.

This strengthens Observation beyond the original Apache example: the same
contract works for cloned value dataflow, source-shared Item acquisition, and
mixed Item/value exports.

## What remains meaningfully complex

Among the **2,106** complex Rule Assessments, overlapping residual causes are:

- nontrivial Variable graph: **1,073**;
- real multi-Test composition: **1,055**;
- Set/Filter semantics: **630**;
- nested evaluation tree: **560**;
- shared acquisition: **301**;
- named State reuse: **214**;
- named Object graph: **154**;
- repeated Test reference: **129**.

**Important refinement in progress:** this first-pass classifier treats every
surviving Variable as a nontrivial Variable graph. Follow-up analysis found that
many Windows survivors are OVAL `external_variable` inputs or constants rather
than derived dataflow. Therefore **30.45% is a conservative upper bound on
meaningful structural complexity**, not the final dataflow-complexity rate.

The next research step is classifying surviving Variables by source kind,
expression/function family, fan-out, and chaining before revising that number.

## Evaluate checkpoint

Across the full corpus, **4,740 / 6,916 (68.5%)** Rule Assessments have a
single-Test explicit root. That is strong evidence for editor/normalizer
authoring convenience, but not for a hidden executable default.

Real composition remains necessary: **147** Rule Assessments repeat Test
references, and representative trees reach depth 5. Keep named Tests and
first-class `evaluate` where composition exists.

## Scope boundary

Applied automatically in this census only when existing proof was exact and
reversible:

- consumer-local Object/State presentation;
- private Set-operand and Variable-local Object locality;
- bounded `foreach` v1;
- proven Observation extraction shapes.

Not rewritten merely to reduce the complexity count:

- native conditional/case authoring;
- typed `linux.fstab`;
- violation-query positive spelling;
- general concat/multi-source `foreach`;
- domain-specific semantic changes.

The detailed 61-package reports and logs remain in the workflow artifact rather
than this repository.
