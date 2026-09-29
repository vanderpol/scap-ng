# SCAP 1.4 ↔ SCAP-NG Semantic Difference Audit

**Iteration:** 003  
**Status:** active conformance gate  
**Authority:** SCAP 1.4 / XCCDF 1.2 / OVAL 5.12.3 XSD + Schematron are authoritative for source semantics.

## Purpose

This audit accounts for every behaviorally relevant SCAP 1.4 construct encountered
or explicitly tested during iteration 003.

Each construct is classified as one of:

- **Preserved exactly** — same semantic role in NG.
- **Preserved, represented differently** — same behavior with different native structure.
- **Intentional NG normalization** — legacy structure removed while preserving behavior.
- **Intentional NG addition** — native capability not required by SCAP 1.4.
- **Rejected/deprecated** — source construct intentionally not accepted in native NG.
- **Unresolved / Board review** — semantics or native representation still requires decision.

Anything behaviorally relevant that cannot be placed in one of these classes is a
conversion gap.

## Current empirical evidence

Pinned RHEL 9 corpus:

- 445 XCCDF Rules
- 11 XCCDF Profiles
- 422 split OVAL documents
- 14 OVAL Test/Object families
- 13 OVAL State families
- 67 OVAL Variables
- UNION and COMPLEMENT Sets
- Filters
- object_component and variable_component chains
- var_check values: all, at least one, only one
- multiple entity_check values
- arithmetic, concat, count, split, unique
- applicability definitions and shared dependencies

Current gates:

- OVAL -> NG -> OVAL semantic round trip: **422 / 422 PASS**
- NG benchmark fidelity audit against source XCCDF: **0 issues**
- Regenerated XCCDF 1.2: schema valid
- XCCDF policy semantic comparison: **0 issues across 445 Rules / 11 Profiles**
- deterministic RHEL 9 NG regeneration: PASS

## OVAL / assessment layer

