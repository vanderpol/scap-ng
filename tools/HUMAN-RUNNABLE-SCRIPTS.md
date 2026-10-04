# Human-runnable SCAP-NG tools

This guide documents intentional command-line tools that a human may run from a local checkout. It does **not** list import-only Python modules or `test_*.py` files.

Run commands from the repository root unless a section says otherwise.

## Common setup

Recommended environment:

```powershell
python --version
python -m pip install PyYAML==6.0.3 lxml==6.1.1 jsonschema cryptography
```

Python 3.12 is the maintained local baseline. Some packaging/signing experiments also require a local OpenSSL executable.

Before using generated native content, read:

- `research/iterations/003/design/CURRENT-DESIGN.md`
- `tools/README.md`

A green schema check, round trip, or converter run is evidence; it is not by itself proof of live-target or independent-scanner equivalence.

---

# 1. Normal human workflows

These are the preferred entry points for routine conversion, normalization, validation, packaging, and review work.

## Convert a pinned SCAP 1.4 package for current full review

**Script:** `tools/scap_upconvert_v003/convert_full_review.py`

Use this when you have a pinned SCAP 1.4 ZIP and want current Benchmark/Rule/Assessment review content.

```powershell
python tools/scap_upconvert_v003/convert_full_review.py ^
  --input "PATH_TO_SCAP.zip" ^
  --sha256 "EXPECTED_SHA256" ^
  --output work/review ^
  --schema third_party/scap-1.4-schemas/omni-schema.xsd
```

Useful options:

- `--benchmark-id`: override generated Benchmark ID.
- `--platform-id` / `--platform-title`: override platform metadata.
- `--split-root`: use component-resolved per-Rule OVAL from the rule splitter.
- `--sha256 auto`: only for a source already pinned by repository revision/path.

**Safety:** the output directory must be new or empty. The tool does not modify the source ZIP.

## Generate a complete NIWC Current review tree

**Script:** `tools/generate_niwc_current_review.py`

This wrapper performs the normal split + current conversion sequence from one original ZIP.

```powershell
python tools/generate_niwc_current_review.py "PATH_TO_SCAP.zip" ^
  --output work/current-review ^
  --split-root work/current-split ^
  --source-revision COMMIT_OR_TAG ^
  --source-repository-path "path/in/source/repository.zip" ^
  --schema third_party/scap-1.4-schemas/omni-schema.xsd ^
  --summary work/current-review-summary.json
```

Use this instead of manually chaining tools when creating a fresh current corpus review.

## Split a SCAP 1.4 benchmark into per-Rule OVAL

**Script:** `tools/scap14_rule_splitter.py`

Creates standalone, dependency-complete OVAL Definitions documents for XCCDF Rules.

```powershell
python tools/scap14_rule_splitter.py "PATH_TO_SCAP.zip" ^
  --output-dir work/rule-split ^
  --schema third_party/scap-1.4-schemas/omni-schema.xsd ^
  --source-revision COMMIT_OR_TAG ^
  --source-repository-path "path/in/source/repository.zip" ^
  --benchmark-key rhel9 ^
  --fail-on-unresolved
```

Use `--fail-on-unresolved` for review/CI-quality runs.

## Normalize exact duplicate Assessments

**Script:** `tools/scap_ng_repo_normalizer.py`

Dry-run/report-only is the default.

```powershell
python tools/scap_ng_repo_normalizer.py work/current-review ^
  --report work/normalizer-report.json
```

To create a normalized **copy**:

```powershell
python tools/scap_ng_repo_normalizer.py work/current-review ^
  --rewrite ^
  --output-root work/current-review-normalized ^
  --report work/normalizer-report.json ^
  --change-manifest work/normalizer-changes.json
```

Useful options:

- `--advisory all|assessments|rules|none`
- `--top-near N`: limit near-duplicate groups retained in the report.
- `--max-rule-candidates N`: limit similar Rule candidates; `0` means all.
- `--fingerprint-cache PATH`: persist fingerprints between runs.

**Safety:** exact semantic duplicates may be promoted automatically. Near duplicates are advisory only. The tool refuses to rewrite the source tree in place.

## Validate native JSON Schemas

**Script:** `tools/validate_native_json_schemas.py`

```powershell
python tools/validate_native_json_schemas.py work/current-review ^
  --schema-dir schema/v0.2.0 ^
  --report work/schema-validation.json
```

