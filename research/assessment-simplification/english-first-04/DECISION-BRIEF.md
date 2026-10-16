# SCAP-NG 0.4 — English-first authoring: interim research decision

**As of 2026-10-16 (pre-alpha). Not a specification proposal, release candidate or Board approval request.** Tracking: [#235](https://github.com/vanderpol/scap-ng/issues/235), semantics [#229](https://github.com/vanderpol/scap-ng/issues/229). This is a technical checkpoint to decide whether more research is justified.

## Verdict

**CONTINUE RESEARCH. DO NOT PROPOSE GRAMMAR ADOPTION YET.**

The English-first approach now has reproducible evidence beyond readable screenshots. But only a narrow class of Test predicates is proved; the capability/collection model is not yet broadly expressive enough to qualify as a lossless replacement for SCAP 1.4/OVAL.

## Evidence — genuinely tested

- [PASS: four pinned individual source Test inversions, six-state generic reference checks](https://github.com/vanderpol/scap-ng/actions/runs/38907309219). RHEL9 SV-257851 nosuid; Windows 11 SV-253495 user-right equality and regular-expression checks; Windows 11 SV-253254 two allowed registry-State alternatives. Each demonstrated macro is capability- and field-scoped, fails closed on unsupported operators/changed cardinalities, and expands to **exact existing 0.4 source Test structure**.
- [PASS: four full real Test-composition tree inversions](https://github.com/vanderpol/scap-ng/actions/runs/38907309219). RHEL9 SV-257889 (2 referenced Tests), Windows 11 SV-253495 (8 Test references, 7 unique), DNS SV-259345 (5), Apache SV-214228 (4). Every Test ref and grouping is unchanged when native AND/OR becomes readable all_of/any_of. **This proves Boolean graph encoding, not faithful execution of the underlying Tests or safe procedural conditionals.**
- [PASS: full unique-archive fail-closed census](https://github.com/vanderpol/scap-ng/actions/runs/38907185233). The immutable r3 six-STIG YAML ZIP has **872 unique automated Assessment files with 1,375 named Test nodes**. Under our **four currently implemented narrow operator/shape templates**, **39 Tests (2.84%)** pass exact source Test inversion. **1,336 remain unsupported by the prototype.** This ratio is not an upper bound on what an English-first grammar could eventually express. No unsupported Test was presented as lossless.
- Pinned official [OVAL 5.12.3 Windows userright_item](https://oval-community-guidelines.readthedocs.io/en/base/oval-schema-documentation/windows-system-characteristics-schema.html#userright-item) documents trustee_name as 0..1 per Item; [OVAL Linux partition_item](https://oval-community-guidelines.readthedocs.io/en/base/oval-schema-documentation/linux-system-characteristics-schema.html#partition-item) has mount_options 0..unbounded. This allows **different capability-specific operators** with exactly declared semantics rather than hidden count defaults.

## What still blocks 0.4

1. **Real collection graphs:** 395 candidate Tests lack a selector/title that the narrow compiler currently knows how to present locally, and 114 have an unresolved/non-inline Object shape under this prototype. These are **research-tool limitations**, not evidence that real Test content lacks collection or should be skipped.
2. **More vocabulary:** 584 Tests have other capabilities/shapes; 172 registry Tests do not have the prototype's exact two-State pattern; more windows.userright and Linux cases also fail strict whitelist. Need general but readable typed operators covering *all* 20 existence × match combinations, not a handful of happy-path aliases.
3. **Dynamic composition:** RHEL account→file for_each, DNS command Variables, Apache config discovery, nested Windows WMI records, Set filters, organizational inputs and reusable Objects require explicit lifecycle/evidence semantics, not shortened captions hiding complexity.
4. **Six-state conformance:** Reference chart tests and source-structure identity are not independent target scanning. Need OVAL → native source conversion and NG assessment execution parity, including incomplete Item streams, errors, unknown, not collected, not applicable, and evidence/provenance.
5. **One real grammar:** The same Check–Inspect–Where/Collect–Require design must express all the above without a second, OVAL-flavored fallback authoring language. No unspoken Boolean defaults.

## Meeting-use recommendation

**Do not ask the vendor to review the current English-first YAML as the proposed v0.4 standard.** It is too early, even though the research is moving in a favorable direction.

**If time allows**, a focused technical question *is* useful:

> The OVAL schema says a Windows user-right trustee_name can occur at most once per Item, while Linux mount_options can repeat. Do you see any pitfalls in designing capability-specific, typed shorthand that expands into the exact existing Test/State/Item semantics, while leaving full six-state behavior to the canonical evaluator?

A second useful technical challenge: ask for concrete source counterexamples involving a single capability with multiple collected Items, missing field statuses, nested records or vendor-dependent collection flags.

## Next work, not delegated to the scanner/editor

- Broaden the source-inversion lowerer first to whole composite Test patterns while retaining typed, explicit collection and strict provenance. Audit unsupported reasons per STIG, not just total failure counts.
- Add exact nested WMI record/field and nonstandard quantifier cases, then DNS/Apache Variable/Dataflow cases and RHEL multi-population foreach.
- Diff results against independent OVAL 5.12.3 six-state model fixtures, with negative counterexamples, and eventually scanner implementation.
- Recheck author readability with full YAML including selectors, not cropped State snippets.
- Only once broad six-STIG coverage is demonstrably stable, consider all 65 STIG packages and decide whether to change the 0.4 candidate schema.

**Source proof links:** [research overview](README.md), [source-inversion code](../../../tools/research_english_first_04.py), [entire six-STIG audit code](../../../tools/research_english_first_04_census.py), [real complex named-Test graph proof](../../../tools/research_english_first_04_evaluate.py).