| SCAP 1.4 / OVAL construct | NG representation | Classification | Evidence / note | Board review |
|---|---|---|---|---|
| Definition criteria tree | Assessment Boolean/result tree | Preserved, represented differently | Full RHEL 9 corpus round trips | No |
| `criterion` → Test | Check reference in Assessment tree | Preserved exactly | Round-trip comparator | No |
| `extend_definition` | Recursively dereferenced result subtree | Intentional NG normalization | 382 initial RHEL 9 mismatches reduced to 0 after result-semantic dereference | **Yes** |
| Definition identity/metadata used only by `extend_definition` | Conversion provenance | Intentional NG normalization | Not executable semantics in NG | **Yes** |
| Criteria `operator` | Native logical operator | Preserved exactly | AND/OR tested | No |
| Criteria/criterion `negate` | Native negation on node/edge | Preserved exactly | Dedicated stress fixture | No |
| `applicability_check` | Applicability/result context | Preserved, represented differently | Dedicated fixture; broader native semantics still evolving | **Yes** |
| OVAL Test | Check | Preserved exactly | 14 RHEL 9 families exercised | No |
| `check` | Check aggregation semantics | Preserved exactly | Schema-derived truth semantics | No |
| `check_existence` | Existence aggregation semantics | Preserved exactly | Multiple values exercised | No |
| `state_operator` | State aggregation operator | Preserved exactly | AND/OR observed | No |
| OVAL Object | Collection | Preserved, represented differently | 422-file corpus | **Yes: terminology** |
| Shared Object identity | Named Collection | Preserved exactly for converted content | Converter SHALL preserve source boundaries | No |
| One-use Object in native NG | Inline local Collection | Intentional NG addition | Native authoring convenience; not used to rewrite converted source structure | **Yes** |
| Object Set | Collection Set | Preserved exactly | UNION and COMPLEMENT in RHEL 9 | No |
| Recursive Set | Recursive Collection Set | Preserved exactly | Dedicated fixture | No |
| Filter referencing State | Filter semantics | Preserved exactly in converted content | RHEL 9 + dedicated fixtures | No |
| Inline native Filter predicate | Colocated Collection filter | Intentional NG addition | One-use colocation principle | **Yes** |
| OVAL State | State/predicate semantics | Preserved exactly | 13 RHEL 9 families | No |
| `entity_check` | Entity aggregation semantics | Preserved exactly | Dedicated many-to-many fixture + corpus | No |
| `var_check` | Variable-value aggregation semantics | Preserved exactly | all / at least one / only one observed | No |
| State record fields | Typed field predicates | Preserved exactly | Dedicated record fixture | No |
| `mask` | Masked state/entity behavior | Preserved exactly | Dedicated fixture | No |
| `xsi:nil` object/state entity | Explicit nil entity | Preserved exactly | Dedicated fixture + RHEL 9 file objects | No |
| Object `behaviors` | Collection behaviors | Preserved exactly | Multiple RHEL 9 behavior values | No |
| constant_variable | Variable | Preserved exactly | 26 in RHEL 9 | No |
| local_variable | Variable with expression | Preserved exactly | 41 in RHEL 9 | No |
| external_variable | External/input Variable | Preserved exactly at OVAL semantics layer | Dedicated fixture includes possible_value/restriction | Integration with policy input model still **Yes** |
| variable_component | Variable reference expression | Preserved exactly | Deep chains in corpus | No |
| object_component | Collection-derived Variable expression | Preserved exactly | Multiple item fields in corpus | No |
| object_component `record_field` | Collection field extraction | Preserved exactly | Dedicated fixture | No |
| literal_component datatype | Typed literal | Preserved exactly | Dedicated fixture | No |
| concat | Variable expression | Preserved exactly | 15 in RHEL 9 | No |
| arithmetic | Variable expression | Preserved exactly | RHEL 9 + Cartesian fixture | No |
| count | Variable expression | Preserved exactly | RHEL 9 | No |
| split | Variable expression | Preserved exactly | RHEL 9 | No |
| unique | Variable expression | Preserved exactly | RHEL 9 | No |
| begin/end/escape_regex/substring/time_difference/regex_capture/merge/glob_to_regex | Variable expressions | Preserved exactly in targeted fixtures | Not all exercised by RHEL 9 production corpus | No |
| Multi-valued function Cartesian product | Variable evaluation semantics | Preserved exactly | Dedicated Cartesian fixture | No |
| Source-file declaration order | No semantic meaning | Preserved as reference-driven semantics | Explicit design rule | No |
| Direct Variable self-reference | Invalid | Preserved restriction | Explicit OVAL documentation | No |
| Indirect dependency cycles | Proposed validation error | Unresolved / possibly stricter NG rule | Legacy schema does not clearly prohibit every indirect cycle | **Yes** |
| Deprecated OVAL Tests | Conversion error / native rejection | Rejected/deprecated | Project requirement | **Yes / compatibility** |
| OVAL System Characteristics bulk persistence | Compact bounded evidence/result data | Intentional NG divergence | NG does not copy the full SC payload into results | **Yes** |
| Observation-wide snapshot semantics | None | Intentional clarification | Each operation observes target when executed | **Yes / guidance** |
| Scanner Collection caching/dedup | Implementation choice | Not normative content semantics | Optimization cannot change observable results | No |
| Decisive short-circuit evaluation | Runtime policy consistent with truth tables | Intentional NG execution option | Exhaustive vs decisive | **Yes** |

## XCCDF / benchmark and Rule layer

