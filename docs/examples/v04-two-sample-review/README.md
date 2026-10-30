# SCAP-NG 0.4.0 — Windows 11 and RHEL 9 human-authoring review

**[For a broader review, open the proposed 40-Rule gallery](../v04-proposed-authoring-review/README.md).**

**October 30, 2026 — REVIEW CANDIDATE, NOT A FULL STIG OR FINAL RELEASE.**
See [review findings](REVIEW-FINDINGS.md), [syntax issue #264](https://github.com/vanderpol/scap-ng/issues/264),
and [broader Benchmark/content issue #265](https://github.com/vanderpol/scap-ng/issues/265).

These are two **one-Rule, four-file authoring excerpts** extracted from the
immutable 65-stream human-readable v2 evidence. The accompanying
`REVIEW-RECEIPT.json` pins original source ZIP/XML hashes, original/candidate
YAML hashes and exact per-State compaction undo records.

## Windows 11 — SV-253475

**UAC registry virtualization**: HKLM `Software\Microsoft\Windows\CurrentVersion\Policies\System`,
value `EnableVirtualization`, DWORD 1.

- [Assessment YAML](ms_windows_11/assessments/automated/SV-253475.automated.yaml)
- [Rule YAML](ms_windows_11/rules/SV-253475.rule.yaml)
- [One-Rule sample Benchmark](ms_windows_11/benchmark.yaml)
- [Applicability placeholder](ms_windows_11/applicability.yaml)

This Assessment is the main compact-`require` example. The pinned original
OVAL trace identifies **one source State**, so its two scalar AND fields may
be expressed as one `fields` mapping with a Test-wide `field_requirement`.
The original State and Test structures are recoverable exactly from the
receipt. This is a deliberate *changed* authoring program, not a retained
historical static proof.

## RHEL 9 — SV-257851

**`/home` mount `nosuid`**: at least one matching mount and every collected
Item must have at least one matching `mount_options` value.

- [Assessment YAML](rhel_9/assessments/automated/SV-257851.automated.yaml)
- [Rule YAML](rhel_9/rules/SV-257851.rule.yaml)
- [One-Rule sample Benchmark](rhel_9/benchmark.yaml)
- [Applicability placeholder](rhel_9/applicability.yaml)

The RHEL 9 Test has only one field with its own non-default value-matching
quantifier (`one_or_more`), so **the compacting tool correctly leaves it as
an explicit local field requirement**. Moving it to a Test-wide default
would add complexity without reducing repetition.

## Review boundary

- The Benchmark is a **new, uniquely identified sample slice** with one Rule;
  it is not an official complete STIG, and its original profiles are not
  represented as valid for a one-Rule excerpt.
- The existing generated `fixture-platform` and empty applicability catalog
  are preserved *on purpose* to expose the unresolved applicability defect.
  **Do not deploy these samples as compliance Benchmarks.**
- The source-derived Rule/Assessment identity and policy values remain
  unchanged. Rule discussions and their raw XML markup are deliberately
  unedited pending publisher-content normalization decisions.
- All **eight** YAML files passed the 0.4.0 JSON Schemas; both isolated
  one-Rule sample packages compiled. These are static structural checks.
  **NOT SCANNER-VERIFIED — RESULT UNAVAILABLE.**
- **Do not compile both excerpts into one combined bundle yet.** They retain
  the same source-generated `fixture-applicability` identity; the compiler
  correctly rejects the collision. See the review findings.
- No change was made to the published 65-stream ZIP, its byte hashes,
  original compiled programs, or previously accepted source-proof ledger.

## Layout

```text
v04-two-sample-review/
  ms_windows_11/
    benchmark.yaml
    applicability.yaml
    rules/SV-253475.rule.yaml
    assessments/automated/SV-253475.automated.yaml
  rhel_9/
    benchmark.yaml
    applicability.yaml
    rules/SV-257851.rule.yaml
    assessments/automated/SV-257851.automated.yaml
  REVIEW-FINDINGS.md
  REVIEW-RECEIPT.json
```

Rebuild locally with the pinned human-v2 evidence extraction:

```bash
python tools/build_v04_two_sample_review.py \
  --source-root <extracted-human-v2-root> \
  --output <new-nonexistent-directory>
```

The tool refuses to overwrite an existing output directory and does not
mutate the immutable source export.
