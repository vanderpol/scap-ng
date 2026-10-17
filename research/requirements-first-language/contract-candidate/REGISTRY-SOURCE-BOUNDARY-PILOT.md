# 0.4-B Windows registry value evidence pilot (research #235)

**17 October 2026 — bounded, non-scanner research. No SCAP 1.4 parity claim. Not an A/B bake-off.**

## Scope

B already has a native named-resource example ([03-named-registry.yaml](examples/03-named-registry.yaml)), but it used synthetic observations only. This pilot adds an **offline, typed Windows registry snapshot normalizer** ([implementation](../../../tools/research_provider_registry_snapshot.py)) feeding the **same B evaluator**. It does **not** read a Windows host: the caller must supply an independently acquired and honestly classified query snapshot.

The pinned six-stream source example is [Windows 11 SV-253291](corpus/source-specimens/windows-registry-0-de183f784659.source.yaml) (Bluetooth must be off), a real converted 0.3 Windows registry Assessment. This is a **source-backed semantic boundary case**, not a successful converted Assessment.

## Typed evidence and adverse cases

Input names **HKLM, key, value name and 32bit/64bit registry view**. A query ID mismatch is an **Error**, never a zero-resource observation. Snapshots distinguish complete-empty from incomplete-empty, uncollected, not applicable and error. Two returned value records are preserved so the B singleton evaluator can reject duplicate logical resources. The adapter does not infer unknown status from absent fields.

The adapter admits only **integer REG_DWORD / REG_QWORD** values within their respective bit widths. REG_SZ string "0" is not silently converted into integer 0: it yields an Item with a **field error**. The evidence retains a value_kind field and diagnostic. This is a deliberately limited native provider contract, not a definition of all SCAP 1.4 registry datatype comparison semantics.

Run the [regression suite](../../../tools/test_research_provider_registry_snapshot.py) with PYTHONPATH=tools python -m unittest -v tools/test_research_provider_registry_snapshot.py. CI runs it from [research-requirements-first-04.yml](../../../.github/workflows/research-requirements-first-04.yml).

## Why this is still NOT an exact conversion of SV-253291

The original published Assessment has existence one_or_more, match one, State value '0' (**text**), and does **not** explicitly supply registry view. The native typed B example's **one selected logical resource** contract and integer comparison are not proved equivalent to source match one, value typing, and original Windows view/Item-creation semantics. In particular, a single source-State match among multiple Items and a singleton provider rejecting duplicates are not automatically identical.

This pilot purposely retains the discrepancy in tests rather than papering it over. The original 0.3 source file is already a conversion: underlying SCAP 1.4 XML, the OVAL registry Item schema, and full source execution must be verified before source parity can be marked.

## Remaining engineering gates

1. Specify/implement an actual read-only Windows registry collector with WOW64 views, value types, access-denied, missing key/value, and source Item flag/completeness behavior; capture raw provenance and identity.
2. Verify source one / Item / State / entity cardinality semantics and type coercions from original OVAL XML with six-state adverse fixtures. Keep compiler-owned compatibility IR for differences; don't force a native rewrite.
3. Reconcile source registry coverage from the complete **six-STIG cohort** (not just SV-253291), expand supported native types and selectors, and track which checks need compatible lowering.
4. Wire successful fixtures to an executable B source importer and combined Rule/Assessment results; do not mark the existing nonexecutable source capsules as converted.

See the [B capability readiness gate](../CAPABILITY-READINESS-GATE.md) and deferred [A improvement ledger #236](https://github.com/vanderpol/scap-ng/issues/236). Candidate A stays unchanged.
