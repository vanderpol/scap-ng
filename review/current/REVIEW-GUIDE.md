# SCAP-NG 0.3 modernization review guide

This is a short guide to the **verified six-benchmark review ZIP** linked from
[Current review](README.md). Open the GitHub Actions run, download the
`scap-ng-board-representative-review` artifact, and inspect its `authoring/`
directory first. The same ZIP contains `packages/` (compiled output),
`results/synthetic-fixtures/` (illustrations, **not** real scans), and
`REVIEW.json` (the generated feature index).

**Important:** Paths below refer to the current six-benchmark ZIP, **not** an
older research comparison package. The ZIP contains native/normalized
0.3 authoring; it does not contain side-by-side faithful and modernized
source trees. Detailed transformation evidence belongs to the research
materials, not this compact Board artifact.

## What to review

| SCAP 1.4 mechanism | SCAP-NG 0.3 improvement | Where in the ZIP |
| --- | --- | --- |
| Separately identified OVAL Object/State for a private Test | Keep private Object and State beside the Test | `authoring/rhel_9/assessments/automated/SV-257851.automated.yaml` |
| Shared acquisition across checks | Explicit named `shared_objects:` only when reuse is needed | `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml` |
| Static Variable plus collection plumbing | Preserve typed literal collections directly | `authoring/ms_windows_11/assessments/automated/SV-253274.automated.yaml` |
| ObjectComponent → Variable → selector iteration | Use `for_each:` to express a proven collection expansion | `authoring/shared/assessments/all-local-interactive-user-home-directories-are-0750-or-less.assessment.yaml` |
| Separate Set and Filter component chains | Localize the structure but preserve its Set/Filter meaning | `authoring/ms_windows_11/assessments/applicability/condition.bluetooth-installation.yaml` |
| OVAL criteria tree spanning multiple Tests | Retain explicit `evaluate:` for nontrivial Boolean composition | `authoring/ms_windows_server_2025/assessments/automated/SV-278001.automated.yaml` |
| Monolithic XCCDF policy and selection | Distinct Benchmark, Rule, and Assessment documents | `authoring/rhel_9/benchmark.yaml` and `authoring/rhel_9/rules/` |

Component names follow descriptive type-suffixed IDs. Computed Variables
remain named when they carry runtime meaning; only provably static Variable
plumbing is folded. Searches for `variable.value`, `for_each:`,
`shared_objects:`, `set:`, and `evaluate:` should target native YAML
rather than embedded shell/PowerShell text.

## Conversion boundary: DNS nested iteration

Windows Server DNS **SV-259388** motivates correlated/nested `for_each`:
the existing PowerShell obtains zones, enumerates hosts, resolves names,
and checks RRSIG records. This is a **real production requirement** but
the nested native rewrite is an **authored research example**, not an
automatic conversion in the ZIP. The source converter keeps the
PowerShell-based check rather than guessing equivalent behavior.

Similarly, Observations and a redesigned `evaluate` are **not** normative
0.3 features. See the
[deferred boundary](../../specification/deferred-after-0.3.md).

## Evidence and review order

1. Read the [Benchmark/Rule example](../../specification/examples/README.md)
   then the [Assessment example](../../specification/examples/assessments.md)
   for a short Rule → Assessment walkthrough.
2. Inspect the real `authoring/` paths above; confirm source identifiers,
   typed comparisons, and which checks remain complex.
3. Inspect `packages/` and the generated `REVIEW.json`. Use
   `results/synthetic-fixtures/` only to understand the proposed reporting
   contract, **not** as runtime-conformance evidence.
4. Check the [0.3 release issue](https://github.com/vanderpol/scap-ng/issues/191)
   and [65-source correctness gate](https://github.com/vanderpol/scap-ng/issues/202)
   before interpreting this six-benchmark build as a complete release.

SCAP-NG preserves unsupported/deprecated and unproven conversion cases as
explicit blockers; schema-valid examples and successful compilation do not
prove live scanner equivalence.
