# Existing SCAP-NG comparison operators — six-STIG proof

**Research only; this is not the adopted 0.4 schema or scanner semantics proof.**

- **871/872** complete automated Assessments, **1374/1375** named Tests exactly inverted.
- Replaced **1494** English-first comparison aliases with existing SCAP-NG operators.
- Reject old-condition mutations in **871** source-backed Assessments.
- Item, matching, record, field and State quantifiers unchanged from the prior experiment.
- 201 importer-legacy all_exist Tests remain explicit and unchanged.

## Windows 11 role query (real SV-253495)

```yaml
require:
  items: at_least_one
  match: all
  states:
    or:
      - result:
          records: at_least_one
          match: all
          domainrole: {equals: "1"}
      - result:
          records: at_least_one
          match: all
          domainrole: {equals: "3"}
```

## Source-derived comparison conversions

| Previous operator alias → existing operator | Instances |
| --- | ---: |
| `is_to_equals` | 1280 |
| `equals_ignoring_case_to_case_insensitive_equals` | 66 |
| `at_least_one_value_is_to_at_least_one_value_equals` | 37 |
| `at_most_to_less_than_or_equal` | 36 |
| `at_least_to_greater_than_or_equal` | 35 |
| `exactly_one_is_to_exactly_one_equals` | 13 |
| `is_not_ignoring_case_to_case_insensitive_not_equal` | 8 |
| `is_not_to_not_equal` | 8 |
| `version_at_least_to_version_greater_than_or_equal` | 3 |
| `when_present_is_to_when_present_equals` | 3 |
| `when_present_at_most_to_when_present_less_than_or_equal` | 2 |
| `at_least_one_value_version_at_least_to_at_least_one_value_version_greater_than_or_equal` | 1 |
| `no_values_is_to_no_values_equals` | 1 |
| `when_present_at_least_to_when_present_greater_than_or_equal` | 1 |

## Limits

- Exact dictionary round-trip is not independent proof of OVAL scanner/runtime/evidence equivalence.
- Structural predicates and value-matching cardinalities are unchanged; genuine boolean values (`false`/`true`) remain data.
- The remaining source-shape exception must not be repaired speculatively.

## Rejected source Assessments

- `authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml`: unproven output or Item scope

## Full source-backed examples

See the neighboring `*.canonical.research.yaml` files.
