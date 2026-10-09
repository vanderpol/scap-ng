<!-- scap-ng-discussion-id: ASSESSMENT-VOCABULARY-ABCD-CLEAN-20261009 -->

# SCAP-NG Assessment authoring: A / B / C / D

**OVAL Board feedback — informal, nonbinding preference vote.**

The same **real RHEL 9 STIG rule SV-257851** (`/home` must be mounted with `nosuid`) is shown below in three authoring styles. Which is easiest to read and maintain?

**How to vote:** After reviewing the three YAML examples, add **👍 to exactly one of the four voting comments directly beneath this opening post**:

- **A — Current SCAP-NG 0.3 / OVAL-aligned**
- **B — Ansible-inspired**
- **C — Inspection-oriented**
- **D — Different or hybrid approach**

D is a substantive alternative (not abstention). A brief explanation is welcome; if undecided, comment without voting. **All examples, distinctions and acceptance requirements are in this post.** No other document is needed.

---

## Three vocabularies at a glance

| What the author means | **A. Current SCAP-NG 0.3** | **B. Ansible-inspired** | **C. Inspection-oriented** |
| --- | --- | --- | --- |
| Independently evaluated unit | `test` / `tests` | `check` | `check` / `checks` |
| Get system Items | `object` + `capability` | `collect` | `inspect` |
| Identify which resources | `select` | `where` | `select` |
| State what values are acceptable | Test-local `states` with direct typed comparisons (no `state:` wrapper) | `expect` | `expect` |
| Compare field to value | `operation: equals`, `value` | `equals` | `equals` |
| Require Items to exist / satisfy | Test `existence`, `match` | `require.collected_items`, `require.matching_items` | `items.existence`, `items.satisfy` |
| Require field instances to exist / satisfy | State `existence`, `match` | `expect.*.existence`, `expect.*.match` | `field_values.existence`, `field_values.satisfy` |
| Choose / combine technical results | `evaluate` / `test` | implicit one-`check` root in this sketch | explicit `evaluate` / `check` |
| Specify visible result fields | `reported_elements` | `report.elements` | `evidence.fields` |
| Declare capability / preserve type identity | Test and inline Object; embedded comparisons inherit it | one `collect` declaration (proposed) | one typed `check` declaration (proposed) |

