# SCAP-NG Source and Result File Naming Convention

**Status:** working design decision  
**Iteration:** 002  
**Scope:** human-facing repository and artifact naming conventions

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Principle

SCAP-NG SHOULD use predictable file naming conventions so humans can identify
an object's role from directory listings, editor tabs, diffs, logs, and links.

File names SHALL NOT define semantic object type or stable identity.

Processors SHALL determine object type and identity from file contents.
Filename/type mismatches SHOULD produce authoring validation warnings or errors
as appropriate.

Moving or renaming a file SHALL NOT create a new logical SCAP-NG object when
the declared object identity is unchanged.

## General pattern

Except for well-known singleton/catalog files, source files SHOULD use:

    <descriptive-name>.<object-type>.<serialization>

Examples:

    RHEL-09-232190.policy.yaml
    RHEL-09-232190.assessment.yaml
    root-login-disabled.assessment.yaml
    cat-i-only.profile.yaml
    site-a.tailoring.yaml

If JSON is used instead:

    RHEL-09-232190.policy.json
    root-login-disabled.assessment.json

The naming convention is independent of the YAML-versus-JSON serialization
decision.

## Recommended suffixes

| Object/artifact | Recommended filename |
| --- | --- |
| Benchmark singleton | `benchmark.yaml` / `benchmark.json` |
| Applicability catalog singleton | `applicability.yaml` / `applicability.json` |
| Rule policy | `<name>.policy.yaml` |
| Assessment Method | `<name>.assessment.yaml` |
| Profile | `<name>.profile.yaml` |
| Tailoring | `<name>.tailoring.yaml` |
| Assessment Request / run request | `<name>.request.yaml` |
| Organizational Input set | `<name>.input.yaml` |
| Individual result | `<name>.result.yaml` |
| Result collection / complete run | `<name>.results.yaml` |
| Future structured remediation object | `<name>.remediation.yaml` |

Equivalent `.json` forms MAY be used where JSON serialization is selected.

## Benchmark and applicability singleton names

Within a Benchmark source directory, `benchmark.*` and `applicability.*`
are intentionally concise singleton names.

Their filenames are still not magic.

For example, the Benchmark explicitly references:

    applicability: applicability.yaml

A processor SHALL NOT load an applicability catalog merely because a file named
`applicability.yaml` happens to exist.

## Policy files

Rule policy files SHOULD normally use the stable publisher-facing Rule name as
their descriptive basename where one exists.

Example:

    policy/
      RHEL-09-212030.policy.yaml
      RHEL-09-232190.policy.yaml

The file still declares its authoritative identity internally.

## Assessment files

Benchmark-specific Assessment Methods SHOULD reside under the Benchmark's
`assessments/` tree.

When Assessment modality is known, repositories SHOULD separate Assessment
Methods by modality:

    assessments/
      manual/
        RHEL-09-232190.manual.assessment.yaml
      automated/
        RHEL-09-232190.automated.assessment.yaml

A Rule with both a manual and automated method therefore has two peer
Assessment objects rather than one file that mixes both procedures.

Benchmark-specific Assessments SHOULD normally use a Rule-oriented descriptive
basename when the Assessment is unique to that Rule.

Reusable shared Assessments SHOULD use semantic names under the corresponding
shared modality tree.

Example:

    shared/
      assessments/
        manual/
          linux/
            account-review.manual.assessment.yaml
        automated/
          linux/
            sshd/
              root-login-disabled.automated.assessment.yaml

Future Assessment modalities MAY define corresponding subdirectories when that
improves repository navigation.

The modality directory and filename are authoring conventions only. The
Assessment object's declared `mode` remains authoritative. Processors SHALL
NOT infer Assessment semantics solely from a path or filename.

Inline Manual Assessment shorthand remains permitted where defined by the
manual-assessment authoring model; an inline object naturally has no external
manual-assessment file path.

The directory hierarchy and filename aid authors but do not define identity.

## Result files

SCAP-NG SHALL distinguish an **individual result artifact** from a **result
collection/run artifact** in naming conventions.

### Individual result

Use singular `.result.*`:

    RHEL-09-232190.result.yaml

For design fixtures and tests, a scenario MAY appear before the object-type
suffix:

    RHEL-09-232190.pass.result.yaml
    RHEL-09-232190.fail.result.yaml
    RHEL-09-232190.short-circuit-fail.result.yaml
    RHEL-09-232190.not-applicable.result.yaml
    RHEL-09-232190.collection-error.result.yaml

The result object itself SHALL contain authoritative Rule, Assessment, run, and
result identity. The filename is only descriptive.

### Complete scan/run results

Use plural `.results.*` for a collection representing a complete assessment
run or result package:

    workstation-1234.results.json
    scan-2026-09-28T132600Z.results.json

A tool MAY instead place a stable filename such as `results.json` inside a
directory whose name identifies the run:

    results/
      <run-id>/
        results.json

The final packaging convention remains open, but singular versus plural SHOULD
remain semantically clear to humans:

- `.result.*` = one result object;
- `.results.*` = a result collection/run.

Runtime result filenames SHOULD NOT be relied upon as globally stable IDs.

## One primary object per source file

Normal SCAP-NG authoring source files SHOULD contain one primary object.

This applies especially to:

- Rule policy;
- Assessment Method;
- Profile;
- Tailoring.

Catalogs and aggregate runtime artifacts are intentional exceptions.

This convention prevents source files from regressing into new monolithic
containers merely because the serialization permits multiple objects.

## Validation

Authoring tools SHOULD validate filename conventions.

Examples:

- an `.assessment.yaml` file containing a Rule policy SHOULD be rejected or
  produce a strong diagnostic;
- a `.policy.yaml` file whose declared Rule ID differs unexpectedly from its
  descriptive basename SHOULD produce a warning unless explicitly permitted by
  repository policy;
- duplicate logical IDs remain invalid regardless of filenames.

Filename validation SHALL supplement, not replace, schema and semantic
validation.

## Repository convention

A repository SHOULD choose one serialization convention consistently for
authoring source even if the future SCAP-NG specification permits both YAML and
JSON.

Generated or compiled artifacts MAY use a different canonical serialization
when clearly separated from source.
