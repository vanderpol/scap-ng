# scap-ng

Repository for researching the future of SCAP.

## Repository structure

- `research/` — numbered architecture/research iterations, prototypes, results, feedback, and design evidence.
- `specification/` — pre-alpha normative SCAP-NG specification text promoted from settled research decisions.
- `schema/` — experimental and eventually normative SCAP-NG schemas.
- `tools/` — reusable schema-analysis, migration, validation, packaging, and research utilities.

The current work is preliminary research rather than a published specification. Current clean-native development is in `research/iterations/003/`; iterations 001 and 002 preserve research history.

Current review: [full RHEL9 source-generated Benchmark, Rules and Assessments](research/iterations/003/review/rhel9-current-full/README.md), including all 445 Rules, comparative evidence and the local Windows conversion command. Start with the [current design contract](research/iterations/003/design/CURRENT-DESIGN.md); historical generated trees are not current authoring guidance.

## Development tracking

- [Detailed roadmap and proposed milestones](ROADMAP.md) — work remaining, completed issue history, dependencies, and beta/1.0 gates.
- [Open GitHub Issues](https://github.com/vanderpol/scap-ng/issues?q=is%3Aissue+is%3Aopen) and [completed issues](https://github.com/vanderpol/scap-ng/issues?q=is%3Aissue+is%3Aclosed).
- [Actions status](https://github.com/vanderpol/scap-ng/actions) and [full-benchmark handoff requirements](research/iterations/003/review/FULL-BENCHMARK-READINESS.md).

Proposed M0–M3 issue prefixes are roadmap groups, not yet native GitHub milestones. A future move to the OVAL Community organization is planned only after a stable beta or 1.0 and explicit approval from the repository owner and receiving organization.
