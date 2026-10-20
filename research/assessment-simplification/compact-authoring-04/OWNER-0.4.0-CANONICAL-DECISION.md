# Owner decision: SCAP-NG 0.4.0 canonical authoring (2026-10-20)

**Accepted direction for 0.4.0 (#227, #232, #239, #246).** The A/B/C/D labels were internal research alternatives. They are not user-visible product versions.

1. Keep the OVAL-aligned names **Assessment, Test, Object, Variable and Item**. Use `object` for a source declaration, `require` for Test predicates and population requirements, `evaluate` for composition of Test results.
2. Test `capability` determines an *inline* Object's capability. Omit the redundant inline `object.capability` from authored 0.4.0. Reject a contradictory explicit duplicate. Standalone or shared Objects retain their own explicit capability.
3. Adopt `require: {items: one_or_more, all_items_must: ...}` for **source-proven** one-or-more/all-match Tests, and `items: may_be_absent` when that is the original existence requirement. Existence and matching are distinct; zero Items must not accidentally pass a one-or-more requirement. Inside the predicate tree, retain independent field/record cardinality and exact `and` / `or` grouping. Do not collapse a per-Item match to a substring check.
4. Do not silently rewrite uncommon existence/match combinations, error/unknown/partial-result boundaries, alternative State semantics or nested record cardinality. A clearly marked explicit requirement fallback remains necessary until independently verified replacements exist; it is *not* a separate release or grammar. Every converted Assessment must roundtrip to the preserved source.
5. Use multiline YAML. Avoid introducing bracket-heavy flow mappings or new language synonyms.
6. Regenerate all **six** benchmark authoring sets in YAML and JSON from the verified, pinned October 15 source. Require schema, source-reconstruction and reference-closure regression gates. No scanner parity claim from a source roundtrip.
7. The browser editor SHALL show *0.4.0* rather than *0.4-A*, explain `object` as collection source and `require` as expectations. It SHALL load and export the actual 0.4.0 structure; older fixtures must be explicitly identified as legacy or migrated, never silently re-saved with different semantics.

**Release gate:** this decision authorizes implementation but does not constitute evidence that all six generated benchmarks, native JSON Schema, YAML editor export, compiler, or scanner pass. Publication of a package as validated requires checking each gate independently. Historical research remains auditable but shall not be advertised as a competing specification.
