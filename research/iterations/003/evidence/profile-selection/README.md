# RHEL 9 compact profile selection audit — Issue #30

Pinned source: `niwc-atlantic/scap-content-library@8c8e5dff860af6b1290ee9273a282db24278f8d5`, `Current/U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip`.
Package SHA-256: `70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5`.

445 Rules, 445 Groups, 11 Profiles, 4,895 rule/profile comparisons: **zero discrepancies and zero selection blockers**. All baseline Rules are enabled. CAT_I_Only enables 28; Disable_Slow_Rules enables 438; the nine MAC profiles each enable 445.

`benchmark.yaml` now states `default_selection: true` explicitly. Profiles retain only exceptions. The generator resolves source selections before rendering baseline `disabled_rules` and profile disabling/enabling deviations, including parent-first Profile extension and cluster targets.

The deterministic gzip JSON report preserves Rule/Group explicit versus schema-default attributes, lexical values, ancestry, effective baseline, every effective profile selection, ordered explicit select histories and their originating Profiles. Decompress with Python's `gzip` module or `gzip -dc`. CI publishes the same uncompressed JSON on success or failure.

Source semantics: Group/Rule `selected` defaults to true independently; a disabled ancestor suppresses descendant selection without changing its stored selected value. Benchmark is not a selectable XCCDF Item. Profile parent actions precede child actions; intentional child overrides are retained in evidence. Duplicate/conflicting actions targeting the same Item in one Profile are blockers. Unknown/ambiguous targets, duplicate identities, missing/cyclic Profile inheritance, and unsupported Item extension are rejected rather than approximated. Native duplicate, unknown and conflicting overrides, plus unsupported profile selection syntax, are blockers.

Seven regression tests pass, including every source profile across all 445 rules and a mutation that flips every rule in one profile and requires 445 discrepancies. Run:

```sh
SCAP_NG_RHEL9_SOURCE=/path/to/pinned.zip python tools/scap_upconvert_v003/test_profile_selection_audit.py
```

Scope: static default/profile selection only. This does not establish requires/conflicts, applicability, check-selector or evaluator parity. Windows 11 remains a separate follow-up acceptance item in Issue #30.

Provenance ledger: **Evidence/Audit** — this report is computed from the pinned published NIWC artifact; **Common** — comparator and tests are project implementation of XCCDF selection semantics; no third-party implementation was copied. Earlier comparator infrastructure is retained and strengthened. Native generation does not embed legacy identities; they remain in migration evidence.
