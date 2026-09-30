# OVAL defaults / behaviors audit — working ledger

**Status:** in progress; not a declaration of full-schema coverage.
**Baseline inspected:** `tools/scap_ng_roundtrip_v003/ng_to_oval.py` on 2026-09-30.
**Scope:** lossless OVAL 5.12.3 → native NG → OVAL semantics, not byte-equivalent XML.

## Confirmed implementation observations

| Area | Observation | Action | Verification |
|---|---|---|---|
| Test `check` | Reverse generator requires an explicit `check` field. | Retain fail-closed behavior; forward conversion must resolve XSD omissions. | Regression to add against pinned XSD |
| Test `check_existence` | Reverse generator requires explicit `check_existence`. | Retain; never guess a missing original default during reverse conversion. | New regression checks missing input fails |
| Test `state_operator` | Previously ignored a supplied field. | Emit supplied value in reverse OVAL. | Regression committed; execution pending |
| State `operator` | Previously ignored a supplied field. | Emit supplied value in reverse OVAL. | Regression committed; execution pending |
| State entity `entity_check` | Previously ignored a supplied field. | Emit supplied value; validate on actual supported state entity type. | Regression committed; execution/schema validation pending |
| Variable-valued entity `var_check` | Explicit input emitted only when `variable` is supplied; omissions are **not normalized**. | Audit forward converter and source defaults for object-vs-state entity declarations. | Pending |
| Object `behaviors` | Explicit behavior attributes are serialized, but omission semantics are not resolved here. | Inventory behavior types, attributes, inheritance, and defaults by platform/test type. | Pending |
| Set filters | Generator supplies `exclude` if action omitted from NG fixture. | Verify against pinned source schema; avoid unjustified default in lossless NG. | Pending |
| Criteria operator | Generator supplies `AND` if NG root omits operator. | Verify source behavior and change to explicit native input if necessary. | Pending |
| State/entity absent vs empty | No general representation-level equivalence checker is established here. | Add separate fixture families for absent item, empty item, missing state field, and multiple values. | Pending |

## Interpretation rules

An XSD-declared default, prose-described behavior, collector implementation convention, and NG native default are **different classes of evidence**; never merge them without verification.

For each relevant construct, capture:
1. XSD qualified declaration and inherited type/attribute-group chain;
2. literal declared `default` or `fixed`, if any;
3. required/optional status, bounds, enumerations, and relevant prose;
4. effective original evaluation for omitted vs explicitly specified input;
5. whether the source case is a known specification defect or implementation discrepancy;
6. lossless NG representation and regression outcome;
7. provenance of any intentional NG behavioral divergence.

**Important:** The inventory utility is deliberately structural. It cannot, by itself, prove effective OVAL runtime behavior, resolve semantics from all cross-file imports, or certify completeness of an SCAP datastream. It records unresolved links and declarations for manual or tool-assisted follow-up.

## Next operational batch

1. Pin/copy the actual OVAL 5.12.3 Omni XSD source set from the approved SCAP content source, with hashes and an input manifest.
2. Run `python3 tools/oval_xsd_default_inventory.py SCHEMA_DIR --output inventory.json`.
3. Join cross-file type/attribute-group references; audit every defaults/optional-attribute declaration and all inherited defaults. Do not infer effective values solely from a local attribute snippet.
4. Build forward-converter default materialization; require explicit NG behavior-affecting fields and reject unhandled cases.
5. Exercise the round-trip regressions: `python3 -m unittest discover -s tools/scap_ng_roundtrip_v003 -p 'test_*.py'`.
6. Validate regenerated XML against pinned Omni schema, then perform semantic differential testing and document unavoidable representational differences.
7. Promote reviewed, stable behavior definitions to the JSON Schema documentation pipeline proposed in iteration 002.

## Source schema flaws tracking

A surprising implementation or an ambiguous schema declaration is initially a **candidate** issue. Promote it to a confirmed schema flaw only with exact XSD/documentation evidence and an independently reproducible counterexample. This prevents tagging legitimate non-obvious defaults as defects.
