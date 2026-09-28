# SCAP Next Gen Tools

This directory stores reusable tooling related to SCAP-NG research, schema analysis, conversion, validation, packaging, and reproducibility.

Iteration-specific data and conclusions belong under `research/iterations/<NNN>/`; utilities that should survive multiple iterations belong here.

## Current tools

### SCAP 1.4 migration toolchain

- `oval_semantic_ir.py` — faithful OVAL 5.12.3 semantic importer, dependency graph, variable/function evaluation planning, set/filter/result algebra, and source accounting.
- `scap14_rule_splitter.py` — extracts one schema-valid standalone OVAL document per XCCDF rule with fixed-point dependency closure.
- `scap14_corpus_convert.py` — broad SCAP 1.4 corpus ingestion/accounting and deprecated-test remediation reporting.
- `scap14_benchmark_ir.py` — joins XCCDF policy/profile/value/check semantics to the per-rule OVAL IR into one benchmark conversion model.
- `scap14_to_scapng.py` — generic benchmark compiler that renders the same migrated semantics into combined-rule and split policy/assessment/binding candidate layouts.
- `verify_scap14_to_scapng_conversion.py` — checks rule accounting and semantic equivalence between the candidate renderings.
- `build_oval_schema_semantic_catalog.py` — schema-derived OVAL construct/deprecation catalog with checked-in OVAL governance reinstatement overrides.
- `analyze_scapng_assessment_reuse.py` — maps rules across converted benchmarks using normalized Check Text and full OVAL semantic equivalence, measures exact reuse and parameterization candidates, and reports maintenance-unit savings.
- `render_scapng_reuse_views.py` — renders measured exact reuse groups as combined shared-rule overlays, split shared assessments/bindings, and Ansible-inspired shared assessments/bindings.
- `test_scapng_assessment_reuse.py` — regression tests for exact semantic fingerprints, literal-only parameterization candidates, and rule-alignment evidence.

The migration tools are shared infrastructure rather than iteration-001-only experiments. Iteration-specific workflows and evidence may invoke them, but later iterations should reuse the same implementations rather than fork them.

### inventory_xsd_semantics.py

Recursively inventories XSD files, named elements/types, imports/includes, target namespaces, and documentation containing deprecation language.

This is intentionally an **inventory tool**, not an XSD-to-NG converter. Existing XSD structure is a migration input, not the desired NG architecture.

### analyze_result_bundle.py

Produces a sanitized structural/size summary of an SCC/SCAP result ZIP without preserving result contents.

Useful for measuring result bloat and element populations while avoiding committing endpoint-specific evidence.

### scaffold_research_iteration.py

Creates the stable directory skeleton for a future numbered research iteration.

Some migration tools require `lxml` and/or `PyYAML`; smaller inventory/scaffolding utilities remain standard-library-only.
