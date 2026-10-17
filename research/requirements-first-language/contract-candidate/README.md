# Requirements-first native authoring — executable research pilot

**17 October 2026 · experimental · issue #235.** [Go/no-go and fallback decision](../GO-NO-GO-ARCHITECTURE-2026-10-17.md).

**Six-stream B engineering now has a [complete source-accounting ledger](corpus/source-accounting.md), [per-capability feature inventory](corpus/feature-inventory.md), and [12 bounded source-backed specimens](corpus/source-specimens/README.md)** spanning high-volume file-text, Windows registry/user rights/WMI, shellcommand and Linux partition cases. These specimens come from the published 0.3 converted authoring ZIP and are *not* original SCAP 1.4 XML or executable native B. The ninth native rule (`exists: linux.mounts`) comes directly from the /var/tmp linux.partition source structure; it is a native policy candidate, not proven OVAL collection parity.

This is NOT normative SCAP-NG 0.4. It is a small runnable demonstration that a human-readable typed resource plus collection language can compile to ONE internal requirement AST. The [compiler](../../../tools/research_native_contract_candidate.py), [fixture evaluator](../../../tools/research_native_contract_evaluator.py), and [deterministic auditor explanation generator](../../../tools/research_native_auditor_explain.py) all consume the same authored structure. The real provider set remains incomplete, and no source SCAP 1.4 parity has been verified.

| Security requirement | Actual researched author YAML | Auditor text generated from its AST |
| --- | --- | --- |
| Required home mount must have nosuid | [YAML](examples/01-required-home.yaml) | [Explanation](generated-explanations/01-required-home.md) |
| Every existing guest account disabled, none needed | [YAML](examples/02-optional-guest.yaml) | [Explanation](generated-explanations/02-optional-guest.md) |
| Uniquely scoped registry policy setting | [YAML](examples/03-named-registry.yaml) | [Explanation](generated-explanations/03-named-registry.md) |
| Apache KeepAlive and numeric MaxKeepAliveRequests >=100 | [YAML](examples/04-apache-two-settings.yaml) | [Explanation](generated-explanations/04-apache-two-settings.md) |
| Forward DNS zones are AD integrated if present | [YAML](examples/05-dns-if-any.yaml) | [Explanation](generated-explanations/05-dns-if-any.md) |
| Windows user-right compliance alternatives | [YAML](examples/06-windows-privilege-or.yaml) | [Explanation](generated-explanations/06-windows-privilege-or.md) |
| Root-derived Linux init files: combined set and permitted octal bits | [YAML](examples/07-linux-permission-bits.yaml) | [Explanation](generated-explanations/07-linux-permission-bits.md) |
| Per-zone DNSSEC signature validity with two required key kinds | [YAML](examples/08-dns-signing-nested.yaml) | [Explanation](generated-explanations/08-dns-signing-nested.md) |
| Filesystem must exist at /var/tmp — pure existence from a real source specimen | [YAML](examples/09-linux-var-tmp-exists.yaml) | [Explanation](generated-explanations/09-linux-var-tmp-exists.md) |

A narrow [compiler-owned source compatibility IR bridge](../../../tools/test_research_common_ir_bridge.py) also runs through the same evaluator dispatcher. It specifically retains four independent Apache OVAL Test existence checks as separate internal nodes and demonstrates that a fluent native two-setting check can Pass when one source compatibility Test necessarily Fails. **This is only a Test-level truth-table bridge, not source conversion, State/Variable execution or an actual scanner.**

The native renderer's pages are **derived text, not a second language or manually-authored source**. GitHub Actions publishes them directly to the repository so work networks do not need to access temporary run artifacts. Do not infer that the explanations encode all future evidence/error rules; this is a deliberately bounded semantic prototype.

## What succeeded

- Named singleton resources compile to the **same cardinality and comparison tree** as collection expressions. A singleton provider that returns duplicates emits an Error instead of selecting a convenient passing value.
- Optional complete-empty populations and explicitly required populations are distinguishable without writing if_empty: fail.
- Native record field comparisons, positive minima, no selected resources, logical all/any, partial/incomplete collection and observed decisive failures are fixture-tested.
- Nested DNS key collections are **scoped to the selected zone Item** and fail closed if parent identity is mismatched or child population status is absent.
- A small actual Linux mount collector, a fixture-defined read-only Apache Include collector, and a structured DNS zone/key normalizer have been wired to this same AST in CI.
- The typed Apache MaxKeepAliveRequests operator parses a canonical decimal value while retaining raw text and refuses malformed values; this is a NEW provider convention, not a claim to reproduce the original shellcommand regex.

## What still fails the final release gate

- This research compiler uses a **small hard-coded fixture provider catalog**. There is no vendor provider extension API, full target OS coverage, org-input data contract, manual check executor, conditional branch engine or complete dynamic field type validation.
- The native fixture evaluator reuses OVAL's published Boolean AND/OR result combiners, but it is **not a full six-state SCAP-NG/OVAL Test evaluator**, and source-specific object/State/item/record behavior is not implemented.
- The versioned sample provider manifests do not prove real source-equivalent collection for Apache, DNS, Linux file traversal, Windows WMI or registry values.
- None of the five pinned original SCAP 1.4 source Assessments has a verified end-to-end native conversion (0/5 proven). Original four-shell Apache, five-shell DNS and WMI State graph checks require a compiler-owned source compatibility route.
- A truly unfamiliar auditor has not been independently tested **authoring** a new complex rule using this language.

**Recommended architecture:** ONE auditor-facing native requirements language, ONE typed internal evaluator/IR with explicitly versioned source-compatible operations for converted SCAP 1.4 content, and ONE result/provenance contract. Preserve earlier OVAL-aligned source-compatibility research until parity can be measured. This is a **proposed path**, not the existing scanner architecture.

## CI

[Research workflow](https://github.com/vanderpol/scap-ng/actions/workflows/research-requirements-first-04.yml) compiles/examples and runs the negative language, field-presence, cardinality, source-pinning and provider fixture tests.

[Publisher workflow](https://github.com/vanderpol/scap-ng/actions/workflows/research-native-auditor-explanations.yml) generates the eight auditor-readable Markdown pages from those same eight YAML/AST files and commits updated pages to main.
