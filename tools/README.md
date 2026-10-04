# SCAP-NG tooling

For commands intended to be run by a person, use the **[Human-runnable SCAP-NG tools](HUMAN-RUNNABLE-SCRIPTS.md)** guide. It is the single maintained operator catalog for conversion, normalization, validation, compilation, audits, and research-only entry points.

The `tools/` directory also contains import libraries, test helpers, historical reproduction utilities, and research harnesses. A script's presence here does **not** make it a supported human entry point or establish that its emitted syntax is current.

Specialized implementation notes remain beside the tools they document, including:

- [current SCAP 1.4 conversion](scap_upconvert_v003/README.md)
- [OVAL → NG → OVAL round-trip research](scap_ng_roundtrip_v003/README.md)

Current semantic/design authority is outside this directory; see [the draft specification](../specification/README.md) and [CURRENT-DESIGN.md](../research/iterations/003/design/CURRENT-DESIGN.md).
