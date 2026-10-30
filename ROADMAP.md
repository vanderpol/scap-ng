# SCAP-NG roadmap

Updated October 30, 2026. **Active authoring review: 0.4.0 pre-alpha.** The current [downloads and Assessment samples index](docs/releases/0.4.0-downloads-and-samples.md) distinguishes the qualified toolchain candidate, full 65-stream DRAFT, normalized editable YAML, and earlier six-STIG demonstrations. The 0.3.0 compiler/source history remains [archived](archive/0.3.0/README.md), not relabeled as 0.4.

## Now — review the 0.4.0 candidate and prepare owner publication decision

The #260 toolchain candidate compiles current native 0.4 authoring; #261 delivered a non-destructive normalized layout and editor-callable maintenance CLI. All 65 original streams /8,892 Rules are accounted for: 6,817 compiled native candidates (4,258 independently statically source-proved, 2,559 UNVERIFIED), 422 blocked automated Rules and 1,653 manual/OCIL originals. Sixty streams have editable native Benchmarks; five are retained as source-only records. No final `v0.4.0` release has been authorized.

1. Review [the exact candidate and release gates](docs/releases/0.4.0-rc.md), source/permitted-license inventory, human-visible examples and known warning/proof limits before a final pre-alpha publication decision.
2. Preserve original source semantics; treat unverified conversion, actual blocked constructs and scanner runtime equivalence as separate future gates. Do not let extra original-OVAL proofs block a clearly labeled authoring DRAFT.
3. Integrate the [offline Python library CLI](docs/developer/NATIVE-LIBRARY.md) with the separate [VS Code Assessment Studio](https://github.com/vanderpol/scap-ng-vscode/issues/3). Avoid duplicate normalization engines and silent Assessment merging.
4. Keep earlier six-STIG sample files and 0.3 releases immutable; use current 65-stream files for large-library maintenance/scale evaluation.

**Schema-valid authoring, compiled packages, independent static OVAL proof, publisher signing, and live scanner parity are different milestones.** An independently tested scanner/evaluator remains later work.

## Next — independent implementations and conformance

Compare real scanner execution against reviewed OVAL 5.12.3 oracles; test result evidence, redaction, signed bundles, caching and enterprise-scale performance. Full automated Self-Assertion generation/execution/comparison remains a later checkpoint ([#206](https://github.com/vanderpol/scap-ng/issues/206)).

[Core objectives](specification/objectives.md) · [Current review](review/current/README.md) · [Issues](https://github.com/vanderpol/scap-ng/issues)
