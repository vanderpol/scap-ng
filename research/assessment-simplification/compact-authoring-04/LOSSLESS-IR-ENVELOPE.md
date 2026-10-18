# 0.4-A lossless Assessment source-envelope IR — 18 October 2026

**Research only — NOT executable; NOT a published 0.4 schema or signed bundle.** Tracking: [#240](https://github.com/vanderpol/scap-ng/issues/240), [#232](https://github.com/vanderpol/scap-ng/issues/232), [#239](https://github.com/vanderpol/scap-ng/issues/239).

## What now exists on main

- [Lossless IR builder and decoder](../../../tools/v04_a_lossless_ir.py): deterministic version 0.2 JSON representation of **every** staged base-authoring document, including complete parsed JSON AST, logical source path and SHA-256. It keeps manual, Rule, Benchmark and applicability sources, not merely automated Tests.
- [Research-only Draft 2020-12 envelope schema](lossless-ir-envelope.schema.json), distinct from the normative versioned schema directory.
- [Adversarial tests](../../../tools/test_v04_a_lossless_ir.py): YAML/JSON logical path and insertion-order equivalence, nested evaluate trees, manual boundaries, Windows record / Variable / Object / Set / Filter / for_each preservation, provenance, missing requirements, malformed identities, broken graph edges and independent index/hash checks.
- [Maintained exact-head six-STIG gate](../../../.github/workflows/research-a-integrated-base-authoring.yml) runs independent YAML/JSON ingestion, established base and generated capability validations, unapproved isolated version staging, deterministic unsigned archive integrity, full source-envelope compile, decoded roundtrip, and research-envelope JSON Schema verification.

No branch was created. Commits reference relevant GitHub issues and do not modify 0.3 or proposed 0.4 normative schemas. No 65-STIG checkpoint was run.

## Repeatable commands

Primary supported command (after fetching the two immutable r3 six-STIG source ZIPs from the pinned release):

    python tools/v04_a_compile_verified_ir.py --json-archive /path/to/six-stig-json.zip --yaml-archive /path/to/six-stig-yaml.zip --out-ir /path/to/a-lossless-ir.json --assert-six --report-json /path/to/verified-ir-report.json

This **one command** parses YAML and JSON independently, validates every base 0.4 Assessment and each generated 0.4 capability-specific Test, checks all Rule choices and version-declaration research staging, creates byte-identical unsigned research packages, independently derives matching typed IRs, decodes and verifies the full source, and checks the research IR Draft 2020-12 JSON Schema. There is no bypass switch for production CLI schema validation.

Focused tests:

    python -m unittest -v tools/test_v04_a_lossless_ir.py tools/test_v04_a_dataflow_index.py tools/test_v04_a_dataflow_census.py tools/test_v04_a_compile_verified_ir.py

Compile independently checked IR from an existing verified unsigned research base-authoring ZIP:

    python tools/v04_a_lossless_ir.py --base-zip /path/to/a-unsigned-base-research.zip --out /path/to/a-lossless-ir.json --assert-six

The existing [end-to-end pipeline](../../../tools/v04_a_end_to_end_base_authoring.py) produces that ZIP from independently parsed, frozen YAML and JSON inputs, verifying package-byte parity. The IR consumes the canonical staged base source, giving the same IR bytes for both routes.

## Meaning and limits

- The full source_ast subtree is lossless, including accepted capability extension fields; the typed index **does not execute** those expressions. The upstream version-local 0.4 capability schema validator rejects unsupported capabilities.
- The assessment_index separates manual/automated mode, named Test identities/capabilities/explicit Item requirement and hashes, Assessment truth dependencies, and Test-local Variable/shared Object source hints. It does not silently convert a collection dependency into Assessment truth.
- The independent decoder recomputes every envelope, source digest, Test index, Object/Variable dependency, ordered Set/Filter/for_each source path, lexical alias lineage, ordering, version inventory, and graph closure from embedded complete source trees; any discrepancy fails closed.
- Existing static graph validation checks Rule choices, evaluate aliases, Test/Variable/shared-Object references; per-Benchmark checks reject mismatched specification declarations. **Static Assessment-to-Assessment target ID, exact version, purpose, authoring namespace, and acyclic dependency closure now fail closed.** Dynamic collector/Variable/Set/for_each scheduling and runtime truth evaluation remain missing.
- Candidate 0.3-to-0.4 Benchmark declaration staging and scoped shorthand lowering remain **research only**, unapproved. No source release is mutated.
- Source expressions involving unknown, error, incomplete and not_applicable are retained in source_ast but **not interpreted or proven result-equivalent**.
- Nothing is signed, scanner executable, OVAL-parity verified, or accepted as a native release.

## Verified checkpoint

The latest exact-head [six-STIG CI run 39140548231](https://github.com/vanderpol/scap-ng/actions/runs/39140548231) **passed**, with 19 lossless-IR tests, 14 Object/Variable/Set/Filter/for_each graph/lineage tests, three source-census tests, **six single-command parity/negative tests**, and 11 maintained integrated tests. The research Draft 2020-12 envelope schema, exact Assessment-dependency closure, 4,001 full source documents, 872 automated Assessments, 1,375 Tests and 2,958 Rule choices all passed. Canonical IR v0.2 digest: 9a9c418b3eaa2dc28831302af76f2911869fafe848f110167888f0b9a5a2dfab. [Full measured source graph counts and real source anchors](DATAFLOW-SIX-STIG-CENSUS.md).

All of these named checks passed on the cited exact-head run. This is still structural evidence only.

## Next engineering gates

1. Extend the now-implemented static target/version/purpose/scope/cycle closure with source-backed runtime scheduling, dependency-completeness propagation and independent result semantics tests.
2. Extend the now verified typed Object/Variable/Set/Filter/for_each source graph and inherited for_each-alias checks with independent original-source-backed status/completeness, negative and error result oracles. Keep source AST as the lossless fallback.
3. Only after semantic and version decisions, build native executable IR instructions, truth/completeness/provenance propagation, signed packaging and scanner conformance. Structural AST equivalence is not runtime parity.

**Keep the status on GitHub. This is concrete compiler preparation, not completion of the native 0.4 compiler.**
