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
- **Six complete STIG conversions (ZIP):** [Download the 0.3 review bundle](https://github.com/vanderpol/scap-ng/actions/runs/37849528026/artifacts/11580544848) · [individual ZIPs](#full-stig-conversion-downloads)
- **Open issues / 0.3 work:** [GitHub issues](https://github.com/vanderpol/scap-ng/issues)
- **Governance and published votes:** [board/README.md](board/README.md)


## Full STIG conversion downloads

The [six-STIG review bundle (ZIP)](https://github.com/vanderpol/scap-ng/actions/runs/37849528026/artifacts/11580544848)
contains the **complete converted 0.3 authoring trees** and **six compiled
`.scapng` packages**. Individual full-conversion ZIPs are also available:

- [Red Hat Enterprise Linux 9](https://github.com/vanderpol/scap-ng/actions/runs/37849528008/artifacts/11580818580)
- [Oracle Linux 9](https://github.com/vanderpol/scap-ng/actions/runs/37849528008/artifacts/11581187923)
- [Windows 11](https://github.com/vanderpol/scap-ng/actions/runs/37849528008/artifacts/11580608540)
- [Windows Server 2025](https://github.com/vanderpol/scap-ng/actions/runs/37849528008/artifacts/11582000947)
- [Windows Server DNS](https://github.com/vanderpol/scap-ng/actions/runs/37849528008/artifacts/11581811893)
- [Apache HTTP Server 2.4 (UNIX)](https://github.com/vanderpol/scap-ng/actions/runs/37849528008/artifacts/11581482203)

These are **SCAP-NG preview conversions** of DISA STIG-based NIWC-enhanced
SCAP 1.4 content, **not official DISA-issued SCAP-NG benchmarks**.
The individual ZIPs contain full faithful and simplified candidate authoring
sources; the combined ZIP includes compiled packages. Both builds
[passed their GitHub Actions workflows](https://github.com/vanderpol/scap-ng/actions/runs/37849528026),
but successful conversion/compilation does not establish live-scanner fidelity.
GitHub Actions artifact downloads may require sign-in and expire; the
[review workflows](https://github.com/vanderpol/scap-ng/actions)
can regenerate them.


## Architecture

SCAP-NG uses **Benchmark → Rule → Assessment**. Native automated Assessments
retain useful OVAL concepts such as Test, Object, State, Variable, and Item while
removing legacy serialization and packaging machinery where it is not
semantically required. Distribution uses modular source compiled into a
self-contained manifest-based package.

**Status:** pre-alpha. Green CI, schema validation, conversion evidence, human
acceptance, and Board ratification are distinct states.
