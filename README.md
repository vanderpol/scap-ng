# SCAP-NG

SCAP-NG is a pre-alpha successor to SCAP 1.4 designed to preserve supported assessment meaning while simplifying authoring, review, collection, results and scalable distribution.

**[0.4.0 downloads and sample Assessments](docs/releases/0.4.0-downloads-and-samples.md)** — start here for the [current human-readable 65-stream authoring ZIP](https://github.com/vanderpol/scap-ng-evidence/releases/download/v04-human-readable-review-20261030-ab5cddd/scap-ng-0.4.0-human-readable-authoring-review.zip), smaller real Assessment examples, the complete original-source DRAFT, and pinned toolchains. The earlier `assessments/local/` package is a historical internal-layout prototype; [#263](https://github.com/vanderpol/scap-ng/issues/263) records the replacement.

**[Full 65-stream proposed authoring review report](docs/audit/v04-full65-proposed-authoring-review-20261030.md)** — 6,817 Assessments processed, 5,203 reformatted, 13,754 schema-valid YAML files and 60 separately compiled native scopes. Review draft only; the public 65-stream source download is unchanged and no original static proofs were transferred.

**[Start with the proposed 40-Rule authoring review](docs/examples/v04-proposed-authoring-review/README.md)** — 20 Windows 11 and 20 RHEL 9 examples using Test-wide field requirements and genuine per-field overrides. 32 Assessments refactored; 8 Item-presence-only checks remain unchanged. [The original generated gallery](docs/examples/v04-expanded-authoring-review/README.md) remains available for comparison. Review only; not scanner-verified.

**[Audit 40 current generated 0.4.0 authoring samples (known noncanonical syntax)](docs/examples/v04-expanded-authoring-review/README.md)** — 20 Windows 11 and 20 RHEL 9 Rule/Assessment pairs covering varied capabilities and logic. These files expose the *as-generated* readability defects; for the proposed compact Windows registry style, [start with SV-253475 here](docs/examples/v04-two-sample-review/ms_windows_11/assessments/automated/SV-253475.automated.yaml). The expanded gallery preserves source YAML bytes exactly, and claims no scanner results.

[Native 0.4 library maintenance and editor-callable CLI](docs/developer/NATIVE-LIBRARY.md)
provides out-of-place layout export and logical-ID checks across the all-65
DRAFT, with original proof/warning status preserved and no automatic deduplication.

## Start here — 0.4.0 pre-alpha candidate

Use the [candidate operator guide](docs/releases/0.4.0-rc.md) for pinned
installation, original SCAP conversion, compilation and independent package
verification. [Release preparation #260](https://github.com/vanderpol/scap-ng/issues/260)
links the exact candidate SHA, CI, revised 65-STIG DRAFT, checksums and release
decision packet. Native conversion, static proof and scanner-runtime evidence
are separate gates. Warning-admitted drafts remain unverified. Final publication
requires owner approval; see the [license inventory](docs/releases/0.4.0-LICENSE-INVENTORY.md).

[Exact-SHA candidate downloads, CI and owner decision packet](https://github.com/vanderpol/scap-ng-evidence/tree/v04-toolchain-rc-20261030-a5db02e1b/runs/v04-toolchain/2026-10-30-v040-rc-a5db02e1b)
· [Complete 65-STIG revised DRAFT](https://github.com/vanderpol/scap-ng-evidence/tree/v04-revised-all65-draft-files-20261030-a08c9beb9/runs/v04-converter/2026-10-30-all-65-revised-draft-download).

### Earlier six-STIG sample checkpoint

**[Earlier 0.4.0 six-STIG downloads and reproducible commands](docs/releases/0.4.0-six-stig-authoring.md)** — version-pinned YAML/JSON authoring (4,012 documents) and six compiled `.scapng` Benchmarks. The compiled content has integrity-verified Test/result programs, but remains **unsigned and unexecuted in an independent scanner**. Earlier checkpoints remain immutable. The [October 20 approved authoring preview](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) is retained for historical reproduction, not as the current download.

- **New to SCAP-NG?** [Content Author and Application Developer Guides](docs/guides/README.md)
- **Learn the content model:** [Benchmark and Rule examples](specification/examples/README.md) · [Assessment examples](specification/examples/assessments.md)
- **Review a real STIG:** [earlier six-STIG review](review/current/README.md) · [short review guide](review/current/REVIEW-GUIDE.md)
- **Validate a source file:** [0.4.0 schema](schema/v0.4.0/README.md) · [source/version guide](docs/public-authoring/VERSION-AND-SOURCES.md)
- **Understand what is still open:** [0.4.0 finalization gates](review/current/0.4.0-FINALIZATION-GATES.md) · [canonical grammar decision](research/assessment-simplification/compact-authoring-04/OWNER-0.4.0-CANONICAL-DECISION.md)
- **Browse historical material:** [archived 0.3.0 release, examples and synthetic results](archive/0.3.0/README.md) · [OVAL Board records](board/README.md)

The six Benchmarks in the **earlier six-STIG checkpoint** declare the exact reachable `0.4.0` automated Assessment specification. Their obsolete `0.3.0` declarations, source hashes and original authoring content remain in pinned historical releases and migration evidence. **0.3.0 is preserved, not deleted or silently converted.**

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
