# Retrieved conversation-search notes — 2026-10-02



These are tool-returned summaries, not verbatim transcripts or an exhaustive conversation inventory. Search coverage cannot enumerate unavailable conversations. Reconstructed dates/attributions and assistant claims require corroboration. External file-proposal extracts were excluded because they do not establish owner decisions.



## early recovery

[convo search]
- [USER_FACT] [c4] U@2026-09-28T13:32:12Z, -4d: SCAP-NG design discussion: Parameters must avoid XCCDF/OVAL stovepipes; reconsider deprecated `refine-value`; define XCCDF check-text placement.
- [USER_CONSTRAINT] [c4] U@2026-09-28T13:35:28Z, -4d: keep `refine-value` simple/small; possible OVAL Board vote. [PRIOR_ASSISTANT_OUTPUT] [c4] A@2026-09-28T13:36:57Z, -4d: proposed SHALL NOT initially define native equivalent; migrate only losslessly or flag review; decision note `research/iterations/002/decisions/parameter-model.md`.
- [PRIOR_ASSISTANT_OUTPUT] [c0] A@2026-09-26T20:32:21Z, -6d: recovered historical RHEL10 publishers provide per-rule→combined OVAL→applicability→datastream pipeline, validation/equivalence checks, and identity migration; supported repository-native builder still proposed. Retrieval gaps: no evidence here for earliest goals, three formats, frozen iteration 001/restart 002/003, four OS anchors, 100k scalability, evidence caps, standalone conversion tools, results, glossary, or provenance.

- [USER_CONSTRAINT] [c2] U@2026-09-25T18:15:50Z, -7d: accepted repository-wide provenance/source ledger for all future remediation, SCAP/OVAL, Anti-STIG, benchmark ports, and substantial changes; record uncertainty rather than guessing.
- [PRIOR_ASSISTANT_OUTPUT] [c2] A@2026-09-25T18:19:26Z, -7d: Apache retrospective: 61 controls (45 Server/16 Site), COMMON 13, ADAPTED 10, ORIGINAL 6, EVIDENCE/AUDIT 32, INHERITED 0; 51 HIGH scrutiny; V-214256 and V-214292 corrected/classified; provenance docs created.
- [USER_PREFERENCE] [c2] U@2026-09-25T20:16:51Z, -7d: accepted broader `SCAP/STIG Automation` project with separate chats per technology/workstream; repository is shared source of truth. Retrieval gap: no evidence here of earliest SCAP-NG design, three formats, iteration freeze/restart, four anchors, 100k scalability, evidence caps, conversion tools, deprecated tests/results, normative spec, glossary, or archive provenance through Sep 28.

- [USER_FACT] [c3] U@2026-09-28T11:53:37Z, -4d: SCAP-NG project context: Jack Vander Pol; archive through Sep 28, 2026; four anchors are RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025.
- [USER_PREFERENCE] [c3] U@2026-09-28T11:40:18Z, -4d: accepted focus on small, simple, concise native NG source for OVAL Board/content-author review; provenance linkages may be YAML comments if available.
- [PRIOR_ASSISTANT_OUTPUT] [c3] A@2026-09-28T11:53:37Z, -4d: goals/design evidence: three renderings—combined rule, split policy/assessment/binding, Ansible-inspired; freeze iteration expansion and manually review representative Linux/Windows cases; preserve XCCDF/OVAL/OCIL as migration provenance, not normative NG; eventual reference scanner follows format selection/stabilization; repository tools/lessons committed.

- [USER_CONSTRAINT] [c5] U@2026-09-27T18:13:49Z, -5d: both formats must transform from existing SCAP 1.4 datastreams; conversion is non-negotiable; converter must cover a versioned public corpus.
- [USER_PREFERENCE] [c5] U@2026-09-27T18:11:22Z, -5d: leave existing 001 tests unchanged; create parallel Ansible-inspired real-world corpus for comparison; accepted semantic-IR-many-renderers architecture.
- [PRIOR_ASSISTANT_OUTPUT] [c5] A@2026-09-27T18:49:33Z, -5d: proposed splitter + semantic IR + renderers; strict closure, standalone validation, provenance, unresolved-ID errors; priority benchmarks RHEL9, OL9, Windows11, Server2025. Retrieval gaps: goals, three formats, freezing/restarting 001/002/003, 100k scalability, evidence caps, deprecated tests/results, normative spec/glossary details.



