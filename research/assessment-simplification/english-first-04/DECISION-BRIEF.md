# English-first SCAP-NG: decision brief

**16 October 2026 · Pre-alpha research · Not a specification approval request**

## Decision now

**Continue researching the English-first design. Do not adopt it as the 0.4 grammar yet.** Keep the current 0.4 preview and release artifacts unchanged.

The six-STIG reports are *engineering evidence*, not evidence that a person can comfortably write a new assessment. We should not ask reviewers to choose a vocabulary based on corpus statistics alone.

## What has actually been demonstrated

| Finding | Decision relevance |
| --- | --- |
| **871/872** complete existing 0.4 Assessment dictionaries reconstruct through the experimental language | Strong structural coverage of current converted content |
| **5.21% shorter YAML** in the newer compact layout | Less repetition, but modest size reduction is **not** a usability measurement |
| **0 missing, malformed or cyclic references** across 871 audited Assessments | The research reference graph is internally connected; this does not prove correct behavior |
| **Apache collection dependencies reach 10 edges** | A major human-authoring complexity problem remains |
| **125,268 supported six-state combinations agree**, with 12 unresolved empty-reference cases | Useful model-level assurance; still **not** OVAL scanner or collected-evidence parity |
| **1 Assessment remains unsupported** (`none_exist` plus attached State) | Needs explicit semantic resolution, not an automatic rewrite |

Source: [current six-STIG reports, run 38932589417](reports/README.md). This is pinned-source research, not a claim of equivalence to the original SCAP 1.4 XML in execution.

**[Before/after review with complete source links](BEFORE-AFTER-REVIEW.md)** — use this page when deciding whether a real author would prefer the proposed form.

## The four examples we should actually review

| Real assessment | What the reader should judge | Current limitation |
| --- | --- | --- |
| [RHEL 9 SV-257889 — derived initialization-file checks](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md#1-linux--account-derived-file-permissions) | Can I discover and author the account collection, foreach, filters, and file checks without guessing? | Named-source and Set syntax still require explanation |
| [Windows 11 SV-253495 — Remote Desktop rights](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md#2-windows-11--remote-desktop-rights-depend-on-domain-role) | Can I clearly express nested WMI records and all three role-dependent alternatives? | Compact rewrites can accidentally change whole-State semantics |
| [DNS SV-259345 — signing and validity](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md#3-windows-server-dns--dynamic-zone-names-and-three-passing-alternatives) | Can I author commands derived from discovered zones? | Command Variable graph remains difficult to write |
| [Apache SV-214228 — loaded configuration](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md#4-apache-unix--required-vs-optional-settings-across-included-files) | Can I follow and author configuration discovery once and reuse it across checks? | Up to 10 dependency edges; repetition still dominates |

The linked excerpts are not independently executable full files; see their source and proof boundaries before comparing designs.

## What must be shown before an adoption decision

1. **A real side-by-side:** current 0.4, complete English-first proposal, and a plain-English explanation for the **same** source check (not an abbreviated showcase).
2. **An authoring exercise:** unfamiliar authors attempt one simple and one difficult check *from scratch*, using only a short vocabulary reference. Track mistakes, lookups and ambiguity—not just whether they can read YAML.
3. **One consistent grammar:** `inspect`, `where`, `collect`, `from`, `gather`, Set operations and `require` must have predictable placement. All referenced sources and Variables must be defined and discoverable.
4. **Semantic gate:** preserve every original collection, filter, cardinality, six-state and evidence behavior; resolve the boot-loader counterexample rather than hiding it. Structural round-tripping is necessary but not sufficient.

**Next proposed decision:** after those tests, choose between adopting a demonstrably better English-first grammar, improving the existing 0.4 grammar selectively, or rejecting the redesign.

Supporting detail: [consistency draft](AUTHORING-CONSISTENCY-WORKING-DRAFT.md) · [four source-backed examples](FOUR-REAL-WORLD-RESEARCH-EXAMPLES.md) · [research issue #235](https://github.com/vanderpol/scap-ng/issues/235).
