# OVAL Board proposals and votes

This is the **single index for Board proposal records, vote links, and proposal status**. Individual proposal files under [`proposals/`](proposals/) are immutable voting records once published; this page is the maintained navigation/status view.

React to each opening Discussion post with 👍 Yes or 👎 No. Comments explain a vote. **Publication does not equal ratification.** If a proposal's substance changes, create a new proposal/version and fresh vote rather than silently rewriting the published record.

## Proposal groups

- **P001–P010:** governance, architecture, native capability design, Objects/Filters/Variables.
- **P011–P020:** evaluation, collection/reuse, applicability, invocation context, versioning.
- **P021–P027:** metadata, informational policy, Results, evidence, completeness.
- **P028–P035:** packaging, signatures/trust, weights, coverage.
- **P036–P046:** Profiles, Tailoring, Parameters, Organizational Input, groups, manual assessment.
- **P047–P052:** CPE/applicability, identity/extensions, migration defects, independent conformance.
- **P053–P058:** canonical execution representation, authoring views, alternate result encodings, semantic retention/deprecation, objectless capabilities, conditional-authoring scope.

## Open proposal gaps

The current 0.2.0 design has several decisions that are **not yet cleanly represented by a current Board vote**. These should become new proposal IDs/versions rather than edits to P001–P058:

- structured native `if / then / else`, explicitly superseding the direction proposed by P058;
- independently executable standalone Assessments;
- Assessment-result dependencies / OVAL `extend_definition`;
- exact-semantic Assessment normalization and deduplication;
- OVAL 5.12.3 as the baseline plus explicitly reviewed later changes;
- disposition of unused XCCDF machinery;
- Organizational Input as the native mechanism for organization-delegated expected values;
- Tests whose natural source is another first-class node rather than an Object.

P058 is the clearest stale proposal relative to the frozen 0.2.0 design: it proposed deferring general conditional authoring, while 0.2.0 now contains structured conditional evaluation. The historical P058 text remains unchanged.

## Published proposals

