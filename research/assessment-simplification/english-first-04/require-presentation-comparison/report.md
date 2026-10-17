# Merged versus split requirements — six-STIG experimental proof

**Research only. Neither grammar is approved; not scanner/OVAL execution parity or an auditor usability study.**

- Corpus: **872 automated Assessments**, **1375 named Tests**.
- Split: **871/872 full Assessments**, **1374/1375 Tests** exactly reconstructed.
- Merged: **871/872 full Assessments**, **1374/1375 Tests** exactly reconstructed.
- Both: 1742 invalid-input mutations rejected by schema AND decoder.
- Source-legacy all_exist Tests retained explicitly: **201**. These are **not** proof they can be changed to at-least-one on incomplete observations.

## One simple real RHEL nosuid requirement

Split (author can see how many Items exist versus how many must match):

```yaml
require:
  items: at_least_one
  match: all
  condition:
    mount_options: {at_least_one_value_is: nosuid}
```

Merged (the Item existence/match rule is named as one thought):

```yaml
require:
  at_least_one_exists_and_all_match:
    mount_options: {at_least_one_value_is: nosuid}
```

## Measured encoding size (requirements only; not cognitive readability)

| Presentation | YAML characters | YAML lines | Longest generated line |
| --- | ---: | ---: | ---: |
| split | 189029 | 9916 | 179 |
| merged | 178250 | 7942 | 179 |

## Six-STIG requirement modes (source exact)

| Source mode | Tests | Split existence / match | Merged name |
| --- | ---: | --- | --- |
| `at_least_one_all_match` | 749 | `at_least_one` / `all` | `at_least_one_exists_and_all_match` |
| `at_least_one` | 156 | `at_least_one` / *(none)* | `at_least_one_exists` |
| `all_exist` | 127 | `legacy_all_exist` / *(none)* | `legacy_all_exist` |
| `none` | 102 | `none` / *(none)* | `none_exist` |
| `all_exist_all_match` | 73 | `legacy_all_exist` / `all` | `legacy_all_exist_and_all_match` |
| `at_least_one_some_match` | 67 | `at_least_one` / `some` | `at_least_one_exists_and_some_match` |
| `if_present_all_match` | 67 | `if_present` / `all` | `if_present_all_match` |
| `at_least_one_one_match` | 21 | `at_least_one` / `exactly_one` | `at_least_one_exists_and_exactly_one_matches` |
| `exactly_one_all_match` | 3 | `exactly_one` / `all` | `exactly_one_exists_and_all_match` |
| `if_present_none_match` | 3 | `if_present` / `none` | `if_present_none_match` |
| `exactly_one` | 2 | `exactly_one` / *(none)* | `exactly_one_exists` |
| `exactly_one_one_match` | 2 | `exactly_one` / `exactly_one` | `exactly_one_exists_and_exactly_one_matches` |
| `all_exist_none_match` | 1 | `legacy_all_exist` / `none` | `legacy_all_exist_and_none_match` |
| `if_present_some_match` | 1 | `if_present` / `some` | `if_present_some_match` |

## Interpreting the result

- These two forms preserve precisely the same typed condition tree and source/collector graph; only the `require` presentation differs.
- `items: none` is not `match: none`; presence and matching remain different concepts.
- `items: exactly_one` detects duplicates and is not equivalent to `match: exactly_one`.
- Complete Windows whole-State OR groups preserve `scope: states`; not flattened into field/record membership.
- One known invalid source Assessment (`none_exist` Test with State) is expected to remain rejected.
- 201 inherited `all_exist` uses remain **importer-only legacy distinctions** pending a native six-state/evidence contract. This test does not remove them.
- Size reduction cannot choose the winning author syntax: blind auditor review of both versions, and independent runtime differential tests remain required.

## Full real research examples

Each example has both complete representations, including all original named sources and `evaluate` logic. See the adjacent `*.split.research.yaml` and `*.merged.research.yaml` files.

## Rejected original Assessment

- `authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml` — unproven output or Item scope
