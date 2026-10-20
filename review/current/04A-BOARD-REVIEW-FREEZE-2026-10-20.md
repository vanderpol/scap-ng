# SCAP-NG 0.4.0 Board-facing authoring freeze — 0.4-A + bounded must/may

**20 October 2026 | Owner direction | Refs #227 #232 #246.**

## Locked presentation scope

The 0.4.0 candidate for the October 22 OVAL Board meeting is **the existing versioned 0.4-A model**, not 0.4-B/C/D/E. No new general-purpose Object/State/Variable language, no mandatory global State registry, and no change to original imported OVAL execution graphs is being introduced.

The one owner-selected author-facing improvement is the **all-items-must** requirement family, limited initially to the exact source-equivalent `one_or_more/all` and `may_be_absent/all` Test/Item pairings. No change to State fields, record cardinality, zero-items, exact-one, matching-selected-only, six-state evaluation, Variables, Sets, Filters, or the `evaluate` topology is implied. Require explicit `items` existence; make local predicate States children of `all_items_must`. An absence-only check keeps a separate `items: none` form.

Source-exact lowering for the limited author-facing syntax:

```yaml
require:
  items: one_or_more
  all_items_must:
    - mount_options:
        require: at_least_one_exists_and_some_match
        equals: nosuid
```

This is **not yet a schema-valid form of native 0.4-A**. The research lowerer reconstructs the original locally scoped State list and original Test requirement token. Do not label review-preview YAML or JSON a validated normative 0.4.0 release before schema promotion, human review and compiler acceptance.

## Frozen authoritative input for Thursday

- Immutable corrected r3 source release: [v0.4.0-joval-meeting-preview-20261015-r3](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3) (YAML+JSON six-STIG source).
- Windows 11 new must/may **research** artifact: [GitHub Actions run 39441513385](https://github.com/vanderpol/scap-ng/actions/runs/39441513385), built from pinned r3 JSON SHA-256 `a1837c03133021f4d13814516a91b372f83b03771519f8361398ff1663056fea`.
- CI for that run passed source package audit (4,001 authoring docs, native scoped Assessments, Test schemas and reference graph), and passed full parsed source AST reverse mapping for *every edited Test*, without changing unaffected documents. It does NOT prove runtime scanner parity, test-failure causality or signed NG bundles.
- The complete release source remains unchanged. Output ZIP is deliberately labeled research and includes unchanged six-STIG documents for graph closure; Windows-specific changes occur only under `ms_windows_11`.

## Review process and guardrails

1. **Freeze architecture:** existing 0.4-A model remains the meeting baseline. Do not merge 0.4-D authoring graph into normative schemas or reinterpret OVAL's uncommon combinations.
2. **Do not silently accept other must/may variants:** `at_least_one_item_must`, `exactly_one_item_must`, and `no_items_may` remain vocabulary proposals until original source examples, missing/incomplete/error evidence and status correctness are independently reviewed. Absence of forbidden items and no matching items are not the same.
3. **Editor demonstration:** update only user-facing explanatory labels, still serializing the original token. Do NOT silently emit proposed authoring structures, advertise scanner support, or silently rewrite a document on open/save. Show schema/provenance pin and research-only status.
4. **Further semantic change:** review against `MAINTAINING.md` human packet before normative schema promotion. No new language, no release claim without explicit gates.
5. **Regression:** existing source/schema/reference gate + reversible must/may proof + browser smoke + deployment. Include focused empty/partial/error negative examples in later technical research rather than assuming scalar Boolean simulation establishes OVAL equivalence.

**Decision framing:** Thursday presentation scope is locked. Formal normative promotion of `all_items_must` is *not* established by the source-equivalence proof alone; the meeting must not be misled into believing it is. For an authoring demo, this limited fully disclosed proposal is acceptable.
