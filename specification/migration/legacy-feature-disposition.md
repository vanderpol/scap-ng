# Legacy Feature Disposition Ledger

**Status:** pre-alpha standards decision record

## Purpose

SCAP-NG intentionally simplifies some SCAP 1.4 / XCCDF / OVAL constructs. No
legacy construct SHALL disappear from the design history without an explicit
disposition record.

This ledger exists so that:

- reviewers can see exactly what was retained, normalized, replaced, deferred,
  or proposed for removal;
- migration tooling can preserve source semantics/provenance even when native
  authoring no longer exposes the original construct;
- standards bodies can revisit a simplification without reconstructing history
  from commits and issue threads;
- a removed feature can be restored deliberately if interoperability evidence
  or implementer feedback justifies it.

A disposition marked **Board decision pending** is not a finalized removal.

## Compatibility preservation rule

A SCAP 1.4 capability or semantic that is exercised by current real-world
content or by the SCAP 1.4 validation/conformance corpus SHALL be preserved in
SCAP-NG unless there is a compelling, explicitly documented reason to remove or
replace it.

Rarity, implementation inconvenience, or apparent lack of popularity are not by
themselves sufficient reasons for removal. When a used capability is normalized,
replaced, blocked, deferred, or dropped, this ledger SHALL identify the concrete
evidence, migration behavior, rationale, and restoration criteria.


## Disposition vocabulary

- **retain** — native NG keeps the construct or equivalent semantic primitive.
- **normalize** — legacy syntax/mechanism is removed from native runtime, but
  its effective semantics are deterministically compiled into retained NG
  constructs.
- **replace** — legacy construct is split or replaced by clearer native
  concepts that preserve the required semantics.
- **provenance-only** — the construct does not affect native execution but is
  retained in migration/result provenance where needed.
- **block** — source construct cannot currently be migrated losslessly and
  fails/quarantines rather than being guessed.
- **Board decision pending** — current project preference exists, but standards
  governance must decide retain/revise/drop.
- **drop** — construct has no retained native semantic role. A final drop SHALL
  include rationale and restoration criteria.

## Restoration rule

For every **normalize**, **replace**, **block**, **Board decision pending**, or
**drop** entry, maintain enough source mapping and rationale to answer:

1. What exact legacy behavior did the construct provide?
2. Where did that behavior move in NG, if anywhere?
3. What information is preserved during migration?
4. What interoperability/complexity problem motivated the change?
5. What evidence would justify restoring a native analogue?
6. What schemas/specification/runtime components would need to change if it
   were restored?

## Current dispositions

