# SCAP-NG 0.4.1 Profiles — independent disabled Rule sets (candidate)

**Scope:** native authoring only; this candidate is not approved or published.

Each native Benchmark Profile specifies its own **complete** `disabled_rules`
array. Rule IDs are selected directly. Rules are enabled by default unless a
selected Profile disables them, subject to the separate Benchmark
`default_selection` control when no Profile is selected. There is no native
`extends`, `enabled_rules`, Group-selection override, or Profile inheritance
of parameters. A Profile's optional `parameters` are independent too.

Example:

```yaml
profiles:
  - id: baseline
    disabled_rules: [rule-a, rule-b]
  - id: specialized
    disabled_rules: [rule-b]
```

Selecting `specialized` leaves `rule-a` enabled without a separate
re-enable syntax. Benchmark/Group/Rule applicability remains a distinct
evaluation gate; a Rule enabled by Profile selection can still be
`NOT_APPLICABLE`.

## Migrating XCCDF source Profiles

XCCDF `Profile extends` is **source-language syntax**, not native
SCAP-NG syntax. The converter must flatten each source Profile's entire
ancestor chain into its own effective native `disabled_rules` list,
including Rule- and Group-targeted XCCDF `select` overrides. Local selectors
override inherited selectors for the same source item. A Rule under an
unselected Group remains unselected until every restricting ancestor is
re-enabled. Do not turn a source Group selector into a native Group selector.

Keep original source Profile IDs, parent IDs, chain order, original XML
digests, source selector IDs, effective Rule-ID decisions, and source-to-native
Rule mappings in provenance. Missing ancestors, duplicate/conflicting local
selectors, cycles, malformed source values, or unsupported XCCDF refinement
must produce an explicit conversion hold; no partial success or silent default
expansion. Preserve source selection semantics when deciding full converted
`disabled_rules` on partial benchmark slices; mark excluded Rule IDs as out
of the slice rather than silently changing the original source selection.

## Qualification gates

- Native Benchmark schema rejects any `Profile.extends` and all Group or
  positive Rule selection fields, including stale legacy authoring.
- RI executes each Profile as an independent complete Rule disable set and
  rejects duplicate Profile IDs or unknown Rule references.
- Converter demonstrates source parent disable → child re-enable; nested
  Groups; multi-level chains; unknown ancestor and cycle rejection; and exact
  original XML identities/selection ledger, without source oracle results
  being supplied as evaluator inputs.
- Regenerate canonical docs, editor metadata, schema family hashes, example
  receipts and consumer pins through the coordinated 0.4.1 schema cascade.
  Do not merge on this isolated schema-only candidate.
