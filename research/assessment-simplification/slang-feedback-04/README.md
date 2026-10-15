# Research: Slang feedback and a smaller improvement to Assessment authoring

**0.4 exploratory study.** [Tracked by issue #224](https://github.com/vanderpol/scap-ng/issues/224) · [12/12 focused prototype tests passed](https://github.com/vanderpol/scap-ng/actions/runs/38662660201). Does not modify the frozen 0.3 grammar, Discussion #213, or any Board votes. This is one constrained *presentation* experiment, **not** a replacement OVAL evaluator.

## What the live Discussion actually shows (14 October 2026)

[Discussion #213](https://github.com/vanderpol/scap-ng/discussions/213) has four predefined voting comments, eight threaded replies and two thumbs-up votes for option C. A, B and D each have zero thumbs-up votes; neither comment volume nor the two votes constitutes Board consensus.

[David Solin's response to D](https://github.com/vanderpol/scap-ng/discussions/213#discussioncomment-18935232) recalls Slang as a schema-constrained, capability-centered check form combining discovery, existence and comparison, with AND/OR/XOR check composition. He explicitly qualifies the historic conversion as *not necessarily lossless in theory*, saying real cases led them to extend the vocabulary. This is a valuable author-experience observation **but not evidence of complete Slang↔OVAL semantic equivalence**, nor proof that a specific translation was incorrect.

[Robert Gendler's feedback](https://github.com/vanderpol/scap-ng/discussions/213#discussioncomment-18931900) expresses mixed feelings about NG but prefers the direction to XML; his separate comments raise the question of Variables surviving simplification. Do not count these comments as preference votes.

## What to borrow, and what not to infer

Borrow Slang's **resource-first mental model** and **typed schema constraining available fields and operations**. Authors should see "what system facts do I inspect, which resources, and what outcome do I require?" rather than four distributed OVAL components.

Do **not** adopt David's short sketch as a losslessly converted equivalent of the real rule without proof. The real published example selects `linux.partition.mount_point` and tests `mount_options = nosuid`; his recollection instead uses `path` and Boolean `suid: false`. Those may express similar administrator intent, but the latter would require a precisely defined computed-field alias and equivalence proof. His single `existence: all` cannot safely be assumed to preserve **all four separately scoped decisions** in the published source:

1. How many collected Items must exist (Test existence).
2. How collected Item results are combined (Test match).
3. How many observed field instances must exist (State-entity existence).
4. How field-value comparisons are combined (State-entity match).

An empty collection, partially missing values, a regex selection, or an error can change the outcome when these are conflated. The evaluator still needs to preserve all six technical outcomes, checked entity cardinalities, lineage, and explicit criteria composition.

## An intentionally modest Slang-inspired hybrid

The following is a *new experimental authoring view*, **not valid NG 0.3 syntax**. It is deliberately less terse than Slang because it keeps the four relevant quantifiers in the exact contexts they affect.

```yaml
checks:
  home-mounted-nosuid-option:
    resource: linux.partition
    select:
      mount_point:
        matches_regex: '.*\\/home'
    expect:
      mount_options:
        equals: nosuid
        values:
          exists: one_or_more
          match: one_or_more
    require:
      items:
        exists: one_or_more
        match: all
    evidence:
      fields: all
evaluate:
  check: home-mounted-nosuid-option
```

The proposed `resource` is the capability type (avoiding the YAML 1.1 parser ambiguity of an unquoted `on` key). A schema supplies *allowed field names and operator types*, **not** default semantic quantifiers. `select` describes collection, `expect` holds field comparisons and field-value cardinality, and `require.items` expresses Item cardinality and matching. `evaluate` remains explicit for complex AND/OR/XOR trees.

This short form has a narrow, mechanical lowering:

| Experimental field | Exact canonical 0.3 field |
|---|---|
| `resource: linux.partition` | Test and private Object `capability` |
| `select.mount_point.matches_regex` | `object.select.mount_point.value` + `operation: pattern_match` |
| `expect.mount_options.equals` | `states: [{field: mount_options, operation: equals, value: nosuid}]` |
| `expect.mount_options.values.exists/match` | Embedded State `existence/match` |
| `require.items.exists/match` | Test `existence/match` |
| `evidence.fields` | Test `reported_elements` |
| `evaluate.check` | `evaluate.test` |

The [focused experimental lowerer](../../../../tools/research_slang_scoped_facade.py) and [negative tests](../../../../tools/test_research_slang_scoped_facade.py) currently support **only one** `linux.partition` check, one selector, one State comparison, and the quantifiers shown. Any missing, unknown, unproven, or ambiguous operator is rejected. That is intentional. It is **not** proof of complete lossless migration, nor a recommendation to replace 0.3 source.

## Initial judgment

The most attractive incremental solution may be an **optional schema-driven authoring/editor view** which compiles to canonical 0.3 and is never sent directly to scanners. It can improve everyday author experience without forcing all vendors to implement another evaluator. Preserve explicit canonical constructs for complex multi-State operators, Set/Filter graphs, Variables, correlated foreach, manual paths, and organizational inputs until each can be lowered exactly.

Before considering standardization: audit actual 0.3 Test/State quantifier combinations across the six-STIG corpus, then make at least one before/after example for each nondefault semantics class (none/only-one/all-exist, missing field, partial collection, negative comparison, multi-State AND/OR, error/unknown, Variables and nested criteria). Use source-paired OVAL closures; verify exact compilation and six-outcome differential behavior. Only standardize a façade if the readability benefit survives these real examples. A good editor might prove more useful than new syntax.

**Request for Board feedback, not a vote:** Is this capability-first, strictly typed presentation easier to author without hiding the existence/match decisions, or would reviewers prefer keeping canonical A while improving schema-backed templates and tooling?