Migration-only content can explicitly enable the legacy conversion bridge with `--allow-unpromoted-conversion-vocabulary`. Strict native validation is the normal default.

## Validate native Assessment semantics

**Script:** `tools/validate_native_semantics.py`

Checks references and capability-specific graph semantics that JSON Schema cannot prove.

```powershell
python tools/validate_native_semantics.py work/current-review ^
  --report work/native-semantics.json
```

## Validate a native package graph

**Script:** `tools/validate_native_package_graph.py`

Checks Benchmark/Rule/Assessment cross-document resolution.

```powershell
python tools/validate_native_package_graph.py work/current-review ^
  --report work/package-graph.json
```

## Check the current authoring contract

**Script:** `tools/check_current_authoring_contract.py`

Checks current Test/Object/State/Variable vocabulary and presentation rules.

```powershell
python tools/check_current_authoring_contract.py work/current-review ^
  --report work/authoring-contract.json
```

This is a naming/structure guard, not a complete semantic evaluator.

## Compile current authoring trees into .scapng bundles

**Script:** `tools/scap_ng_content_compiler.py`

```powershell
python tools/scap_ng_content_compiler.py work/current-review-normalized ^
  --output-dir work/bundles ^
  --metrics work/compiler-metrics.json ^
  --source-revision SOURCE_COMMIT ^
  --scap-ng-revision SCAP_NG_COMMIT
```

Optional research signing:

```powershell
--sign-self-signed-test-cert
```

A self-signed test certificate demonstrates mechanics only; it does not establish publisher trust.

## Run the current OVAL → NG → OVAL round-trip corpus census

**Script:** `tools/scap_ng_roundtrip_v003/roundtrip_corpus_v003.py`

```powershell
python tools/scap_ng_roundtrip_v003/roundtrip_corpus_v003.py ^
  --corpus work/rule-split ^
  --out work/roundtrip ^
  --report work/roundtrip-report.json
```

Use `--inventory-only` to inventory without full round-trip work. Current layout is the default; historical layout must be selected explicitly.

## Reproduce the six 0.2.0 OVAL Board pilot conversions

**Script:** `tools/convert_board_pilot_v02.py`

Verify committed output from the pinned Self-Assertion checkout:

```powershell
python tools/convert_board_pilot_v02.py ^
  --source-root PATH_TO_PINNED_SELF_ASSERTION ^
  --check
```

Write regenerated pairs to a separate directory:

```powershell
python tools/convert_board_pilot_v02.py ^
  --output work/board-conversion
```

This is a bounded adapter around the maintained converter; it is not a second general converter.

## Audit repository preservation and current/archive boundaries

**Script:** `tools/audit_repository_layout.py`

```powershell
python tools/audit_repository_layout.py --check
```

To regenerate audit evidence:

```powershell
python tools/audit_repository_layout.py --output docs/audit
```

It inventories and checks; it never deletes or moves repository content.

---

# 2. Conversion pipeline and source-analysis utilities

These are useful for converter development, migration research, and detailed source accounting.

## Parse standalone OVAL into the semantic IR

**Script:** `tools/oval_semantic_ir.py`

```powershell
python tools/oval_semantic_ir.py input-oval.xml ^
  --output work/oval-ir.json ^
  --provenance work/oval-provenance.json ^
  --fail-on-unresolved
```

## Build unified SCAP 1.4 Benchmark IR

**Script:** `tools/scap14_benchmark_ir.py`

```powershell
python tools/scap14_benchmark_ir.py "PATH_TO_SCAP.zip" ^
  --split-root work/rule-split ^
  --output work/benchmark-ir.json
```

## Run the general SCAP 1.4 corpus research harness

**Script:** `tools/scap14_corpus_convert.py`

```powershell
python tools/scap14_corpus_convert.py INPUT1 INPUT2 ^
  --output-dir work/corpus-analysis ^
  --gate none
```

`--gate` accepts `none`, `ingest`, or `native`. This is a research harness, not the preferred current full-review converter.

## Build benchmark-level reuse inventory

**Script:** `tools/scap14_benchmark_reuse_inventory.py`

```powershell
python tools/scap14_benchmark_reuse_inventory.py "PATH_TO_SCAP.zip" ^
  --split-root work/rule-split ^
  --schema-catalog work/oval-schema-catalog.json ^
  --output work/reuse-inventory.json
```

## Analyze exact and parameterization-candidate Assessment reuse

**Script:** `tools/analyze_scapng_assessment_reuse.py`

