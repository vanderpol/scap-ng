# Candidate OVAL 5.12.3 schema and semantic-validation issues

**Scope:** original upstream `OVAL-Community/OVAL@v5.12.3`.  
**Status:** working defect/errata register; **no issue below has yet been submitted upstream**. The distinction between confirmed validation gaps and requests for clarification matters.  
**Policy:** SCAP-NG conversion faithfully preserves the original OVAL semantics. Changing upstream OVAL is a separate, reviewed upstream-maintenance activity. Do not automatically rewrite existing content or modify upstream XSDs.

## Complete upstream schema inventory result

The full automated scan of the pinned upstream `OVAL-Community/OVAL@v5.12.3`
schemas succeeded in GitHub Actions run
[36709423605](https://github.com/vanderpol/scap-ng/actions/runs/36709423605).

| Category | Inventory count | Interpretation |
| --- | ---: | --- |
| Schema files parsed | 54 | No XML parsing failures |
| Explicit schema defaults | 280 | Not necessarily 280 distinct behaviors |
| Type extension/restriction declarations | 1,642 | Must resolve inheritance for effective contracts |
| Optional element declarations | 4,362 | Optionality alone does not establish omission semantics |
| Semantic documentation passages | 1,357 | Search index requiring contextual interpretation |
| Default/omission documentation candidates | 296 | **Not** 296 proven defects |
| Embedded Schematron assertions/reports | 1,182 | Must integrate with semantic-validator analysis |

Machine-readable inventories and original source line mappings were uploaded as
the `upstream-oval-5.12.3-xsd-audit` artifact of that run. The scanner is
`tools/scap_ng_roundtrip_v003/audit_oval_xsd_defaults.py`.

**Next triage order:** (1) existence and quantifier semantics;
(2) prose-only defaults such as `var_check`; (3) Object behavior
inheritance and omitted parent semantics; (4) datatype/operation defaults;
(5) existence/error status propagation; (6) publisher-versus-standard
Schematron behavior.

## Triage definitions

- **Confirmed validation gap:** concrete published source or synthetic fixture passes the current validation set while containing an independently established inconsistency.
- **Potential schema/documentation flaw:** ambiguity or divergence between XSD declaration, annotation and processor expectations; requires formal interpretation/fixtures.
- **Not a flaw:** legitimate inherited/implicit behavior that a converter simply failed to recognize.
- **Publisher extension:** differences from the authoritative upstream schema attributable to NIWC/SCC or another publisher. Do not label upstream schema defective.

## OV-XSD-001 — Cross-family Test/Object/State reference compatibility

**Classification:** Confirmed validation gap; proposed enhancement pending precise normative rule.  
**Source:** nginx STIG SV-278400 / OVAL definition `oval:navy.navwar.niwcatlantic.scc.nginx:def:278400`, published NIWC corpus.  
**Observed:** source Test is `unix.file_test` but referenced Object and State are `independent.shellcommand_object` and `independent.shellcommand_state`. Existing schema-validation processing did not reject this combination. The independent SCAP-NG semantic comparator first identified retagging in reverse conversion; preserving each family restored source fidelity, **not source correctness**. The user confirmed this as an upstream content defect and will report it to the content author.

**Candidate upstream change:** extend embedded Schematron or create a reference-resolution validator asserting that each Test references compatible Object and State element types, with a well-defined exception policy only if the language permits cross-family references. XSD keyrefs verify identity/reference existence but not necessarily substitutable *compatible* element identity.

**Regression:** negative fixture modeled on SV-278400, valid file/object/state pairs, and nested valid Object components whose collector family is independent of a containing Test. Do not falsely reject cross-family *dependencies* that are otherwise legal.

**Open:** document the normative exact rule per Test type/substitution group before proposing a specific XPath or upstream PR.

## OV-XSD-002 — Implicit `var_check=all` is prose-only, not XSD default

**Classification:** Potential documentation/schema usability gap; **not** an established OVAL semantic defect.  
**Source:** upstream `oval-definitions-schema.xsd`, `EntityAttributeGroup`, `var_check` annotation (near lines 1396–1405 in tag v5.12.3).  
**Observed:** `var_check` is optional without an XSD `default` attribute; normative prose says it is treated as `all` when `var_ref` is supplied and `var_check` omitted. Tools that only inspect XSD default declarations will omit the effective behavior.

**Candidate upstream improvement:** clarify/document why no XSD default is used, add an explicit effective-default rule to accessible machine-readable behavioral metadata if possible, or adjust annotations. A blanket XSD `default="all"` may not be semantically equivalent without `var_ref`; do **not** propose it blindly.

**Regression:** missing versus explicit `all` with `var_ref`; absent `var_ref`; multi-valued variables; each CheckEnumeration choice.

## OV-XSD-003 — State-level entity existence needs independent, explicit test coverage

**Classification:** Specification/test coverage concern; **not** evidence of a defective schema.  
**Source:** `oval-definitions-schema.xsd` `EntityStateSimpleBaseType`/`EntityStateComplexBaseType` (near lines 1605–1630), `oval-common-schema.xsd` `ExistenceEnumeration` evaluation tables.
**Observed:** State entities inherit `check_existence="at_least_one_exists"` and `entity_check="all"`; this is distinct from Test-level existence. A single flattened existence checker would mis-evaluate repeated entities, missing fields and item statuses. Attribute inheritance hides this from readers of leaf collector types.

**Candidate upstream action:** add concrete examples/test vectors for missing/repeated record and scalar fields, EX/DNE/ER/NC item entities, plus interactions with `var_check`. Confirm which cases are expressible and whether every existing annotation is consistent before filing errata.

## OV-XSD-004 — Omission versus empty `behaviors` element

**Classification:** Potential specification ambiguity, not confirmed defect.  
**Source:** platform-family behavior types and inheritance under OVAL 5.12.3 XSD; see `oval-object-behaviors-audit.md`.
**Observed:** attributes may have schema defaults, but absence of the optional parent `behaviors` element is not necessarily identical to an empty element. For Unix file traversal, `max_depth=-1` does *not* enable recursion if `recurse_direction=none`.

**Candidate upstream action:** type-by-type clarification for absent, empty and partially populated behaviors, with expected collection/status consequences; avoid altering declarations until compatibility is verified.

## OV-XSD-005 — External-variable restrictions and multi-value inputs

**Classification:** Audit candidate, no confirmed flaw.  
**Source:** `oval-definitions-schema.xsd` external variable, `possible_value`, `possible_restriction`, `restriction` declarations and prose (near lines 553–600).
**Observed:** `possible_restriction` defaults to AND internally while possible alternatives are OR-combined according to documentation. A generic schema walker might overlook the two layers or misapply constraints to multiple input values.

**Candidate upstream action:** test vectors for optional restrictions, AND/OR, disallowed values, invalid datatype, and multi-value input; clarify error semantics in prose if needed.

## OV-XSD-006 — Upstream schema identity and NIWC/SCC augmentation

**Classification:** Publisher packaging/provenance issue; **not an upstream OVAL bug**.
**Source:** SCC-augmented bundled `independent-definitions-schema.xsd` contains `sqlext_test`, `sqlext_object`, `sqlext_state`; upstream v5.12.3 lacks them.
**Disposition:** `sqlext` is explicitly out of scope for SCAP-NG standard OVAL. Do not file this as a defect against upstream XSD. Future user-maintained SQL source may migrate to standard `sql512`. Generic converters should inspect pinned upstream schema vocabulary and independently classify publisher extensions.

## OV-XSD-007 — Nested-set same-type assertion covers only depths 1 through 3

**Classification:** Confirmed coverage gap in the specific embedded pattern,
not a general OVAL variable/expression depth limit.
**Source:** pinned OVAL 5.12.3 `oval-definitions-schema.xsd`, `set` annotation,
Schematron pattern `oval-def_setobjref`.

The set grammar is recursive, but this pattern spells out three XPath contexts
for Object references at depths 1, 2 and 3. It does not cover depth 4 or deeper.
The regression `test_deep_set_schematron_coverage_gap` constructs a
`unix.file_object` referencing `unix.fileextendedattribute_object` through
nested sets. The source is XSD-valid; the isolated upstream pattern detects the
mismatch at depths 1 and 3, but accepts it at depths 4 and 32. Our independent
source audit detects it at all four depths with qualified type identities.
This is a claim about this pattern's coverage, not all possible validator tools.

**Tracking:** [issue #37](https://github.com/vanderpol/scap-ng/issues/37), with
#8 and #11. No upstream schema was changed and no upstream issue was submitted.
The source audit reports defects without changing Object types.

**Candidate upstream improvement:** derive the owner from ancestors and match
all descendant set references rather than enumerating nesting levels. Review
namespace-aware type comparison and portability of the replacement XPath before
proposing an upstream patch.

**Evidence:** `tools/test_variable_filter_dependencies.py`; valid/mismatching/
missing references at depths 1, 3, 4 and 32; different namespaces with identical
local names. Variable chains and function nesting at depth 32 are separately
XSD/round-trip evidence, not scanner runtime proof.

## Rules for filing upstream tickets

For any proposed upstream correction, record: exact original source tag/commit, file and line/element, reproducer valid under current XSD/Schematron, expected versus actual semantic result, impact, minimum fix, backward-compatibility assessment, and a regression test. Avoid proposing an XSD change on intuition alone: interpret annotations, constraint inheritance, formal OVAL documentation and any governing OVAL Board decision first.

This ledger is an upstream-defect *candidate register* and does not assert all listed items are bugs. Maintain it alongside the complete machine-readable XSD inventory and SCAP-NG conformance research.


## OV-XSD-008 — `wuaupdatesearcher_state` omits collected `source_path`

**Classification:** Confirmed schema-language surface mismatch.  
**Source:** OVAL 5.12.3 Windows definitions/system-characteristics schemas.

**Observed:** `wuaupdatesearcher_item` includes scalar `source_path`, documented as the Windows Update Server URL or offline CAB filepath used as the update source. `wuaupdatesearcher_state` has no corresponding `source_path` entity. The Item field is not deprecated.

**Impact:** OVAL content can collect `source_path` but cannot test/filter it through a State, including Set-filter use. This breaks the otherwise expected scalar State/Item symmetry.

**SCAP-NG treatment:** native `windows.wuaupdatesearcher` includes `source_path` in the canonical State/Item model. Migration retains provenance that OVAL 5.12.3 could not express a State predicate for this field.

**Candidate OVAL 5.12.4 change:** add `source_path` to `wuaupdatesearcher_state` with the same string semantics as the Item field, subject to OVAL Board review and backward-compatibility confirmation.

**Regression:** require State/Item parity for `source_path` in NG and retain a source fixture proving its absence from the 5.12.3 State schema.
