# SCAP-NG 0.2.0 schema

**Status:** frozen pre-alpha technical baseline for human and OVAL Board review.

This directory contains the complete SCAP-NG **0.2.0** schema snapshot: Benchmark and Rule policy structures, automated and manual Assessment structures, result schemas, packaging schemas, shared capability contracts, and reviewed OVAL-to-NG capability mappings.

Technical baseline commit: `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`.

Later commits may improve documentation, examples, tests, and Board-review material without changing the frozen 0.2.0 schema meaning unless a focused defect is explicitly accepted.

## Start here

If you are new to SCAP-NG, read these in order:

1. **[SCAP 1.4 → SCAP-NG key changes](../../board/SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md)** — the shortest explanation of what changed and why.
2. **[Assessment reference](../../specification/assessment/reference/README.md)** — author/implementer guidance for automated Assessment semantics.
3. **[`benchmark.schema.json`](benchmark.schema.json)** — top-level Benchmark policy structure.
4. **[`rule.schema.json`](rule.schema.json)** — Rule requirements and Assessment selections.
5. **[`assessment.schema.json`](assessment.schema.json)** — automated Assessment structure.
6. **[`capability-mappings/supported/`](capability-mappings/supported/)** — reviewed native capability contracts mapped from supported OVAL semantics.
7. **[`assessment-result.schema.json`](assessment-result.schema.json)** and **[`scan-result.schema.json`](scan-result.schema.json)** — execution/result structures.

For a small source-to-NG example rather than reading schemas first, use the **[0.2.0 Board review examples](../../board/review-content/0.2.0/README.md)**.

## How the main pieces fit together

The policy path is:

```text
Benchmark
  └─ Rule
      └─ selected Assessment
```

A **Benchmark** organizes policy. A **Rule** states a requirement and identifies one or more Assessment choices. An **Assessment** defines how the requirement is evaluated.

Automated Assessments are independently valid executable units. They do not require a Benchmark or Rule wrapper to express their technical assessment semantics.

The Assessment language retains recognizable OVAL concepts such as **Test, Object, State, Variable, and Item**, while avoiding a literal recreation of the OVAL XML type hierarchy.

## Schema groups

### Policy and authoring

- [`benchmark.schema.json`](benchmark.schema.json) — Benchmark metadata, Rules, Profiles, grouping, and policy structure.
- [`rule.schema.json`](rule.schema.json) — individual policy requirements and Assessment choices.
- [`applicability.schema.json`](applicability.schema.json) — policy-level applicability references.
- [`tailoring.schema.json`](tailoring.schema.json) — organization-specific Rule selection and permitted tailoring.
- [`organizational-input.schema.json`](organizational-input.schema.json) — typed organization-supplied values intentionally delegated by the publisher.
- [`manual-assessment.schema.json`](manual-assessment.schema.json) — first-class human/manual assessment procedures.

### Automated Assessment

- [`assessment.schema.json`](assessment.schema.json) — top-level automated Assessment document.
- [`expression.schema.json`](expression.schema.json) — Assessment evaluation expressions.
- [`capability-common.schema.json`](capability-common.schema.json) — shared native capability primitives.
- [`capability-scope.json`](capability-scope.json) — capability support/scope metadata.
- [`capability-mappings/supported/`](capability-mappings/supported/) — supported native Test/Object/State/Item mappings.
- [`capability-mappings/experimental/`](capability-mappings/experimental/) — research mappings not in the supported 0.2.0 content-development scope.

### Results and evidence

- [`assessment-result.schema.json`](assessment-result.schema.json) — one automated Assessment execution.
- [`manual-assessment-result.schema.json`](manual-assessment-result.schema.json) — one manual Assessment result.
- [`test-result.schema.json`](test-result.schema.json), [`state-result.schema.json`](state-result.schema.json), [`variable-result.schema.json`](variable-result.schema.json), and [`entity-result.schema.json`](entity-result.schema.json) — lower-level execution evidence.
- [`collected-item.schema.json`](collected-item.schema.json) and [`collection-result.schema.json`](collection-result.schema.json) — collected target data and collection status/completeness.
- [`expression-invocation.schema.json`](expression-invocation.schema.json) and [`expression-result.schema.json`](expression-result.schema.json) — evaluation trace.
- [`rule-result.schema.json`](rule-result.schema.json), [`benchmark-result.schema.json`](benchmark-result.schema.json), and [`scan-result.schema.json`](scan-result.schema.json) — policy-facing result hierarchy.
- [`item-materialization.schema.json`](item-materialization.schema.json), [`item-report.schema.json`](item-report.schema.json), and [`reported-elements.schema.json`](reported-elements.schema.json) — bounded evidence/materialization controls.
- [`result-types.schema.json`](result-types.schema.json) and [`result-field-extensions.json`](result-field-extensions.json) — shared result definitions and extension metadata.