| Legacy construct | Current NG disposition | Effective semantic handling | Restoration / review note |
| --- | --- | --- | --- |
| XCCDF Rule `role` | **retain working policy control; replacement deferred** | Current Rule source/schema retains role; technical Assessment truth stays independent from scoring/reporting/non-execution. | Owner Oct 1 decision retains the control until an adequate replacement is agreed. Do not remove it based on earlier replacement proposals. |
| XCCDF `role=unscored` caused by missing organization-specific policy value | **replace** | Ordinary compliance Assessment + explicit Organizational Input; missing input => `not_evaluated` with reason. | Do not restore informational coercion merely for legacy convenience. |
| XCCDF genuinely reporting-only `unscored` | **retain semantics / replace syntax** | Context-specific Rule reporting/scoring disposition, or intrinsic informational Assessment if Board adopts that class. Informational characterization is layered over the six-state technical Assessment result; it is not a seventh OVAL-style truth value. | Board review of standardized `information` Assessment class remains open. Restore a role-like shorthand only if the separated model proves materially worse for authors/implementers. |
| XCCDF `role=unchecked` | **replace** | Explicit policy-driven non-execution; canonical result records `not_evaluated` with stable reason. | Native shorthand could be reconsidered if Rule authoring becomes awkward. |
| OVAL/XCCDF XML Digital Signature on imported source | **normalize / provenance-only** | Verify original representation before conversion; preserve verification facts; sign NG package independently. | Legacy XML signature cannot cryptographically authenticate converted representation. |
| XCCDF ordered `check-content-ref` fallback + embedded `check-content` | **normalize** | Resolve first successful ref in source order at build time; embedded content only after refs fail; record provenance. | Restore runtime fallback only if a concrete deployment requires mutable late binding and reproducibility/trust issues are solved. |
| XCCDF `cluster-id` | **normalize** | Expand Profile operation to explicit compatible members in source order before normal Profile resolution. | Restore only if native cluster authoring provides material value beyond ordinary groups/explicit operations. |
| XCCDF `hidden` | **provenance/presentation-only** | Does not alter Assessment execution; optional migration/presentation metadata may retain it. | A future document-generation profile may standardize a native presentation analogue. |
| XCCDF Rule/Value/Profile `extends` | **normalize** | Resolve XCCDF property-specific inheritance during migration; emit complete effective native object. | Native inheritance could be reconsidered independently, but should not be reintroduced solely for compatibility. |
| XCCDF `abstract` | **normalize** | Template marker used during inheritance resolution; effective abstract items are not independently executable native objects. | Restore native templates only if authoring reuse warrants a clean NG-native mechanism. |
| Deprecated XCCDF Group extension | **block by default** | Do not invent generated descendant IDs because XCCDF defines no interoperable generation algorithm. | Can be revisited if a deterministic compatibility algorithm is standardized. |
| OVAL entity `mask` | **drop from generic native assessment surface** | Pinned corpus census found no source-explicit usage; sensitive evidence should use explicit result/evidence redaction instead. Migration diagnoses unexpected explicit legacy usage. | Restore only with concrete source corpus/interoperability evidence showing comparison-level mask semantics are required. |
| Deprecated OVAL UNIX `FileBehaviors` enum values (`recurse=none/files/files and directories`; `recurse_direction=up`) | **drop from native authoring / migration blocker** | Pinned OVAL 5.12.3 marks these values deprecated. Corpus audit run 36935791611 scanned 212 files and 878 source-explicit `unix.file` behavior attributes with **0 deprecated-value occurrences**. Generated native `unix.file` schema excludes them but retains deprecation metadata. Legacy source that explicitly uses one SHALL be diagnosed/quarantined rather than silently rewritten. | Restore a value only if an external corpus/interoperability requirement demonstrates active semantics that cannot be represented by supported behavior values; if restored, add explicit evaluator/conversion tests and document why the upstream deprecation is insufficient. |
| OVAL Results `reported` directives | **replace** | Native `reported_elements` is an explicit author-visible evidence projection and never changes collection/evaluation truth. | Restore a different directive model only if interoperability evidence shows `reported_elements` cannot express the required projection. |
| OVAL Results `thin` / `full` | **drop as normative result profiles** | 0.3 uses one canonical result contract with bounded evidence/completeness and optional deterministic projections/exports. | Restore normative profiles only if one canonical contract proves unable to support interoperable constrained deployments. |
| OVAL Results `include_source_definitions` | **normalize** | Package/result logical references provide source identity without changing the canonical result shape. | Restore embedded source definitions only if a concrete offline interoperability requirement cannot be met by manifest-bound references. |
| OVAL Results `variable_instance` authored identity | **replace** | Native Assessment invocation identity captures effective binding/target context; legacy integer may remain provenance. | Restore explicit integer only if an external interoperability contract requires it. |
| OVAL `extend_definition` | **retain semantics / replace serialization** | Static Assessment-result dependency used as an `evaluate` leaf; preserve result-domain semantics/provenance. | No reason to restore XML-specific construct name. |
| OVAL filter non-Boolean State behavior | **clarify** | Native rule: non-Boolean filter State outcome => collection/evaluation error. | Revisit only if stronger normative evidence contradicts this; MITRE ovaldi currently supports the chosen legacy sanity-check direction. |
| Deprecated OVAL Definition instances | **drop native execution feature / provenance diagnostic** | Detect, report, and quarantine reachable deprecated Definitions rather than inventing a deprecated-Assessment mode. | Revisit only with real published content requiring interoperable execution semantics. |

## Maintenance requirement

Whenever a future change removes, normalizes, replaces, blocks, or defers a
legacy construct, the same change set SHOULD update this ledger.

Issue/Board discussion links and corpus/conformance evidence SHOULD be added as
the design stabilizes so the ledger can become part of the formal compatibility
crosswalk.
