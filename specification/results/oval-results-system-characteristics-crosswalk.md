# OVAL Results and System Characteristics to SCAP-NG result crosswalk

Status: pre-alpha Issue #40 design crosswalk.

This crosswalk documents semantic preservation. It does not require SCAP-NG to
reproduce OVAL XML nesting or element names.

| OVAL / SCAP 1.4 concept | SCAP-NG result location | Preservation rule |
| --- | --- | --- |
| Definition/Test result domain | Assessment/Test Result `outcome` | Preserve `true`, `false`, `error`, `unknown`, `not_evaluated`, and `not_applicable` distinctly. |
| `tested_item` | Test Result `item_refs` + Assessment Result `items` | Tests reference reusable first-class collected Items. |
| `tested_variable` / variable value | Variable Result | Preserve datatype, zero/one/many cardinality, values, status, and provenance. |
| `check_existence` | Test Result `check_existence` + `existence_outcome` | Existence evaluation remains distinct from State comparison. |
| Test `check` | Test Result `check` + per-Item outcomes | Preserve per-Item aggregation semantics. |
| Test `state_operator` | Test Result `state_operator` | Preserve multi-State aggregation level separately. |
| State result | Test Result `per_item_results[].state_results[]` | Preserve per-State result before Test aggregation. |
| State entity result / `entity_check` | Entity Result `entity_check` + State Result `entity_results` | Preserve entity-level aggregation separately from State and Test aggregation. |
| `var_check` | Entity Result `var_check` + Variable Result | Variable aggregation remains a separate semantic level and SHALL NOT be flattened into Test truth. |
| collected_object flag | Collection Result `status` | Preserve `error`, `complete`, `incomplete`, `does_not_exist`, `not_collected`, and `not_applicable`. |
| collected_object item refs | Collection Result `item_refs` | Preserve Object-to-Item relationship. |
| system_characteristics Item | Collected Item Result | Preserve capability identity, Item status, fields, and provenance. |
| system_info / host identity | Scan/Benchmark target identity and inventory | Preserve host/product identity at the run/target layer instead of duplicating it in every Assessment result. |
| Item entity datatype/value/status | Collected Item `fields` typed values | Preserve datatype/value/status and explicit redaction. |
| OVAL `mask` | Result/evidence redaction metadata | Generic comparison-level mask is not a native authoring primitive; sensitive-result handling is explicit and separately governed by the legacy disposition ledger. |
| Definition/Test `variable_instance` | Assessment invocation identity | Distinct effective bindings become distinct invocations; source integer may remain provenance only. |
| OVAL Results `reported` | Board decision pending | Canonical results currently prefer complete logical results plus projections. |
| OVAL Results `thin` / `full` | Board decision pending | Candidate replacement is one canonical detailed result plus deterministic projections. |
| `include_source_definitions` | Board decision pending | Candidate replacement is package/content references rather than changing canonical result shape. |

## Layer ordering

For an Object-backed Test the preserved evaluation layers are:

1. Object collection and collection status;
2. `check_existence`;
3. State/entity/Variable evaluation;
4. per-State result;
5. Test `state_operator` for each Item;
6. Test `check` across Items;
7. final Test result;
8. Assessment result;
9. Rule policy interpretation.

SCAP-NG result consumers SHALL NOT infer that a later layer replaces or erases
the earlier diagnostic layer.

## Evidence and completeness

SCAP-NG separates logical completeness, population completeness, and retained
evidence completeness. Bounded evidence records observed failures, the actual
failure population when known, the configured evidence maximum, returned
evidence count, truncation state, and stop reason. An evidence maximum is not a
compliance threshold and SHALL NOT alter Assessment truth.

Worked bounded-evidence examples are maintained under
`research/iterations/003/results/issue40/`.

## Informational Rule disposition

XCCDF Rule role remains a policy/result concern. `informational` is therefore
not added to the six-state Assessment/Test technical outcome domain. A Rule may
be reporting-only or excluded from scoring while the underlying Assessment
truth remains available.

## Compatibility guardrail

Any SCAP 1.4 result/system-characteristics capability exercised by current
content or validation/conformance content is presumed retained unless a
compelling, explicitly documented disposition says otherwise.
