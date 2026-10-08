# One Assessment, two vocabularies

> **RESEARCH ONLY — the Ansible-inspired YAML below is NOT SCAP-NG 0.3 syntax, is NOT schema-valid, and is NOT executable by the current converter/compiler/scanner.** No specification or 0.3 decision changes here.

**Question:** Which words best express a simple check: the existing OVAL-aligned `Test / Object / State / evaluate`, or verbs such as `collect / where / expect / require / report`?

Both examples start from **RHEL 9 STIG SV-257851**: check whether the `/home` filesystem has the `nosuid` mount option. The current code is copied from the maintained [Assessment showcase](../../../specification/examples/assessments.md#2-the-automated-check-keeps-its-object-and-state-nearby). Both snippets omit surrounding Assessment metadata. Only the first uses actual 0.3 field names.

## Current SCAP-NG 0.3 — actual syntax

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

The **Test** uses `linux.partition`; its **Object** selects the mount point by regex; its **State** compares reported mount-option values; `evaluate` chooses this named Test. Nothing here is a proposed new language.

## Ansible-inspired phrasing — deliberately invalid YAML for SCAP-NG

```yaml
check:
  id: home-mounted-nosuid-option-test
  collect: linux.partition
  where:
    mount_point:
      matches_regex: '.*\/home'
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

This speculative shorthand keeps a named check for result provenance and preserves the visible selector regex, datatype, existence and aggregation choices. It deliberately does **not** claim to be a lossless lowering rule or a validated replacement for the real Test.

## Which verbs read better?

| Current 0.3 | Research-only wording | Question for authors |
| --- | --- | --- |
| `tests` and single-Test `evaluate` | `check` | Is one direct check easier to understand without sacrificing Test identity and multi-Test composition? |
| `capability` + `object` | `collect` | Is acquisition clearer as a verb? How would Objects whose capability differs from their Test stay explicit? |
| `object.select` + `operation: pattern_match` | `where` + `matches_regex` | Does `where` signal selection rather than a security expectation? |
| `states` and `state.field` | `expect` | Does `expect` read better than `state` without implying a simple Boolean assertion? |
| `existence` and `match` at the Test | `require.collected_items` and `require.matching_items` | Do these names explain which quantifier applies to Items? |
| `reported_elements: all` | `report.elements: all` | Is `report` concise without confusing evidence retention with collection/evaluation? |

## Semantics we cannot abbreviate away

- The exact source selection regex remains `.*\/home`; silently changing it to the literal path `/home` could change which partitions match.
- **Two levels of quantification remain distinct:** the Test requires at least one collected Item and checks *all* matched Items; the State requires one or more present `mount_options` values, with one or more satisfying the equality comparison.
- Source Test, Object and State each declare `linux.partition`. Collapsing those into one `collect` name would require rules for different-capability combinations, not an implicit default.
- Missing Items, missing fields, datatype errors, `unknown` and other OVAL truth/status behavior must retain their real meaning. Neither `expect` nor `require` may turn those into a fabricated pass or fail.
- A direct `check` would need a defined answer for **multiple Tests, `evaluate` trees, named references, Variables, shared Objects, Organizational Input and provenance** before it could replace anything.
- `report` describes visible fields, **not** a scanner's evidence cap, redaction authority, collection limit, or change to technical truth.

**Discussion boundary:** This page is only about naming and the readability of one simple Assessment. It does not propose adopting Ansible modules, Jinja, arbitrary shell commands, implicit defaults, or a second accepted SCAP-NG language. A syntax change would need a separately reviewed schema/compiler mapping, counterexamples and independent semantic tests.

Further background: [earlier Ansible-inspired research](README.md) and its [straw-man vocabulary](STRAW-MAN-SYNTAX.md). The accepted current language remains in the [0.3 Assessment specification](../../../specification/assessment/assessment-method.md). The broader post-0.3 architecture discussion is tracked in [issue #197](https://github.com/vanderpol/scap-ng/issues/197).
