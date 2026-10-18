# 0.4-A expression result boundary — 18 October 2026

**Pre-alpha research implementation, not approved semantic language or a SCAP-NG scanner.** Tracking: [native compiler #232](https://github.com/vanderpol/scap-ng/issues/232), [conformance #229](https://github.com/vanderpol/scap-ng/issues/229), [Linux pilot #238](https://github.com/vanderpol/scap-ng/issues/238).

## What is implemented and independently checked

- [Source expression compiler + result-only executor](../../../tools/v04_a_truth_plan.py) emits deterministic postorder instructions with exact source-lexical paths for the established `test`, `assessment`, `all`, `any`, `one`, `odd`, `not` and `not_applicable` expression nodes. The operator engine independently implements the six-state OVAL 5.12.3 Boolean combination tables. Every Test and Assessment dependency outcome **must** be explicitly supplied; an omitted or unknown result fails closed rather than turning into true, false or unknown.
- [Source-backed six-STIG expression compiler/census](../../../tools/v04_a_truth_plan_census.py) independently verifies the full 0.4-A lossless source IR and compiles authored `evaluate` (and, when present, `applicability`) trees. Every compiled tree is checked against a [separate OVAL-chart source-tree evaluator](../../../tools/v04_a_truth_plan_source_oracle.py): six homogeneous and three **mixed** artificial leaf-state assignments, without reading the compiled postorder plan. Every source tree is either compiled or explicitly blocked; no omitted sources or guesswork.
- [Cross-checked oracle regression](../../../tools/test_v04_a_truth_plan.py): every ordered pair and triple of the six states, for each of AND/OR/ONE/XOR, compared against the **separate** pinned OVAL reference combiner (4 x (6² + 6³) = **1,008** combination cases). Plus nested source paths, NOT, Test vs Assessment dependency, explicit not-applicable terminal, applicability scope, repeat leaves, unknown errors, invalid/missing leaf outcomes and conditional/unsupported operator fail-closed tests.
- [Read-only Linux Test-to-expression bridge](../../../tools/v04_a_linux_mount_expression_bridge.py): the existing strictly pinned `/home` `linux.partition` research Test pilot supplies an observed result to the new generic `evaluate` executor, without reinterpreting the Test's policy. [Nine boundary/live fixtures](../../../tools/test_v04_a_linux_mount_expression_bridge.py) cover true/false/unknown/error, incomplete collections, missing fields, wrong source syntax and the actual runner mount namespace.

## Verified evidence

- [Full six-STIG expression CI 39141369078 — PASS](https://github.com/vanderpol/scap-ng/actions/runs/39141369078): **872/872** automated Assessments had compilable `evaluate` expressions; **0** unapproved conditional blockers; **1,764** total expression-plan instructions, including leaf references; **5,232** earlier synthetic leaf scenarios (872 x 6) expanded in [strict source-oracle CI 39142241941](https://github.com/vanderpol/scap-ng/actions/runs/39142241941) to **7,848** independently checked source-tree/topology evaluations, including **2,616 mixed six-state assignments** (872 x 3); zero discrepancies. The six-STIG sources were independently parsed from frozen YAML and JSON, base/capability validated, normalized and roundtripped before expression plans were produced. This is an **expression** acceptance slice, not full Test/Item correctness.
- [Bounded Linux pilot CI 39141624205 — PASS](https://github.com/vanderpol/scap-ng/actions/runs/39141624205): the actual runner observed 24 mount entries, found no `/home` mount, and the independent Test and Assessment expression both returned **false**. This is a result about the CI runner's private mount namespace, not a statement about any assessed workstation or the original DISA STIG.
- The code/CI gates now fail on any unapproved conditional expression or uncovered `evaluate` tree in the pinned six-STIG research check. All work committed directly to `main`, no Codex/Work or 65-STIG corpus run.

## Real simple source example

The pinned [Linux Assessment](runtime-slice/home-nosuid.assessment.json) contains:

```yaml
evaluate:
  test: home-mounted-nosuid-option-test
```

The Linux Test evaluator observes mountinfo and returns an explicit six-state Test outcome. The result-only expression plan reads that named Test outcome without inventing another collection or another truth function. On an incomplete read the Test returns `unknown` unless a failure is already decisive, and that `unknown` flows into the Assessment expression rather than turning into a pass.

## Real complex expression topology witnesses (frozen six-STIG source)

The [source-backed expression census CI 39142006452](https://github.com/vanderpol/scap-ng/actions/runs/39142006452) recovered the original logical file paths inside the immutable r3 authoring ZIP. These are **actual 0.4-A authoring evaluate trees**, not illustrative syntax inventions:

| Actual Assessment | Source path inside r3 | Expression instructions and topology |
| --- | --- | --- |
| Windows 11 `SV-253260.automated` | `authoring/ms_windows_11/assessments/automated/SV-253260.automated.json` | 14 instructions; 3 `all`, 3 `any`, 1 `not` |
| Server 2025 `SV-278001.automated` | `authoring/ms_windows_server_2025/assessments/automated/SV-278001.automated.json` | 11 instructions; 3 `all`, 1 `any`, 1 `not` |
| RHEL 9 `SV-258236.automated` | `authoring/rhel_9/assessments/automated/SV-258236.automated.json` | 13 instructions; 1 `all` |
| Shared Linux audit syscall groups | `authoring/shared/assessments/linux/files/audit-uses-fsetxattr-lsetxattr-removexatt.assessment.json` | 30 instructions; 6 `all` |

The complete six-STIG source contains **1,393 Test-leaf occurrences**, **246 `all`**, **100 `any`**, and **25 `not`** operations across 872 automated `evaluate` trees. All of these trees passed structural compilation without introducing an unapproved conditional operator. This helps select real, complex cases for later Test-result and evidence propagation. It **does not** mean their Test/State/collector implementations have been executed or found equivalent to source OVAL.

## Scope that remains unproved

**No broad native executable 0.4 compiler, signed .scapng, arbitrary capability/Test evaluator or SCAP 1.4 parity is claimed.** Even though all six-STIG `evaluate` trees compile, the 872 Test/State implementations have not been executed. In particular:

- Actual typed collection/Item/State/Windows record, Set/Filter and correlated `for_each` evaluation is still absent except for the **single pinned Linux mount pilot**.
- Synthetic Test result values are intentionally supplied by the tests, not generated from system observations or original OVAL results.
- `if/then/else` is explicitly refused by this evaluator pending the outstanding six-state semantics decision in #229. The frozen six-STIG normal-form content currently has **no such expression**, so no source was omitted.
- Test-level applicability declarations are compiled **separately**, not silently combined into Assessment evaluation or Rule applicability; the native scanner disposition/selection contract remains open.
- Running the pilot's Linux `mountinfo` is not proven equivalent to OVAL `linux.partition` semantics or to a Joval/OpenSCAP/vendor scanner. Publisher migration/version choices in #232 remain open.

## Next scope (no owner decision required yet)

Proceed with independently expected **Item and State result** fixtures for at least one additional high-value capability/complex source graph, preserving collection flags, incomplete evidence, and context. Verify the Test-level result against its source-derived expected outcome *before* sending it to this generic `evaluate` plan. Keep conditionals and specification-version promotion outside this work until the owner reviews them.

This keeps **source-graph correctness**, **Test-result correctness**, **Assessment Boolean result correctness**, **bundle compilation** and **scanner execution** as separate, auditable gates.
