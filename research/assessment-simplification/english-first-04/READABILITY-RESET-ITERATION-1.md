# 0.4 authoring readability reset — iteration 1

**18 October 2026 · Issue [#235](https://github.com/vanderpol/scap-ng/issues/235) / [#227](https://github.com/vanderpol/scap-ng/issues/227) · Research only.** This is an editor-independent, human-authoring investigation. **No normative schema, compiler, converter, pinned content, or accepted semantic contract changes.**

## Finding: replacing technical nouns with more English is not sufficient

After rereading [all five complete before/after examples](BEFORE-AFTER-REVIEW.md), the critical cost is **how far a reader must jump to understand where data comes from and what makes a Test pass**, not line count. The existing English-first research makes the small case arguably longer and the Apache case scarcely easier. We should not call the English-first candidate the winner on evidence from reconstruction, YAML savings or machine-green conversion alone.

| Grounded case | What a first-time author has to resolve | What the current English-first rewrite does | First improvement to test |
| --- | --- | --- | --- |
| [Simple Linux /home nosuid](FULL-01-linux-home.md) | Distinguish matching at least one **mount option** from requiring at least one **mount Item**, and know what happens if /home is missing | Splits one explicit Item requirement into a Boolean pair under `require`; uses `some_values_is` (awkward English); adds empty `sources: {}` and `description: null` | Keep distinct explicit requirements but remove decorative containers; prefer an ordinary field-key predicate |
| [Linux initialization files](FULL-02-linux-files.md) | Discover actual users, exclude system/root-directory accounts, expand **collected** home directories, select dotfiles, exclude directories, compare eight bits; understand **different zero-Item policies** for root/non-system | `gather.union` of one operand and nested `from.inspect` obscures the actual operation; reads like Test-per-user rather than collecting files per user | Show collection dataflow as named, ordered sources; explain once why unary Set remains for roundtrip; do **not** silently remove it |
| [Windows 11 deny RDP](FULL-03-win11-rights.md) | Separate WMI role records, user-right trustee identities and the **three OR branches**; keep nested record/record-field cardinality | Long names and deeply nested `any_of` / `every_record` obscure cross-test choices | Show branches as a review outline tied to *exact* Test IDs; do not rewrite six-state logic into procedural `if/else` |
| [Windows Server DNS](FULL-04-dns.md) | Understand zone discovery, command Variables, signed zones and two distinct validity-period Tests; distinguish **no output lines** from **no collected command Item** | Adds readable checks but hides command construction behind still-complex Variables; `no_values_exist` under `at_least_one_item_exists` is easily misread as a contradiction | Make command dataflow discoverable; preserve separate command-Item and stdout-field multiplicity; verify that each Variable is defined |
| [Apache configuration](FULL-05-apache.md) | Follow 18 Variables/derived shell commands, included versus actually loaded files, and mandatory/conditional `KeepAlive`/`MaxKeepAliveRequests` policies | Despite a better check section, the ~345-line after document keeps a long, hard-to-author expression graph | Prioritize source composition/reuse and explicit dataflow, *not* another round of keyword replacements; do not change command execution or optional-field semantics |

**The first-read threshold:** The reviewer must be able to answer (a) *what was collected and from where*, (b) *what population or fields must exist*, (c) *which predicates are enforced and for how many Items/values*, and (d) *how errors/incomplete results affect the conclusion* **without guessing a keyword default**.

## A tighter third candidate for the complete simple check

Below is **illustrative authoring research, neither current valid 0.4 nor a runnable compiler input**. It tests one design direction: keep the source's exact field predicates and distinct quantifiers; reduce wrappers instead of inventing longer paraphrases. This is deliberately presented against the [complete unchanged current 0.4 and generated English-first documents](FULL-01-linux-home.md) rather than silently replacing either.

```yaml
# RESEARCH — one candidate authoring grammar, NOT a supported spec.
assessment:
  id: ng.shared.home-is-mounted-with-the-nosuid-option
  version: 1
  assessment_title: >-
    Linux must prevent files with the setuid and setgid bit set from being
    executed on file systems that contain user home directories.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
  checks:
    home-mounted-nosuid-option-test:
      check: /home is mounted with the nosuid option.
      inspect: linux.partition
      where:
        mount_point:
          matches_regex: .*\/home
      collected_items_require: at_least_one_exists_and_all_match
      states:
        - mount_options:
            require: at_least_one_exists_and_some_match
            equals: nosuid
      reported_elements: all
  evaluate:
    test: home-mounted-nosuid-option-test
```

**Why this is an experiment worth testing, not an acceptance proposal:** It has no empty `sources`, no artificial `gather`, and keeps the exact original regular expression, Test Item rule, mount-options rule and Test reference. It keeps `states` for now because changing it to `must` or `expect` without defining alternative States and nested Windows records creates another ambiguity. The actual original `object.capability` and inline `select` lowering need explicit reversible verification, even though the simpler research `where` mapping exists.

This candidate retains technical names intentionally. We have not established that `check` is better than `test_title`, `inspect` than `capability`, `where` than `select`, or `and/or` than `all/any` to a novice. Test the concepts independently rather than coupling them to superficial word changes.

### Terms that still require explicit semantics, even in a readable syntax

- `collected_items_require: at_least_one_exists_and_all_match` describes the **Item population**. A complete collection with zero /home Items must not pass.
- `mount_options.require: at_least_one_exists_and_some_match` describes a **multi-valued field** on each selected Item; it does not change the number of selected mounts required.
- The `where` regex is the original selector, not automatically an anchored exact `/home` lookup.
- `reported_elements: all` is retained explicitly; dropping it would need a declared default and evidence policy.
- A partial collection, missing field, duplicate Item, unexpected field type, unavailable capability, and `unknown/error/not_applicable` cannot be compressed to Boolean success/failure. No hidden default is permitted.

## Five grammar goals with measurable authoring tests

1. **One concept, one placement.** Ordinary native selection is alongside the collector. A named reference uses `from`. A composed Set has an explicit operator/operands and filters on the *operand* they apply to. An optional `gather` wrapper is justified only if it distinguishes a new concept; today it does not clearly do so.
2. **One explicit Item-versus-field distinction.** Prefer the demonstrated `collected_items_require` and field/record `require` scoping to long Boolean prose if the latter misleads authors. Keep record-cardinality and `states_match` separate. Repetition-elimination via scoped `state_fields_require` is promising, but review on real Windows exception `SV-253274` before adoption.
3. **No obscure synonyms.** The current experimental `some_values_is`, `exactly_one_is`, `all_states`, `all_of` and `any_of` should be compared to consistent comparator names and existing `all/any/not`. `and/or` may be accepted only when it does not conflict with field keys or alter six-state behavior.
4. **Collections visible before magic names.** A reader should follow every `for_each.in`, `from`, Variable and command input to a locally defined source; show which collected Item supplies `user.home_dir`. Do not treat long source IDs as sufficient documentation.
5. **Explainable rather than merely shorter.** An authoring IDE may help, but human-visible source must stand alone. If a real Apache or DNS check requires ten hops, reducing indentation alone does not meet the goal.

## Next safe iteration — no language decision required yet

- Use [blind-review packet](AUDITOR-FIRST-READ-PACKET.md) with **no answer key** for a reviewer unfamiliar with the design. Track inferred meaning, unsupported defaults, and different interpretations—do not ask whether the YAML “looks nice.”
- Revisit one **complex** complete example at a time: first the Linux initialization-file collection, then the seven-Test Windows role/right check; document all source references and preserve the original evaluate shape. Avoid presenting a selected excerpt as a full valid Assessment.
- Make a human readability change *only if* it reduces a concrete ambiguity, number of lookup hops, copy/paste errors or time-to-author. For each survivor, prove reversible 0.4-A lowering and expected-results boundaries separately.
- Keep the current schema, conversion/IR and 65-STIG release gates unchanged; there is **no** new compiler assignment from this readability work.

**Request for later owner review:** Compare the full original 0.4, the complete previously generated English-first, and this shorter simple third candidate. The goal is a single standard—not a permanent second or third dialect.
