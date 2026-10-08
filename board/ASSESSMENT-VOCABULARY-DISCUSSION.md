# Board discussion: what should an SCAP-NG Assessment look like?

> **Pre-0.3 decision discussion / informal preference vote — NOT an approved schema change.** A is an excerpt of actual SCAP-NG 0.3 YAML. B and C are **speculative, not schema-valid, not executable, and not yet proven equivalent**. This page is for choosing words, not relaxing technical requirements.

**Question for the OVAL Board:** Given the same straightforward STIG requirement, which authoring vocabulary is easiest to read and least likely to be misunderstood? Should we revisit terminology **before finalizing 0.3**, or retain 0.3 and investigate for the next release?

**[Participate in the discussion and vote on GitHub #207](https://github.com/vanderpol/scap-ng/issues/207)**. Add a **👍 to exactly one** option comment, and add a regular comment to explain your preference or propose a hybrid:

- [Vote A — Current SCAP-NG / OVAL-aligned](https://github.com/vanderpol/scap-ng/issues/207#issuecomment-6071169165)
- [Vote B — Ansible-inspired](https://github.com/vanderpol/scap-ng/issues/207#issuecomment-6071169545)
- [Vote C — Inspection-oriented](https://github.com/vanderpol/scap-ng/issues/207#issuecomment-6071169947)

The poll is **nonbinding**. Choosing words is not a decision to adopt a second language or change existing Test outcomes. Formal standards approval, schema changes, and migration would be separate decisions.

## Three vocabularies at a glance

| What the author means | **A. Current SCAP-NG 0.3** | **B. Ansible-inspired** | **C. Inspection-oriented** |
| --- | --- | --- | --- |
| Independently evaluated unit | `test` / `tests` | `check` | `check` / `checks` |
| Get system Items | `object` + `capability` | `collect` | `inspect` |
| Identify which resources | `select` | `where` | `select` |
| State what values are acceptable | `states` / `state` | `expect` | `expect` |
| Compare field to value | `operation: equals`, `value` | `equals` | `equals` |
| Require Items to exist / satisfy | Test `existence`, `match` | `require.collected_items`, `require.matching_items` | `items.existence`, `items.satisfy` |
| Require field instances to exist / satisfy | State `existence`, `match` | `expect.*.existence`, `expect.*.match` | `field_values.existence`, `field_values.satisfy` |
| Choose / combine technical results | `evaluate` / `test` | implicit one-`check` root in this sketch | explicit `evaluate` / `check` |
| Specify visible result fields | `reported_elements` | `report.elements` | `evidence.fields` |
| Remain independently typed | Test, Object and State capabilities | one `collect` suggests a shortcut — **unresolved** | capabilities explicit at each scope |

The terms in B and C are *discussion candidates*, not approved enumerations. `inspect` is meant to denote read-only **assessment intent**, not to ban safe collector execution; `expect` is comparison, not remediation. This table is not a complete language mapping.

## Same real source requirement

**RHEL 9 STIG, SV-257851:** The `/home` filesystem must use the `nosuid` mount option. Each version is **intended** to select the same partition Items and evaluate the same expected mount option. That intended equivalence **has not been established** for B or C.

## A — Current SCAP-NG 0.3 (OVAL-aligned, actual syntax)

This is **the real converted automated RHEL 9 Assessment excerpt** from the active [Assessment examples](../specification/examples/assessments.md#2-the-automated-check-keeps-its-object-and-state-nearby). Only surrounding metadata is omitted.

```yaml
tests:
  home-mounted-nosuid-option-test:
    capability: linux.partition
    object:
      capability: linux.partition
      select:
        mount_point:
          value: .*\\/home
          operation: pattern_match
          datatype: string
    states:
      - capability: linux.partition
        state:
          field: mount_options
          value: nosuid
          operation: equals
          datatype: string
          match: one_or_more
          existence: one_or_more
    reported_elements: all
    existence: one_or_more
    match: all
evaluate:
  test: home-mounted-nosuid-option-test
```

## B — Ansible-inspired (research-only syntax)

```yaml
check:
  id: home-mounted-nosuid-option-test
  collect: linux.partition
  where:
    mount_point:
      matches_regex: '.*\\/home'
      datatype: string
  expect:
    mount_options:
      equals: nosuid
      datatype: string
      existence: one_or_more
      match: one_or_more
  require:
    collected_items: one_or_more
    matching_items: all
  report:
    elements: all
```

This reads as *collect partitions → where the mount point matches → expect `nosuid` → require matching Items → report fields*. The compact shape hides the independent Test/Object/State capability declarations and drops the explicit single-Test `evaluate`; a production translator would need to reconstruct both without ambiguity. This is **not Ansible playbook syntax**.

## C — Inspection-oriented (research-only syntax)

```yaml
checks:
  home-mounted-nosuid-option-test:
    capability: linux.partition
    inspect:
      capability: linux.partition
      select:
        mount_point:
          matches_regex: '.*\\/home'
          datatype: string
    expect:
      - capability: linux.partition
        field: mount_options
        equals: nosuid
        datatype: string
        field_values:
          existence: one_or_more
          satisfy: one_or_more
    items:
      existence: one_or_more
      satisfy: all
    evidence:
      fields: all

evaluate:
  check: home-mounted-nosuid-option-test
```

This reads as *inspect partitions → select the mount → expect the option → apply explicit Item and field-value constraints → retain evidence → evaluate a named check*. It keeps independent capability declarations and a visible root. It is slightly longer than B by design, not a claim of better scanner behavior.

## What must not change just because the words change

- **Source selection:** All three examples preserve the source regex scalar `.*\\/home` (two literal backslash characters in the authored YAML). The source-derived regex text must be preserved **exactly under YAML decoding and regex processing**. Replacing it with a literal `/home` would potentially change the selected resources. The prototype must prove exact literal/regex semantics.
- **Different quantifier scopes:** Test `existence: one_or_more` applies to collected Items; Test `match: all` combines Item outcomes. State `existence: one_or_more` applies to observed field instances; State `match: one_or_more` combines State field comparisons. These cannot be silently collapsed.
- **Technical outcomes:** `true`, `false`, `error`, `unknown`, `not_evaluated` and `not_applicable` retain their meanings. A policy pass is not universally identical to an Assessment's technical `true`.
- **Capabilities, collection, evidence:** Multiple capabilities, missing or incomplete Items, typed selectors and expectations, reporting/redaction rules, and evidence/provenance remain explicit. `evidence` must not silently become a collection limit or permission to omit required proof.
- **More complicated Assessments:** Multi-Test `evaluate`, named Test results, Set/Filter/Variable algebra, correlated `for_each` Item populations, and Organizational Input must be representable without inventing Ansible-like procedural semantics.
- **No hidden defaults:** A shorter authoring presentation would need a strict, versioned, lossless translation to the canonical typed model or an equally explicit canonical schema. The current two speculative excerpts **do not** meet that bar.

## What feedback would help?

Please vote for your preferred **direction**, and explain whether `inspect` or `collect` better conveys *obtain target facts*, whether `select` or `where` more clearly means *identify relevant resources*, and whether `items.satisfy` is clearer than `match`. If you prefer a **hybrid** (for example, current SCAP-NG with `expect` replacing `state`), say so in the [discussion](https://github.com/vanderpol/scap-ng/issues/207) rather than voting reluctantly.

There is a genuine timing decision: **if the Board strongly prefers different terms, should 0.3 wait for a defined, tested change, or should we freeze its current vocabulary and make the improvement in a future version?** A straw poll alone cannot settle that technical or release question.

For engineering background (not prerequisite reading), see the [feasibility and compatibility study](../research/assessment-simplification/ansible-authoring-09/VOCABULARY-FEASIBILITY-2026-10-08.md) and [architecture audit #197](https://github.com/vanderpol/scap-ng/issues/197). The maintained current [Assessment showcase](../specification/examples/assessments.md) remains the authority for 0.3 authoring.
