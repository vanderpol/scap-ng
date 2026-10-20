# SCAP-NG roadmap

Updated October 20, 2026. **Current authoring review: 0.4.0.** The 0.3.0 compiled demonstration release and source research remain [archived](archive/0.3.0/README.md), not erased or relabeled as 0.4.

## Now — finalize 0.4.0 authoring and native compilation

The owner approved one 0.4.0 authoring grammar and an exact-reachable **0.4-only Benchmark specification declaration** policy. The [six-STIG authoring samples](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) contain 4,001 YAML and JSON documents and resolve 2,958 Rule-choice links. [Versioned gate tracking](review/current/0.4.0-FINALIZATION-GATES.md) records schema, source graph and generic OVAL-result evidence.

1. Finish native 0.4.0 authoring-to-bundle compilation, deterministic manifests, checksums and independent signature verification.
2. Verify exceptional source matching and capability-specific OVAL semantics, including Variables, Sets, Filters, record fields and incomplete/error/unknown results.
3. Align the browser editor with current 0.4.0 files and schemas; test import/edit/export roundtrips.
4. Complete concise versioned reviewer material and release evidence before considering a final native package checkpoint.

**Parsed source, a signed bundle and scanner parity are different milestones.** An independent full scanner/evaluator remains to be demonstrated.

## Archived 0.3.0

The historical six-STIG source ZIP and independently compiled `.scapng` samples are preserved in the [0.3 archive](archive/0.3.0/README.md). Earlier full-corpus runs, decisions and issue records remain historical; the 0.3 pipeline is not the default for new 0.4 demonstrations.

## Next — independent implementations and conformance

Compare real scanner execution against reviewed OVAL 5.12.3 oracles; test result evidence, redaction, signed bundles, caching and enterprise-scale performance. Full automated Self-Assertion generation/execution/comparison remains a later checkpoint ([#206](https://github.com/vanderpol/scap-ng/issues/206)).

[Core objectives](specification/objectives.md) · [Current review](review/current/README.md) · [Issues](https://github.com/vanderpol/scap-ng/issues)
