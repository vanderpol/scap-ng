# ESX adoption hold and upstream guidance questions — 2026-10-03

Owner direction at 18:48 America/New_York: consider waiting for guidance from the
person who submitted the ESX work to OVAL. **Pause further ESX adoption.**
Base: main `9c729604509e80c7e66bc663a668ab9152fd8ce9`.

Four new ESX contracts are already merged through #140/#141. This branch preserves
five additional host-wide contracts as **unadopted implementation drafts**:
acceptancelevel, lockdown, ntpserver, coredump and authentication. Do not count
these as merged coverage, finalized semantics or approved upstream interpretation.
No 0.1.0 mapping/schema changed. No ESX collector or OVAL 6.0 importer was added.

The draft uses explicit empty selection on named host-wide Objects and existing
single-operand Set filters. That native modeling decision is not an upstream
OVAL requirement. It needs review alongside the real acquisition contract before
promotion. The draft excludes the authentication Item's empty category placeholder;
that exclusion is provisional, not an accepted source correction.

## Questions for the original ESX implementer

1. Can you provide small ESX definition/content examples with corresponding
   collected Items and evaluator results, including host-wide checks and repeated
   NTP-server/lockdown-user observations? Include host/version/privilege context,
   expected outcomes, licensing and sanitized identifiers.
2. What exactly is the target/collection scope of selectorless host Objects:
   one explicitly assessed host, multiple host Items, or a management-plane scope?
   How are target identity, filter execution, empty populations, denied access and
   incomplete collection represented in actual implementations?
3. The source lockdown State/Item supports disabled/normal/strict, while its
   illustrative acquisition uses Boolean adminDisabled. How does the collector
   actually obtain the three-valued mode and repeated lockdown exception users?
4. EntityItemDomainMembershipStatusType permits an empty string documented as a
   Variable-reference placeholder, although collected Items do not reference
   Variables. Is this a copied schema artifact, or an intentional observed value?
   How should an unjoined host, unavailable directory service and broken trust be
   distinguished? Is Unknown an observed category in each of these contexts?
5. host_module State declares version semantics while its Item declares string.
   Which datatype/comparison interpretation is implemented, and are there result
   examples that disambiguate it without coercion or changed comparison behavior?
6. Do repeated NTP-server and lockdown-user values live in one host Item or
   multiple Items, and how are duplicate, empty and partially observed lists handled?
7. Which schema/version differences from the original unofficial CIS/Arctic Wolf
   implementation affect these examples? Please distinguish intended semantics
   from proposal-era examples or documentation defects.

## Source/contact attribution

[Investigation](esx-source-evidence-2026-10-03.md) links primary records.
OVAL PR #215 was submitted by vanderpol to adapt the pre-existing extension;
that is not proof of originating collector authorship. Discussion #165 documents
Arctic Wolf use through maxullman. Discussion #207 includes solind's endorsement
and the jOVAL schema source. These are leads for the owner, not verified recipient
resolution or permission to contact anyone. No external message has been sent.

## Local evidence and limits

- New focused host-wide suite: 8 tests pass (source fields/cardinality/categories,
  version isolation, explicit/invalid/unused Objects, filtered Set graph,
  Items/status/redaction, equality expectations, reporting/provenance and real
  unsigned bundle compilation/verification).
- Source validator: 9 standalone ESX Assessments structurally pass.
- Current authoring guard: 9 documents pass; not semantic equivalence.
- Documentation checker: 14 documents, 11 references, 12 source pins; zero errors.
- Existing ESX suites were also rerun; consult the branch validation log/result
  before claiming additional totals. No full CI or live ESX execution was run.

Passing local checks does not resolve the questions above. Hold this branch;
resume ESX adoption only after owner/upstream guidance. Keep 5.12.3 behavior as
baseline and OVAL 6.0 review limited to newly added tests. #128/#131 remain open.

Provenance: Inherited licensed XSD sources; Adapted provisional mapping metadata;
Common native draft syntax/fixtures; Evidence/Audit investigation, questions and
local validation. No upstream files were repaired and no source ambiguity is
claimed resolved.
