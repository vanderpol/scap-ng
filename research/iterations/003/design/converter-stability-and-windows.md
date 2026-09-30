# Converter stability and Windows developer delivery

Owner requirement, 2026-09-30: at a stable conversion checkpoint, provide the script that produces the reviewed NG content and allow the owner to run it on a Windows development computer. The converter currently serves as the executable expression of the emerging NG specification. This requirement informs implementation now; final handoff follows demonstrated stability.

## Required delivery

- One documented maintained entry point for SCAP input → accepted NG source; internal parser/render/validation modules may remain separate. No requirement for the owner to select among historical iteration scripts.
- Exact converter revision, Python/dependency versions, pinned source artifacts and checksums, design/schema version, supported features and explicit blockers.
- PowerShell instructions covering environment setup, local input selection, output location, running conversion, reading diagnostics and repeating validation.
- Local conversion and validation shall not depend on GitHub Actions, a signed-in browser, a Linux shell, GitHub credentials or an implicit download of moving source branches. A separately documented optional fetch step may prepare pinned inputs.
- Portable file handling, encodings and paths; no dependence on process working directory or Linux-only helper programs. Explicit relative source references remain portable and package-boundary checked.
- Deterministic output identity and semantics for the same inputs/tool/configuration. Document any intentional run metadata separately so timestamps do not hide substantive deltas.

## Stability gate

The converter SHALL NOT be called stable merely because a full generated tree or one successful round trip exists. Before owner handoff:

1. Reconcile output and all consumers against the current decision record. Eliminate obsolete authoring paths and ambiguous mixed grammar.
2. Validate Rule selections/defaults/profiles, applicability, manual methods and source accounting.
3. Preserve named and embedded Collection authoring support, source sharing, Variables, complete dependency closure, functions, sets, filters, defaults, cardinality, type contracts and diagnostics.
4. Run focused positive/negative fixtures and full pinned production conversion/round-trip comparisons. Keep deprecated-Test rejection cases and separate runtime-semantic conformance evidence.
5. Execute the same supported command on Windows and Linux, compare meaningful artifacts/diagnostics, and publish the actual platform/version/results. Claims of portability require Windows evidence.
6. Provide a small reproducible input/output example plus full RHEL 9 and Windows 11 feature/support reports. Unsupported source SHALL produce precise blockers instead of complete-looking partial success.

No final CLI command is invented here. Current tools are research components; an exact tested Windows command will be supplied with the stabilized entry point. README examples, fixtures, source grammar and implementation changes SHALL be reviewed together. Formal specification text will continue to record semantics that successful conversion alone cannot prove.

Provenance: **Evidence/Audit** of the owner's direct requirement; implementation acceptance criteria translate that requirement into verifiable delivery conditions.
