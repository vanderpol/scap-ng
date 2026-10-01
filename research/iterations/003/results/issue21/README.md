# Issue #21 result projection fixtures

This directory contains a small canonical SCAP-NG result package slice and the
deterministic JSONL/SIEM projection expected from it.

Files:

- `scan-result.json` — run-level canonical result index.
- `benchmark-result.json` — policy-facing Benchmark/Rule result.
- `expected.jsonl` — derived projection produced by
  `tools/project_results_jsonl.py`.

The projection intentionally contains one `scan_summary` event followed by one
independently useful `rule_result` event. Detailed Assessment execution graphs
remain referenced through `assessment_result_ref` and are not duplicated into
the SIEM event.

The regression suite compares the generated JSONL byte-for-byte with
`expected.jsonl` on Linux and Windows.

## ARF size comparison status

A defensible size comparison against SCAP 1.4 ARF requires a representative ARF
produced for the same Benchmark, target, and result population. No ARF result
artifact is currently checked into this repository. The project therefore does
not publish a synthetic or guessed compression/size claim here. Once a matched
ARF sample is available, compare raw bytes and compressed transport bytes
against both the canonical SCAP-NG package and this JSONL projection.
