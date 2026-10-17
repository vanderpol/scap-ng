# One-grammar SCAP-NG 0.4: scoped and/or + editor prototype

**Research checkpoint · October 17, 2026 · not normative SCAP-NG.**

The grammar uses familiar OVAL `and`, `or`, and `not` for logical Test composition. Within `require.condition`, `and`/`or` also mean logical composition, but a **sibling enum** identifies which semantic scope is combined. This is an editor affordance *and* a protection against accidental State/record flattening.

## Three concrete shapes

**One field — no redundant scope:**

```yaml
require:
  items: at_least_one_all_match
  condition:
    mount_options: {at_least_one_value_is: nosuid}
```

**Several predicates within one State:**

```yaml
require:
  items: if_present_all_match
  condition:
    scope: fields
    and:
      - setuid: {is: false}
      - setgid: {is: false}
    all_fields_must_exist: true
```

**Alternative whole States (real Windows 11 WMI DomainRole example):**

```yaml
require:
  items: at_least_one_all_match
  condition:
    scope: states
    or:
      - result:
          at_least_one_record_exists: true
          every_record:
            domainrole: {is: '1'}
      - result:
          at_least_one_record_exists: true
          every_record:
            domainrole: {is: '3'}
```

The last two examples have the **same grouped `scope` + logical operator layout**. Unlike wrapping all alternatives under an additional `states:` hierarchy, this adds no extra indentation solely for scope. The same source Test may contain nested logical groups, with each group expressing its own `scope`.

## Empirical gate

The pinned six-STIG r3 source has **872 automated Assessments / 1,375 Tests**. The current editor grammar reconstructed **871/872 complete Assessments (99.89%) and 1,374/1,375 Tests (99.93%)** as equal source dictionaries, with **3,484 malformed-input rejection checks**.

Of the 1,374 admitted Tests:
- **331** have one or more grouped conditions, where scope must be declared.
- **247** are logical groups within one State (`scope: fields`).
- **128** are groups over complete alternative States (`scope: states`). Group counts exceed the number of grouped Tests because some Tests contain nested groups.
- **1,043** use only single-field/record predicates and need no extra scope label.

This experiment does **not** establish native scanner/evidence six-state equivalence, standard conformance, or a successful blind readability study.

## Editor compatibility

[Prototype JSON Schema](fixed-require.editor.schema.json) contains `items` dropdowns with descriptions; required `condition` for match-bearing choices; required and mutually exclusive logical `scope` and `and`/`or` keys; recursive State groups; and observed field-name autocomplete from actual source capability mappings for **linux.partition, windows.registry, windows.userright, windows.wmi.query**.

An actual `linux.partition` source field `mount_options` passes, while typo `mount_optoins` and Windows-only `trustee_name` fail schema validation. The converter additionally rejects invalid logical groups and unknown source predicates. WMI mixed-record alternatives remain distinct from an unsafe per-record OR; [explicit regression checks](https://github.com/vanderpol/scap-ng/blob/main/tools/test_research_04_scoped_condition_editor.py) guard this.

**Not yet complete:** The other capability mappings need equivalent schema-driven completions; type-appropriate comparison operations, WMI WQL-derived result fields, and shared-reference checks need their own semantic validator. The pilot's source-exact inversion is not a six-valued scanner.

## Remaining source-conformance exception

The single rejected native Assessment is `authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml`. Original-source [OVAL investigation](reports/source-bootloader-none-exist.md) establishes the **NIWC-origin** Test shapes:

- RHEL 9 `oval:navy.navwar.niwcatlantic.scc.rhel9os:tst:25778901`
- Oracle Linux 9 `oval:navy.navwar.niwcatlantic.scc.rhel9os:tst:27145101`

Both contain `check_existence="none_exist"` **with an attached State**, prohibited by OVAL 5.12.3 Schematron `not(*[local-name()='state'])`. This is inherited from original NIWC-added OVAL, **not created by the native converter**. The source selects lines containing banned GRUB superuser names; the attached State appears redundant, but there is **no valid lossless lowering from an invalid source construct until the intended result behavior is formally agreed**. Do not add a new native language exception or silently delete that State.

## Next approval gates

1. Decide whether the sibling `scope:` enum is genuinely readable to security auditors *without an editor*.
2. Complete capability-based field/operator autocomplete, starting with records and missing/unknown/error semantics.
3. Close the original NIWC `none_exist`/State source defect with an explicit content-owner decision or fail-closed importer diagnostic.
4. Validate conditional, nested, multi-record and incomplete/error evaluations with an independent native scanner before calling SCAP 1.4 conversion lossless in runtime behavior.
5. Only then promote a chosen syntax into normative 0.4. Do not equate this reversible prototype to a finished language.

### Reproducible evidence

- [Whole six-STIG pilot report](reports/fixed-require-editor-pilot.md)
- [Passing CI: source exact, schema and targeted negative tests](https://github.com/vanderpol/scap-ng/actions/runs/39034513658)
- [Full Windows 11 WMI example](fixed-require-samples/windows-wmi-rights.research.yaml)
- [Full Linux file-permissions example](fixed-require-samples/linux-files.research.yaml)
- [Source XML anomaly evidence](reports/source-bootloader-none-exist.json)
