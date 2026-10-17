# Consistent cardinalities and structural groups — six-STIG proof

**Research only: not approved 0.4 grammar or scanner/OVAL execution parity.**

- **871/872** complete Assessments, **1374/1375** Tests exactly reconstructed.
- `some` → `at_least_one`: **70** matching quantifiers (Item and record).
- `scope: states|fields` → explicit structural groups: **128** whole-State groups, **247** field groups.
- `all_fields_must_exist: true` → `fields.presence: all`: **200** scoped field groups.
- Inadmissible wrapper mutations rejected: **871**.
- Reserved/ambiguous name collision Assessments: **0**.

## Real Windows 11 WMI DomainRole requirement

```yaml
require:
  items: at_least_one
  match: all
  states:
    or:
      - result:
          records: at_least_one
          match: all
          domainrole: {is: "1"}
      - result:
          records: at_least_one
          match: all
          domainrole: {is: "3"}
```

`states.or` combines full alternative State evaluations; it does not mean per-record `domainrole` membership.

## Source boundary and unsupported shortcuts

- The example is a transformation of the original **Windows 11 SV-253495** WMI check; the complete 7-Test Assessment and its `evaluate.or` graph remain intact.
- Every record branch still requires at least one record and all observed records to satisfy its own role condition.
- Converting both branches to `domainrole: {in: [1,3]}` **would change results** for mixed records.
- Literal Boolean field tests (`is: true` or `is: false`) are intentionally preserved. No legacy Test `all_exist` semantics are normalized.
- Parser/schema coverage and source structure do not establish independent scanner/OVAL evidence parity.

## Source exceptions

- `authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml` — unproven output or Item scope

## Complete source-backed sample Assessments

Complete six-STIG derived RHEL, Windows, DNS and Apache examples are adjacent to this report as `*.consistent.research.yaml`.
