# SCAP-NG

SCAP-NG is research toward a simpler successor to SCAP 1.4, designed to support **lossless semantic upgrades from SCAP 1.4** while improving authoring, migration, packaging, and results. The native representation may normalize and simplify legacy structures, but supported conversions are intended to preserve effective policy, assessment behavior, applicability, inputs, dependencies, evidence behavior, and source provenance rather than merely reproduce the original XML.

**Status:** pre-alpha. SCAP-NG 0.2.0 is technically frozen for bounded human/OVAL Board review. It is not a released standard or production scanner, and passing conversion/schema tests do not establish live-target equivalence.

## Start here

- **Draft specification:** [specification/README.md](specification/README.md)
- **OVAL Board / external review:** [board/README.md](board/README.md)
- **SCAP 1.4 → SCAP-NG key changes:** [board/SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md](board/SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md)
- **OVAL 5.12.3 → SCAP-NG capability crosswalk:** [specification/migration/oval-5.12.3-capability-crosswalk.md](specification/migration/oval-5.12.3-capability-crosswalk.md)
- **SCAP-NG 0.2.0 schemas:** [schema/v0.2.0/README.md](schema/v0.2.0/README.md)
- **Human-runnable tools:** [tools/HUMAN-RUNNABLE-SCRIPTS.md](tools/HUMAN-RUNNABLE-SCRIPTS.md)
- **Maintenance / semantic-change process:** [MAINTAINING.md](MAINTAINING.md)
- **Roadmap:** [ROADMAP.md](ROADMAP.md)
- **History/archive:** [archive/README.md](archive/README.md)

Maintainers who need the implementation/design contract should use [CURRENT-DESIGN.md](research/iterations/003/design/CURRENT-DESIGN.md). Historical research, transition records, old generated content, and passing tests are evidence; they do not override current specification/design authority or imply Board acceptance.

## Current architecture

SCAP-NG uses **Benchmark → Rule → Assessment**. There is no separate Policy object.

Native automated assessment keeps useful OVAL-aligned concepts—**Test, Object, State, Variable, and Item**—while removing legacy XML/serialization machinery where it is not semantically required. `evaluate` replaces OVAL criteria/criterion. Applicability is explicit content, manual assessment is first-class, migration provenance stays outside executable content, and Results are designed to explain outcome and evidence without reproducing ARF.

## Repository map

| Path | Purpose |
| --- | --- |
| `board/` | Board briefing, sample content, proposals, and voting |
| `specification/` | Draft normative specification and migration/crosswalk material |
| `schema/` | Versioned native schemas and capability mappings |
| `review/` | Compact reviewer-facing summaries and frozen review iterations |
| `tools/` | Converter, normalizer, validators, compiler, audits, and research utilities |
| `tests/` | Focused conformance/regression fixtures |
| `research/` | Design rationale and evidence; much of it is historical |
| `transition/` | Dated handoff/freeze records; not current design authority |
| `archive/` | Preserved historical indexes/artifacts |

[Issues](https://github.com/vanderpol/scap-ng/issues) · [Actions](https://github.com/vanderpol/scap-ng/actions) · [Discussions](https://github.com/vanderpol/scap-ng/discussions)
