# 0.4 research — make Item and field requirements understandable

**Status: proposal for author review, NOT adopted 0.4 syntax.** Source-backed context: [RHEL 9 `/home` `nosuid` example](ASSESSMENT-REVIEW-OVERVIEW.md#three-ng-examples-from-the-actual-six-stig-r3-content) and [Discussion #213's Slang feedback](../slang-feedback-04/README.md). Before freezing 0.4, test whether the language itself can express this check in ordinary words, rather than relying on explanatory prose.

## The actual requirement, without OVAL terminology

> **Find one or more partitions selected by the Object. Every selected partition must have at least one mount option equal to `nosuid`.** Other mount options (such as `rw` and `nodev`) are allowed.

| Selected partition | Its observed `mount_options` | Field expectation | Whole Test |
| --- | --- | --- | --- |
| `/home` | `[rw, nosuid, nodev]` | Pass: `nosuid` occurs | Pass if this is the only selected partition |
| `/home` | `[rw, nodev]` | Fail: no `nosuid` | Fail |
| `/home` and `/var/home` | first contains `nosuid`, second does not | First pass, second fail | **Fail**: not all selected partitions pass |
| None | no selected Items | No field check | **Fail**: at least one Item must exist |

Incomplete and error collections are **not** automatically false (or true); OVAL's six-result reference semantics must be preserved. The source Object currently selects `mount_point` by regex `.*\\/home`; do not tighten it to exact `/home` simply for better readability.

## A. Current 0.4 research preview: long fused names

```yaml
      states:
      - mount_options:
          equals: nosuid
          require: at_least_one_exists_and_some_match
      collected_items_require: at_least_one_exists_and_all_match
```

**Strength:** one field per scope; every combined existence/matching pair is explicit. **Problem:** author must decode 20 controlled phrases and remember *which population* each phrase describes. The same word `match` refers to distinct Item and field scopes.

## B. Candidate to test: short, structured requirements with two explicit axes

```yaml
      states:
      - mount_options:
          equals: nosuid
          require: {exists: at_least_one, matches: some}
      collected_items_require: {exists: at_least_one, matches: all}
```

**How to read:** “Some **values** of `mount_options` equal `nosuid`. All selected **Items** must have a matching State. Both populations must be nonempty.”

- `exists` and `matches` are **independent axes**. They replace *one* fused name; they do not introduce a second authoring dialect.
- `exists:` values: `none`, `exactly_one`, `at_least_one`, `all`, `optional` map to the five original existence modes. **Do not** interpret `all` as `at_least_one`; OVAL collection semantics can differ.
- `matches:` values: `none`, `exactly_one`, `some`, `all` map to OVAL match cardinality. `some` means **one or more**, not “any value including zero.”
- Both keys are mandatory for a State-bearing Test or State field, including rare `none` existence combinations; do not invent defaults or drop “inert” original comparisons.
- For a **State-free Test**, only `exists` is needed after the existing source-equivalence proof that its matching mode is inoperative. The context must be known to the compiler and source audit.
- Preserve scoping: `state_fields_require` at Test/group scope can use this same map; **record and nested record-field scopes stay separate**. `value_match` of array/Variable expected operands is a third independent dimension and **must not** be merged.
- No implicit inheritance across the collected-Item/State-field boundary. Missing either axis for a State-bearing predicate, unknown scope, or conflicting scoped overrides **fails validation**.

This uses two small typed enums instead of asking a human to decode twenty concatenated enum labels. It is *not* fewer YAML parameters than OVAL, but the nesting and explicit scope are easier to teach and can be rendered on one short inline line.

## C. A tempting natural-language membership predicate — needs much stronger limits

```yaml
      states:
      - mount_options:
          includes_value: nosuid     # hypothetical, NOT legal 0.4
      collected_items_require: {exists: at_least_one, matches: all}
```

This is attractive: “the `mount_options` field **includes** `nosuid`.” But `includes_value` would have to be a **fully specified compound operator**, not `equals` with a hidden default. It would lower to *exactly* `equals: nosuid` plus `exists: at_least_one, matches: some` **only when** the capability schema confirms the field is a multi-valued entity of the correct datatype. It must not be a substring comparison on a scalar string.

Before adding such a key, disprove mismatches for missing field, empty/partial Item collection, errors, duplicate observed values, unexpected datatype, and expected-value arrays/Variables (`value_match`). A general `contains` or `includes` synonym is **not recommended** without that proof. Nor should the author be offered both A and B as optional legal ways to spell one normative 0.4 Assessment.

## Apply the same idea to harder real content

| Real example | Existing label | Candidate structured form | Important scope |
| --- | --- | --- | --- |
| RHEL 9 `mount_options=nosuid` | `at_least_one_exists_and_some_match` | `{exists: at_least_one, matches: some}` | Field values within one partition |
| RHEL 9 collected partitions | `at_least_one_exists_and_all_match` | `{exists: at_least_one, matches: all}` | Collected Items |
| Win Server DNS `stdout_line=True` | `only_one_exists_and_matches` | `{exists: exactly_one, matches: all}` | Field values of one command Item |
| Apache optional `KeepAlive On` line | `may_be_absent_and_all_match` | `{exists: optional, matches: all}` | Field values; absent is not error |
| Win 11 `stderr_line` must be absent | `none_exist` | `{exists: none, matches: all}` when a State comparison survives | Field absence (not zero command Items) |
| Win 11 nested WMI record | `at_least_one_exists_and_all_match` | `{exists: at_least_one, matches: all}` | **Both** record and `domainrole` member, separately |

These are **syntactic translations**, not newly executed scan examples. Preserving the exact original OVAL two-axis pair is required; any special absence-only simplification must be separately proven.

## Proposed decision gate — before freezing 0.4

1. Test **A vs B**, blind, with novice readers and at least one original author/OVAL implementer. Ask them to predict outcomes for: `[rw,nosuid]`, `[rw]`, two selected mounts with one failing, no mounts, and incomplete/error collection.
2. Exhaustively round-trip every current **20 State-bearing requirement names** and **5 State-free presence names** between current 0.4 candidate and B. Reject missing/conflicting keys. Compare results against existing pinned six-state reference fixtures, **not just byte-equivalent serialization**.
3. Include Windows nested records, alternative registry States, source `none`/exact-one conditions and array `value_match`. Be able to point to the exact OVAL source graph and collection status for each.
4. If B is genuinely clearer, promote **one** structured form everywhere in the 0.4 schema, native capability schemas, converter, examples and editor. Do not expose A and B as permanent mutually accepted dialects.
5. Treat C as a later candidate only if it clearly improves author comprehension *and* has a strict source/capability proof. Otherwise stop at B and retain `equals` plus explicit scoped requirements.

**Provisional recommendation:** B deserves a real readability/semantic proof before 0.4 becomes normative. A has enough validated source coverage to be a comparison baseline, not necessarily the best human-facing syntax. A reviewer's inability to explain the original pair is a genuine authoring-design warning, **not** grounds for weakening the source assessment meaning.

Tracking: [vocabulary / semantics #227](https://github.com/vanderpol/scap-ng/issues/227) · [semantics gate #229](https://github.com/vanderpol/scap-ng/issues/229) · [scope inheritance research](SCOPED-FIELD-REQUIRE-REVIEW.md) · [source pair census](../slang-feedback-04/EXISTENCE-MATCH-CATALOG.md).
