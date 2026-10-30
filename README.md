# SCAP-NG

SCAP-NG is a pre-alpha successor to SCAP 1.4 designed to preserve supported assessment meaning while simplifying authoring, review, collection, results and scalable distribution.

## Start here — 0.4.0 pre-alpha candidate

Use the [candidate operator guide](docs/releases/0.4.0-rc.md) for pinned
installation, original SCAP conversion, compilation and independent package
verification. [Release preparation #260](https://github.com/vanderpol/scap-ng/issues/260)
links the exact candidate SHA, CI, revised 65-STIG DRAFT, checksums and release
decision packet. Native conversion, static proof and scanner-runtime evidence
are separate gates. Warning-admitted drafts remain unverified. Final publication
requires owner approval; see the [license inventory](docs/releases/0.4.0-LICENSE-INVENTORY.md).

### Earlier six-STIG sample checkpoint

**[Current 0.4.0 six-STIG downloads and reproducible commands](docs/releases/0.4.0-six-stig-authoring.md)** — version-pinned YAML/JSON authoring (4,012 documents) and six compiled `.scapng` Benchmarks. The compiled content has integrity-verified Test/result programs, but remains **unsigned and unexecuted in an independent scanner**. Earlier checkpoints remain immutable. The [October 20 approved authoring preview](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) is retained for historical reproduction, not as the current download.

- **New to SCAP-NG?** [Content Author and Application Developer Guides](docs/guides/README.md)
- **Learn the content model:** [Benchmark and Rule examples](specification/examples/README.md) · [Assessment examples](specification/examples/assessments.md)
- **Review a real STIG:** [current six-STIG review](review/current/README.md) · [short review guide](review/current/REVIEW-GUIDE.md)
- **Validate a source file:** [0.4.0 schema](schema/v0.4.0/README.md) · [source/version guide](docs/public-authoring/VERSION-AND-SOURCES.md)
- **Understand what is still open:** [0.4.0 finalization gates](review/current/0.4.0-FINALIZATION-GATES.md) · [canonical grammar decision](research/assessment-simplification/compact-authoring-04/OWNER-0.4.0-CANONICAL-DECISION.md)
- **Browse historical material:** [archived 0.3.0 release, examples and synthetic results](archive/0.3.0/README.md) · [OVAL Board records](board/README.md)

All six current Benchmarks declare the exact reachable `0.4.0` automated Assessment specification. Their obsolete `0.3.0` declarations, source hashes and original authoring content remain in pinned historical releases and migration evidence. **0.3.0 is preserved, not deleted or silently converted.**

## What SCAP-NG changes

SCAP-NG uses **Benchmark → Rule → Assessment** for policy, requirement and evaluation method. Automated Assessments retain useful OVAL concepts—Test, Object, Variable and collected Item—but ordinarily put collection and expected `require` predicates near each Test instead of requiring readers to chase separate XML IDs.

Content is modular and reusable, with explicit applicability, manual choices, source provenance, bounded result evidence, signatures and cross-platform implementation as project objectives.

**0.4.0 remains pre-alpha.** Native YAML/JSON and compiled packages are review
artifacts. Current coverage and blockers are measured in the candidate's Rule
ledger; the earlier six-STIG checkpoint and its 221 review leads remain
historical evidence. Scanner parity and real publisher signing/trust remain
open. Historical 0.3.0 bundles are not native 0.4.0 packages. See
[versioned toolchain release policy](docs/releases/TOOLCHAIN-RELEASES.md) and
[developer implementation guide index](docs/developer/README.md).

[Objectives](specification/objectives.md) · [Maintaining](MAINTAINING.md) · [Roadmap](ROADMAP.md) · [Issues](https://github.com/vanderpol/scap-ng/issues)
