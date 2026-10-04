# SCAP-NG

Research toward a simpler successor to SCAP 1.4 that preserves useful OVAL/SCAP semantics while improving authoring, migration, packaging, and results.

**Status:** pre-alpha. SCAP-NG 0.2.0 is technically frozen for bounded human/OVAL Board review. It is not a released standard or production scanner, and passing conversion/schema tests do not establish live-target equivalence.

## Start here

- **New reviewers:** [START-HERE.md](START-HERE.md)
- **OVAL Board:** [board/README.md](board/README.md)
- **Current review set:** [review/current/README.md](review/current/README.md)
- **Current design authority:** [research/iterations/003/design/CURRENT-DESIGN.md](research/iterations/003/design/CURRENT-DESIGN.md)
- **Draft specification:** [specification/README.md](specification/README.md)
- **SCAP-NG 0.2.0 schemas:** [schema/v0.2.0/README.md](schema/v0.2.0/README.md)
- **OVAL 5.12.3 → SCAP-NG capability crosswalk:** [specification/migration/oval-5.12.3-capability-crosswalk.md](specification/migration/oval-5.12.3-capability-crosswalk.md)
- **Human-runnable tools:** [tools/HUMAN-RUNNABLE-SCRIPTS.md](tools/HUMAN-RUNNABLE-SCRIPTS.md)
- **Maintenance process:** [MAINTAINING.md](MAINTAINING.md)
- **Cross-interface handoff:** [transition/README.md](transition/README.md)
- **History/archive:** [archive/README.md](archive/README.md)

## Current architecture

SCAP-NG uses **Benchmark → Rule → Assessment**. There is no separate Policy object.

Native automated assessment keeps useful OVAL-aligned concepts—**Test, Object, State, Variable, and Item**—while removing legacy XML/serialization machinery where it is not semantically required. `evaluate` replaces OVAL criteria/criterion. Applicability is explicit content, manual assessment is first-class, migration provenance stays outside executable content, and Results are designed to explain outcome and evidence without reproducing ARF.

## 0.2.0 checkpoint

Technical schema baseline: `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`.

The six-case converter-produced OVAL Board pilot is present under [`board/review-content/0.2.0/`](board/review-content/0.2.0/) and is pending human review. Current work should challenge the frozen design with small focused cases rather than expanding schema semantics casually.

## Repository map

| Path | Purpose |
| --- | --- |
| `board/` | OVAL Board briefing, sample content, proposals, and voting links |
| `review/current/` | Current external review navigation and durable review summaries |
| `specification/` | Draft normative specification and SCAP/OVAL crosswalks |
| `schema/` | Versioned native schemas and reviewed capability mappings |
| `tools/` | Converter, normalizer, validators, compiler, audits, and research utilities |
| `tests/` | Focused conformance/regression fixtures |
| `research/` | Design records and dated evidence; historical iterations are not current authority |
| `transition/` | Current handoff state, freezes, decisions, and interface continuity |
| `archive/` | Preserved historical material |

[Roadmap](ROADMAP.md) · [Issues](https://github.com/vanderpol/scap-ng/issues) · [Actions](https://github.com/vanderpol/scap-ng/actions) · [Discussions](https://github.com/vanderpol/scap-ng/discussions)
