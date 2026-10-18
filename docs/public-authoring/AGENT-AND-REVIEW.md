# Public agent/editor behavior — fast, visible, reviewable

**Curated guidance · 18 October 2026 · [#242](https://github.com/vanderpol/scap-ng/issues/242).** Use this with [public knowledge entry](README.md) and [version/source contract](VERSION-AND-SOURCES.md). Applicable to a ChatGPT plugin, Claude/Gemini/Grok model adapter, offline VS Code editor or ordinary author.

**Source authority:** [Publisher versus discovery-source policy](AUTHORITATIVE-STIG-SOURCES.md). The agent can follow third-party Rule lookup leads, but must not treat STIGViewer.com as the official publisher or assert a Rule revision without verified Cyber Exchange or verifiable local content.

## The fast-first authoring loop

**When a user names a Rule or provides an Assessment, the first useful reply should show the actual source or draft.** Don't spend ten minutes retrieving entire benchmarks before showing anything. Do not invoke heavyweight autonomous research for ordinary edits.

1. **Open minimally:** one Rule, its linked Assessment (if available), and the selected version profile. Show the Assessment immediately with its source identity. If user uploaded a file, work from that file without re-fetching its whole corpus.
2. **Show meaningful content:** complete manageable YAML/JSON, a source/graphical editor if available, and a short plain-English statement of data collected, existence/matching and Test combination. Clearly label an existing file versus an AI-proposed change.
3. **Offer concrete review actions:** change one requirement, inspect collected Item/field/record conditions, show a diff, add sample evidence, inspect alternative source or export a file/patch. The author retains control.
4. **Search prior art selectively:** examine linked original OVAL and nearest trusted equivalent first. Search adjacent OS/public patterns more deeply only if needed to modernize a requested change, or if the user asks. **Reuse behavior; modernize structure** with version-supported SCAP-NG features.
5. **Edit incrementally:** preserve one versioned canonical source document and render synchronized guided/graphical/source presentations if the host supports them. Never imply that a skills-only plugin implements a persistent graphical editor.
6. **Test correctly:** author/sample cases may be created without a scanner. A **tested scanner's evaluation kernel**, fed the selected sample Items and status, must calculate authoritative Test/Assessment outcomes; if absent, say `NOT SCANNER-VERIFIED`.
7. **Save deliberately:** download/export without GitHub, or request explicit authorization and display a complete diff before GitHub writes. A public user without an account connector should not be blocked from local content creation.

## Human review checklist

The reviewer needs to be able to answer:

- What **specific Rule and version** is this, and where was its original check or source OVAL obtained?
- What capability/Object selects what population? If no Items are present, which requirement controls that case?
- Which **Items, scalar fields, record members and expected-value arrays** must exist, and which must match? Is exactly one **existing** different from exactly one **matching**?
- Are Windows multi-record fields correlated within the same Item/record, not satisfied by pieces of other records?
- Are multiple required Tests combined exactly as source behavior requires? Were independent alternatives such as the Windows Everyone branch kept?
- What occurs with **zero/many values, incomplete/error/not-collected sources, Variables, Sets/Filters or for_each**? Unsupported behavior must be called out, not guessed.
- Does the proposed Assessment use **only the selected profile's allowed syntax**, including any explicit overlay? What has a deterministic tool actually checked?
- Has a **tested scanner** run on these samples? If not, are expected outcomes plainly marked as proposed/research?
- What files/values changed, which changes are merely vocabulary/layout, and which might affect results?

## Publication and privacy boundary

A public plugin's default knowledge should consist of these **curated public documents**, a coherent pinned version profile, and just the source-backed examples necessary for a user's request. It should **not** load conversations, private memories, credentials, unrelated user's documents, internal scratchpads, or development issue history. Public GitHub research remains publicly accessible, but is **not automatically normative**.

The agent can explain how to switch target profiles, but it must not silently migrate reviewed Assessment files or assume renames preserve semantics. Private examples, uploaded benchmarks and host evidence require the individual author's authorization, not a shared public-agent account.

Keep the rule concise: **AI drafts; deterministic schema tooling diagnoses structure; tested scanner evaluates samples; humans approve source.**
