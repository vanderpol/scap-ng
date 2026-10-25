# Canonical Object processing correction — #251

2026-10-25. Started clean on current main
`ce9eadca76e2d7b740c9888d6dd47088598da00b` after fetch/fast-forward check.
[Owner scope and stop conditions](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6396984623).
Implementation commit:
[`f851e3abb432e0853bbb15bde5ec68b163e7445e`](https://github.com/vanderpol/scap-ng/commit/f851e3abb432e0853bbb15bde5ec68b163e7445e).
Portability follow-up and terminal hosted CI are recorded below. No schema,
normative specification, release gate, original
fixture, pinned archive, six-STIG bundle or proof-coverage ledger was changed.

## Engineering result

The shared flat-Object visitor previously omitted acquisition Objects inside
Variable expressions. Broad Variable/common structural schemas also allowed
the nested legacy wrapper through public validation and compiler preflight.
Both public CLIs at the starting checkpoint reproduced the defect: the raw
SV-278139 Assessment was accepted with exit 0. New regression tests require
validator/compiler exit 1 with the exact path:

`assessment.variables.icacls-path-sysvol-directory-variable.expression.concat[1].regex_capture.value.values.object.select`

`tools/v04_object_contract.py` now supplies the single grammar-owned acquisition
visitor to migration and mandatory public validation/compiler preflight. It
uses the existing generated, closed, version-local capability Object schema at
each Test, shared/named, nested Set and Variable acquisition site. The check
does not repair input. Generic select/collect, unknown fields/capabilities,
capability conflicts and invalid selectors fail. Native cmdlet.select remains
an acquisition parameter. Literal/record/evidence maps are opaque. Variable
capability scope starts fresh, so the Registry acquisition does not inherit
the consuming Shell Test capability. Public schema validation here means the
complete public validator with mandatory capability checking; the unchanged
generic Draft202012 structural schema alone is insufficient.

The historical migration entrypoint uses this same visitor, verifies exact
source inverse, preserves nested capability identity, and emits compact hybrid
YAML with parsed JSON parity. Current validation never calls migration. The
stronger gate also exposed a source-backed Registry adapter defect: it emitted
a bare hive enum instead of the existing required equality predicate. Only the
0.4 adapter output was corrected. Its source attestation and independent OVAL
round-trip tests remain enforced; 0.3 generation is unchanged. Two older Unix
positive fixtures now use their actual approved `full_path`/`filesystem` Object
shape. Apache migration tests now verify the nested-Object inverse and genuine
cmdlet preservation instead of expecting the old traversal omission.

## SV-278139 source and candidate

Original XCCDF `xccdf_mil.disa.stig_rule_SV-278139r1182083_rule`, Definition
`oval:navy.navwar.niwcatlantic.scc.windows:def:278139`, Test
`oval:navy.navwar.niwcatlantic.scc.windows:tst:27813901`; Shell Object suffix
`obj:27813901`, nested Registry Object suffix `obj:27813902`.
Original Server 2025 ZIP SHA-256:
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0`;
original XML SHA-256:
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.
The full XCCDF/catalog/OVAL closure and source hashes are preserved in
[candidate-proof.json](v04-object-processing/SV-278139.candidate-proof.json).

Before, at the exact Variable-local acquisition site (descriptive Object title
omitted here only for readability):

```yaml
object:
  capability: windows.registry
  select:
    hive: {equals: local_machine}
    key: {equals: SYSTEM\\CurrentControlSet\\Services\\Netlogon\\Parameters}
    name: {equals: SysVol}
```

After explicit historical migration:

```yaml
object: {capability: windows.registry, hive: {equals: local_machine}, key: {equals: SYSTEM\\CurrentControlSet\\Services\\Netlogon\\Parameters}, name: {equals: SysVol}}
```

The [complete corrected YAML](v04-object-processing/SV-278139.corrected.assessment.yaml)
and [JSON](v04-object-processing/SV-278139.corrected.assessment.json) retain that
title, command construction, Variable expression, field conditions and ordering.
Independent original-source comparison of this complete corrected Assessment:
**PROVED**, without a new normalization. Exact source inverse: PASS. Both public
CLI validation and paired compilation: PASS. The closed compilation harness
uses a synthetic wrapper Benchmark/Rule only; the source comparison uses the
actual original Rule/Definition and complete corrected Assessment.

Compiled program SHA-256:
`d11776285ff48dae2e7684816d6d262b69871a740a0c7ef27076dfb3184acb1c`.
JSON/YAML compiled bytes and source operands agree. This candidate is **not a
replacement package**, and does not promote the old packaged SV-278139 or change
24/883 proof coverage. Scanner and publisher-trust gates remain separate.

## Read-only corpus audit

Pinned JSON archive SHA-256:
`1e913e9a037c0fa6eb0477ab55a3fefe7100b73152e8fa91391d0eff512688f9`;
YAML archive SHA-256:
`5f5e6d3316182b820ce5612a06619426edeb2ddf4c16ea06ecd37b9d5edfd86f`.
All 4,012 parsed documents agree. All six bundle hashes/CRCs were checked against
the previous acceptance pins. Auditing did not write any archive or bundle.

| View | Documents | Object sites | Variable sites | Generic wrappers | cmdlet.select | Invalid docs before → after wrapper flattening |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Authoring source | 4,012 | 1,563 | 112 | 110 | 22 | 54 → 5 |
| Apache | 665 | 985 | 79 | 78 | 1 | 31 → 3 |
| Windows 11 | 1,151 | 1,003 | 13 | 12 | 12 | 15 → 3 |
| Server 2025 | 1,236 | 1,010 | 22 | 20 | 11 | 17 → 4 |
| Server DNS | 724 | 913 | 15 | 14 | 1 | 16 → 3 |
| Oracle Linux | 1,488 | 908 | 7 | 6 | 1 | 9 → 3 |
| RHEL | 1,498 | 969 | 11 | 10 | 1 | 11 → 4 |

Package totals include repeated shared dependencies and must not be summed as
unique source Assessments. Before/after is an **in-memory wrapper-only view**,
not a rebaseline or blanket validity/equivalence claim. Every changed document
has an exact migration inverse; no initially accepted canonical document loses
acceptance. The source has 110 wrappers in 51 documents: 108 Variable roots and
two Variable Set children. By capability: Shell 82, Registry 13, textfilecontent54
6, environmentvariable58 4, unix.file 2, sid_sid 1, appcmd 1, unix.password 1.

[object-sites.csv](v04-object-processing/object-sites.csv) has all 7,351
source/package site rows, exact paths, parent sections, capabilities, explicit
versus inherited scope, exceptions and before/after hashes.
[object-audit.json](v04-object-processing/object-audit.json) records exact
counts by capability/section, every invalid document and diagnostic, source and
bundle pins, and the candidate proof. Source schema diagnostics fall 123 → 7.

Remaining wrapper-only-view defects: Server 2025 SV-278028 Variable Set Filter
scalar `require`; RHEL SV-258134 two `value_match: all` selectors; shared Linux
initialization-files-0740 two Set Filter sites; interactive-user-home-dirs-0750
one Filter site; uids-unique one Filter site. Five source documents, seven Object
schema errors. These historical predicate tokens are newly exposed invalid
input, not a reason to weaken the gate or silently infer migration semantics.
The pinned six bundles therefore remain invalid under complete Object checking;
their old structural-schema acceptance is insufficient release evidence.
Future source-backed predicate migration and an explicitly authorized package
rebuild are required; neither is performed here.

## Validation and reproduction

Local Python 3.12 venv:
`/workspace/.onboarding/rebaseline-venv/bin/python` (existing pinned dependency
environment). No credential changes. Commands run from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/audit_v04_object_processing.py \
  --source-json /workspace/.onboarding/package-acceptance/current.json.zip \
  --source-yaml /workspace/.onboarding/package-acceptance/current.yaml.zip \
  --bundles-dir /workspace/.onboarding/package-acceptance/compiled \
  --inputs-dir /workspace/.onboarding/package-acceptance/inputs \
  --output-dir /tmp/object-audit
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/test_generate_capability_schema_v04_corpus.py \
  --output /tmp/100-capability-census.json
```

Mandatory execution used the unchanged 23 pinned source bindings from the prior
workflow reconciliation. To reproduce the exact local command with those inputs:

```python
import json, os, subprocess, sys
bindings = json.load(open('/workspace/.onboarding/workflow-reconciliation/bindings.json'))
env = {**os.environ, **bindings, 'PYTHONDONTWRITEBYTECODE': '1',
       'PYTHONPATH': '.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003'}
subprocess.run([sys.executable, 'tools/run_current_tool_regressions.py',
                '--report', '/tmp/mandatory.json'], env=env, check=True)
```

Source/input provisioning is documented in the existing workflow-reconciliation
and package-acceptance reports. The three operator tests also require the pinned
XSD work link `work/oval-5123/oval-schemas` to
`third_party/scap-1.4-schemas/oval_5.12.3`. This test workspace is not committed.

Baseline: **2,960 tests, 0 failures, 0 errors, 1 optional skip**. Final mandatory:
**2,974 tests, 0 failures, 0 errors, the same 1 skip**, after the portability
follow-up (initial implementation: 2,973). No tests removed, demoted,
skipped or weakened. Nine new Object tests and five read-only decision tests.
The first development run exposed two obsolete Apache expectations and nine
Registry/fixture errors; shared causes were corrected and the suite rerun.
[mandatory-results.json](v04-object-processing/mandatory-results.json) preserves
final counts and the exact preexisting optional original-corpus census skip.
The 100-capability audit: **100 generated, zero failures**, 140 selectors,
694 named predicates; complete report committed alongside the inventory.
Final targeted suite: **89 tests, all passed** (initial implementation: 88), using:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python -m unittest \
  test_v04_object_contract test_v04_windows_all_exist_decisions \
  test_scap_converter_core test_v04_approved_pipeline test_v04_public_cli_smoke \
  test_v04_public_validator test_v04_package_consumer test_v04_flat_object_authoring \
  test_v04_apache_preview_compatibility test_v04_canonical_source_ir \
  test_v04_native_bundle_compiler
```

The read-only decision packet's five tests were rerun after adding the exact
source-text discrepancy: all passed. Terminal hosted checks are recorded in
the handoff.

## Hosted-CI follow-up and historical classification

At the implementation SHA, hosted canonical fast checks, current-design
regression, rebaseline smoke, draft schema, converter bridge and clean-extract
smoke passed. Two additional workflows initially failed:

- [Windows XML pilot](https://github.com/vanderpol/scap-ng/actions/runs/40191627191):
  failed at the historical flat-Object projection/export step. Its environment
  installs PyYAML/lxml, not jsonschema. The shared visitor's initial eager
  validation imports introduced a new implicit dependency. Local cold-import
  reproduction with jsonschema/referencing unavailable produced
  `ModuleNotFoundError`; the portability correction makes validation imports
  lazy, preserves mandatory validation, and adds a `python -S` visitor regression.
  Full migration/inverse also passes with those imports explicitly forbidden.
  The workflow now tracks the shared visitor path, so the correction is actually
  exercised in hosted CI. No dependency failure is ignored or validation skipped.
- [Proposed condition-fields proof](https://github.com/vanderpol/scap-ng/actions/runs/40191627161):
  existing historical proposal tooling expects removed schema definition
  `all_items_requirement`. Exact local error: `KeyError: 'all_items_requirement'`.
  The workflow's five-module first step runs 54 tests with the **same four errors
  on unchanged ce9eadca7 and the implementation**. This is not introduced by the
  Object correction. The historical tests/workflow remain visible and unchanged;
  no new schema alias or release-gate change is authorized here. Reproduce using
  `python -m unittest test_v04_ci_integration test_validate_v04_fields_condition_preview test_build_v04_and_or_fields_candidate test_rename_v04_field_requirement_preview test_research_v04_oval_logic_scopes`
  with `PYTHONPATH=tools`, on each pinned checkout.

Public run/job pages expose step conclusions and the annotation
`Process completed with exit code 1.`. The public raw-log request returned
`curl: (22) The requested URL returned error: 404`; diagnoses above distinguish
locally reproduced errors from unavailable hosted stack traces.

An unrelated preexisting workflow also starts automatically when the public
validator changes: [0.3 six-STIG publisher](https://github.com/vanderpol/scap-ng/actions/runs/40191627218).
Its definition can create 0.3 release assets and post to #200. This task did not
dispatch it, alter it or authorize a new 0.3 publication. On discovering that
side effect during CI review, `gh run cancel 40191627218 --repo vanderpol/scap-ng`
was attempted once. Cancellation was blocked before the request by exact error:

`Get "https://api.github.com/repos/vanderpol/scap-ng/actions/runs/40191627218?exclude_pull_requests=true": Forbidden`

**External permission/owner action:** inspect/cancel that unrelated publishing
run and decide separately how to prevent automatic historical publication on
ordinary validator changes. No gate was changed or bypassed here. No local
six-STIG regeneration or replacement was performed. Terminal CI and any observed
publication outcome will be stated explicitly in the final handoff.

## Decisions and handoff

The separate [two-case all_exist packet](v04-windows-all-exist-decisions.md)
analyzes each of three original Tests, preserves error/unknown and mixed-item
counterexamples, and records a newly exposed incomplete-result reference-helper
discrepancy. Owner review is required; no new normalization or helper correction
was implemented. The independent Object implementation is not blocked by that
separate semantic decision.

GitHub issue-write access was previously blocked by exact sanitized error
`Post "https://api.github.com/graphql": Forbidden`. No repeated write attempt
was made; this committed report is the authorized issue #251 fallback handoff.
