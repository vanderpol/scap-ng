# Assessment documentation foundation — 2026-10-03

Owner requested one authoritative knowledge source for Assessment files and
accepted starting foundational Markdown during 0.2.0 stabilization, with bounded
Codex expansion after structure and examples exist.

## Delivery

- [Reference entry point](../specification/assessment/reference/README.md), shared
  behavior guide, reusable capability template, and Unix file/direct-Variable
  references with every mapped field and approved Unix result-only name.
- Source byte/blob pins at NG checkpoint
  `303419800ffcab05522edadc043e7f282a391812`, with adapted source locators and
  distinct implementation/coverage limits.
- Links from the specification, Assessment Method, current review, and draft
  0.2.0 guide. No parallel review surface and no frozen iteration changes.
- `python tools/check_assessment_reference.py` checks links, documented command
  paths, exact committed source bytes and both starter field tables. It uses Git
  blobs so CRLF checkout conversion does not corrupt provenance checks. Current
  regression CI runs this check on Linux and Windows.

Local validation: all 73 maintained current-regression commands pass, including
the reference consistency check (five Markdown documents, 12 source pins, two
capability field inventories). The preservation audit reports zero failures
across 34,242 baseline paths. Remote exact-head CI remains a publication gate.

## Authority and limits

Shared runtime semantics retain their maintained Markdown home. Existing JSON
capability mappings still generate structural schema projections. A structured
YAML catalog generating schemas and documentation is an intended future design,
not an implemented replacement. Useful field descriptions/examples should carry
through to schema annotations; collection/evaluation requirements cannot exist
only in those annotations.

The references retain gaps rather than invent target behavior. Direct-Variable
zero-value Test execution still requires an independently justified conformance
table; Object-selector and expected-State zero-value rules must not be guessed
onto it without source-backed analysis. Callback guard results, recorded Item
comparisons and migration round trips are different evidence from real target
acquisition/comparison. This checkpoint does not finalize 0.2.0.

## Next work

Implement bounded native ESX host capability groups from the merged 22-new-Test
inventory (#131), preserving existing 5.12.3 behavior and source-backed field
meanings. Add each new capability's reference and positive/negative source cases
alongside its mapping. Keep VMware VM inherited contracts and management-plane
target identity explicit. Kubernetes follows with its version prerequisites.

Track full documentation/corpus expansion in #128. Notify the owner with a
verbose self-contained Codex task only once the finalized 0.2.0 checkpoint and
its acceptance inputs are ready; the starter catalog is not that readiness gate.

Provenance: Common native explanatory organization, Adapted pinned OVAL field
documentation, Evidence/Audit owner scope and exact implementation limits.
