# First visit to SCAP-NG

SCAP-NG explores how to keep the investment in SCAP content while making content easier to author, scanners easier to implement, and assessment results easier to understand.

The current model is **Benchmark → Rule → Assessment**. A Benchmark groups requirements. A Rule describes a requirement and offers named assessment choices. An Assessment describes how software or a person checks it. Rule policy and technical evaluation have separate responsibilities.

## A short reading path

1. Read the [Board overview](board/README.md) for the working design, what is demonstrated, and what needs a decision.
2. Browse the [RHEL 9 review guide](docs/rhel9-review.md) or [Windows 11 review guide](research/iterations/003/review/windows11-current-full/README.md) for complete source-generated examples. These are review candidates; their generation date and evidence matter.
3. Read the [specification contents](specification/README.md) for the detailed model and its intentional differences from SCAP 1.4.
4. Use the [voting proposal index](board/proposals/README.md) to respond to individual yes/no questions through GitHub Discussion reactions.

You do not need to run a converter to review the work. If you do want to reproduce it, start with the [maintained converter instructions](tools/scap_upconvert_v003/README.md), using a pinned original SCAP package.

## How to interpret status

- **Working design:** direction accepted by the project owner; formal Board approval may still be needed.
- **Draft specification/schema:** a proposed contract under development.
- **Generated review candidate:** inspect alongside its source pin, command, warnings and exclusions.
- **Historical artifact:** preserved so reasoning and experiments can be reconstructed; its syntax may be obsolete.
- **Passing conversion or round trip:** evidence about representation and migration. It does not demonstrate scanner behavior on a target machine.

The latest bounded [full-corpus schema/normalization/compiler run](https://github.com/vanderpol/scap-ng/actions/runs/37004465863) passed. It accounts for 65 pinned NIWC packages, validates 25,147 fresh native documents and 19,655 after normalization, and compiles 65 bundles. Self-Assertion language evidence is tracked separately. The repository contains no released reference scanner with established target-runtime equivalence.

For an older example or an unfamiliar script, consult the [repository map](docs/repository-map.md) before treating it as current.
