# 0.4-A RHEL 9 must/may vocabulary — research checkpoint

**20 October 2026 · Refs #227 and #246 · research only; no schema or scanner change.**

## Purpose and prior work

Focus on ordinary RHEL 9 checks, not Apache outliers. Preserve v0.4-A Test-local States and private Objects. Reuse prior English-first studies, including `research/assessment-simplification/english-first-04/FULL-02-linux-files.md` and `research/assessment-simplification/compact-authoring-04/ONE-GRAMMAR-DECISION.md`; do not claim earlier constant inlining or quantifier work as novel.

## Candidate: source-backed /home nosuid check (SV-257851)

The pinned source-derived 0.4 preview uses a `linux.partition` selection with `mount_point.matches_regex: .*\\/home`, a `mount_options` field requiring at least one matching value, and a Test requiring one-or-more Items with *all* matching.

```yaml
# Illustrative alternative, NOT valid 0.4-A
tests:
  home-mounted-nosuid-option-test:
    capability: linux.partition
    object:
      select:
        mount_point:
          matches_regex: .*\\/home
    require:
      items: one_or_more
      all_items_must:
        mount_options:
          contains: nosuid
```

Interpretation: at least one selected filesystem Item must exist; each selected Item must have at least one mount-option value equal to `nosuid`. Do **not** silently tighten the inherited regex to an exact /home selector. The `contains` predicate here is a proposed capability/field-specific shorthand for `mount_options.require: at_least_one_exists_and_some_match; equals: nosuid`, not a generic string-substring comparison and not yet a validated lowering.

## Negative packages: do NOT substitute predicate quantification for nonexistence

RHEL 9 SV-257826's 0.3 source-derived `linux.rpminfo` Test selects packages matching `ftp` and asserts `existence: none_exist` without a State. If the selector enumerates the prohibited population, absence is properly stated as `items: none` (subject to source-exact 0.4 selectors). The tempting form `no_items_may: name equals ftp` is **not** an automatic substitute: it conflates the selection population with State matching, and can differ under partial/error/unknown evidence. Do not translate it mechanically.

```yaml
# Conceptual shape only; exact source selector and empty/error
# policy must be preserved by an explicit, verified translator.
require:
  items: none
```

## Permissions: preserve field-vs-Item cardinality and vacuous success distinctions

RHEL 9 SV-257889 uses a `unix.file` Test for non-system-user initialization files allowing zero Items, plus a different Test for root files requiring at least one Item. Both test eight independent per-file permission bits, and both require *every selected file* to satisfy them. A uniform `all_items_must` does **not** imply nonempty collection.

```yaml
# Conceptual Test requirement for non-system-user files
require:
  items: zero_or_more
  all_items_must:
    setuid: {equals: false}
    setgid: {equals: false}
    sticky: {equals: false}
    group_write: {equals: false}
    group_execute: {equals: false}
    other_read: {equals: false}
    other_write: {equals: false}
    other_execute: {equals: false}
```

A separate root-file Test would set `items: one_or_more`. These fragments omit the necessary source selectors and per-field existence requirements; they are **not** complete replacement assessments or proven semantic parity.

## Vocabulary evaluation / decision gate

- Favor `all_items_must`, `at_least_one_item_must`, `exactly_one_item_must`, `no_items_may` for candidate UI labels/grammar **only when a predicate exists**.
- Quantifier `exactly_one_item_must` denotes exactly one satisfying Item among the selected Items; this is **not** the same as exactly one Item existing. Keep `items: exactly_one` separate.
- `no_items_may` means no collected Item may satisfy the predicate; it must NOT mean the Object returns zero Items. Distinguish this from `items: none`.
- `items` and `*_items_must` should not acquire implicit existence defaults. A bounded candidate may permit no-match/optional combinations, but must define empty/partial/error/unknown/not-evaluated/not-applicable behavior and reject unsupported source pairs.
- The `all_items_must` structure is clearer when its predicates are State-local; never move predicates to top-level shared States merely to shorten a file.
- `contains` must explicitly mean element membership for multivalued `mount_options`, not a scalar substring operation. Prefer `contains_value` if ambiguity survives independent first-read evaluation.
- The permission-bit source represents eight named Boolean assertions; do not collapse to numeric chmod comparison without source proof.
- Avoid overclaiming: these are first-read design candidates; no code-based compiler or six-state runtime equivalence test has been run for the syntax in this document.

## Next validation boundary

Build an explicit, context-sensitive lowerer for the existing pinned RHEL 9 /home, package absence, and initialization-file examples; then evaluate empty, multiple, partial, and error evidence. Measure first-read comprehension, not just line counts. Only then consider a 0.4-A schema change; remain on main and leave normative files unchanged.
