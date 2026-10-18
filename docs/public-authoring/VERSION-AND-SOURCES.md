# Select a coherent version and trustworthy sources

**Public authoring contract · 18 October 2026 · [#242](https://github.com/vanderpol/scap-ng/issues/242).** When the language is pre-alpha and changing quickly, **every authored file and agent draft needs a reproducible target version.**

## What is current versus experimental?

| Surface | Status for authors | How to use |
| --- | --- | --- |
| [Draft specification](../../specification/README.md) and [0.3 schema](../../schema/v0.3.0/) | 0.3 is the active development baseline, **not a released/ratified final standard** | Consult the coherent 0.3 source for 0.3 material |
| [0.4 schema directory](../../schema/v0.4.0/README.md) | **Working pre-alpha 0.4 draft**, not Board approved | Use for controlled experiments, never silently assume it is accepted standard |
| [October 15 r3 six-STIG preview](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3) | **Source-backed 0.4 research candidate**, including separate scoped State/Item-requirement vocabulary | Explicitly label **r3 research overlay**; it is not interchangeable with the 0.4 base schema |
| Proposed English-first/B/other research syntax | **Non-normative research** until separately approved | Do not generate it as if it were the selected supported grammar |

**Critical example of version drift:** In the 0.4 base working draft, a Test's Item requirement uses `require`; the r3 scoped research candidate may use `collected_items_require` and allow `state_fields_require`. An agent or editor **must not mix them** or report base-schema validation from preview syntax. See [0.4 status and limitations](../../schema/v0.4.0/README.md).

## Minimal profile to pin

For each Assessment creation/edit session, record:

- Source repository and **immutable release tag/commit SHA**, never mutable `main` as a reproducible reference.
- Declared Assessment `specification.version`, exact schema set and coherent capability mappings.
- Optional research **overlay identity plus its own verified content hash**, not just a version number.
- STIG Rule ID/revision and exact origin, original OVAL/XCCDF source when applicable, and hashes/identities for reused content.
- Schema validator **and** tested scanner evaluator identity/coverage separately, or clear `NOT VALIDATED` / `NOT SCANNER-VERIFIED` indicators.

A pinned reference may be a local verified offline pack. The editor and offline VS Code workflow must not require fetching GitHub after the pack is installed.

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