Run `python tools/analyze_scapng_assessment_reuse.py --help` for the accepted converted-benchmark inputs, then supply `--output`.

This distinguishes exact technical equivalence from literal-abstracted parameterization candidates.

## Aggregate reuse inventories

**Script:** `tools/aggregate_scapng_reuse_inventories.py`

```powershell
python tools/aggregate_scapng_reuse_inventories.py work/a.json work/b.json ^
  --output work/reuse-summary.json
```

## Render exact-reuse research views

**Script:** `tools/render_scapng_reuse_views.py`

Consumes a reuse report and the canonical converted benchmark inputs and writes candidate presentation views with `--output-dir`. Use `--help` for the current input option names.

## Promote proven exact shared Assessments

**Script:** `tools/promote_exact_shared_assessments.py`

Consumes the exact-reuse report plus canonical converted benchmarks and writes promoted shared source under `--output-dir`.

Only proven exact semantic-reuse groups are eligible; parameterization candidates are not promoted automatically.

---

# 3. Validation, audit, and evidence utilities

## Validate the vendored SCAP 1.4 schema bundle

**Script:** `tools/validate_scap14_schema_bundle.py`

```powershell
python tools/validate_scap14_schema_bundle.py third_party/scap-1.4-schemas
```

## Build an OVAL schema semantic catalog

**Script:** `tools/build_oval_schema_semantic_catalog.py`

```powershell
python tools/build_oval_schema_semantic_catalog.py PATH_TO_OVAL_SCHEMAS ^
  --parser tools/oval_semantic_ir.py ^
  --output work/oval-schema-catalog.json
```

## Inventory OVAL XSD defaults and structural hazards

**Script:** `tools/oval_xsd_default_inventory.py`

```powershell
python tools/oval_xsd_default_inventory.py PATH_TO_OVAL_SCHEMAS ^
  --output work/xsd-defaults.json
```

## Inventory general XSD semantics

**Script:** `tools/inventory_xsd_semantics.py`

```powershell
python tools/inventory_xsd_semantics.py PATH_TO_SCHEMAS ^
  --output work/xsd-semantics.json
```

## Census explicit OVAL attribute values

**Script:** `tools/census_oval_attribute_values.py`

```powershell
python tools/census_oval_attribute_values.py INPUTS... ^
  --namespace NAMESPACE_URI ^
  --element ELEMENT_NAME ^
  --attribute ATTRIBUTE_NAME ^
  --output work/attribute-census.json
```

Repeat `--attribute` for multiple attributes.

## Census explicit OVAL mask usage

**Script:** `tools/census_oval_mask_usage.py`

```powershell
python tools/census_oval_mask_usage.py INPUTS... ^
  --output work/mask-census.json
```

## Audit OVAL 6 new-Test inventory

**Script:** `tools/audit_oval_new_tests.py`

```powershell
python tools/audit_oval_new_tests.py ^
  --upstream-repo PATH_TO_PINNED_OVAL_REPO ^
  --output work/oval-new-tests.json ^
  --check
```

The 5.12.3 baseline is intentionally preserved; this tool inventories genuinely new OVAL 6 work.

## Audit current capability mapping/test-content coverage

**Script:** `tools/audit_capability_coverage.py`

```powershell
python tools/audit_capability_coverage.py ^
  --output work/capability-coverage.json
```

This is conservative static evidence, not target-execution coverage.

## Audit Object/State/Item field parity

**Script:** `tools/audit_capability_state_item_parity.py`

Run with `--help` for the current mapping/root inputs; add `--json` for machine-readable output.

## Audit explicit defaults in generated v003 content

**Script:** `tools/audit_v003_explicit_defaults.py`

```powershell
python tools/audit_v003_explicit_defaults.py ^
  --root work/current-review ^
  --report work/default-audit.json
```

## Inventory result-only collected Item fields

**Script:** `tools/inventory_collected_item_fields.py`

```powershell
python tools/inventory_collected_item_fields.py ^
  --output work/collected-item-fields.json
```

## Inventory XCCDF Value/Profile/CPE gaps

**Script:** `tools/inventory_xccdf_valid_gaps.py`

```powershell
python tools/inventory_xccdf_valid_gaps.py PATH_TO_SCAP.zip ^
  --output work/xccdf-gap-inventory.json
```

## Census observed native document shapes

**Script:** `tools/native_schema_census.py`

```powershell
python tools/native_schema_census.py work/current-review ^
  --output work/native-schema-census.json
```