| XCCDF construct | NG representation | Classification | Evidence / note | Board/spec review |
|---|---|---|---|---|
| Benchmark title/description/language/status/version | Benchmark metadata | Preserved exactly | RHEL 9 fidelity audit | No |
| Benchmark Dublin Core metadata | Benchmark metadata | Preserved exactly | RHEL 9 fidelity audit | No |
| notice/front-matter/rear-matter/plain-text | Benchmark publication metadata | Preserved, represented differently | RHEL 9 fidelity audit | No |
| Benchmark references | Benchmark references | Preserved exactly semantically | RHEL 9 fidelity audit | No |
| Rule title/severity/weight/role | Rule fields | Preserved exactly | RHEL 9 fidelity audit | `role` result-semantics question deferred |
| STIG identifiers / CCI | Rule identifiers | Preserved exactly | RHEL 9 fidelity audit | No |
| Rule discussion | Rule discussion | Preserved, represented differently | Parsed from DISA description wrapper | No |
| DISA description extension fields | Rule `extensions.disa_stig` | Preserved, represented differently | Includes documentable and related fields | No |
| Rule reference metadata | Rule references | Preserved exactly semantically | 445 DPMS refs verified | No |
| `fixtext` remediation | `rule.remediation.guidance` | Preserved exactly semantically | 445 verified | No |
| empty XCCDF `fix` identity linked by `fixref` | Provenance / exporter reconstruction candidate | Unresolved structural fidelity | Content carries no executable fix body in RHEL 9, but identity/link is source structure | Review |
| XCCDF inline manual `check-content` | Manual Assessment `procedure` | Preserved, represented differently | 445 manual procedures verified | No |
| XCCDF check selector | Rule named check selector | Preserved exactly | default / automated / manual | No |
| Default check | `default_check` / default selector | Preserved exactly | Fidelity audit | No |
| XCCDF Group used as one-Rule wrapper | Native semantic grouping may replace it | Intentional NG normalization | All 445 RHEL 9 source Groups verified semantically inert | **Yes / document** |
| Non-inert Group semantics | Must be preserved | Preserved requirement; not exercised by RHEL 9 | Audit fails if source group has semantic attributes | **Yes: native placement** |
| Profile effective selection | NG Profile disabled/enabled rule result | Preserved exactly | 11 profiles verified | No |
| Verbose explicit `select selected=true` list | Effective profile delta | Intentional NG normalization | Thousands of source entries collapse to effective selection | No |
| XCCDF Value | NG Parameter/input model | Not exercised by current RHEL 9 source | Requires separate corpus/stress coverage | **Yes** |
| refine-value / refine-rule | Tailoring/profile semantics | Pending detailed audit | Deferred earlier | **Yes** |
| Benchmark direct CPE target | Native platform applicability conditions | Preserved, represented differently | RHEL/Rocky/Alma conditions verified | **Yes: CPE is not native authoring concept** |
| CPE platform-specification | Native applicability Assessments/catalog | Intentional NG normalization | 17 native applicability conditions in RHEL 9 | **Yes** |
| Rule `platform` | Rule applicability conditions | Preserved, represented differently | 44 RHEL 9 Rules verified | No |
| `requires` / `conflicts` | Rule dependency metadata | Preserved exactly | RHEL 9 has none; generic audit exists | No |
| source Group hierarchy used only for presentation | Native grouping | Intentional authoring divergence | NG groups by meaningful domain instead | **Yes / authoring guidance** |

## Result model

| SCAP 1.4 construct | NG direction | Classification | Status |
|---|---|---|---|
| XCCDF TestResult + ARF embedding | Compact NG result record | Intentional NG divergence | Design ongoing |
| Complete source XCCDF/OVAL copied into result | Stable IDs + version/context references | Intentional NG divergence | Design ongoing |
| System Characteristics full collected item set | Bounded evidence + counts/summary | Intentional NG divergence | Evidence capping required |
| Failure explanation implicit in raw items | Human-readable root-cause summary | Intentional NG addition | Required |
| Tailoring/input provenance | Explicit result provenance | Intentional NG addition/strengthening | Required |
| Observation timing | Per operation/evidence timing where useful | Intentional NG addition | No global snapshot guarantee |

## Current known structural differences in RHEL 9 XML round trip

The canonical XCCDF XML diff is intentionally large even though semantic audits
pass. Known causes include:

1. benchmark publication metadata not all emitted by the conformance-only XCCDF
   exporter even though it is present in NG;
2. CPE platform-specification replaced by native applicability;
3. source one-Rule Groups replaced by native semantic grouping;
4. verbose Profile true selections collapsed to effective deltas;
5. Rule reference wrappers not emitted by the surrogate exporter even though
   reference semantics are present in NG;
6. manual inline check-content moved to Manual Assessments;
7. empty XCCDF `fix` wrapper IDs/fixref links not currently reconstructed;
8. regenerated IDs/URIs differ by design.

These differences are diagnostics and SHALL NOT be used to waive semantic loss.
Each source semantic field is audited independently against NG.

## Exit criteria for iteration-003 lossless conversion model

Before declaring the split Rule/Assessment conversion model mature:

1. RHEL 9 full OVAL round trip SHALL remain 100% passing.
2. RHEL 9 benchmark fidelity audit SHALL report zero unclassified issues.
3. Every source-side XCCDF/OVAL construct in supported corpora SHALL appear in
   this audit as preserved, intentionally changed, rejected/deprecated, or
   explicitly deferred.
4. Additional corpora SHALL be run to cover constructs absent from RHEL 9,
   beginning with Oracle Linux 9 and then Windows 11 / Windows Server 2025.
5. XSD/Schematron surface not exercised by those corpora SHALL receive targeted
   stress fixtures.
6. Production converter refactoring SHALL follow this validated semantic model,
   not the earlier prototype serialization model.
