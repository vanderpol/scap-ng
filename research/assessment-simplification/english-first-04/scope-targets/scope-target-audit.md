# Combined Item/field scope — real six-STIG feasibility audit

**Research only; no proposed `scope: items_and_fields` form is approved or source-evaluator verified.**

The question is whether one cardinality declaration can apply to both **collected Items** and **ordinary State field values**. They are different populations, and Windows record members form another separate population. Equal source enum names do not imply identical data or scanner result behavior.

- Corpus: **872 unique automated Assessments / 1375 named Tests**.
- With States: **988**; with ordinary scalar field leaves: **922**.
- Ordinary scalar field requirements with one common mode: **906 Tests**, including **295** with multiple scalar fields.
- Field requirements differ from their Item Test requirement in at least one scalar field: **355 Tests**.
- Entire scalar field set uses the *same named requirement mode* as the Item Test: **567 Tests**; no record wrapper: **567 Tests**.
- Of those potential combined-scope cases, **323** have only one scalar field (new scope likely adds syntax); **244** have multiple fields (more promising for a shared default).
- Tests containing records: **66**; record wrappers found: **86**.
- Shared Test-level scalar field policies: **108 Tests**; grouped ones: **200**.
- Missing effective scalar field requirements: **0** (expected 0).

## Key comparisons

| Approach | Reader sees | Risk |
| --- | --- | --- |
| Separate Item and shared field rule | `items` and `match`; group-level `fields` policy | Slight duplication, but each population is explicit |
| New `scope: items_and_fields` shorthand | One policy targets two populations | Wrong or misleading for differing cardinalities; additional branch in editor grammar |
| Structural `fields` grouping, no `scope` key | Item rules stay at `require`; any field policy applies only within its `fields` structure | Can avoid repeated field clauses without pretending Item and field matching are the same |

## Counterexamples from actual source intent

- RHEL `/home` nosuid: all selected *Items* pass if each partition has **at least one** `nosuid` option; not all mount-option values need equal `nosuid`. A shared Item+field `match: all` is incorrect for `rw,nosuid`.
- Apache optional `stdout_line`: the collected shellcommand Item must exist while a State field can be absent; one shared Item/field presence policy would change this.
- Windows user-right membership: at least one collected Item *matches*, while its `trustee_name` field has its own value-presence/matching rule; do not conflate count of matching Items with count of member values.
- WMI `result.record` and its `domainrole` field are independent nested populations and must not inherit a scalar State-field policy by accident.

## Recommendation for next design iteration

Prefer a **shared field policy at the nearest existing `fields` group or Test scope, with explicit leaf overrides**; reserve combined Item+field shorthand unless its corpus benefit and lossless AST expansion justify a new `scope` keyword. A missing policy at every ancestor must be rejected, not silently defaulted. Keep no `condition` wrapper. The prior independently verified scoped prototype saved **1,106 / 2,550** requirement declarations (43.4%) across six benchmark appearances; that is not a new unique-Test count from this report.

## Real source examples for why the scope matters

- **same_scalar_policy:** `authoring/apache_server_2-4_unix_server/assessments/applicability/platform.cpe-apache-http-server-2-4.yaml` / `gather-all-installation-directories-from-running-apache-httpd-processes-test`; Item mode `at_least_one_exists_and_all_match`; scalar field modes `['at_least_one_exists_and_all_match']`; record wrappers 0.
- **same_as_items:** `authoring/apache_server_2-4_unix_server/assessments/applicability/platform.cpe-apache-http-server-2-4.yaml` / `gather-all-installation-directories-from-running-apache-httpd-processes-test`; Item mode `at_least_one_exists_and_all_match`; scalar field modes `['at_least_one_exists_and_all_match']`; record wrappers 0.
- **candidate_both:** `authoring/apache_server_2-4_unix_server/assessments/applicability/platform.cpe-apache-http-server-2-4.yaml` / `gather-all-installation-directories-from-running-apache-httpd-processes-test`; Item mode `at_least_one_exists_and_all_match`; scalar field modes `['at_least_one_exists_and_all_match']`; record wrappers 0.
- **differs:** `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml` / `if-keepalive-directive-defined-in-other-loaded-configuration-files-verify-test`; Item mode `at_least_one_exists_and_all_match`; scalar field modes `['may_be_absent_and_all_match']`; record wrappers 0.
- **candidate_both_multi:** `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214268.automated.yaml` / `verify-that-sessioncookiename-directive-exists-configured-httponly-secure-in-httpd-test`; Item mode `at_least_one_exists_and_all_match`; scalar field modes `['at_least_one_exists_and_all_match']`; record wrappers 0.

## Evidence boundary

- Raw Test/field source-requirement equality only, NOT proof that Items and scalar field Values share a six-state evaluation domain.
- Record fields are independently quantified and never implicitly inherit ordinary State-field policy.
- A combined-scope shorthand needs its own exact AST lowering and negative six-state tests before it could be admitted.
- The six STIG source has one known original invalid none_exist+State Test; this descriptive census does not accept that Test as valid grammar.
