# SCAP-NG Content Author Guide

**Status: 0.4.0 pre-alpha draft.** This is a short introduction to the current authoring model, not a substitute for the [versioned schema](../../schema/v0.4.0/README.md) or [specification](../../specification/README.md). Track corrections and review questions in [#252](https://github.com/vanderpol/scap-ng/issues/252).

## 1. Start with the policy

Read SCAP-NG from the outside inward:

| Part | Purpose |
| --- | --- |
| **Benchmark** | Defines the publisher's policy, target Platform, and member Rules. |
| **Rule** | Defines one requirement and its Assessment choices. |
| **Assessment** | Defines the method used to determine the relevant fact or requirement outcome. |
| **Result** | Records what was evaluated, the outcome, and supporting explanation/evidence. |

A Benchmark's Rule membership defines its baseline. A publisher Profile can deselect member Rules; external Tailoring is a separate policy layer. Organizational Input supplies authorized expected-state data and is not the same as Tailoring. These distinctions are explained in [Benchmark/Rule](../../specification/policy/benchmark.md), [Profiles/Tailoring](../../specification/policy/profiles-and-tailoring.md), and [Parameters/Organizational Input](../../specification/policy/parameters-and-organizational-input.md).

## 2. Select an Assessment method

A Rule may declare named manual and automated choices. Its `default_assessment_choice` names the publisher's selected default; other declared choices remain available under the rules of the [Assessment choice model](../../specification/policy/benchmark.md). A manual Assessment records a human procedure. An automated Assessment expresses technical collection and evaluation. See [manual assessments](../../specification/assessment/manual-assessment.md) and [assessment methods](../../specification/assessment/assessment-method.md).

## 3. Read an automated Assessment

An automated Assessment combines Tests through `evaluate`. A Test names a collection `capability`, selects data with `object`, and states the expected conditions with `require`.

The following is a **short syntax illustration**, not a complete STIG Assessment:

```yaml
tests:
  home-mount-requires-nosuid-test:
    test_title: The /home mount must use nosuid
    capability: linux.partition
    object: {mount_point: {equals: /home}}
    require:
      items: one_or_more
      all_items_must:
        - mount_options:
            require: at_least_one_exists_and_all_match
            equals: nosuid

evaluate:
  test: home-mount-requires-nosuid-test
```

Here, `object` selects the mount, `items` constrains the collected Item population, and the field condition constrains `mount_options`. **Item existence is not the same as field existence or matching.** Collection failure is not an empty population. For current syntax and source-backed full examples, use the [0.4.0 Assessment examples](../../specification/examples/assessments.md) and their pinned release.

More complex Assessments may use multiple Tests, logical composition, Variables, Sets, Filters, and nested record conditions. Consult the exact [0.4.0 schema](../../schema/v0.4.0/README.md) before writing them; avoid replacing uncommon source-proven behavior with an attractive but unproved shortcut.

## 4. Validate, compile, then distribute

1. Use a single versioned authoring format. The current review set supplies equivalent YAML and JSON.
2. Check syntax and the applicable JSON Schema; then check references and semantic constraints. **Schema validity alone does not establish semantic or scanner conformance.**
3. Compile resolved authoring content into self-contained, scanner-facing content. Compiled logical references must not depend on original authoring paths.
4. Keep source/conversion evidence distinct from executable content, and do not describe an unsigned or unexecuted package as a verified scanner result.

See [conformance layers](../../specification/core/conformance.md), [packaging and integrity](../../specification/package/package-and-integrity.md), and the [current compilation limitations](../developer/CONVERTER-COMPILER-RUNBOOK.md).

## 5. Before publishing

- Confirm exact SCAP-NG version, source identity, references, and Assessment choices.
- Confirm that Items, fields, expected values, and logical composition express the intended requirement.
- Preserve publisher identifiers and distinguish observed facts from policy values.
- Cite the governing normative sections and record unproved behavior for review.

### Appendix: migration terminology

SCAP-NG does not require prior OVAL knowledge. For migration, use the [SCAP 1.4 concept crosswalk](../../specification/crosswalk/scap-1.4-concept-crosswalk.md) and [OVAL 5.12.3 mapping](../../specification/migration/oval-5.12.3-to-ng.md). Legacy behavior must be checked against the pinned upstream XSD, its annotations, and other applicable normative text; the legacy XML shape does not independently define native NG semantics.
