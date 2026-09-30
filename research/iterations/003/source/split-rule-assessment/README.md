# Split Rule / Policy / Assessment Source (iteration 003 — work in progress)

> **Design review warning:** The committed `rhel9-full/` source is **generated conversion evidence**, not a ratified native authoring format or production content. The complete Rule → Policy → Assessment reference chain is **not yet implemented**. See [issue #31](https://github.com/vanderpol/scap-ng/issues/31) and the [review readiness checklist](../../review/FULL-BENCHMARK-READINESS.md).

## Accepted logical design

```text
Benchmark
  ├─ profiles: overrides of effective baseline rule selections
  ├─ groups, parameters and applicability references
  └─ Rule ID
        └─ Policy ID                    [NOT YET IMPLEMENTED]
             ├─ named check selector(s)
             ├─ default selector
             └─ Assessment ID
                  └─ resolved exact assessment file via manifest/registry
```

A Rule must not choose an assessment implementation directly. Policy declares selectors and how they resolve to assessments. An applicability ID maps to an applicability assessment through the separate registry.

## What the current RHEL 9 generated artifacts actually contain

- `rhel9-full/benchmark.yaml` contains benchmark metadata, profiles, groups, a list of 445 Rule IDs and the applicability registry file.
- `rhel9-full/rules/SV-257777.rule.yaml` has `checks` pointing to **assessment IDs**, not paths or independent Policy objects.
- `rhel9-full/assessments/automated/SV-257777.automated.assessment.yaml` is the associated assessment, and `assessments/manual/` holds manual variants. Filenames happen to follow IDs today, but implicit path inference is not accepted as a normative reference protocol.
- `rhel9-full/applicability.yaml` contains separate applicability binding information.
- Profiles currently express only `disabled_rules` exceptions for rule selections turned off; empty profiles carry no explicit changes. The effective baseline and XCCDF Group/Rule defaults must still be verified against the source. See [issue #30](https://github.com/vanderpol/scap-ng/issues/30).

For a current **illustrative** trace, follow `SV-257777` from `benchmark.yaml` to `rules/SV-257777.rule.yaml`, read its `checks.default` assessment ID, then inspect `assessments/automated/SV-257777.automated.assessment.yaml`. This is a temporary reviewer navigation aid, **not** the final SCAP-NG authoring contract.

## Planned directory shape (not implemented in full)

```text
<benchmark>/
  benchmark.yaml
  applicability.yaml
  rules/
  policies/             # new: explicit Rule → Policy check bindings
  assessments/
    automated/
    manual/
    applicability/
```

The Benchmark owns its profiles, groups and parameters. Legacy XCCDF/OVAL/CPE XML IDs, input XML metadata, conversion diagnostics and provenance belong in evidence, not native source. No SCAP 1.4 serialization structure is permitted in native assessment logic.

## Proposed authoring links — explicit relative paths (not yet generated)

**Decision proposed for iteration-003 implementation:** Human-authored source SHALL use
explicit relative paths for file-backed Rule → Policy and Policy → Assessment
references. Logical IDs identify the objects *inside* those files; filenames
do not define identity. This follows the existing
[`specification/assessment/assessment-method.md`](../../../../specification/assessment/assessment-method.md)
source-reference/compiled-identity distinction.

Example directory-local authoring:

```yaml
# rules/SV-257777.rule.yaml
rule:
  id: SV-257777
  policy: ../policies/SV-257777.policy.yaml
```

```yaml
# policies/SV-257777.policy.yaml
policy:
  id: SV-257777.policy
  default_check: default
  checks:
    default:
      assessment: ../assessments/automated/SV-257777.automated.assessment.yaml
    automated:
      assessment: ../assessments/automated/SV-257777.automated.assessment.yaml
    manual:
      assessment: ../assessments/manual/SV-257777.manual.assessment.yaml
```

```yaml
# assessments/automated/SV-257777.automated.assessment.yaml
assessment:
  id: SV-257777.automated
  mode: automated
  # Other source assessment fields follow ...
```

These are **illustrations of the proposed linkage fields**; the committed
`rhel9-full` directory has not yet been regenerated with them.

### How authors and tools resolve links

1. A Rule path resolves **relative to the directory containing that Rule file**,
   not relative to the working directory or repository root.
2. The referenced Policy's Assessment paths resolve **relative to the Policy
   file's directory**. Paths use forward slashes for portability.
3. The loader normalizes `.` and `..`, validates the target is inside the
   explicitly declared source/package boundary, and rejects missing targets,
   symlink escapes, wrong object types, duplicate conflicting identities, and
   cycles. Local source processing SHALL NOT silently fetch remote files.
4. The compiler loads the target document and reads the contained `policy.id`
   or `assessment.id`; **these IDs, not path basenames, are semantic identities**.
   Multiple selectors MAY deliberately reference the same Assessment file.
5. The compiler produces a reference index/package manifest mapping logical
   IDs and versions to exact packaged members and hashes. The scanner consumes
   **that explicit index**, validating integrity and resolution; it SHALL NOT
   guess a path from the identifier or search directories for matching names.
6. Moving an Assessment file requires updating source references (or an
   authoring-tool refactor), but does not by itself change the Assessment
   semantic ID or version. Changes to test semantics require proper versioning.
7. Tailoring selects a published check selector, not an arbitrary source file
   path; applicable evaluation uses the already-resolved immutable package.

For example, a scanner seeing the *compiled* check selection
`SV-257777.automated` consults the package object index, not a convention
like `assessments/automated/<id>.assessment.yaml`. The index specifies the
concrete package member and its digest.

An **ID-only source reference** MAY eventually be supported when backed by
an explicit versioned source-object registry with exactly one matching entry.
Until that grammar is specified and validated, ID-only references are not
interoperable, and no author/scanner SHALL infer filenames from them.

The source compiler and package resolver will implement these rules as part
of [issue #31](https://github.com/vanderpol/scap-ng/issues/31).
The existing benchmark-level `applicability_catalog: applicability.yaml`
already demonstrates an explicit relative source path.

## Reviewer status

This iteration is still under active development. The incomplete Policy boundary and unproven inherited profile selection are **handoff blockers**, even where package ID resolution and OVAL regression tests pass. RHEL 9 and Windows 11 readiness must be evaluated independently.
