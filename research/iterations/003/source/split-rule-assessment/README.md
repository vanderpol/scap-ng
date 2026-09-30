# Split Rule / Assessment Source (iteration 003 — active development)

The current authoring architecture is:

```text
Benchmark
  ├─ profiles, groups, parameters and applicability
  └─ Rule
       ├─ policy/assertion metadata
       ├─ named Assessment selections
       ├─ default Assessment selection
       └─ explicit relative path(s) to Assessment YAML
```

A **Rule is the policy/assertion object**. SCAP-NG does not introduce a
separate Policy file between Rule and Assessment. This terminology keeps Rule
appropriate for compliance, vulnerability, patch, inventory and other
assertion roles while Assessment remains the method used to evaluate it.

The relative-path decision remains unchanged: authors and reviewers should be
able to follow a Rule directly to an Assessment file without an
author-maintained index or filename-guessing convention.

## Current full RHEL 9 review source

The maintained full review is under:

```text
research/iterations/003/review/rhel9-current-full/
```

Its Rule source uses explicit relative paths for all 445 Rules. The current
pre-alpha field names are `assessment_choices` and
`default_assessment_choice`:

```yaml
rule:
  id: SV-257777
  assessment_choices:
    default:
      assessment: ../assessments/automated/SV-257777.automated.assessment.yaml
    automated:
      assessment: ../assessments/automated/SV-257777.automated.assessment.yaml
    manual:
      assessment: ../assessments/manual/SV-257777.manual.assessment.yaml
  default_assessment_choice: default
```

Selection names are extensible and are not limited to `automated` and
`manual`. Multiple names MAY intentionally point to the same Assessment
file. Tailoring selects a published Rule Assessment choice; it does not supply
an arbitrary file path.

## How links resolve

1. Each Assessment path resolves relative to the Rule YAML file containing the
   reference, not the process working directory.
2. The loader normalizes the path and rejects missing files, wrong object
   types, source-boundary escapes and conflicting identities.
3. The referenced Assessment's logical identity comes from its document
   contents, not from its filename.
4. Compilation converts source paths into stable logical object bindings and
   writes those bindings into the package manifest.
5. A scanner uses the immutable package manifest to resolve Rule and Assessment
   objects and verify their digests. It SHALL NOT infer filenames, scan
   directories, or reopen authoring paths at runtime.
6. Moving an Assessment source file requires updating referring Rule paths but
   does not by itself change the Assessment's semantic identity.

A separate Assessment index is therefore unnecessary for source authoring.
The package manifest is still required because it solves a different problem:
deterministic scanner-time object resolution and integrity verification.

## Directory shape

```text
<benchmark>/
  benchmark.yaml
  applicability.yaml
  rules/
  assessments/
    automated/
    manual/
    applicability/
```

Reusable/shared Assessments may later move into a shared subtree after exact
semantic reuse is demonstrated.

## Applicability

The small `applicability.yaml` registry remains a separate native
indirection layer:

```text
applicability ID -> applicability Assessment
```

Rules reference applicability IDs. This registry expresses reusable named
applicability conditions; it is not a general Assessment lookup index.

## Status

Iteration 003 remains pre-alpha. The maintained current review paths, converter
tests and readiness documents are authoritative over older generated
`rhel9-full` artifacts that may preserve superseded intermediate shapes for
evidence. Passing structural or round-trip checks does not by itself establish
runtime execution equivalence or final benchmark readiness.

See:

- [Native source layout](../../design/native-source-layout.md)
- [Assessment Method specification](../../../../../specification/assessment/assessment-method.md)
- [Full benchmark readiness gates](../../review/FULL-BENCHMARK-READINESS.md)
