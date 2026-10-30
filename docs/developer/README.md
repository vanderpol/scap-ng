# SCAP-NG developer implementation guidance

**Status: 0.4.0 pre-alpha; implementation guidance is incomplete.** These
links are part of the release toolchain, but they do not independently add
normative requirements or establish scanner/runtime conformance.

For current installation, conversion, compilation and verification, use the
[0.4.0 candidate operator guide](../releases/0.4.0-rc.md).

For ongoing approved work and recovery, use the
[autonomous development checkpoint](AUTONOMOUS-PROGRESS.md) and the standing
workflow in [AGENTS.md](../../AGENTS.md).

For native library maintenance and editor subprocess integration, use the
[0.4 layout/index/analyze/check/apply contract](NATIVE-LIBRARY.md). It preserves
the frozen #260 candidate and performs no automatic shared-Assessment promotion.

| Area | Version-pinned source | Remaining work |
| --- | --- | --- |
| Core format and conformance | [Specification](../../specification/README.md), [conformance](../../specification/core/conformance.md) | Reconcile all approved 0.4 semantics at release promotion. |
| Authoring | [Public authoring guide](../public-authoring/README.md), [examples](../../specification/examples/README.md) | Verify all examples against final release schema. |
| Assessment capabilities | [Assessment reference](../../specification/assessment/reference/README.md) | Finish capability-specific implementation contracts and limitations. |
| Conversion from SCAP 1.4 | [OVAL migration rules](../../specification/migration/oval-5.12.3-to-ng.md), [round-trip harness](../../tools/scap_ng_roundtrip_v003/README.md), [0.4 consolidation checkpoint](../releases/0.4.0-CONVERTER-CONSOLIDATION.md), [converter/implementation runbook](CONVERTER-COMPILER-RUNBOOK.md) | Direct signed-SCAP converter supports a bounded native subset; keep draft compatibility and independent proof separate. |
| Compilation and CLI use | [Converter/implementation runbook](CONVERTER-COMPILER-RUNBOOK.md), [human-runnable scripts](../../tools/HUMAN-RUNNABLE-SCRIPTS.md), [release instructions](../releases/TOOLCHAIN-RELEASES.md) | See the exact-SHA clean-extract evidence linked from #260; portability beyond the pinned Linux environment remains separate. |
| Bundle integrity and signatures | [Package specification](../../specification/package/package-and-integrity.md) | Document the publisher trust and verifier interoperability contract. |
| Results and reporting | [Results specification](../../specification/results/results.md) | Add complete interoperable implementation examples and scanner-result tests. |
| Scanner-specific operations | [Windows NTUSER guide](../scanner/OVAL-5.12.3-WINDOWS-NTUSER-IMPLEMENTATION.md) | Extend guidance beyond the documented capability. |

The specification is normative; schemas enforce structural constraints;
developer guides show implementation approaches and boundary cases. When
they disagree, record a defect and resolve it through the human-reviewed
change process rather than silently treating examples as new semantics.

Release documentation must be taken from the same tag/source commit as the
compiler and schemas. Do not link to moving `main` for normative definitions
from a historical toolchain release.
