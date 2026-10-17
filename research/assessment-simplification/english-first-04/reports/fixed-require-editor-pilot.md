# Fixed `items` + `condition` six-STIG editor pilot

**Research-only. The authoring syntax is not approved.**

**871 of 872** complete automated Assessments reconstructed exactly
(**1374 of 1375** Tests); 3484 malformed-input rejection checks passed.
This is source-data structural equality only, **not OVAL scanner parity or independently demonstrated author usability**.

## One consistent requirement form

```yaml
require:
  items: at_least_one_all_match
  condition: {mount_options: {at_least_one_value_is: nosuid}}
```

The `items` field is a **documented editor-dropdown enum**, `condition` is mandatory
when the chosen Item mode evaluates a State, and absent for State-free checks.

The nested evaluate tree uses OVAL-aligned `and` / `or` (not `all_of` / `any_of`).
Conditions use `and` / `or` too. Whole-State alternatives are explicitly headed `states`.
This rename is **strictly scoped to evaluate**: State alternatives and nested State-field groups are
not indiscriminately renamed, because conflating distinct grouping scopes can change results.

## Per source folder

| Folder | Exact Assessments | Rejected |
| --- | ---: | ---: |
| apache_server_2-4_unix_server | 23 | 0 |
| ms_windows_11 | 93 | 0 |
| ms_windows_server_2025 | 110 | 0 |
| ms_windows_server_dns | 21 | 0 |
| oracle_linux_9 | 41 | 0 |
| rhel_9 | 57 | 0 |
| shared | 526 | 1 |

## Remaining blockers

- `authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml` — unproven output or Item scope

## Meaning of this result

- Legacy exact-one and all_exist variants retained separately for source-dictionary exactness; not endorsed as author dropdowns.
- Condition predicates in the pilot schema are not capability-constrained to all 100 mappings; inverse parser must validate them.
- Source-exact structural inversion is not evidence of running scanner, OVAL XML source equivalence, or human readability.
- The source 0.4 native corpus contains one known contradictory none_exist-with-attached-State Assessment; no guess or quiet repair.

## Next acceptance gates

1. Blind reading and hand-editing of these files by a security auditor.
2. Enforce capability-specific State field/operator completions for all 100 capabilities, including WMI record fields and dynamic sources.
3. Resolve/reject the single source contradiction with original DISA/NAVWAR provenance and six-state proof, not conversion guessing.
4. Independently compile and execute representative native scanner results; validate error, unknown and incomplete behavior.
5. Decide whether to retire legacy `all_exist` and collapse source-exact duplicate `exactly_one` labels under the native real-Item contract.
