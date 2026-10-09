# SCAP-NG

SCAP-NG is a pre-alpha successor to SCAP 1.4 focused on preserving supported
assessment meaning while making security content easier to author, review,
implement, execute, package, and consume.

## Core objectives

1. Preserve meaning through migration.
2. Make authoring and review substantially simpler.
3. Make semantics explicit and predictable.
4. Scale through safe reuse of content and collected facts.
5. Produce smaller, more useful results.
6. Cover the complete policy lifecycle.
7. Be trustworthy, interoperable, and governable.
8. Reduce implementation complexity and enable efficient execution.

See the [full objectives](specification/objectives.md) and
[objective-to-issue traceability](OBJECTIVES.md).

## Start here

- **Specification:** [specification/README.md](specification/README.md)
- **Real-world examples:** [Benchmark and Rule policy](specification/examples/README.md) · [technical Assessments](specification/examples/assessments.md) · [result fixtures](specification/examples/0.3.0/results/README.md)
- **Current review:** [review/current/README.md](review/current/README.md)
- **0.3.0 schema:** [schema/v0.3.0/](schema/v0.3.0/)
- **Six complete STIG conversions (ZIP):** [Direct six-STIG source ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-six-stig-source-preview.zip) · [individual ZIPs](#full-stig-conversion-downloads)
- **Open issues / 0.3 work:** [GitHub issues](https://github.com/vanderpol/scap-ng/issues)
- **Governance and published votes:** [board/README.md](board/README.md)


## Full STIG conversion downloads

**Current source-derived six-STIG preview (October 9, 2026).** These ZIPs are attached to a [durable GitHub prerelease](https://github.com/vanderpol/scap-ng/releases/tag/v0.3.0-six-stig-preview-324b6d4802c2), **not** transient GitHub Actions artifacts. Select a benchmark for its complete `candidate-authoring/` and `faithful-authoring/` trees and `SCORECARD.md`.

| Benchmark | Direct ZIP download |
| --- | --- |
| Red Hat Enterprise Linux 9 | [Download RHEL 9](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-rhel9-source-preview.zip) |
| Oracle Linux 9 | [Download Oracle Linux 9](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-oracle-linux9-source-preview.zip) |
| Windows 11 | [Download Windows 11](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-windows11-source-preview.zip) |
| Windows Server 2025 | [Download Windows Server 2025](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-windows-server-2025-source-preview.zip) |
| Windows Server DNS | [Download Windows Server DNS](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-windows-server-dns-source-preview.zip) |
| Apache HTTP Server 2.4 (UNIX) | [Download Apache 2.4](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-apache-unix-server-source-preview.zip) |

**All six in one:** [Download the combined six-STIG source ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/scap-ng-0.3-six-stig-source-preview.zip) · [SHA-256 checksums](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/SHA256SUMS.txt) · [source SHA and embedded-Filter counts](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/BUILD-MANIFEST.json).

Built from SCAP-NG commit `324b6d4802c2961a774912291fb86138eb7d122b` and pinned NIWC SCAP 1.4 source revision `8c8e5dff860af6b1290ee9273a282db24278f8d5`. The six conversions contain **222 embedded Filter predicates**, counted in candidate YAML by the [published build manifest](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-324b6d4802c2/BUILD-MANIFEST.json). Native authoring uses direct embedded Test and Filter predicates; the older faithful conversion remains in each archive for comparison. [The six-source build and validation](https://github.com/vanderpol/scap-ng/actions/runs/37931389745) passed.

**Status:** These are pre-alpha, source-only authoring/design previews of DISA STIG-based NIWC-enhanced SCAP 1.4 content. They are **not official DISA SCAP-NG benchmarks**, compiled `.scapng` scanner packages, observed scan results, verified runtime equivalence, or an invitation to review/freeze SCAP-NG 0.3.0. The [current review guide](review/current/REVIEW-GUIDE.md) explains what to inspect; the Board's current [A/B/C/D vocabulary Discussion](https://github.com/vanderpol/scap-ng/discussions/213) is separate from release acceptance.

## Architecture

SCAP-NG uses **Benchmark → Rule → Assessment**. Native automated Assessments
retain useful OVAL concepts such as Test, Object, local typed State predicates, Variable, and Item while
removing legacy serialization and packaging machinery where it is not
semantically required. Distribution uses modular source compiled into a
self-contained manifest-based package.

**Status:** pre-alpha. Green CI, schema validation, conversion evidence, human
acceptance, and Board ratification are distinct states.
