# First visit to SCAP-NG

SCAP-NG explores a next-generation SCAP model that keeps the investment in existing SCAP/OVAL content while making content easier to author, migrate, validate, and explain.

The current architecture is **Benchmark → Rule → Assessment**. A Rule owns the requirement/policy context and named Assessment choices. An Assessment owns the technical or manual evaluation method. There is no separate Policy object.

## Read in this order

1. [SCAP 1.4 → SCAP-NG key changes](board/SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md) — short architecture/semantic briefing.
2. [Current review set](review/current/README.md) — the external-review navigation surface.
3. [0.2.0 Board review](board/README.md) — sample conversions, Board questions, and voting.
4. [Draft specification](specification/README.md) — detailed normative direction.
5. [Current design contract](research/iterations/003/design/CURRENT-DESIGN.md) — implementation/design authority for maintainers.
6. [Human-runnable tools](tools/HUMAN-RUNNABLE-SCRIPTS.md) — conversion, normalization, validation, packaging, and audits.

## Current status

SCAP-NG 0.2.0 is technically frozen at schema baseline `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d` for bounded content/conformance review.

The six-case OVAL Board pilot has been generated through the maintained converter and is now awaiting human semantic/readability review. Automated gates are strong evidence, but they are not equivalent to independent scanner/live-target conformance or Board ratification.

## Important distinctions

- **Working design:** current project direction; may still require Board ratification.
- **Draft specification/schema:** proposed contract, not a released standard.
- **Generated review content:** inspect with source pins, provenance, warnings, and expected results.
- **Passing conversion/round trip:** migration/representation evidence, not target-runtime proof.
- **Historical artifact:** preserved evidence; its syntax or architecture may be superseded.
- **Human-accepted / Board-ratified:** separate status from machine validation.

## If you want to run the project

Start with [the human tooling guide](tools/HUMAN-RUNNABLE-SCRIPTS.md). The preferred conversion path is the current `scap_upconvert_v003` converter; historical renderers remain available only for reproduction/research.

If you will modify semantics, read [MAINTAINING.md](MAINTAINING.md) first. Machine-green does not mean human-accepted.
