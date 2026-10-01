# Issue 21 result-size comparison

Status: controlled matched-fixture comparison, not scanner-performance data.

The files in this directory describe the same one-target, one-Benchmark,
one-Rule failed scan population.

## Raw file sizes

| Representation | Bytes | Scope |
| --- | ---: | --- |
| Minimal schema-valid SCAP 1.4 ARF/XCCDF result | 1,223 | Run/target/Rule policy result only; no detailed OVAL Results/System Characteristics payload. |
| SCAP-NG JSONL projection | 2,138 | Self-contained scan-summary event plus self-contained Rule event. |
| SCAP-NG canonical scan index | 1,064 | Normalized run/target/result references. |
| SCAP-NG canonical Benchmark result | 2,584 | Benchmark/Rule result and policy-facing context. |
| SCAP-NG detailed Assessment result | 2,345 | Detailed Test/Object/Item/State evidence for the failed Rule. |
| SCAP-NG canonical package members above, total | 5,993 | Detailed logical result for the same Rule. |

For this deliberately tiny one-Rule sample, the JSONL projection is 915 bytes
(about 74.8%) larger than the minimal XCCDF-only ARF. The detailed NG members are
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

## Matched detailed comparison

A second fixture, `matched-scap14-detailed.arf.xml`, adds detailed OVAL Results
and System Characteristics to the same XCCDF Rule result. It represents the same
logical failed observation as the NG detailed result: UID 0 and UNIX permission
bits equivalent to mode `0666`, with the Test/Definition outcome false.

| Detailed representation | Bytes |
| --- | ---: |
| SCAP 1.4 ARF + XCCDF + OVAL Results/System Characteristics | 6,196 |
| SCAP-NG canonical scan + Benchmark + detailed Assessment members | 5,993 |

For this deliberately tiny one-Rule detailed case, the normalized NG package is
203 bytes, or about **3.3%**, smaller than the matched detailed ARF.

This is a fixture result, not a general compression claim. Fixed overhead,
number of Rules, amount of evidence, repeated context, projection choice, and
serialization details can all materially change the ratio. The earlier minimal
XCCDF-only comparison remains important: NG JSONL is larger there because each
SIEM event is intentionally self-contained.

Compression should be measured separately from raw size because both XML and
JSON compress heavily and production transport/storage may use compression.
