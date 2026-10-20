# Select a coherent version and trustworthy sources

**Public authoring contract · 18 October 2026 · [#242](https://github.com/vanderpol/scap-ng/issues/242).** When the language is pre-alpha and changing quickly, **every authored file and agent draft needs a reproducible target version.**

## What is current versus experimental?

| Surface | Status for authors | How to use |
| --- | --- | --- |
| [Current 0.4.0 six-STIG samples](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) and [0.4.0 schema](../../schema/v0.4.0/README.md) | **Current pre-alpha authoring profile**, not Board-ratified or scanner-conformant | Use one pinned 0.4 release/schema; preserve source provenance and explicit exceptional requirements |
| [0.3.0 archive](../../archive/0.3.0/README.md) and [0.3 schema](../../schema/v0.3.0/) | **Historical and reproducible** | Use only for reproducing legacy authoring, compiled demo bundles or synthetic results |
| [October 15 r3 six-STIG preview](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3) | Historical source-backed **research input** | Do not use `collected_items_require` as if it were the current output grammar |
| Proposed English-first/B/other research syntax | **Non-normative research** until separately approved | Do not generate it as if it were the selected supported grammar |

**Critical version drift:** Current canonical 0.4 output uses `require`, including source-proven structured `items`/`all_items_must`. The older r3 source includes `collected_items_require` and separate State-field forms. An agent/editor **must not mix dialects or assume the research form is current**; unusual source matching requirements are preserved explicitly. See [current 0.4 schema](../../schema/v0.4.0/README.md).

## Minimal profile to pin

For each Assessment creation/edit session, record:

- Source repository and **immutable release tag/commit SHA**, never mutable `main` as a reproducible reference.
- Declared Assessment `specification.version`, exact schema set and coherent capability mappings.
- Optional research **overlay identity plus its own verified content hash**, not just a version number.
- STIG Rule ID/revision and exact origin, original OVAL/XCCDF source when applicable, and hashes/identities for reused content.
- Schema validator **and** tested scanner evaluator identity/coverage separately, or clear `NOT VALIDATED` / `NOT SCANNER-VERIFIED` indicators.

A pinned reference may be a local verified offline pack. The editor and offline VS Code workflow must not require fetching GitHub after the pack is installed.

**STIG trust note:** [Authoritative DISA source policy and third-party discovery limits](AUTHORITATIVE-STIG-SOURCES.md). STIGViewer.com may help locate a Rule but does **not** establish official Check text/revision; distinguish it from DISA's separate STIG Viewer application. When official provenance cannot be verified, label the draft's source uncertainty and offer an uploaded, verifiable publisher package rather than silently substituting a mirror.

## Reuse trusted logic, modernize safely

Preferred source order for initial drafting:

1. Existing **linked Assessment for the selected Rule** and its original source content.
2. Reviewed, reusable **SCAP-NG shared collections/Assessments** in the same coherent version profile.
3. Official DISA STIG source: only use [cyber.mil](https://www.cyber.mil/) for DISA manuals, with verifiable revision.
4. Other public SCAP/OVAL content and adjacent OS versions as **comparison candidates**, verifying provider/OS differences, scope, predicates, result-status rules and exceptions.
5. User-uploaded STIGs/OVAL/datastreams, with displayed provenance and trust/identity limitations.

**When source is not verified:** produce an explicitly unvalidated draft based on available user material, and name the evidence gap. Do not invent official citations, silently substitute another OS's policy, or let a similar title prove equivalent behavior.

## Truth and confidence are different things

- AI proposes source, explains it, and prepares sample cases; **AI does not declare validity or Assessment outcomes**.
- A versioned deterministic validator can report structural/schema/reference diagnostics.
- Only a **tested scanner evaluation core** can issue authoritative six-state outcomes on provided sample data, and the resulting verdict refers to **that supplied evidence**, not a real host.
- Schema passing, source conversion, sample fixture acceptance, real scanner execution and Board acceptance are **separate checkpoints**. Unsupported evaluation must report unavailable rather than a false success.

Canonical project process: [Maintaining SCAP-NG](../../MAINTAINING.md). Public quick reference: [README](README.md).
