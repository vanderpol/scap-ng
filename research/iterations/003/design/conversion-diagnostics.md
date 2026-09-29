# Conversion Diagnostics

**Status:** iteration 003 conversion contract

SCAP-NG migration tooling SHALL produce structured diagnostics with stable
machine-readable codes and human-readable messages.

## Severity levels

### INFO

An expected normalization or noteworthy source condition that does not imply
semantic loss.

Conversion continues and the affected native content remains valid.

### WARN

A non-semantic or descriptive source condition is missing, unusual, or
degraded, but executable semantics remain faithfully representable.

Conversion continues and the affected native content remains valid.

Examples include absent OVAL Test/Object/State/Variable comments when the
corresponding NG descriptive title is therefore emitted as null.

### ERROR

A specific source semantic unit cannot be carried forward faithfully under the
current SCAP-NG specification or supported capability set.

Conversion SHOULD continue when the failure can be isolated safely so that a
complete diagnostic inventory is produced.

The affected semantic unit SHALL NOT be silently approximated or emitted as if
conversion succeeded.

The overall conversion/CI gate SHALL fail when one or more ERROR diagnostics
are present.

A deprecated OVAL test that is intentionally not part of the SCAP-NG
capability set SHALL produce an ERROR. The automated Assessment depending on
that test SHALL NOT be emitted. Other independently convertible content, such
as the Rule or a manual Assessment, MAY still be emitted when their references
remain internally valid.

### FATAL

A package-wide or foundational condition makes continued conversion unsafe or
likely to produce misleading output.

Conversion SHALL stop.

Examples include inability to identify required source components or a
fundamental source/package integrity failure.

## Diagnostic record

Each diagnostic SHALL contain:

- `severity`;
- stable `code`;
- human-readable `message`.

When available it SHOULD also include:

- native Rule ID;
- native Assessment ID;
- source object ID;
- affected field;
- source location or other relevant context.

Example:

    {
      "severity": "warn",
      "code": "OVAL_TEST_COMMENT_MISSING",
      "rule_id": "SV-257777",
      "assessment_id": "SV-257777.automated",
      "source_id": "oval:example:tst:123",
      "field": "test_title",
      "message": "OVAL Test comment is absent; test_title is emitted as null."
    }

## End-of-run summary

Migration tooling SHALL report counters for all four severity levels.

The machine-readable diagnostics artifact SHALL include the same counters.

A full conversion SHOULD also report high-level source/conversion accounting,
including at minimum:

- Rules discovered;
- Rules converted;
- Rules requiring review or blocked by errors;
- Assessments emitted;
- semantic-accounting totals where available.

The goal is to make a large conversion reviewable without requiring authors to
inspect every generated file manually.

## Stable diagnostic codes

Diagnostic codes are part of the migration tooling interface. Tooling SHOULD
keep their meaning stable across runs and versions.

Initial codes include:

- `OVAL_TEST_COMMENT_MISSING`;
- `OVAL_OBJECT_COMMENT_MISSING`;
- `OVAL_STATE_COMMENT_MISSING`;
- `OVAL_VARIABLE_COMMENT_MISSING`;
- `BENCHMARK_METADATA_NOT_NORMALIZED`;
- `DEPRECATED_OVAL_TEST_NOT_SUPPORTED`.

Additional codes SHALL be introduced for distinct conditions rather than
overloading one generic warning/error message.