### Packaging

- [`package-manifest.schema.json`](package-manifest.schema.json) — compiled SCAP-NG content package manifest.
- [`result-package-manifest.schema.json`](result-package-manifest.schema.json) — result-package manifest.
- [`assessment-result-set.schema.json`](assessment-result-set.schema.json) — development/result-set transport wrapper; not the final package architecture.

## Conditional evaluation

Version 0.2.0 supports structured conditional evaluation in `evaluate`:

```yaml
evaluate:
  if:
    test: is-server
  then:
    test: server-setting
  else:
    test: workstation-setting
```

The condition is evaluated first. Only the selected branch executes.

The complete technical result domain is preserved:

| Condition outcome | Behavior |
| --- | --- |
| `true` | execute `then` only |
| `false` | execute `else` only |
| `error` | execute neither branch; result is `error` |
| `unknown` | execute neither branch; result is `unknown` |
| `not_evaluated` | execute neither branch; result is `not_evaluated` |
| `not_applicable` | execute neither branch; result is `not_applicable` |

All references are validated before execution, including references in an unselected branch. Ordinary `all`, `any`, `one`, and `odd` expressions remain logical aggregation; they are not silently rewritten as conditional control flow.

## Capability mapping provenance

The files under `capability-mappings/supported/` contain durable source provenance for the OVAL semantics from which each native capability was derived.

That source information is **not** a runtime dependency on OVAL XML or XSD files. It exists so reviewers and migration tools can answer questions such as:

- Which OVAL Test/Object/State/Item semantics produced this native capability?
- Which OVAL version and namespace were reviewed?
- Did a native name intentionally remove a historical numeric/version suffix?
- Can a future standards reviewer trace a native field back to its source semantics?

Removing or materially rewriting those source references therefore requires provenance review rather than ordinary documentation cleanup.

Mappings under `capability-mappings/experimental/` are research artifacts. In particular, ESX/VMware expansion remains deferred pending upstream semantic guidance. Deferred experimental mappings are not part of the supported 0.2.0 content-development scope.

## Version metadata

Every version-local JSON artifact carries human-visible version metadata.

JSON Schema files use:

```json
"x-scap-ng-version": "0.2.0",
"x-last-modified": "YYYY-MM-DD"
```

Non-schema support JSON uses:

```json
"specification_version": "0.2.0",
"last_modified": "YYYY-MM-DD"
```

The `x-` prefix identifies SCAP-NG-specific JSON Schema annotations rather than JSON Schema validation keywords. `last_modified` records the most recent substantive or normalization change to that file; it is not a release date.

Automated Assessments currently identify the provisional assessment specification as `scap-ng.pre-alpha.assessment` version `0.2.0`. The final standards name and identifier remain an OVAL Board decision.

## Validate content yourself

From the repository root:

```powershell
python -m pip install PyYAML==6.0.3 lxml==6.1.1 jsonschema cryptography

python tools/validate_native_json_schemas.py PATH_TO_CONTENT --schema-dir schema/v0.2.0
python tools/validate_native_semantics.py PATH_TO_CONTENT
python tools/validate_native_package_graph.py PATH_TO_CONTENT
```

For conversion, normalization, packaging, and other human-runnable commands, see **[Human-runnable SCAP-NG tools](../../tools/HUMAN-RUNNABLE-SCRIPTS.md)**.

## What schema validation does — and does not — prove

A document passing JSON Schema validation means its structure conforms to the 0.2.0 structural contract.

It does **not** by itself prove:

- semantic equivalence to the original SCAP 1.4 content;
- correct collector implementation;
- correct behavior on a live target;
- interoperability with an independent scanner;
- OVAL Board approval.

Those require separate semantic, conversion, known-result, round-trip, collection, and live/runtime evidence.

## Review status

0.2.0 is intentionally frozen for review rather than presented as a finished standard.

The current review goals are to identify demonstrated semantic gaps, confirm that used non-deprecated OVAL semantics are preserved, verify that normalization does not change assessment meaning, and obtain Board guidance on the remaining standards decisions.

See:

- **[OVAL Board review landing page](../../board/README.md)**
- **[0.2.0 review checkpoint](../../board/SCAP-NG-0.2.0-REVIEW-CHECKPOINT.md)**
- **[Proposal coverage audit](../../board/PROPOSAL-COVERAGE-AUDIT.md)**
- **[OVAL 5.12.3 capability crosswalk](../../specification/migration/oval-5.12.3-capability-crosswalk.md)**
