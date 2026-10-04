# First visit to SCAP-NG

SCAP-NG explores how to keep the investment in SCAP content while making content easier to author, scanners easier to implement, and assessment results easier to understand.

The current model is **Benchmark → Rule → Assessment**. A Benchmark groups requirements. A Rule describes a requirement and offers named assessment choices. An Assessment describes how software or a person checks it. Rule policy and technical evaluation have separate responsibilities.

## A short reading path

1. Start with the [current review set](review/current/README.md). It is the single navigation surface for material we want external reviewers to examine together.
2. If you will change or maintain the project, read [MAINTAINING.md](MAINTAINING.md) and [BRANCH-MANAGEMENT.md](BRANCH-MANAGEMENT.md) before making changes. Machine-green is not the same as human-accepted.
3. Read the [Board overview](board/README.md) for what needs a decision.
4. Browse the [RHEL 9 full-review summary](review/current/examples/rhel9-full.md) or [Windows 11 full-review summary](review/current/examples/windows11-full.md) for complete source-generated examples. These are review candidates; their generation date and evidence matter.
5. Read the [specification contents](specification/README.md) for the detailed model and its intentional differences from SCAP 1.4.
6. Use the [voting proposal index](board/proposals/README.md) to respond to individual yes/no questions through GitHub Discussion reactions.

You do not need to run a converter to review the work. Development and reproduction tools are intentionally outside the `review/` surface. If you do want to reproduce it, start with the [maintained converter instructions](tools/scap_upconvert_v003/README.md), using a pinned original SCAP package.

## How to interpret status

- **Working design:** direction accepted by the project owner; formal Board approval may still be needed.
- **Draft specification/schema:** a proposed contract under development.
- **Generated review candidate:** inspect alongside its source pin, command, warnings and exclusions.
- **Historical artifact:** preserved so reasoning and experiments can be reconstructed; its syntax may be obsolete.
- **Passing conversion or round trip:** evidence about representation and migration. It does not demonstrate scanner behavior on a target machine.

The 0.2.0 technical content-development freeze is recorded at `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`. Its exact-SHA full NIWC schema/normalization/compiler run passed, along with Self-Assertion, smoke, preservation, and Ubuntu/Windows current-design gates. See `transition/0.2.0-freeze-record-2026-10-04.md`. This is strong technical evidence, not an exhaustive independent human semantic audit. The repository contains no released reference scanner with established target-runtime equivalence.

For an older example or an unfamiliar script, consult the [repository map](docs/repository-map.md) before treating it as current.
