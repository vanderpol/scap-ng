# Issue 21 result-size comparison

Status: controlled matched-fixture comparison, not scanner-performance data.

The files in this directory describe the same one-target, one-Benchmark,
one-Rule failed scan population.

## Raw file sizes

| Representation | Bytes | Scope |
| --- | ---: | --- |
| Minimal schema-valid SCAP 1.4 ARF/XCCDF result | 1,223 | Run/target/Rule policy result only; no detailed OVAL Results/System Characteristics payload. |
| SCAP-NG JSONL projection | 1,890 | Self-contained scan-summary event plus self-contained Rule event. |
| SCAP-NG canonical scan index | 1,064 | Normalized run/target/result references. |
| SCAP-NG canonical Benchmark result | 2,138 | Benchmark/Rule result and policy-facing context. |
| SCAP-NG detailed Assessment result | 2,345 | Detailed Test/Object/Item/State evidence for the failed Rule. |
| SCAP-NG canonical package members above, total | 5,547 | Detailed logical result for the same Rule. |

For this deliberately tiny one-Rule sample, the JSONL projection is 667 bytes
(54.5%) larger than the minimal XCCDF-only ARF. The detailed NG members are
larger still because they contain detailed evidence that the minimal ARF fixture
does not.

This result is intentionally retained even though it does not show a size win.
A self-contained SIEM event repeats context that a normalized package stores
once, and fixed-format overhead dominates a one-Rule sample.

## What this comparison proves

- The comparison population is matched.
- The ARF fixture is intended to be validated against the vendored ARF/XCCDF
  schemas in CI.
- The JSONL projection is byte-stable and generated from the canonical NG
  result fixtures.
- A minimal policy-result ARF is not an apples-to-apples substitute for detailed
  OVAL Results/System Characteristics.

## Remaining apples-to-apples comparison

The meaningful detailed comparison is:

- ARF containing XCCDF Rule results **plus** matched detailed OVAL Results and
  System Characteristics; versus
- the canonical SCAP-NG scan + Benchmark + Assessment result package for the
  same observations.

That detailed SCAP 1.4 fixture should be schema-valid and contain the same
observed mode value, expected value, Test outcome, and collected Item represented
by the NG Assessment result. Until that fixture exists, no claim that NG
detailed results are smaller than ARF is justified.

Compression should be measured separately from raw size because both XML and
JSON compress heavily and production transport/storage may use compression.
