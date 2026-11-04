# Issue #14 author-facing schema documentation audit

This is the separate authoring-text workstream for issue #14. It audits the
34 canonical JSON Schema roots and their nested `title`/`description` text as
shown by schema-driven editor hover/help. It does not change validation
keywords, scanner behavior, conversion semantics, or historical provenance.

The audit inventories titles, descriptions, and schema `examples` values across the roots. The current roots contain no `examples` keyword; the marker check also covers any examples added later. It removed internal design-history markers from author-facing text,
including numbered Decision references, issue/PR references, and implementation
alignment notes. The detailed rationale remains in `docs/PROVENANCE.md`, issue
trackers, and the design records. Technical terms such as OVAL, State, legacy,
cardinality, and native datatype remain where they explain the current grammar.

Changes include:

- `variables` now explains named typed variables and supported expressions in
  plain language rather than citing a numbered design decision.
- Dependency `purpose` and specification descriptions explain author meaning
  without issue references or provisional implementation history.
- Reserved function-expression and result-schema descriptions identify their
  authoring status without presenting internal candidate terminology as guidance.
- `tests/test_authoring_documentation.py` scans every canonical schema title and
  description and fails on obvious internal decision/PR markers.

This draft is intentionally separate from the operator/validation PR. It does
not censor legitimate technical terminology or remove historical evidence.