This records observed shapes; it does not generate the normative schema.

---

# 4. Result and reporting research tools

These are runnable human tools, but the 0.2.0 result model remains a draft/research surface.

## Analyze an SCC/SCAP result ZIP

**Script:** `tools/analyze_result_bundle.py`

Read-only summary:

```powershell
python tools/analyze_result_bundle.py result.zip ^
  --output work/result-bundle-summary.json
```

## Validate/assemble draft Assessment result sets

**Script:** `tools/assessment_results_v02.py`

```powershell
python tools/assessment_results_v02.py ^
  --assessments board/review-content/0.2.0/content ^
  --result-set board/review-content/0.2.0/expected/unix-file.result-set.json
```

It does not acquire target data or independently prove State comparison truth.

## Build or verify an unsigned draft result package

**Script:** `tools/result_package_v02.py`

Verify a package:

```powershell
python tools/result_package_v02.py work/result.scapng-results.zip ^
  --assessments PATH_TO_ASSESSMENTS
```

For package construction, use `--build-input` with the JSON input described by `--help`.

## Project canonical results to JSONL/SIEM form

**Script:** `tools/project_results_jsonl.py`

```powershell
python tools/project_results_jsonl.py ^
  --scan-result PATH_TO_SCAN_RESULT.json ^
  --output work/results.jsonl
```

The JSONL view is derived/denormalized and does not redefine canonical result semantics.

## Generate collected-Item contract examples

**Script:** `tools/collected_item_contract_v02.py`

```powershell
python tools/collected_item_contract_v02.py ^
  --output work/collected-item-contract.json
```

## Exercise draft reported-elements controls

**Script:** `tools/reported_elements.py`

This CLI has subcommands. Use:

```powershell
python tools/reported_elements.py --help
```

The generate path uses `--mapping` and `--output`; the projection path uses `--assessment`, `--observations`, and `--output`.

## Run conditional-semantics conformance fixtures

**Script:** `tools/conditional_conformance.py`

```powershell
python tools/conditional_conformance.py ^
  --suite tests/conditional-0.2.0 ^
  --report work/conditional-report.json
```

This is a controlled-result semantics model, not a scanner.

## Resolve the worked Tailoring example

**Script:** `tools/resolve_tailoring_example.py`

```powershell
python tools/resolve_tailoring_example.py ^
  --benchmark PATH_TO_BENCHMARK.yaml ^
  --tailoring PATH_TO_TAILORING.yaml ^
  --organizational-input PATH_TO_INPUT.yaml ^
  --output work/resolved-policy.json
```

It validates documented policy boundaries; it does not execute Assessments.

---

# 5. Round-trip specialist utilities

These support deeper OVAL/NG equivalence investigations.

## Run fixture round trips

**Script:** `tools/scap_ng_roundtrip_v003/run_roundtrip.py`

```powershell
python tools/scap_ng_roundtrip_v003/run_roundtrip.py ^
  --fixtures PATH_TO_FIXTURES ^
  --repo-root . ^
  --out work/fixture-roundtrip
```

## Build an aggregate OVAL omni-schema

**Script:** `tools/scap_ng_roundtrip_v003/build_full_oval_omni.py`

```powershell
python tools/scap_ng_roundtrip_v003/build_full_oval_omni.py ^
  --schemas PATH_TO_OVAL_SCHEMAS ^
  --output work/full-oval-omni.xsd
```

## Audit OVAL XSD defaults/contracts

**Script:** `tools/scap_ng_roundtrip_v003/audit_oval_xsd_defaults.py`

```powershell
python tools/scap_ng_roundtrip_v003/audit_oval_xsd_defaults.py ^
  --schemas PATH_TO_OVAL_SCHEMAS ^
  --out work/oval-xsd-default-audit
```

## Compare Schematron findings with the source baseline

**Script:** `tools/scap_ng_roundtrip_v003/compare_schematron_baseline.py`

```powershell
python tools/scap_ng_roundtrip_v003/compare_schematron_baseline.py ^
  --schemas PATH_TO_SCHEMAS ^
  --corpus PATH_TO_SOURCE_CORPUS ^
  --report PATH_TO_REGENERATED_REPORT ^
  --output work/schematron-comparison.json
```

## Verify aggregate regenerated roots

**Script:** `tools/scap_ng_roundtrip_v003/verify_aggregate_roots.py`

