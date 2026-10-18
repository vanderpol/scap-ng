# SCAP-NG 0.4 — complete before-and-after Assessment review

**October 16, 2026 · Pre-alpha research · Not a specification adoption request**

## Sample-data editor test bench — research opportunity

**The editor can help decide whether split existence/matching fields or a merged requirement phrase is clearer.** The [six-state sample-data playground research](EDITOR-SAMPLE-DATA-PLAYGROUND.md) designs a regex101-style authoring pane with user-supplied synthetic system Items, completeness flags, expected-versus-actual regression cases, and source-linked explanations. [Eight representative sample scenarios](EDITOR-SAMPLE-DATA-EXAMPLES.json) cover RHEL9 `/home` and Windows11 WMI DomainRole evidence, including zero Items, incomplete streams and missing nested record members. **These are proposed input fixtures, not runnable editor tests.** Tracked in [#241](https://github.com/vanderpol/scap-ng/issues/241). This is **not** permission to change the compiler or ship fixtures in signed bundles.

## New readability candidates and first-read tests — 18 October 2026

**Research only.** The complete paired baseline documents below remain unchanged. None of the new candidates has an accepted 0.4 grammar, standalone lossless lowering, complete scanner parity or independent novice-review scores.

| Topic | Complete candidate or evidence | Reader test |
| --- | --- | --- |
| Simple Linux /home | [Five-case friction audit + lean third candidate](READABILITY-RESET-ITERATION-1.md) | [Unprimed three-way full YAML review](AUDITOR-FIRST-READ-PACKET.md) ([facilitator-only key](AUDITOR-FIRST-READ-SCORING.md)) |
| Windows 11 deny-RDP | [Complete seven-Test lean candidate](FULL-03-win11-LEAN-THIRD-CANDIDATE.md) | [Complex Windows/Linux meaning maps](COMPLEX-FIRST-READ-MAPS.md) |
| DNS signing | [Complete inline-command candidate](FULL-04-dns-INLINE-COMMAND-CANDIDATE.md) | [Unprimed full DNS A/B](DNS-COMPOSITION-BLIND-REVIEW.md) ([facilitator-only key](DNS-COMPOSITION-REVIEW-KEY.md)) |
| Apache configuration | [Complete inline-command candidate](FULL-05-apache-INLINE-COMMAND-CANDIDATE.md) · [Second-pass inlining limits and staged-source sketch](APACHE-SECOND-PASS-READABILITY.md) | [Full Apache authorability exercise](APACHE-COMPOSITION-AUTHORING-CHALLENGE.md) |

Supporting analysis: [Original Apache/DNS Variable chains](APACHE-DNS-COMPOSITION-RESEARCH.md) · [OVAL 5.12.3 concat vs merge values](OVAL-5123-CONCAT-MERGE-READABILITY.md) · [Value operator comparison with real DNS/Apache snippets](VALUE-OPERATOR-AUTHORING-BAKEOFF.md) · [Unprimed two-operator comprehension packet](VALUE-OPERATOR-BLIND-PACKET.md) · [Command composition/typing/provenance contract](COMMAND-COMPOSITION-CONTRACT.md).

**Your feedback question:** Which format makes it easier to understand **and author a complete check**—existing 0.4 or proposed English-first—without needing to guess what a referenced collection or Variable means?

Each comparison below includes **both complete YAML documents directly on its own Markdown page**: metadata, source collections, variables, checks, field/Item requirements, and final evaluation. **There are no shortened snippets or omitted parts in the paired YAML blocks.** They can be read entirely on `github.com`, including on a phone or restricted proxy network.

## Open a full comparison

| Order | Assessment | Why review it |
| --- | --- | --- |
| 1 | **[RHEL 9 — /home with nosuid (full check)](FULL-01-linux-home.md)** | Smallest complete before/after: selector, multi-value mount option, presence and evaluation |
| 2 | **[RHEL 9 — account-derived initialization-file permissions (full check)](FULL-02-linux-files.md)** | All named account sources, union/difference, per-user file collection and eight permission fields |
| 3 | **[Windows 11 — Remote Desktop deny rights (full check)](FULL-03-win11-rights.md)** | Seven Tests, WMI record scoping, named Windows sources and three OR alternatives |
| 4 | **[Windows Server DNS — zone signing and RRSIG validity (full check)](FULL-04-dns.md)** | Five Tests, three command-building Variables, shared zone discovery and evaluation tree |
| 5 | **[Apache UNIX — included configuration and directives (full check)](FULL-05-apache.md)** | Four Tests, 18 local Variables, source discovery chain, required versus optional conditions |

Each page starts with **what changed**, followed by the complete 0.4 YAML and complete experimental YAML. The highlights are editorial; they do **not** modify the YAML under review.

## How to judge

- **Comprehension:** Can you understand how the entire check works, including where inputs come from and how the final result is determined?
- **Authorability:** Could you write the proposed version of a new DISA check from scratch with a short vocabulary reference?
- **Consistency:** Are `inspect`, `where`, `collect`, `from`, `gather`, Set operators and `require` placed predictably?
- **Faithfulness:** Where might shorthand obscure counts, missing data, records, dynamic collection or six technical result states?

You can give feedback per example instead of making a single decision on the whole proposal. The most useful comments are **what you would change in the after version**, especially where you have to hunt for definitions.

## Proof boundaries

The four complex **after** files are generated by the experimental compact-layout translator from the pinned existing 0.4 Assessment files and were reconstructed with exact source-dictionary equality in the [six-STIG research workflow](https://github.com/vanderpol/scap-ng/actions/runs/38934771985). The **simple Linux after** was assembled using the same mapping and is clearly labeled as not separately round-trip tested on its page.

**Structural equality is not SCAP 1.4 runtime/evidence parity.** One `none_exist` plus State source shape remains unresolved outside these examples. Human authoring usability has not yet been established. Nothing here changes the normative 0.4 schema or scanner.

Research issue [#235](https://github.com/vanderpol/scap-ng/issues/235) · [Authoring consistency working draft](AUTHORING-CONSISTENCY-WORKING-DRAFT.md) · [Decision brief](DECISION-BRIEF.md).
