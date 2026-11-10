# Pinned-source documentation fidelity

This pack reconciles the mapped OVAL source annotations with the proposed SCAP-NG JSON Schema descriptions. The renderer still reads only the proposed schemas. The extraction and crosswalk are provenance and editorial evidence, not a second documentation model.

Stack: #39 → #41 → #44 → #45 → this change. The exact starting point is PR #45 commit `976a5fa67e8195ca5fc2eb2779eab0da502b1afe`. Frozen `schema/` files, production pins, prior editorial decisions and semantic holds are unchanged.

## Coverage

| Measure | Count |
| --- | ---: |
| Mapped capability families reconciled | 104 |
| Families mapped to OVAL 5.12.3 | 100 |
| Experimental ESX families mapped only to the separate OVAL 6.0 source | 4 |
| Unique `xs:documentation` passages | 3,501 |
| Unique source statements | 6,696 |
| Capability/statement/declaration bindings | 49,661 |
| A — retained | 847 |
| B — adapted | 771 |
| C — historical behavior withheld | 45,977 |
| D — conflict or unresolved contract withheld | 45 |
| E — duplicate or irrelevant boilerplate excluded | 2,021 |

Disposition counts refer to bindings, not distinct source statements. Direct declaration bindings account for 1,613 retained/adapted statements (844 A, 769 B), 1,503 withheld bindings and 1,111 exclusions; the rest arise from referenced declarations. Shared type declarations are reached by many capabilities, so the large C count includes repeated bindings to the same legacy type/evaluation rules. A completed reconciliation means every extracted statement has a checked disposition. It does **not** mean that every legacy contract has a native resolution or that scanner equivalence has been proved.

Field coverage remains 1,858/1,866 Object/Item/Require routes: 102 fully field-described capabilities and two partial capabilities with eight missing descriptions. The shared inventory remains 2,872/3,020 documented nodes, with 148 gaps. These existing coverage gaps and all 104 unverified runtime contracts remain visible; this change does not relabel them as resolved.

## Review entry points

- [Short shellcommand comparison](SHELLCOMMAND-SUMMARY.md), [complete passage comparison](SHELLCOMMAND-REVIEW.md), [before](shellcommand-before.md), and [generated after](../reference/capabilities/independent.shellcommand.md).
- [Source extraction](source-documentation.json): exact pinned commit, file SHA-256, XPath, normalized text, original parsed annotation XML, declaration roles and explicit multi-construct associations. Item associations inferred from a name family are labeled rather than presented as explicit native metadata.
- [Statement spans](source-statements.json): exact offsets into normalized source passages; no non-whitespace source text may disappear.
- [Crosswalk](crosswalk.jsonl): classification, rationale, declaration binding and, for every A/B statement, exact schema description pointer and destination substring offsets.
- [Semantic ledger](semantic-ledger.jsonl): C/D statements with source text and exact pointers; these are not native requirements.
- [Coverage](coverage.json) and [manifest](manifest.json): per-capability reconciliation and hashes of source evidence, proposed schemas and derived audit outputs.
- [Test evidence](test-evidence.json): exact local commands, pinned dependencies, validation comparisons and independent hash-seed output digests. Remote CI results belong to the PR's exact head.

Only actual schema `description` values supply published prose and editor-help descriptions. Full field explanations remain accessible in advanced pages; basic tables retain concise first sentences. Capability and role overviews precede the tables. Shared Require grammar is linked rather than copied onto every page. Value datatype annotations expose native declarations without adding validation restrictions.

## Sources and reproduction

Required: Python 3.12, Git and the pinned packages in `requirements-dev.txt`. Normal generation and CI are offline after dependency installation:

```sh
python -m pip install -r requirements-dev.txt
python tools/generate_documentation.py
python tools/audit_documentation_fidelity.py
python tools/generate_documentation.py --check
python tools/audit_documentation_fidelity.py --check
python -m unittest discover -s tests -v
```

Re-harvesting requires checkouts of the original `OVAL-Community/OVAL` repository, not rendered documentation:

```sh
git clone https://github.com/OVAL-Community/OVAL.git /tmp/oval-documentation-5
git -C /tmp/oval-documentation-5 checkout 2f140ee5c5dd1ed9606fcd5afc301f6baeb48706
git clone https://github.com/OVAL-Community/OVAL.git /tmp/oval-documentation-6
git -C /tmp/oval-documentation-6 checkout 5afcf590fb5d334687bfdc47f98716424cdb7f3d
python tools/extract_oval_documentation.py \
  --oval-dir /tmp/oval-documentation-5/oval-schemas \
  --oval6-dir /tmp/oval-documentation-6/oval-schemas --check
```

The extractor follows mapped Test/Object/State/Item declarations, related deprecated declarations and referenced types/groups/attributes. It checks checkout commits and source hashes. The corpus is the mapped declaration/reference closure, not every unrelated annotation in the upstream repository. Four experimental ESX mappings have no 5.12.3 counterpart; their separate 6.0 statements remain withheld.

For maintenance, edit accepted wording in its schema description and update the associated crosswalk spans and disposition explicitly. Run generation, audit and tests. To change the source pin, re-extract first, then reconcile every new or changed statement before regenerating the audit. The audit rejects missing accepted text, invalid associations, omitted source spans, duplicate bindings and stale outputs. Classification is an editorial decision; successful auditing does not prove the classification semantically correct.

## Outstanding semantic review

Review C/D entries by capability before implementing collection guarantees. Priorities remain shellcommand execution/cardinality/error handling, registry traversal/views and file traversal/link/error handling. Newly exposed source copy errors include firmware-password prose naming FileVault, SEStatus prose describing AppArmor counts and registry-key rights prose naming files. Their original wording remains in the evidence; it is not copied into native overviews.

No schema validation keyword or scanner behavior was changed. No signing requirement, default shell, collection multiplicity, OVAL datatype restriction or legacy error aggregation has been adopted. No native runtime or scanner-equivalence proof is claimed.