```powershell
python tools/scap_ng_roundtrip_v003/verify_aggregate_roots.py ^
  --source PATH_TO_SOURCE_OVAL ^
  --regenerated PATH_TO_REGENERATED_OVAL ^
  --mapping-report PATH_TO_MAPPING.json ^
  --output work/root-verification.json
```

## Summarize a current corpus census

**Script:** `tools/scap_ng_roundtrip_v003/summarize_current_corpus.py`

```powershell
python tools/scap_ng_roundtrip_v003/summarize_current_corpus.py work/corpus-results ^
  --output work/corpus-summary.json
```

---

# 6. Capability-schema development

## Generate a capability schema from a reviewed mapping

**Script:** `tools/generate_capability_schema.py`

```powershell
python tools/generate_capability_schema.py ^
  --mapping schema/v0.2.0/capability-mappings/supported/unix.file.json ^
  --output work/unix.file.schema.json
```

This is **not** a mechanical XSD-to-JSON-Schema translator. The reviewed mapping is the semantic control point.

---

# 7. Historical/research reproduction commands

These remain executable for evidence and comparison, but are **not normal current-design entry points**.

## Historical generic SCAP 1.4 → candidate NG compiler

**Script:** `tools/scap14_to_scapng.py`

```powershell
python tools/scap14_to_scapng.py work/benchmark-ir.json ^
  --output-dir work/historical-ng ^
  --schema-catalog work/oval-schema-catalog.json
```

Use for historical/research comparison only; do not treat its output as the current native baseline.

## Historical package builder

**Script:** `tools/build_scapng_from_converted_source.py`

```powershell
python tools/build_scapng_from_converted_source.py work/historical-ng ^
  --output-dir work/historical-bundles
```

This builds older prototype signed packages and is superseded by `scap_ng_content_compiler.py` for current work.

## Historical Ansible-inspired renderer

**Script:** `tools/render_ansible_inspired_benchmark.py`

```powershell
python tools/render_ansible_inspired_benchmark.py work/canonical-benchmark.json ^
  --output-dir work/ansible-inspired
```

This is an authoring-style experiment; there is no Ansible runtime dependency.

## Historical conversion verifier

**Script:** `tools/verify_scap14_to_scapng_conversion.py`

```powershell
python tools/verify_scap14_to_scapng_conversion.py work/historical-ng
```

Optional expected-count arguments and Ansible-inspired comparison are available through `--help`.

## Historical prototype bundle verifier

**Script:** `tools/verify_scapng_prototype_bundle.py`

```powershell
python tools/verify_scapng_prototype_bundle.py work/prototype.scapng
```

Verifies the older Ed25519 prototype package format; it is not the current trust profile.

## Historical local runner

**Script:** `tools/scap_upconvert_v003/run_local.py`

Retained for reproduction only. Current local conversion uses `convert_full_review.py`. See `tools/scap_upconvert_v003/README.md` for the preserved historical instructions.

## Fixed-path RHEL 9 diagnostic inventory

**Script:** `tools/build_rhel9_diagnostic_review.py`

No arguments. It inventories existing repository output for diagnosis and does not regenerate/normalize native content. Use only when reproducing the research checkpoint that expects its fixed paths.

---

# 8. Repository/research maintenance

## Scaffold a new research iteration

**Script:** `tools/scaffold_research_iteration.py`

```powershell
python tools/scaffold_research_iteration.py 004
```

This creates the standard research-iteration skeleton. It does not make design decisions or populate content.

## Check starter-reference/source-pin consistency

**Script:** `tools/check_assessment_reference.py`

```powershell
python tools/check_assessment_reference.py
```

This is documentation/source-pin consistency evidence, not runtime conformance.

---

# Choosing the right command

For most human users:

1. **Convert:** `generate_niwc_current_review.py` or `convert_full_review.py`.
2. **Validate:** `validate_native_json_schemas.py`, `validate_native_semantics.py`, and `validate_native_package_graph.py`.
3. **Check authoring:** `check_current_authoring_contract.py`.
4. **Normalize:** `scap_ng_repo_normalizer.py` — dry run first.
5. **Compile:** `scap_ng_content_compiler.py`.
6. **Measure conversion fidelity:** `roundtrip_corpus_v003.py`.
7. **Use audit/research tools only when the question specifically requires them.**

When in doubt, run:

```powershell
python PATH_TO_SCRIPT.py --help
```

If a script is not listed here and is not a test, assume it is an internal/importable helper until its human-use contract is documented.
