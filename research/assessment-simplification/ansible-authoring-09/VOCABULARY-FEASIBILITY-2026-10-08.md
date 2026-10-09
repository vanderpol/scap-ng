# Would Ansible-inspired verbs improve SCAP-NG authoring?

> **RESEARCH ONLY — not 0.3 schema-valid, not a proposed standard, and not a decision to change the converter or scanner.** This is the post-0.3/#197 design discussion, not a release blocker.

**Finding:** A more natural `collect / where / expect` vocabulary is **feasible and worth testing**. A presentation/authoring adapter can preserve the current typed Test/Object/State/evaluate model; replacing that model with Ansible task execution or unqualified shorthand is substantially harder and **not recommended**. Prefer testing the smallest semantic-preserving vocabulary change first.

The [Board's three-way same-Rule comparison](https://github.com/vanderpol/scap-ng/discussions/212) shows current `linux.partition` RHEL 9 SV-257851 alongside two speculative forms. This page evaluates implementation cost and potential misunderstandings; it does not repeat that full example.

## What existing production research proves — and what it does not

- In six pinned NIWC production conversions, **1,350 automated Assessments** were analyzed. **53.11%** had one Test, one Object, at most one State, no Variables/Sets/Filters, and a direct `evaluate` pointer; **77.63%** had wholly local Test/Object/State relationships without shared nodes or Variables/Sets/Filters. Of 2,051 Tests, **91.57%** had zero or one State. These are **structural locality measurements**, not safe rewriting or usability results. [Underlying study](../authoring-08/README.md).
- A **previous, research-only renderer** mechanically expressed **390 of 445 RHEL 9 Rules (87.6%)** after expanding support for Sets, Filters and constant Variables. It was **one-way shape rendering**, not a proof of 0.3-conformant syntax, source-equivalent outcomes, or independent implementation. [Renderer evidence](WHOLE-RHEL9-RENDERER-RESULTS.md); implementation: [`research_render_ansible_like.py`](../../../tools/research_render_ansible_like.py).
- **Critical caveat:** the older renderer suppresses some source-present fields when it assumes common values (e.g. an `all` entity check or at-least-one entity existence). That is **not acceptable** for a canonical 0.3 design requiring explicit behavior and no hidden defaults. The older renderer also consumes an earlier converted content structure. Its 87.6% coverage must **not** be reused as a 0.3 losslessness claim.
- [Independent `evaluate` census](../evaluate-20/README.md): **976/1,350 (72.3%)** are trivial single-Test roots, but complex trees reach depth 5, repeated Test references exist, and six-state evaluation is not ordinary procedural task order. [Collection `for_each`](../../../specification/assessment/foreach.md) is an Item-population operation, **not** a per-Item task-verdict loop.

**Fresh 0.3 cross-check (October 8, [latest six-benchmark artifact, run 37849528026](https://github.com/vanderpol/scap-ng/actions/runs/37849528026)):** Parsed all `authoring/**/assessments/*.yaml` including shared Assessments, treating each YAML file once. Among **883 automated Assessment files** there were **1,390 Tests**; **623** Assessments had exactly one Test and **613** had that Test as a direct `evaluate` root, while **260** had multiple Tests. All **1,390** Tests explicitly specified `existence`, `match`, and `reported_elements`. Of the observed inline Object capability declarations, **1,166/1,166** matched their Test capability; likewise **1,162/1,162** inline States matched. **This is evidence of repetition, not permission for implicit inheritance:** the language independently types these components, and other capabilities or mixed Test/State models may require exceptions. There were **110** Test Object references instead of inline maps and **114** other/missing Object shapes; these cannot automatically be rendered as one simple `collect`. The sample had **7** `for_each` Assessments. This is a **six-benchmark sample, not the full 65-source equivalence census or a scanner run**.

**Overall:** readability potential is well evidenced; lowering correctness, cross-platform coverage, and measured author preference remain unproven.

## Implementation choices and relative cost

| Choice | Scope of actual work | Risk | Assessment |
| --- | --- | --- | --- |
| **A. Better labels in documentation/editor** | Human labels only; canonical YAML and scanner untouched | Low | **Easy, safe, but does not improve authored source YAML** |
| **B. Strict authoring-only aliases** (`collect` for Object acquisition, `where` for selection, `expect` for State comparison) | Write versioned front-end parser + fail-closed, deterministic lowering into existing canonical 0.3, authoring validation, round-trip/differential tests, tooling and migration docs | Medium | **Most promising 0.4 experiment. No evaluator rewrite if lowering preserves the canonical model** |
| **C. Make readable verbs the only canonical schema vocabulary** | In addition to B, update shared and capability schemas, mapping/reference docs, converter/normalizer/compilation, examples, result provenance conventions as needed, all relevant contract tests, and vendor authoring APIs | Medium–high | Feasible before stable release, but more ecosystem churn; not merely a search-and-replace |
| **D. Fully compact task DSL** (implicit datatypes/quantifiers, merged Objects/States/Tests, Ansible-style loops/conditionals) | Specify new defaults and algebra; prove outcome preservation for Set/Filter/Variables/Errors/Unknown/Inputs/iteration/composition; migrate source and implement new validator/compiler | High | **Do not adopt based on short examples** |
| **E. Run actual Ansible tasks as the assessment evaluator** | Replace collector/evaluation semantics, distinguish configuration mutation/changed/skipped from technical truth, rebuild results/provenance/conformance | Very high | **Not recommended** |

A direct schema rename has broad reach: the active tree contains **135 JSON schema/mapping files**, including **100 supported capability mapping JSON files**, and `tools/` has many conversion/normalization/validation paths. **These inventory counts do not mean all files require modification**; they explain why a simple field-name rename still needs impact analysis. A front-end compiled to unchanged canonical source avoids forcing immediate changes on scanners.

Avoid maintaining two equally normative dialects indefinitely: one declared authoring dialect can be lowered to **one** validated, canonical interchange representation. The transformed output, not shorthand, must be what packages and scanners rely on. No implicit magic defaults.

## Terminology: what is clearer, what could confuse?

| Proposed word | Useful reading | Possible ambiguity / design guardrail |
| --- | --- | --- |
| `collect` | Obtain typed system Items | Ansible modules often **change** the system. SCAP-NG is assessment, not remediation. The Test/Object/State capabilities can be independently typed; one `collect` cannot silently merge them. |
| `where` | Choose which resources to collect | Do not confuse selector filtering with applicability or Ansible's `when` execution guard. Only Object selection should live here, with datatype, operation, completeness and variable matching preserved. |
| `expect` | Compare collected fields with required values | Strong improvement over `state` for novices; but needs multi-State AND/OR, entity missing/status, operation, value-match, and Organization Input binding. Ansible's `state` typically describes desired configuration and can cause mutation. |
| `check` | One assessable Test | Conflicts conceptually with Ansible **check mode** (dry-run prediction) and can hide named Test identity/evidence, multi-Test `evaluate` and manual-vs-automated choices. |
| `require` | Specify obligations | Vague unless it names **which level**: Item existence, Item match, State entity existence, entity match, Variable value match. The current 0.3 `existence`, `match`, `value_match` scopes cannot be merged into one Boolean. |
| `report` | Choose reported evidence fields | Must not imply different evaluation, collection caps, hiding required witnesses, authorization to redact, or selective passing/failing truth. |
| `when` / `loop` | Familiar Ansible words | **Do not copy these uncritically.** `when` is task execution gating; `for_each` currently expands a correlated Item population into **one Object**, not separate result-bearing tasks. |

See current [assessment semantics](../../../specification/assessment/assessment-method.md), [shared result/quantifier reference](../../../specification/assessment/reference/shared-behavior.md), and [explicit collection iteration contract](../../../specification/assessment/foreach.md).

**External evidence:** [Ansible conditionals](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html) use `when` to control execution; [check mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html) predicts configuration changes and may skip unsupported modules; [file `state`](https://docs.ansible.com/projects/ansible-core/stable-2.21/collections/ansible/builtin/file_module.html) can create/remove/mutate files; [Ansible `assert`](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/assert_module.html) tests ordinary conditional expressions. These are **not** replacements for OVAL/SCAP-NG's six-state technical outcomes and typed evidence.

## Four acceptance cases for a real feasibility prototype

1. **Simple:** RHEL 9 SV-257851 `linux.partition` — preserve the **exact regex**, three independently declared capability positions, Test `existence/match`, State entity `existence/match`, `reported_elements`, Test ID and root `evaluate`. The short research [comparison](VERB-COMPARISON-SINGLE-ASSESSMENT.md) is **not yet an equivalence proof**.
2. **Composed:** RHEL 9 SV-257786 two systemd properties, then Windows Server 2025 SV-278001 nested alternate-path `evaluate`. Preserve repeated Test identity, six-state algebra and false/unknown/error cases; do not replace Boolean composition with an imperative `when`. [Prior composition research](../evaluate-20/README.md).
3. **Dataflow:** RHEL 9 SV-257889 collected users → projected home directories → file population, plus one Set/Filter and Variable case. A new `for_each` authoring alias must preserve one combined target Item population, correlation, identity, missing-field errors and evidence. [Proven source families](FOREACH-PROVEN-CASE-TRANSLATIONS.md).
4. **Inputs and outcomes:** Direct typed Organizational Input feeding expected State, with missing/mismatched/redacted inputs, per-Test evidence and Rule summary. One `expect` must not let input rewrite the collector or invent a pass; preserve Rule/Assessment/Benchmark provenance. Track [#193](https://github.com/vanderpol/scap-ng/issues/193), [#203](https://github.com/vanderpol/scap-ng/issues/203), [#205](https://github.com/vanderpol/scap-ng/issues/205).

For each case: parse experimental authoring; lower it to **byte-independent, semantically equivalent canonical typed IR**; compare canonical data and Test/Assessment results over positive, negative, missing, unknown/error and many-Item fixtures; fail closed on unsupported/ambiguous fields. Compare human comprehension and time-to-find-the-check, **not just line count**. Automated corpus expansion follows the four-case equivalence proof; the 65-source corpus is a later compatibility gate, not the first test loop.

## Proposed decision

**Recommend B as the bounded experiment**, then survey Board members and DISA content authors with blind side-by-side examples. Consider **C** only if the readability improvement is sustained across Linux, Windows and complicated Assessments and the implementation cost is acceptable. Reject D/E unless a distinct, proven benefit warrants replacing precise existing semantics.

As a first lexical preference, **`collect` and `expect` merit a trial**; retain explicit `existence / match / value_match`, capability identities, named Test IDs and explicit complex `evaluate`. Test `where` alongside existing `select`; **avoid** overloading Ansible `when`, `check_mode` or `state`.

**No 0.3 blocker or schema change is proposed.** This report is evidence and a decision agenda for [post-0.3 issue #197](https://github.com/vanderpol/scap-ng/issues/197), not Board ratification.
