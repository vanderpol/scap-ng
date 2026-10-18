# 0.4-A lossless Assessment source-envelope IR — 18 October 2026

**Research only — NOT executable; NOT a published 0.4 schema or signed bundle.** Tracking: [#240](https://github.com/vanderpol/scap-ng/issues/240), [#232](https://github.com/vanderpol/scap-ng/issues/232), [#239](https://github.com/vanderpol/scap-ng/issues/239).

## What now exists on main

- [Lossless IR builder and decoder](../../../tools/v04_a_lossless_ir.py): deterministic version 0.1 JSON representation of **every** staged base-authoring document, including complete parsed JSON AST, logical source path and SHA-256. It keeps manual, Rule, Benchmark and applicability sources, not merely automated Tests.
- [Research-only Draft 2020-12 envelope schema](lossless-ir-envelope.schema.json), distinct from the normative versioned schema directory.
- [Adversarial tests](../../../tools/test_v04_a_lossless_ir.py): YAML/JSON logical path and insertion-order equivalence, nested evaluate trees, manual boundaries, Windows record / Variable / Object / Set / Filter / for_each preservation, provenance, missing requirements, malformed identities, broken graph edges and independent index/hash checks.
- [Maintained exact-head six-STIG gate](../../../.github/workflows/research-a-integrated-base-authoring.yml) runs independent YAML/JSON ingestion, established base and generated capability validations, unapproved isolated version staging, deterministic unsigned archive integrity, full source-envelope compile, decoded roundtrip, and research-envelope JSON Schema verification.

No branch was created. Commits reference relevant GitHub issues and do not modify 0.3 or proposed 0.4 normative schemas. No 65-STIG checkpoint was run.

## Repeatable commands

Focused test: python -m unittest -v tools/test_v04_a_lossless_ir.py

Compile independently checked IR from an existing verified unsigned research base-authoring ZIP:

    python tools/v04_a_lossless_ir.py --base-zip /path/to/a-unsigned-base-research.zip --out /path/to/a-lossless-ir.json --assert-six

The existing [end-to-end pipeline](../../../tools/v04_a_end_to_end_base_authoring.py) produces that ZIP from independently parsed, frozen YAML and JSON inputs, verifying package-byte parity. The IR consumes the canonical staged base source, giving the same IR bytes for both routes.

## Meaning and limits

- The full source_ast subtree is lossless, including accepted capability extension fields; the typed index **does not execute** those expressions. The upstream version-local 0.4 capability schema validator rejects unsupported capabilities.
- The assessment_index separates manual/automated mode, named Test identities/capabilities/explicit Item requirement and hashes, Assessment truth dependencies, and Test-local Variable/shared Object source hints. It does not silently convert a collection dependency into Assessment truth.
- The independent decoder recomputes every envelope, source digest, Test index, ordering, version inventory, and graph closure from embedded complete source trees; any discrepancy fails closed.
- Existing static graph validation checks Rule choices, evaluate aliases, Test/Variable/shared-Object references; per-Benchmark checks reject mismatched specification declarations. **Full cross-Assessment target/version/scope closure and executable collector/Variable/Set/for_each scheduling remain missing.**
- Candidate 0.3-to-0.4 Benchmark declaration staging and scoped shorthand lowering remain **research only**, unapproved. No source release is mutated.
- Source expressions involving unknown, error, incomplete and not_applicable are retained in source_ast but **not interpreted or proven result-equivalent**.
- Nothing is signed, scanner executable, OVAL-parity verified, or accepted as a native release.

## Verified checkpoint

The first exact-head [six-STIG CI run 39137508758](https://github.com/vanderpol/scap-ng/actions/runs/39137508758) **passed**, covering 4,001 documents, 872 automated Assessments, 1,375 Tests, 2,958 Rule choice links and independently decoded full authoring ASTs. Canonical IR digest for that run: b8683d48428024dbbd579567ff5b68efcb23e8946cbe99a4ef24528e7a9fdc10.

A follow-up exact-head CI run must pass before the additional research JSON Schema check is considered verified.

## Next engineering gates

1. Add source-backed Assessment-to-Assessment dependency target/version/purpose/scope closure with adversarial cases.
2. Index typed Variable, Set/Filter, Windows record and for_each dependency subtrees against representative original content, retaining the lossless AST as an always-available fallback.
3. Only after semantic and version decisions, build native executable IR instructions, truth/completeness/provenance propagation, signed packaging and scanner conformance. Structural AST equivalence is not runtime parity.

**Keep the status on GitHub. This is concrete compiler preparation, not completion of the native 0.4 compiler.**
