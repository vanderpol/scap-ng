# Issue 21 result-size comparison

Status: controlled matched-fixture comparison, not scanner-performance data.

The files in this directory describe the same one-target, one-Benchmark,
one-Rule failed scan population.

## Raw file sizes

| Representation | Bytes | Scope |
| --- | ---: | --- |
| Minimal schema-valid SCAP 1.4 ARF/XCCDF result | 1,223 | Run/target/Rule policy result only; no detailed OVAL Results/System Characteristics payload. |
| SCAP-NG JSONL projection | 1,823 | Self-contained scan-summary event plus self-contained Rule event. |
| SCAP-NG canonical scan index | 1,064 | Normalized run/target/result references. |
| SCAP-NG canonical Benchmark result | 1,764 | Benchmark/Rule result and policy-facing context. |
| SCAP-NG detailed Assessment result | 2,345 | Detailed Test/Object/Item/State evidence for the failed Rule. |
| SCAP-NG canonical package members above, total | 5,173 | Detailed logical result for the same Rule. |

For this deliberately tiny one-Rule sample, the JSONL projection is 600 bytes
(about 49.1%) larger than the minimal XCCDF-only ARF. The detailed NG members are
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

The detailed fixture, `matched-scap14-detailed.arf.xml`, now includes:

- the XCCDF Rule result;
- OVAL Definition/Test results;
- OVAL System Characteristics with the observed UNIX permissions equivalent to
  mode `0666`;
- the source OVAL Definition/Test/Object/State expressing the required root-owned
  permissions equivalent to mode `0644`.

This makes the detailed fixture self-contained for the same observed-versus-
required root-cause question exposed by the NG Rule + Assessment results.

| Detailed representation | Bytes |
| --- | ---: |
| Self-contained SCAP 1.4 ARF + XCCDF + OVAL source/Results/System Characteristics | 9,316 |
| SCAP-NG canonical scan + Benchmark + detailed Assessment members | 5,173 |

For this deliberately tiny one-Rule self-contained detailed case, the normalized
NG package is 4,143 bytes, or about **44.5%**, smaller than the matched ARF.

The ratio is a controlled fixture result, not a general compression claim.
Fixed overhead, Rule count, evidence volume, repeated context, projection choice,
and serialization details can materially change it. The minimal XCCDF-only
comparison remains important: the self-contained NG JSONL event is larger there
because it deliberately repeats context for SIEM indexing.

Strict ARF and nested OVAL XSD validation is part of the regression suite.
Current-design regression run 36942343930 passed on both Ubuntu and Windows with
the self-contained source OVAL Definitions included, so the 9,316-byte ARF
fixture and the comparison inputs are schema-validated at this checkpoint.

Compression should be measured separately from raw size because both XML and
JSON compress heavily and production transport/storage may use compression.
