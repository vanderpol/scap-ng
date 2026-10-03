# Research findings and evidence boundary

Checkpoint 2026-10-03. Source baseline: `vanderpol/scap-ng` main at `e7c4d235d33789b6665f5518c41456df733b19ae`. Local checkout was fetched from the requested GitHub repository before work. Earlier local checkouts with schema/build modifications were inspected only for locating source inputs; their uncommitted changes were not copied. The packet and NIWC pins are authoritative for this study.

## Supported conclusions

1. **Finite authoring tables are worth a tooling prototype before new runtime features.** Original OVAL XML independently resolves to the same 24 regex strings as the audit table. Twelve crypto source path/field/expectation tuples equal the proposed rows. These comparisons preserve literal requirements; they do not prove the complete collector/result semantics of an expanded assessment. General expansion, source variable-instance behavior and precise per-row collection/status lowering remain unimplemented.
2. **Keep permission booleans.** All 4096 modes agree between eight independent forbidden-bit predicates and a subset-bit comparison. Numeric ordering fails for 0604. The current descriptive permission model is already appropriate; no new runtime mode feature is supported by this study.
3. **Use existing per-Item record semantics before inventing correlation.** Apache cookie States already combine both flags within one Item. Typed DNS/interface observations could make scope/status review clearer, but a general join is not shown necessary. Losing identities or checking unrelated favorable arrays has concrete synthetic counterexamples.
4. **Separate refactoring from intent corrections.** Apache explicit/default/override, audit persisted/loaded and DNS truncated/exact-duration cases yield different results. A better policy implementation is not automatically equivalent to the source.
5. **Share acquisition, without hiding its semantics.** All three Apache cases repeat installation/config/include discovery. A library or typed collector can remove repeated author dataflow, but product semantics, installed instances and native filesystem acquisition remain substantial implementation obligations.

## Source observations needing future publisher/implementation follow-up

| Observation | Source trace | What is actually established |
| --- | --- | --- |
| Two root b64 audit branches use b32 patterns | RHEL9 SV-258179 original Variables/Tests and extracted patterns | Confirmed source reference/value anomaly, preserved in table and regression; not repaired |
| Audit automated graph reads persisted file, Check Text reads auditctl | RHEL9 SV-258179 | Confirmed scope difference; not proof of target false-pass rate |
| DNS key duration command drops minutes/seconds | DNS SV-259345 original command Variables | Confirmed integer-hour projection; synthetic 168h+1s divergence; target UI/cmdlet representability unproven |
| Crypto graph omits utility equality check and displayed openssl_fips back end | RHEL9 SV-258236 source versus Check Text | Confirmed coverage difference; operational implications require publisher review |
| Apache default-document graph is root-level index.html existence | Apache Site SV-214292 | Does not establish every descendant directory/equivalent-default requirement |
| Registry command omits numeric RegistryRights displays | Windows2025 SV-278001 command | Confirmed output filtering; a real omitted dangerous ACE is not demonstrated |
| Root/config Variables can generate Cartesian paths | Apache discovery/concat | Synthetic difference proved; real multi-installation collector behavior not executed |

These are research findings, not automatically filed upstream bugs. The task brief requires coordination before Board publication; no new vote or source-remediation patch was published. Preserve the exact source pins when opening focused follow-up issues and check existing issues first. Do not group unrelated findings into a single vague schema bug.

## Tests and validation actually run

- 83 original packet/context hashes verified unchanged.
- Five original NIWC ZIP SHA-256 values match source-generation pins.
- Configuration dependency closure for all 12 selected Rules: Definitions/extended Definitions, Tests, Objects, States, Variables, Set/Filter dependencies and check selectors; no unresolved references or external Variables in these selected graphs. No arbitrary graph depth limit.
- Complete per-family source applicability bindings/closures retained separately. 44 extracted OVAL documents (12 configuration and 32 applicability) validate against the pinned omni-schema.
- 14 reached OVAL Test types inspected against pinned XSD deprecation metadata plus governance overrides: none effectively deprecated. This is not a claim that the full corpus has no deprecated Tests. Windows accesstoken remains excluded; userright is its established replacement.
- 73 unchanged YAML snapshots pass current authoring vocabulary and v0.1.0 JSON Schema checks. Proposal sketches are not asserted to validate against that production schema.
- 12 experimental sketches pass the vocabulary/presentation guard only; they are not production schema-validity or execution claims. Repeating extraction yields identical hashes for all 56 Rule/OVAL XML extracts. Inherited Rule XML preserves original Check Text whitespace, including trailing spaces; authored-code/document diff checks exclude only those original Rule extracts.
- 22 new bounded semantic-model test methods pass: exact audit pattern/crypto-row comparisons, 294 audit text fixtures using Python regex, 4096 permission modes, UID/home boundaries, record identity/coverage, partial/error/unknown/duplicate cases, ACL order/whitelist distinctions, DNS RR/key/duration boundaries, interface rows, and Apache directive/cookie/file-scope counterexamples.
- 63 inherited schema-derived truth-table/evaluator tests pass, including existence, result aggregation, records, Sets/Filters and exhaustive generic charts. Logs: [research](evidence/test-results.txt), [inherited evaluator](evidence/inherited-evaluator-tests.txt), [static source evidence](evidence/static-verification.json).

No RHEL, Windows, DNS or Apache target acquisition was executed. No production scanner, upstream Self-Assertion target suite, OpenSCAP/ovaldi differential scan, performance benchmark or author-usability study was run. Python regex covers these fixtures but is not asserted to implement OVAL's full regex dialect. Exact pattern identity is stronger evidence about representation than matched fixture results; neither establishes collector equivalence. Synthetic record/ACL/path models explicitly define a smaller contract than OVAL or Windows.

## Research iterations and revisions

Wave 1: pilot audit/Apache explanation and adversarial models. Rejected parsed audit/effective Apache as transparent replacements; retained source-preserving regex tables and explicit-presence distinction.

Wave 2: filesystem control, crypto, Windows and DNS cases. Exhaustive permission results argued against a new mode primitive. Correlation experiments retained existing Item-local State aggregation and proposed collector records rather than a mandatory join. Duration and root-directory cases established policy corrections as separate work.

Wave 3: refinement after falsification. Added explicit row instance/collection behavior, separate applicability closures, per-case matrices and missing/error/unknown/duplicate contracts. Reduced general feature claims: no new runtime primitive is proved necessary; collector sketches remain experimental and require implementation/testing. Four regex templates, not two, are required to retain the source grammars and auid forms exactly.

## Provenance

Inherited: immutable packet snapshots and pinned original NIWC Rule/OVAL extracts. Full package notices remain in family benchmark-context files and referenced originals. Adapted: research-only extraction/presentation and proposal sketches derived from those graphs. Common: original bounded experiment code and fixtures. Evidence/Audit: findings, matrices, hash/deprecation/XSD reports, measurements and test logs. No external scanner implementation was copied. Source identifiers/XML stay in evidence; proposals have native local names and no executable dependence on legacy serialization.
