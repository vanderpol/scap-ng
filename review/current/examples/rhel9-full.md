# RHEL 9 review example

The maintained RHEL 9 conversion is available as a [direct, durable RHEL 9 source ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-rhel9-source-preview.zip), with
`rhel9/candidate-authoring/` for the updated, embedded-predicate design,
`rhel9/faithful-authoring/` for comparison, and `rhel9/SCORECARD.md`.
These are complete source-derived STIG trees, not runtime scanner results.

For the short source-backed walk-through, use the
[Benchmark → Rule](../../../specification/examples/README.md) and
[Assessment](../../../specification/examples/assessments.md) examples.
The old research tree that this page linked to was removed; its historical
review is recoverable in Git history. Current generated source is held in
the downloadable release attachment, not duplicated in Markdown.

Conversion and compilation do not demonstrate live-scanner equivalence.
See the [0.3 release gate](https://github.com/vanderpol/scap-ng/issues/202).
