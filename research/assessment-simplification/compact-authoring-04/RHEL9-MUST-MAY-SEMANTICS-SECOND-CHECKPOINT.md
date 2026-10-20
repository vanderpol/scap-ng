# RHEL 9 0.4-A must/may — semantics-first decision log (research)

**2026-10-20 | Refs #227 #246 | Not an approved grammar.** This note builds on, and does not claim to originate, the prior 0.4-A English-first, scoped requirements, and quantifier-alias research.

## Current evidence

Pinned full *actual 0.4.0 source documents* for home-nosuid and initialization-file permissions are embedded in `tools/test_rhel9_must_may_full_source.py`, including source Git blob identifiers. They contain three Tests in two complete Assessments. `tools/test_rhel9_must_may_inline_states.py` tests placing existing local State expressions **under** `require.all_items_must`, rather than using a Boolean placeholder. The complete document can then be lowered back to the original parsed Assessment without changing Objects, States, filtering, `for_each`, evaluation trees, or other source fields. These scripts were committed; independent GitHub Actions results must be inspected before asserting green CI.

`tools/test_rhel9_must_may_complete_evidence.py` enumerates known Boolean predicate outcomes for Item populations of length 0..4. It rejects incomplete/nonboolean evidence and highlights these semantics:

| Requirement | Empty selected Items | One item, predicate false | Two items, both predicate false |
| --- | --- | --- | --- |
| `items: one_or_more` + `all_items_must` | false | false | false |
| `items: may_be_absent` + `all_items_must` | true | false | false |
| `items: may_be_absent` + `no_items_may` | true | true | true |
| `items: none` (no predicates) | true | false | false |

The third and fourth rows **are not equivalent**. An absence check for prohibited packages is naturally `items: none` after selecting the prohibited population. Predicate quantification operates over existing Items.

## Local State syntax candidate

Use Test-local Objects and put the previously local State clauses directly under the human-facing requirement.

```yaml
# Illustrative only; not legal versioned 0.4-A YAML
home-mounted-nosuid-option-test:
  capability: linux.partition
  object:
    capability: linux.partition
    select:
      mount_point:
        matches_regex: .*\\/home
  require:
    items: one_or_more
    all_items_must:
      - mount_options:
          require: at_least_one_exists_and_some_match
          equals: nosuid
```

This does **not** yet solve State-field vocabulary. It intentionally keeps the inner quantifier visible: each collected filesystem may expose multiple `mount_options`, at least one of which equals `nosuid`; do not require all options to equal `nosuid`. Retain the original regex and avoid silently narrowing to the exact `/home` mount.

For RHEL 9 initialization files the `all_items_must` entry would be a local `and` group with eight permission flags, not a remote shared State. The two original Tests differ in `items: may_be_absent` versus `items: one_or_more`. They are deliberately not merged.

## No premature adoption

- The small reversible mapping covers only the tested RHEL 9 common combinations. It does not encompass all OVAL 5.12.3 existence/match pairs or original six-state result tables.
- `exactly_one_item_must` counts satisfying Items, while `items: exactly_one` restricts *collected* Item population. `at_least_one_item_must` and `no_items_may` should only be adopted after validating true source uses, not from attractive names alone.
- Inline `all_items_must` is the more coherent choice versus a separate `states` plus `all_items_must: true` declaration, but it is an experimental authoring syntax, not yet tested through native schema/source compiler.
- The next engineering gate is a semantic-differential six-state evaluation against original OVAL formulas on empty/partial/error/unknown/not-evaluated/not-applicable collections, with negative fixtures and a reviewer who has not seen the proposal.
- Do not ship another competing language or change 0.4-A without evidence. Follow trunk-only workflow and preserve older experimental files as evidence.