| ID | Decision | GitHub Discussion |
| --- | --- | --- |
| [P001](proposals/P001.md) | [VOTE P001] Reaction voting procedure | [Vote](https://github.com/vanderpol/scap-ng/discussions/58) |
| [P002](proposals/P002.md) | [VOTE P002] Benchmark, Rule and Assessment architecture | [Vote](https://github.com/vanderpol/scap-ng/discussions/59) |
| [P003](proposals/P003.md) | [VOTE P003] Clean native capability design | [Vote](https://github.com/vanderpol/scap-ng/discussions/60) |
| [P004](proposals/P004.md) | [VOTE P004] Exact OVAL to native mapping and suffixes | [Vote](https://github.com/vanderpol/scap-ng/discussions/61) |
| [P005](proposals/P005.md) | [VOTE P005] Deprecated source Test exclusion | [Vote](https://github.com/vanderpol/scap-ng/discussions/62) |
| [P006](proposals/P006.md) | [VOTE P006] Named and private embedded Objects | [Vote](https://github.com/vanderpol/scap-ng/discussions/63) |
| [P007](proposals/P007.md) | [VOTE P007] Capability ownership and typed bindings | [Vote](https://github.com/vanderpol/scap-ng/discussions/64) |
| [P008](proposals/P008.md) | [VOTE P008] Colocated filter predicates | [Vote](https://github.com/vanderpol/scap-ng/discussions/65) |
| [P009](proposals/P009.md) | [VOTE P009] Dependency cycles and source order | [Vote](https://github.com/vanderpol/scap-ng/discussions/66) |
| [P010](proposals/P010.md) | [VOTE P010] Variable depth and resource limits | [Vote](https://github.com/vanderpol/scap-ng/discussions/67) |
| [P011](proposals/P011.md) | [VOTE P011] Decisive evaluation permission | [Vote](https://github.com/vanderpol/scap-ng/discussions/68) |
| [P012](proposals/P012.md) | [VOTE P012] Exhaustive evaluation default | [Vote](https://github.com/vanderpol/scap-ng/discussions/69) |
| [P013](proposals/P013.md) | [VOTE P013] Skipped evaluation reporting | [Vote](https://github.com/vanderpol/scap-ng/discussions/70) |
| [P014](proposals/P014.md) | [VOTE P014] Collection reuse requirement | [Vote](https://github.com/vanderpol/scap-ng/discussions/71) |
| [P015](proposals/P015.md) | [VOTE P015] Collection cache identity | [Vote](https://github.com/vanderpol/scap-ng/discussions/72) |
| [P016](proposals/P016.md) | [VOTE P016] Assessment internal applicability | [Vote](https://github.com/vanderpol/scap-ng/discussions/73) |
| [P017](proposals/P017.md) | [VOTE P017] OVAL applicability marker migration | [Vote](https://github.com/vanderpol/scap-ng/discussions/74) |
| [P018](proposals/P018.md) | [VOTE P018] Class versus invocation context | [Vote](https://github.com/vanderpol/scap-ng/discussions/75) |
| [P019](proposals/P019.md) | [VOTE P019] Assessment versioning | [Vote](https://github.com/vanderpol/scap-ng/discussions/76) |
| [P020](proposals/P020.md) | [VOTE P020] Local node versioning | [Vote](https://github.com/vanderpol/scap-ng/discussions/77) |
| [P021](proposals/P021.md) | [VOTE P021] Nullable Assessment title | [Vote](https://github.com/vanderpol/scap-ng/discussions/78) |
| [P022](proposals/P022.md) | [VOTE P022] Generator metadata placement | [Vote](https://github.com/vanderpol/scap-ng/discussions/79) |
| [P023](proposals/P023.md) | [VOTE P023] Informational policy disposition | [Vote](https://github.com/vanderpol/scap-ng/discussions/80) |
| [P024](proposals/P024.md) | [VOTE P024] Thin and full legacy result controls | [Vote](https://github.com/vanderpol/scap-ng/discussions/81) |
| [P025](proposals/P025.md) | [VOTE P025] Result ownership hierarchy | [Vote](https://github.com/vanderpol/scap-ng/discussions/82) |
| [P026](proposals/P026.md) | [VOTE P026] Self describing Rule results | [Vote](https://github.com/vanderpol/scap-ng/discussions/83) |
| [P027](proposals/P027.md) | [VOTE P027] Evidence caps and completeness | [Vote](https://github.com/vanderpol/scap-ng/discussions/84) |
| [P028](proposals/P028.md) | [VOTE P028] ZIP content and logical manifest | [Vote](https://github.com/vanderpol/scap-ng/discussions/85) |
| [P029](proposals/P029.md) | [VOTE P029] Self contained compiled distribution | [Vote](https://github.com/vanderpol/scap-ng/discussions/86) |
| [P030](proposals/P030.md) | [VOTE P030] Result signing container | [Vote](https://github.com/vanderpol/scap-ng/discussions/87) |
| [P031](proposals/P031.md) | [VOTE P031] CMS signature profile direction | [Vote](https://github.com/vanderpol/scap-ng/discussions/88) |
| [P032](proposals/P032.md) | [VOTE P032] Signer trust across platforms | [Vote](https://github.com/vanderpol/scap-ng/discussions/89) |
| [P033](proposals/P033.md) | [VOTE P033] Signing policy versus verification | [Vote](https://github.com/vanderpol/scap-ng/discussions/90) |
| [P034](proposals/P034.md) | [VOTE P034] Deterministic effective weights | [Vote](https://github.com/vanderpol/scap-ng/discussions/91) |
| [P035](proposals/P035.md) | [VOTE P035] Coverage separate from compliance score | [Vote](https://github.com/vanderpol/scap-ng/discussions/92) |
| [P036](proposals/P036.md) | [VOTE P036] Publisher Profiles subtractive only | [Vote](https://github.com/vanderpol/scap-ng/discussions/93) |
| [P037](proposals/P037.md) | [VOTE P037] Tailoring publisher Parameter boundary | [Vote](https://github.com/vanderpol/scap-ng/discussions/94) |
| [P038](proposals/P038.md) | [VOTE P038] Tailoring Rule selections and provenance | [Vote](https://github.com/vanderpol/scap-ng/discussions/95) |
| [P039](proposals/P039.md) | [VOTE P039] Typed Organizational Input | [Vote](https://github.com/vanderpol/scap-ng/discussions/96) |
| [P040](proposals/P040.md) | [VOTE P040] Refine value normalization | [Vote](https://github.com/vanderpol/scap-ng/discussions/97) |
| [P041](proposals/P041.md) | [VOTE P041] Group ownership | [Vote](https://github.com/vanderpol/scap-ng/discussions/98) |
| [P042](proposals/P042.md) | [VOTE P042] Manual procedure ownership | [Vote](https://github.com/vanderpol/scap-ng/discussions/99) |
| [P043](proposals/P043.md) | [VOTE P043] Inline manual authoring shorthand | [Vote](https://github.com/vanderpol/scap-ng/discussions/100) |
| [P044](proposals/P044.md) | [VOTE P044] Manual result and workflow states | [Vote](https://github.com/vanderpol/scap-ng/discussions/101) |
| [P045](proposals/P045.md) | [VOTE P045] Manual comments and evidence | [Vote](https://github.com/vanderpol/scap-ng/discussions/102) |
| [P046](proposals/P046.md) | [VOTE P046] Human inputs versus observed evidence | [Vote](https://github.com/vanderpol/scap-ng/discussions/103) |
| [P047](proposals/P047.md) | [VOTE P047] CPE naming versus executable applicability | [Vote](https://github.com/vanderpol/scap-ng/discussions/104) |
| [P048](proposals/P048.md) | [VOTE P048] CPE matching capability admission | [Vote](https://github.com/vanderpol/scap-ng/discussions/105) |
| [P049](proposals/P049.md) | [VOTE P049] Stable identity and revisions | [Vote](https://github.com/vanderpol/scap-ng/discussions/106) |
| [P050](proposals/P050.md) | [VOTE P050] Publisher extension isolation | [Vote](https://github.com/vanderpol/scap-ng/discussions/107) |
| [P051](proposals/P051.md) | [VOTE P051] Source migration and defects | [Vote](https://github.com/vanderpol/scap-ng/discussions/108) |
| [P052](proposals/P052.md) | [VOTE P052] Independent conformance evidence | [Vote](https://github.com/vanderpol/scap-ng/discussions/109) |
| [P053](proposals/P053.md) | [VOTE P053] Canonical execution representation | [Vote](https://github.com/vanderpol/scap-ng/discussions/110) |
| [P054](proposals/P054.md) | [VOTE P054] Rule centric authoring view | [Vote](https://github.com/vanderpol/scap-ng/discussions/111) |
| [P055](proposals/P055.md) | [VOTE P055] JSONL and alternate result encodings | [Vote](https://github.com/vanderpol/scap-ng/discussions/112) |
| [P056](proposals/P056.md) | [VOTE P056] Retain demonstrated semantics and govern deprecation | [Vote](https://github.com/vanderpol/scap-ng/discussions/113) |
| [P057](proposals/P057.md) | [VOTE P057] Objectless unknown capability | [Vote](https://github.com/vanderpol/scap-ng/discussions/114) |
| [P058](proposals/P058.md) | [VOTE P058] General conditional authoring deferral | [Vote](https://github.com/vanderpol/scap-ng/discussions/115) |


## Voting governance

Eligibility, quorum, voting duration, abstention/conflict handling, and official disposition still require Board agreement before Discussion reactions are binding. The current working design may therefore be newer than an earlier proposal's background text; the proposal's yes/no question remains the historical record of what was asked.