The terms in B and C are *discussion candidates*, not approved enumerations. `inspect` denotes read-only **assessment intent**, not a ban on safe collector execution; `expect` means comparison, not remediation. **Current 0.3 structural baseline:** `capability` remains on the Test and the inline Object (which owns acquisition). Test-local `states` and Object/Set `filters` contain **direct, typed predicates without a separately named State, a `state:` wrapper, a title, or a duplicate capability**. B and C *propose* going further with a single capability declaration; that still requires safe lexical binding and is **not implemented in native 0.3 authoring**. Do not choose a vocabulary merely because it has fewer repeated lines. [Embedded-predicate contract #208](https://github.com/vanderpol/scap-ng/issues/208) · [architecture research #197](https://github.com/vanderpol/scap-ng/issues/197).

## Same real source requirement

**RHEL 9 STIG, SV-257851:** The `/home` filesystem must use the `nosuid` mount option. Each version is **intended** to select the same partition Items and evaluate the same expected mount option. That intended equivalence **has not been established** for B or C.

## A — Current SCAP-NG 0.3 (OVAL-aligned, actual syntax)

This is **the real converted automated RHEL 9 Assessment excerpt**, presented in the active 0.3 direct-predicate form from [Assessment examples](https://github.com/vanderpol/scap-ng/blob/main/specification/examples/assessments.md#2-the-automated-check-embeds-its-expectation). Only surrounding metadata is omitted.

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
      - field: mount_options
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

This reads as *collect partitions → where the mount point matches → expect `nosuid` → require matching Items → report fields*. It also proposes a single capability declaration and an implicit single-check evaluation root. Neither shorthand is supported by the 0.3 schema; a production translator would need to materialize and validate both deterministically. This is **not Ansible playbook syntax**.

## C — Inspection-oriented (research-only syntax)

```yaml
checks:
  home-mounted-nosuid-option-test:
    capability: linux.partition
    inspect:
      select:
        mount_point:
          matches_regex: '.*\\/home'
          datatype: string
    expect:
      - field: mount_options
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

This reads as *inspect partitions → select the mount → expect the option → apply explicit Item and field-value constraints → retain evidence → evaluate a named check*. The **single** `capability` on this named Check is proposed to determine the private inline Object's acquisition capability and expected comparison field types; unlike B it also retains an explicit evaluation root. This lexical binding is **not yet a valid 0.3 construct** and must be proven safe rather than assumed.

---

## Non-negotiable acceptance gate: lossless forward conversion from SCAP 1.4

**All three candidates (A, B, and C) MUST support lossless, automated forward conversion from the supported SCAP 1.4/XCCDF and OVAL 5.12.3 source constructs.** This is an entry requirement, **not an optional benefit of A or a feature that members are voting to remove**. Any fourth/hybrid proposal must satisfy the same gate. Lossless means *equivalent technical and policy meaning*, not byte-for-byte identical XML or identical authoring layout.

In particular, conversion SHALL preserve resource selection, collected-Item and Filter/Set membership (including ordering and include/exclude), capabilities, variable computations and bindings, typed values and all quantifiers, Boolean evaluation, applicability, policy/Rule/check selection, manual assessment intent, evidence/redaction requirements, and six technical outcomes (`true`, `false`, `unknown`, `error`, `not_evaluated`, `not_applicable`). No translator may silently change a check into a weaker or stronger assessment, replace a regex with a literal, or hide an unsupported construct.

**Proof status is deliberately different from the requirement:** A has a source-derived 0.3 converter and active corpus/conformance testing; that is not a blanket claim that its final runtime equivalence gate is complete. B and C are **single-rule vocabulary sketches only**. They have **not** demonstrated complete SCAP 1.4 representational coverage or a working lossless converter. Before either could replace A, they would need versioned grammars, precise mapping of complex source constructs, converter implementation, and differential six-state/corpus validation. The short YAML excerpts are not intended to contain every feature by themselves.

Deprecated or deliberately excluded input constructs (for example, legacy `independent.sqlext`) SHALL produce explicit source-specific conversion errors, not invented equivalents. This defined exclusion is not permission to drop supported semantics. **Backward conversion into SCAP 1.4 is not a requirement.**

Please choose the clearest **authoring direction**, assuming it must ultimately satisfy these gates—not merely the shortest one-rule excerpt.

## What must not change just because the words change

- **Source selection:** All three examples preserve the source regex scalar `.*\\/home` (two literal backslash characters in the authored YAML). The source-derived regex text must be preserved **exactly under YAML decoding and regex processing**. Replacing it with a literal `/home` would potentially change the selected resources. The prototype must prove exact literal/regex semantics.
- **Different quantifier scopes:** Test `existence: one_or_more` applies to collected Items; Test `match: all` combines Item outcomes. State `existence: one_or_more` applies to observed field instances; State `match: one_or_more` combines State field comparisons. These cannot be silently collapsed.
- **Technical outcomes:** `true`, `false`, `error`, `unknown`, `not_evaluated` and `not_applicable` retain their meanings. A policy pass is not universally identical to an Assessment's technical `true`.
- **Capabilities, collection, evidence:** 0.3 requires the Test's and independently typed inline Object's capabilities to agree; direct embedded comparisons inherit their effective capability and carry no redundant declaration. A hypothetical one-declaration private-component binding (as in B/C) must resolve capability deterministically, keep independently named/shared and nested components correctly typed, and fail on incompatible cross-capability use. Missing/incomplete Items, typed selectors and expectations, reporting/redaction rules, and evidence/provenance remain explicit. `evidence` must not silently become a collection limit or permission to omit required proof.
- **More complicated Assessments:** Multi-Test `evaluate`, named Test results, Set/Filter/Variable algebra, correlated `for_each` Item populations, and Organizational Input must be representable without inventing Ansible-like procedural semantics.
- **No hidden defaults or loss of conversion coverage:** A shorter authoring presentation SHALL have a strict, versioned, lossless translation from the supported SCAP 1.4/XCCDF and OVAL 5.12.3 constructs, with typed semantics and explicit failures for excluded inputs. B and C do **not yet** have the grammar, converter, or differential conformance evidence needed to satisfy that requirement.

## What feedback would help after your vote?

Please vote for the direction you actually support. In explaining an A–C vote, consider whether `inspect` or `collect` better conveys *obtain target facts*, whether `select` or `where` more clearly means *identify relevant resources*, and whether `items.satisfy` is clearer than `match`. **Use D** if a different vocabulary or hybrid would be preferable; please explain the needed improvement in the comments below. Do not vote A–C merely to avoid choosing D.

There is a genuine timing decision: **if the Board strongly prefers different terms, should 0.3 wait for a defined, tested change, or should we freeze its current vocabulary and make the improvement in a future version?** A straw poll alone cannot settle that technical or release question.

For engineering background (not prerequisite reading), see the [feasibility and compatibility study](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/ansible-authoring-09/VOCABULARY-FEASIBILITY-2026-10-08.md) and [architecture audit #197](https://github.com/vanderpol/scap-ng/issues/197). The maintained current [Assessment showcase](https://github.com/vanderpol/scap-ng/blob/main/specification/examples/assessments.md) remains the authority for 0.3 authoring.

**Implementation / conformance tracking:** [authoring-vocabulary issue #207](https://github.com/vanderpol/scap-ng/issues/207) (historical context) · [embedded Test/Filter predicates and migration #208](https://github.com/vanderpol/scap-ng/issues/208) · [Board decisions #209](https://github.com/vanderpol/scap-ng/issues/209) · [architecture research #197](https://github.com/vanderpol/scap-ng/issues/197).

**Voting occurs only in the four A/B/C/D comments below this post.** This is a request for direction, not ratification or a promise to change 0.3.
