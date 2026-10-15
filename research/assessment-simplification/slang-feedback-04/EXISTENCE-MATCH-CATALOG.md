# Complete observed existence/match pair catalog — 0.4 research

**Scope:** Published immutable 0.3 six-STIG authoring corpus (318 automated Assessment files), **560 named Tests** and **360 State-field predicates**. This is a complete census of **observed pairs in this corpus**, not a list of all theoretically valid combinations or adopted shorthand identifiers. The full [reproducible analysis](https://github.com/vanderpol/scap-ng/actions/runs/38663775848) and [source/code](../../../../tools/research_04_quantifier_aliases.py) are available.

## 13 distinct observed combinations (920 total occurrences)

`existence` applies to the relevant domain (collected Test Items or observed State-field instances); `match` then combines the result of evaluating that domain's members. The two axes are independent. The exact *canonical* pair survives macro expansion, including collection statuses and six technical outcomes.

| Canonical `existence` | Canonical `match` | Test uses | State-field uses | Total | Possible authoring preset |
|---|---|---:|---:|---:|---|
| `one_or_more` | `all` | **359** | **266** | **625** | `at_least_one_all_match` — **tested prototype** |
| `none` | `all` | 68 | 21 | **89** | `none_found` — idea only |
| `one_or_more` | `one_or_more` | 47 | 11 | **58** | `at_least_one_some_match` — idea only |
| `all` | `all` | 43 | 0 | **43** | `all_exist_all_match` — idea only |
| `optional` | `all` | 20 | 22 | **42** | `optional_all_match` — idea only |
| `one` | `all` | 0 | 18 | 18 | Keep explicit until review |
| `one_or_more` | `none` | 0 | 15 | 15 | Keep explicit until review |
| `one_or_more` | `one` | 14 | 0 | 14 | Keep explicit until review |
| `optional` | `none` | 3 | 7 | 10 | Keep explicit until review |
| `none` | `one` | 2 | 0 | 2 | Keep explicit |
| `one` | `one` | 2 | 0 | 2 | Keep explicit |
| `none` | `one_or_more` | 1 | 0 | 1 | Keep explicit |
| `optional` | `one_or_more` | 1 | 0 | 1 | Keep explicit |
| **Total** | | **560** | **360** | **920** | |

- **Top one:** 625/920 (67.9%).
- **Top three:** 772/920 (83.9%).
- **Top five:** 857/920 (93.2%).
- **13** unique pairs are present, but some exist only in one scope: **11** Test-level variants and **7** State-field variants.
- All counts are occurrences in this published six-STIG sample, not claims about all OVAL authoring worldwide.
- The proposed names other than `at_least_one_all_match` have **not** been implemented or verified by the research compiler, although a mechanically defined name→pair expansion is straightforward.

## Important difference between Test and State scope

Research-only example:

```yaml
# On a named Test — Items:
require: at_least_one_all_match
# expands to Test existence: one_or_more, match: all

# On a State field — observed values:
require: at_least_one_all_match
# expands to State field existence: one_or_more, match: all
```

The semantics do not merge across these scopes. The actual RHEL 9 SV-257851 `/home` rule's Test pair qualifies; its `mount_options` field has `existence: one_or_more, match: one_or_more` and must **not** adopt the all-match shorthand.

## Naming caution and proposed selection principle

Only introduce an alias when a human reader understands it **faster** than the two explicit fields. For instance:

- `at_least_one_all_match`: at least one found, and **every** found member matches.
- `at_least_one_some_match`: at least one found, and at least one found member matches. (Potentially clearer as `at_least_one_matches`; still unapproved.)
- `none_found`: no member may exist; the expansion would still hard-code `match: all`, not silently remove it.
- `all_exist_all_match`: **not** the same as `one_or_more/all`; OVAL all-exist semantics have distinct status handling.
- `optional_all_match`: existence mode `optional` is **not** permission to reinterpret errors, unknowns or incomplete collection.

A preset is explicit authoring syntax and must be expanded **before canonical validation**. Missing, conflicting or unsupported pairs still fail; avoid schema defaults. An editor could instead show human-language choices while storing the unchanged pair, requiring **zero new standard tokens**.

**Suggested next gate:** Evaluate at most the top three names against side-by-side real examples and six-outcome differential tests, then separately decide whether the less-common `all/all` and `optional/all` aliases improve readability. Do not revise Discussion #213 or current 0.3 grammar based on this catalog alone.

[Issue #224](https://github.com/vanderpol/scap-ng/issues/224) · [initial one-preset proof](QUANTIFIER-PRESETS.md)
