# Authoring simplification: short Board preview (0.4 research)

**Not a vote, not accepted 0.4 syntax.** Canonical 0.3 is the common output for both ideas below. The numbers here refer to the verified six-STIG evidence; [full-corpus analysis #225](https://github.com/vanderpol/scap-ng/issues/225) is a separate gate.

## Same check: RHEL 9 SV-257851, /home nosuid

**Current canonical SCAP-NG 0.3** (source-derived; metadata omitted):

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
    states:
      - field: mount_options
        value: nosuid
        operation: equals
        existence: one_or_more
        match: one_or_more
    reported_elements: all
    existence: one_or_more
    match: all
evaluate:
  test: home-mounted-nosuid-option-test
```

**Hypothetical compact authoring YAML** (explicit opt-in, separate versioned schema; not currently valid 0.3):

```yaml
authoring_format: scap-ng-compact/0.4
tests:
  home-mounted-nosuid-option-test:
    capability: linux.partition
    object:
      capability: from_test
      select:
        mount_point:
          matches_regex: '.*\\/home'
    expect:
      field: mount_options
      equals: nosuid
      existence: one_or_more
      match: one_or_more
    reported_elements: all
    require: at_least_one_all_match
evaluate: sole_test
```

The compact check must expand to the **exact canonical comparison/evaluation semantics**. Notice the field remains `one_or_more/one_or_more`, while the Test is `one_or_more/all`. Making both `all` would change meaning. Combining all example shortcuts into one fully validated compiler is **not yet complete**; independent research prototypes have proved the underlying limited transformations.

**Editor/template approach:** A user chooses `linux.partition`, selects `/home`, expects `nosuid`, chooses **at least one Item, all Items match**, chooses **at least one matching mount option**, and saves the **full canonical block above**. No new standard syntax or alternative parser is needed.

## Other instructive check: absence-only

A Windows Test with no State can currently specify:

```yaml
existence: none
match: one
```

Where `match` is never consulted because there are no States. Research shorthand:

```yaml
require: none_exist
```

The compiler can write `existence: none`, `match: all`; the research [absence audit](../slang-feedback-04/NONE-EXISTS-CANDIDATE.md) proved the technical outcome is unchanged for the 71 State-free absence Tests in the six-STIG sample. **Never** apply that no-State proof to a State field by assumption.

## Critical authoring-governance question

| Choice | Discoverability | Compiler complexity | Standard complexity |
| --- | --- | --- | --- |
| Explicit compact YAML schema | Dedicated JSON Schema, autocomplete, complete grammar and strict `oneOf` rules | Separate front-end compiler with exact lowering | Second *source grammar* to document/version |
| Editor/templates emit canonical YAML | Editor help and template catalog | Templates generate ordinary canonical files | **No new grammar**, but editor dependence for convenience |

In either case, validation SHALL reject missing or conflicting quantifiers and shall not apply implicit defaults. Full canonical NG remains readable, mandatory in packages and available to advanced authors.

**Review question:** Which approach most improves understanding and maintenance of real Checks, not merely line count? Ask this *after* the structured-capability 65-source census. Do not revisit the existing Discussion #213 ballot based solely on this draft.
