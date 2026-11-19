# RI PCRE2 prototype results (Issue #62, Phase 2)

**Status: isolated prototype only; not a production RI implementation.**

The RI prototype is in unmerged RI review PR
[#57](https://github.com/vanderpol/scap-ng-ri/pull/57), branch
[`codex/issue62-regex-prototype`](https://github.com/vanderpol/scap-ng-ri/tree/a80d1d2/prototype/regex),
at commit `a80d1d2`. Its source and machine-readable result receipt are
published in the RI repository; this canonical document records the result
against the Phase 1 profile and vector pin. No RI evaluator entry point,
collector, schema, converter, archive, fixture, or pin was changed.

## What was tested

Both modes use the same bounded PCRE2 10.49 C core, UTF-8 + UCP, `ANYCRLF`,
JIT disabled, and a one-entry compiled-pattern cache:

| Bound | Prototype value |
| --- | ---: |
| Pattern bytes | 10,000 |
| Subject bytes | 100,000 |
| Match steps | 1,000,000 |
| Match depth | 1,000 |
| Match heap | 64 MiB |
| Wall deadline | 2 seconds (automatic callout; helper can additionally be killed) |

* **cgo:** PCRE2 runs in the RI process.
* **Native helper:** a persistent native process uses a length-prefixed binary
  protocol; Go remains `CGO_ENABLED=0` and IPC is included in timings.

The shared vectors were consumed directly from `scap-ng` commit `6983525`.
Held/editor-only and owner-decision cases were skipped; diagnostic outcomes
never become nonmatch. The editor cancellation witness returned a PCRE2 depth
limit in this interpreter, so the vector accepts `resource_limit` alongside
`cancelled`; both are diagnostic outcomes.

## Results

Linux amd64, Go 1.27.4, PCRE2 10.49, Unicode data 17.0.0:

| Mode | Vector cases | 100,001 Items | Median time (5 trials) | Median throughput |
| --- | ---: | ---: | ---: | ---: |
| cgo | 33/33 pass | 100,001 | 177.009 ms | 564,948.7 Items/s |
| native helper | 33/33 pass | 100,001 | 2,487.632 ms | 40,199.3 Items/s |

The helper is approximately 14.1x slower in this microbenchmark because each
Item crosses the persistent process protocol. This is not a scanner benchmark:
all Items reuse one pattern and one short subject, and no collector or
Assessment evaluation path is involved.

## Batched/streaming helper results

The follow-up prototype adds a streaming batch protocol. One pattern and batch
count are sent once; subject frames and result frames stream in order. The
helper retains one subject/result, while the Go client retains only the current
batch. Five trials used 100,001 Items at each batch size:

| Batch size | cgo median Items/s | Helper median Items/s | cgo median ms | Helper median ms | Max client input/result buffers |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 566,225 | 21,658 | 176.610 | 4,617.253 | 10 bytes / 1 result |
| 100 | 588,750 | 362,130 | 169.853 | 276.147 | 1,000 bytes / 100 results |
| 1,000 | 601,166 | 409,474 | 166.345 | 244.218 | 10,000 bytes / 1,000 results |
| 10,000 | 590,116 | 416,751 | 169.460 | 239.954 | 100,000 bytes / 10,000 results |

Streaming improves helper throughput by about 19.2x from batch 1 to 10,000,
while cgo remains faster. The one-trial process RSS observations were 11,176
KiB for cgo and 9,336 KiB for the helper; Go heap deltas varied with allocator
state and are not memory-budget claims.

The batch contract probes passed: ordering was preserved, each Item received a
separate status/capture diagnostic, the malicious `(a+)+$` batch produced only
diagnostic outcomes, and terminating the helper made the next operation return
`engine_unavailable`. In-flight cancellation is not claimed; it requires a
supervisor contract.

The Windows plan is now explicit in the prototype README: build and hash
Unicode-enabled PCRE2 10.49 with JIT disabled using pinned MinGW-w64 (or a
separately qualified MSVC/DLL route), produce signed amd64/arm64 helper and
cgo artifacts, run the full vector/batch/crash/timeout/RSS matrix on clean
Windows hosts, and record SBOM/license/DLL-loading evidence.

## Linux/Windows comparison

| Alternative | Linux result | Windows result in this environment | Packaging implication |
| --- | --- | --- | --- |
| cgo/native PCRE2 | Built and ran the vectors and benchmark. | The pure cgo build was not possible: the environment has no Windows C headers/toolchain (`windows.h` missing). | Requires per-architecture C toolchain and PCRE2 library, static/DLL strategy, ABI/SBOM/signing, and a changed cross-build lane. |
| Native helper | Built and ran the same vectors and benchmark. | The pure-Go helper launcher cross-compiled as a PE32+ amd64 binary with `CGO_ENABLED=0`; native helper compilation was not run because `x86_64-w64-mingw32-gcc` is unavailable. | Keeps Go cross-build simple and gives process cancellation/memory isolation, but requires signed helper packaging, IPC, lifecycle handling, and a native PCRE2 build per Windows architecture. |

Neither option has Windows runtime qualification. The result favors a helper
for the first security/isolation proof-of-concept and cgo for the performance
baseline; it does **not** select a release architecture. The next owner gate
is a reproducible Linux/Windows amd64+arm64 packaging matrix with native
cancellation, status mapping, and the same vectors.

## Scope boundary

This prototype does not authorize:

* adding PCRE2 to RI production dependencies or changing Go build flags;
* capability-specific regex engines or collector changes;
* schema/profile fields or regenerated YAML/archive output; or
* claiming scanner/runtime equivalence from these results.

The Phase 1 profile remains owner-review proposal status.
