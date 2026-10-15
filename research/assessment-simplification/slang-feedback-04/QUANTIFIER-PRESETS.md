# 0.4 research: a named requirement for common matching/existence pairs

**Research only · not native 0.3 syntax · no implicit defaults.** The wording comes from a [SCAP-NG 0.4 design review](https://github.com/vanderpol/scap-ng/issues/224):

> **At least one is found, and all found match expectations.**

This describes one particularly common **pair of independent requirements**. They remain separately defined in the canonical Assessment and retain all OVAL technical result semantics.

## What was measured

The [reproducible six-STIG census](https://github.com/vanderpol/scap-ng/actions/runs/38663775848) reads the published immutable 0.3 authoring ZIP, inspects 318 automated Assessment files, and tests exact shorthand expansion by comparing the complete Python dictionaries (not visually similar text).

| Scope | Canonical `existence` + `match` | Occurrences | Share |
|---|---|---:|---:|
| Test's collected Items | `one_or_more` + `all` | **359 / 560 Tests** | **64.1%** |
| State field instances | `one_or_more` + `all` | **266 / 360 field predicates** | **73.9%** |
| Combined | Same pair; **scope preserved** | **625 / 920** | **67.9%** |

Every counted candidate independently re-expanded to the **identical complete parsed Test or State field**, retaining all surrounding metadata and properties. The separate local prototype has **11 focused negative/positive guard tests**; more conformance is needed before normative adoption.

The candidate replaces two adjacent parameters with a single, **explicit** recognized preset:

```yaml
# BEFORE — canonical 0.3
existence: one_or_more
match: all

# AFTER — research-only shorthand (same scope, exact expansion)
require: at_least_one_all_match
```

The compiler looks at **where** the preset appears:
- At a Test: one or more collected Items must exist, and all collected Items must satisfy its State requirements.
- On a State field: one or more relevant observed field instances must exist, and all those field instances must satisfy the specified comparison.

The author does not lose the ability to express each parameter separately. **A partial/missing pair, an unrecognized shorthand, or a collision with explicit quantifiers is an error.** There are no inferred quantifiers.

## An essential counterexample from the real /home check

The [real RHEL 9 `/home` nosuid example in Discussion #213](https://github.com/vanderpol/scap-ng/discussions/213) uses:

```yaml
tests:
  home-mounted-nosuid-option-test:
    # Collector and predicates omitted from this focused excerpt
    states:
      - field: mount_options
        value: nosuid
        operation: equals
        existence: one_or_more
        match: one_or_more
    existence: one_or_more
    match: all
```

The **Test** pair qualifies. The **State field** pair does NOT: it requires *at least one matching mount option*, not *every observed option to equal nosuid*. The research compiler intentionally refuses to shorten that State with the all-match alias.

A future second preset could cover `one_or_more / one_or_more` where it occurs, but proliferation of barely distinguishable macro names could be **less intuitive than two explicit parameters**. Prototype only clear, frequent combinations; preserve explicit notation otherwise.

## Important boundaries and Board consideration

- **No Boolean algebra trick:** The two OVAL/NG quantifiers have different domains (Items versus observed fields), and combinations with none/only-one/optional and multi-State operators are not generally reducible. The preset is a **named pair**, not one generalized matching operator.
- **No behavior or scanner change:** The publisher/compiler expands the pair to canonical 0.3 *before* validation/packaging. Keep technical `true`, `false`, `error`, `unknown`, `not_evaluated`, `not_applicable`, collection incomplete flags, State operators and evidence requirements unchanged.
- **Do not normalize away information:** The shortcut must retain exact source values and explicit field-vs-Test scopes, with traceable compiler lowering and readable generated diagnostics.
- **Readability over raw line count:** This saves one YAML line per occurrence, but the gain we want is understanding the intended requirement. Validate that novice readers actually find `at_least_one_all_match` clearer than the two original fields.
- **Naming remains open:** An English-language UI could present “At least one exists, all match.” The serialized token is only a demonstration, not an approved enumeration.

**Provisional recommendation:** Take this narrowly scoped, strongly evidenced shorthand to the Board as an informational 0.4 alternative—not a change to the frozen 0.3 grammar or to the current vote on Discussion #213. [Implementation/census](../../../../tools/research_04_quantifier_aliases.py) · [unit guards](../../../../tools/test_research_04_quantifier_aliases.py) · [tracking issue #224](https://github.com/vanderpol/scap-ng/issues/224).
