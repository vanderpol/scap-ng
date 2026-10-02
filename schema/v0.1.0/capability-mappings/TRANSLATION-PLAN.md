# Assessment capability translation plan

Status: active post-rebaseline workstream.

Baseline: `a4f8410f7de87e04f0262c977fe28a6354ff05ac` (2026-10-02). Both the rebaseline smoke regression and repository preservation/current-archive boundary workflow passed at this commit. Capability work after this point must preserve that baseline contract.

## Goal

Translate the supported OVAL 5.12.3 assessment capability surface into reviewed native SCAP-NG capability mappings and generated deep schemas without mechanically reproducing XML structure.

A capability is complete only when all of the following exist:

1. Exact pinned OVAL Test/Object/State source family.
2. Reviewed native Object/Test/State/Item shape, with Object data fields a subset of State fields and State fields aligned 1:1 with collected Item fields.
3. Explicit treatment of behavior-affecting OVAL defaults.
4. Migration crosswalk and intentional divergences.
5. Semantic-validator rules for constraints that do not belong in JSON Schema.
6. Focused positive and negative fixtures.
7. Current-design regression success.
8. Corpus or Self-Assertion evidence appropriate to the capability.
9. Crosswalk/specification update marking the mapping reviewed.

Generated JSON Schema alone is not capability completion.

## Current reviewed mappings

- `unix.file`
- `file.hash` (source: `independent:filehash58_test`)
- `windows.file`
- `windows.registry`
- `variable.value` (source: `independent:variable_test`)
- `windows.wmi.query` (source: `windows:wmi57_test`)
- `linux.rpminfo` (first post-rebaseline expansion)

## Translation ordering

Use observed production use as the primary implementation order, then use OVAL Self-Assertion to fill language-conformance gaps. Do not infer that a low-use capability is removable merely because it is uncommon.

### Production-first tranche

The current crosswalk identifies these high-value unmapped candidates:

- `independent.textfilecontent54` — production: 797 — **reviewed mapping complete**
- `windows.auditeventpolicysubcategories` — production: 143 — **reviewed mapping complete**
- `windows.userright` — production: 92 — **reviewed mapping complete**
- `independent.shellcommand` — production: 80 — **reviewed mapping complete**
- `linux.rpminfo` — production: 68 — **mapping started/completed after baseline**
- `unix.sysctl` — production: 66 — **reviewed mapping complete**
- `linux.partition` — production: 64 — **reviewed mapping complete**
- `linux.systemdunitproperty` — production: 40 — **reviewed mapping complete**
- `windows.fileeffectiverights53` — production: 32 — **reviewed mapping complete**
- `windows.cmdlet` — production: 22 — **reviewed mapping complete**
- `unix.symlink` — production: 15 — **reviewed mapping complete**
- `windows.lockoutpolicy` — production: 14 — **reviewed mapping complete**
- `windows.passwordpolicy` — production: 14 — **reviewed mapping complete**
- `unix.password` — production: 10 — **reviewed mapping complete**

Counts are evidence for prioritization only; they do not define normative support.

### Production-first checkpoint — 2026-10-02

All listed production-first capabilities at or above 10 observed production occurrences now have reviewed mapping files and focused generated-schema regressions. `windows.cmdlet` additionally established the shared authored record-Object input primitive; singleton Windows policy capabilities established the no-fake-Object Test source pattern; file-oriented capabilities share the corrected traversal base while preserving Unix/Independent `symlinks` versus Windows `junctions` terminology.

The next gate is a green maintained smoke/current-design regression on the combined tranche, followed by lower-frequency production and Self-Assertion language-conformance coverage.

### Conformance-completion tranche

After the production-heavy capabilities are stable, cover remaining supported OVAL 5.12.3 candidates exercised only or primarily by Self-Assertion. Reinstated tests remain supported according to the checked-in governance override record. Effectively deprecated tests remain migration blockers and SHALL NOT gain native capability schemas.

## Shell command guardrail

`independent.shellcommand` is a legitimate native capability and may simplify some legacy OVAL that became complex because older SCAP/OVAL authoring environments lacked it.

It SHALL NOT become the default escape hatch for functionality that is better represented by native scanner capabilities.

In particular:

- do not replace native filesystem selection/traversal with shell commands merely to shorten source;
- retain scanner-controlled local-filesystem scope, traversal depth, symlink policy, evidence capping and efficient collection where those semantics matter;
- prefer shell command for bounded command-oriented checks whose intent is clearer as a command and that do not discard useful scanner-native collection semantics;
- preserve the independent/platform-neutral capability identity; the selected shell/interpreter determines operational platform applicability;
- retain the source security requirement that execution of content-supplied commands is trust-sensitive, but express package/signature trust through SCAP-NG packaging/security policy rather than legacy XML wording.

The later complexity-discovery study may classify complex legacy checks as native capability, new abstraction, shell command, or inherently complex. That research is separate from the current faithful capability translation.

## Working method

Translate one semantic family at a time. For every Object/State/Item family, enforce the invariant `Object data fields ⊆ State fields = Item fields`; collection controls such as OVAL behaviors are not Item fields. State/Item field identity and datatype semantics SHALL come from one canonical capability entity model so authored State predicates and runtime collected evidence cannot drift.

Translate one semantic family at a time. When several OVAL tests share a native abstraction (file traversal, hierarchical traversal, record predicates, command/query result records, package metadata), update the shared primitive first and keep capability mappings narrow.

If a source capability exposes an OVAL schema inconsistency, hidden default, deprecated behavior, or apparent design defect, record it instead of silently encoding it into NG.

Do not bulk-generate mappings from XSD names. Codex may implement bounded mapping/test batches after the intended native semantics are reviewed; ChatGPT remains the semantic review point for ambiguous mappings.