## recent recovery

[convo search]
- [USER_CONSTRAINT] [c0] U@2026-10-02T11:30:09Z, -7m: accepted delaying Codex transition until existing ChatGPT SCAP-NG work reaches partial completion

- [USER_CONSTRAINT] [c1] U@2026-09-30T15:30:29Z, -2d: continue backlog work autonomously; prompt only for semantic, architecture, or agreed-native-design decisions; proceed with clear bug fixes.
- [USER_PREFERENCE] [c1] U@2026-09-30T15:09:05Z, -2d: prioritize semantic equivalence over byte-for-byte XML; report explainable NG-induced round-trip noise rather than changing it automatically.
- [PRIOR_ASSISTANT_OUTPUT] [c1] A@2026-09-30T15:55:33Z, -2d: structural inheritance milestone: 445/445 complex types resolved, 0 unresolved references; broader hidden-behavior, platform-specific, and runtime-result audit remains incomplete.

- [USER_CONSTRAINT] [c2] U@2026-09-30T13:50:12Z, -1d22h: profiles should compactly list disabled rules; rules inherently enabled; assessment linkages must be obvious; RHEL9 sanity check only when ready.
- [USER_CONSTRAINT] [c2] U@2026-09-30T14:12:39Z, -1d21h: accepted relative YAML paths for authoring; no separate assessment index; scanners should use package manifest.
- [USER_CONSTRAINT] [c2] U@2026-09-30T14:28:48Z, -1d21h: separate non-voting discussions from frozen, explicitly phrased Board vote topics; reactions used for official votes.
- [PRIOR_ASSISTANT_OUTPUT] [c2] A@2026-09-30T21:58:02Z, -1d13h: later architecture restored Benchmark→Rule→Assessment, with Rule-owned selections; separate Policy files removed. Current blockers include variables/functions/inputs, sets/filters/result propagation, resource limits, and corpus failures; RHEL9/Windows not review-ready.

- [USER_PREFERENCE] [c3] U@2026-10-01T14:41:04Z, -23h: retain OVAL naming where semantics remain; Object preferred over Collection; new vocabulary only if fully divorcing from OVAL.
- [USER_CONSTRAINT] [c3] U@2026-10-01T15:12:48Z, -20h: retain `evaluate` unless OVAL Board objects; it must preserve arbitrarily nested criteria/criterion Boolean trees for conversion.
- [USER_CONSTRAINT] [c3] U@2026-10-01T15:07:38Z, -20h: `comment`→`test_title/object_title/state_title/variable_title` is a hard required change; accepted terminology/model alignment before generated schemas.

- [USER_FACT] [c4] U@2026-10-02T10:57:51Z, -39m: Jack Vander Pol SCAP-NG transition archive spans Sept 29–Oct 2; current work emphasizes a clean-break native Assessment capability model, executable semantic validation, and simpler shared schema machinery rather than reproducing OVAL structure.
- [PRIOR_ASSISTANT_OUTPUT] [c4] A@2026-10-02T02:54:05Z, -8h42m: Established result-schema scope: 25,147/25,147 native documents validate; runtime result removed from authored Test schema; normalization still blocked by 33 Assessment identity conflicts. #46 source-invalid quarantine and #11 set/filter/result propagation closed; #7, #9, #10, #38 remain open.
- [PRIOR_ASSISTANT_OUTPUT] [c4] A@2026-10-01T21:57:51Z, -13h39m: Signing decision: legacy XML signatures authenticate original XML only and must be verified before conversion; they cannot be carried forward as signatures on SCAP-NG packages. New simple vendor-friendly Benchmark Result signing was proposed; package/signing details remain elsewhere unresolved.

