# SCAP-NG JSON Schema 0.1.0 stability checkpoint

**Status:** structurally stable candidate  
**Checkpoint date:** 2026-10-02  
**Current-design verification head:** `a0f92b373b26d86d9fa264c97d6bf70b24012125`

This checkpoint records that the native SCAP-NG JSON Schema **0.1.0 structure is stable enough to use as the current schema baseline**. It does not declare the entire SCAP-NG project, converter, or reference assessor complete.

## Evidence at this checkpoint

- Native JSON Schema validation passed after the result-redaction schema changes in Actions run `37067399891`.
- OVAL Self-Assertion semantic validation passed after those changes in run `37067399885`.
- Current-design regression contracts passed on both Ubuntu and Windows at head `a0f92b3` in run `37067713303`.
- Rebaseline smoke regression passed at the same head in run `37067713332`.
- The authoritative OVAL 5.12.3 XSD/default audit passed in run `37066304635`: all 36 named behavior types resolved, 44 behavior-element declarations were inventoried, and no transitive inheritance blocker remained.
- Every behavior-bearing OVAL Object is dispositioned in `research/iterations/003/design/oval-object-behavior-disposition.md` as either a current reviewed native mapping or a source family not currently claimed as a reviewed 0.1.0 native capability.

## Corrections incorporated before the checkpoint

- Generic legacy OVAL `mask` is not part of native comparison syntax.
- Native `redact_result: true` is an explicit results/evidence disclosure directive; false is omitted/rejected as authored noise.
- Legacy `mask=true` migrates to `redact_result: true`; default/effective `mask=false` is omitted from native authoring while source provenance remains migration evidence.
- Runtime `redacted: true` values SHALL omit the corresponding cleartext `value`.
- Nested redaction conflicts resolve toward redaction.
- `independent.xmlfilecontent` now explicitly materializes the behavior-affecting `item_creation` setting.
- Manual response affordances and organizational-input requiredness are explicit authored booleans rather than hidden authoring defaults.
- Capability-specific behavior defaults already reviewed for text-file content, shell command, RPM verification/info, Windows NTUSER, SID/SID-SID, WUA Update Searcher, file traversal, and hierarchy traversal remain explicit or have documented migration dispositions.
- Deep Test/Collection graph transforms have stack-safety regressions, and recursive lowering now checks elapsed conversion budgets during work rather than only before/after it.

## Meaning of “structurally stable candidate”

For 0.1.0, changes to the following should now be treated as deliberate schema changes requiring focused regression evidence rather than routine cleanup:

- top-level Benchmark, Rule, Assessment, Tailoring, Organizational Input, package-manifest, and result document shapes;
- shared Object/State/Test/Variable authoring primitives;
- result redaction representation;
- common comparison, existence, quantifier, Set/filter, record/list, and traversal primitives;
- reviewed capability-mapping schema generation contracts.

This is a **baseline**, not a promise that no defect will be found. A demonstrated semantic defect, missing non-deprecated source capability used by supported content, or schema contradiction still justifies correction.

## Work intentionally outside this schema-stability claim

The following remain active work without preventing the 0.1.0 structural schema baseline:

- independent runtime/reference-assessor equivalence and differential execution evidence;
- complete result propagation/runtime truth-table execution proof;
- remaining converter computation-policy decisions such as default budgets and cumulative accounting;
- record/field/default provenance proof beyond the currently reviewed mapping set;
- schema-only OVAL capabilities that have no current reviewed native 0.1.0 mapping;
- upstream OVAL 5.12.4 defect/proposal work;
- final standards naming, governance ratification, and later schema-version evolution.

## Change discipline after this checkpoint

1. Do not silently reintroduce legacy XML serialization structure or hidden authoring defaults.
2. Preserve any non-deprecated semantic exercised by supported production or validation content unless an explicit documented decision removes it.
3. A schema change SHALL include a focused positive/negative fixture and SHALL pass maintained smoke/current-design gates.
4. Capability-specific semantic changes SHALL additionally use appropriate Self-Assertion or production evidence.
5. Migration/provenance evidence remains separate from clean native authored content.
