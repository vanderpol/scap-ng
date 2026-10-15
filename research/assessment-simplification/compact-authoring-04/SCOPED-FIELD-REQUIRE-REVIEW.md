# 0.4 research review — requirements scoped to Test, State group, or field

**Status:** Candidate for human review, **not accepted 0.4 syntax**. The active 0.3 specification, published 0.4 interim ZIPs, and present 0.4 JSON Schema are unchanged. This proposal addresses author review of real Windows 11 `SV-253254` and `SV-253274`.

**One rule for authors:** put the requirement at the broadest scope where it is true; override it at a narrower scope **only for an exception**. An author can inspect the nearest enclosing explicit declaration. No implicit or undocumented existence/matching defaults are introduced.

## Exactly what each scope means

- **Test `require`** controls the population of collected items and matching States. It remains mandatory, separate, and unchanged by this proposal.
- **Test `state_fields_require`** declares the requirement for *ordinary scalar State fields* across that Test's State expressions.
- **Logical State group's `state_fields_require`** overrides the Test field scope for its scalar descendants, including nested groups, when that particular State alternative needs a different requirement.
- **Individual field `require`** overrides the nearest explicit State field scope only for that field. If neither a field nor its enclosing Test/group declares one, validation **SHALL fail**. Explicit but redundant same-value overrides should be rejected to keep authoring unambiguous.
- **Windows record and nested record-field `require`** belong to independent native scopes and do not inherit ordinary scalar State-field requirements. No implicit propagation into record children.
- `all` and `any` logical State branches could be written `and` and `or`; this is an exact spelling change for logic operators, **not** the OVAL cardinality `all` or the separate `states_match: any`. A real field literally named `all`, `and`, etc. remains distinguishable by its map-shaped field predicate rather than array-shaped logical group.

## Real Windows 11 sample — SV-253254

The source has **two allowed registry editions** and two conjunctive fields in each alternative. All four scalar fields carry the same `at_least_one_exists_and_all_match` requirement. The candidate makes that visible **once**, without changing its meaning:

```yaml
tests:
  editionid-enterprise-or-enterprises-test:
    capability: windows.registry
    # unchanged source Object omitted here for readability
    require: at_least_one_exists_and_all_match   # collected item/State matching
    state_fields_require: at_least_one_exists_and_all_match
    states_match: any                            # either edition alternative
    states:
      - and:
          - type: {equals: string}
          - value: {equals: Enterprise}
      - and:
          - type: {equals: string}
          - value: {equals: EnterpriseS}
```

The short excerpt above omits required Test metadata and the full Object: it is **not** a stand-alone Assessment.

## Real Windows 11 exception — SV-253274

Some `independent.shellcommand` Tests require `exit_status` and `stdout_line` to exist/match, but **`stderr_line` must not be present**. An explicit group scope naturally preserves the exception:

```yaml
states:
  - and:
      - exit_status: {equals: 0}
      - stdout_line:
          matches_regex: ['... original regex expressions ...']
          value_match: one_or_more
      - stderr_line:
          equals: ''
          require: none_exist
    state_fields_require: at_least_one_exists_and_all_match
```

The omitted regex values are only for excerpt readability; the complete native content remains unchanged in conversion. `none_exist` is about the **`stderr_line` field**, not about requiring zero collected command-result items. The Test `require` is independently retained. The original predicate is not removed merely because an absent field cannot equal a value.

## Proof across six released benchmark sources

The reproducible script converts the immutable published 0.3 source through the existing verified 0.4 one-grammar path, including certified Windows selector enumeration migration, and then proves exact **0.4 compressed → explicit 0.4 expansion**. It also asserts fail-closed behavior for missing and redundant requirements, native record isolation, and field/logical-key collisions.

| Source | Automated/applicability Assessments | Existing field `require`s | After scoped declarations | Net removed |
| --- | ---: | ---: | ---: | ---: |
| RHEL 9 | 423 | 574 | 370 | 204 |
| Oracle Linux 9 | 407 | 579 | 330 | 249 |
| Windows 11 | 251 | 543 | 311 | 232 |
| Windows Server 2025 | 268 | 726 | 315 | 411 |
| Windows Server DNS | 24 | 65 | 59 | 6 |
| Apache 2.4 UNIX | 23 | 63 | 59 | 4 |
| **Total** | **1,396** | **2,550** | **1,444** | **1,106 (43.4%)** |

The after-count includes each new Test/group `state_fields_require` and every retained exceptional field `require`, not just the number of remaining leaf declarations. This is a measurement of **authoring declarations**, not a claim about result size or actual scanner performance.

**Evidence:** [six-anchor PASS / run 38808020283](https://github.com/vanderpol/scap-ng/actions/runs/38808020283) · [individual proof report](https://github.com/vanderpol/scap-ng/actions/runs/38808020283/artifacts/12006084546) · [source-inverse tool](../../../tools/research_04_scoped_state_require.py) · [tracking issue #227](https://github.com/vanderpol/scap-ng/issues/227).

## Promotion gates — do not silently adopt this proposal

1. Review the three-level explicit precedence vocabulary and the `and`/`or` aliases with the owner and Board; Test cardinality must not be confused with field cardinality or State logical grouping.
2. Implement **fail-closed scope-aware schema/semantic validation** for the candidate, including negative cases, record-field isolation and capability-specific keys. The present 0.4 draft schema does **not yet** accept `state_fields_require` or `and`/`or` State groups.
3. Extend the reference-model tests for absent/error/unknown/incomplete fields; structural inverse is evidence of expression preservation, **not** scanner-result conformance. No SCAP-NG scanner exists yet.
4. Only then update the normative schema, compiler and separate authoring preview; do not silently rewrite the already-published 0.4 research ZIPs.

Rejected shortcuts: undocumented `require` defaults; overriding Test `require` using a field declaration; inheriting scalar field requirements into Windows record subfields; deleting an apparently contradictory comparison from an absent-field predicate; silently flattening nested `and`/`or` structures.
