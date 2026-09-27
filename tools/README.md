# SCAP Next Gen Tools

This directory stores reusable tooling related to SCAP-NG research, schema analysis, conversion, validation, packaging, and reproducibility.

Iteration-specific data and conclusions belong under `research/iterations/<NNN>/`; utilities that should survive multiple iterations belong here.

## Current tools

### inventory_xsd_semantics.py

Recursively inventories XSD files, named elements/types, imports/includes, target namespaces, and documentation containing deprecation language.

This is intentionally an **inventory tool**, not an XSD-to-NG converter. Existing XSD structure is a migration input, not the desired NG architecture.

### analyze_result_bundle.py

Produces a sanitized structural/size summary of an SCC/SCAP result ZIP without preserving result contents.

Useful for measuring result bloat and element populations while avoiding committing endpoint-specific evidence.

### scaffold_research_iteration.py

Creates the stable directory skeleton for a future numbered research iteration.

These scripts currently use only the Python standard library so they remain easy to run in restricted development environments.
