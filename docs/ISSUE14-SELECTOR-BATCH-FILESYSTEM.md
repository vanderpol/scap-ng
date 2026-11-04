# Issue #14 selector contract batch 01: filesystem and Windows

This is the first follow-on batch after draft PR #15 (`c5399a1`). Draft PR
#16 (`74e414d`) was reviewed as a separate author-documentation change. Neither
draft is merged by this work; the owner must approve compatibility-changing
schema restrictions.

## Scope and priority

The batch is ordered from the converted-content usage counts in the generated
capability catalog, then by capability importance:

| Capability | Catalog usage count | Selectors resolved in this batch |
|---|---:|---:|
| `windows.fileeffectiverights` | 24 | 4 |
| `unix.file` | 23 | 3 |
| `windows.regkeyeffectiverights` | 22 | 3 |
| `windows.file` | 19 | 3 |
| `windows.ntuser` | 15 | 2 |
| **Batch total** | **103** | **13** |

The count above is the sum of capability uses, not selector contracts. This
batch resolves **13 selectors**. The repository inventory is now **19 resolved
and 122 unresolved of 141 total**; the original baseline was 4 resolved and
137 unresolved.

## Source and mapping review

Each mapping remains the source crosswalk authority and identifies the pinned
OVAL 5.12.3 definition schema, namespace, test, object, and state. The review
used these source object definitions without copying third-party XSD prose:

| Capability | Pinned source object | Existing native mapping reviewed |
|---|---|---|
| `unix.file` | `unix-definitions-schema.xsd` / `file_object` | `filepath → full_path`, `path → directory`, `filename → name`; file traversal remains explicit |
| `windows.file` | `windows-definitions-schema.xsd` / `file_object` | `filepath → full_path`, `path → directory`, `filename → name`; per-directory filesystem case context remains explicit |
| `windows.fileeffectiverights` | `windows-definitions-schema.xsd` / `fileeffectiverights53_object` | file selectors plus `trustee_sid`; `filename` remains nullable |
| `windows.regkeyeffectiverights` | `windows-definitions-schema.xsd` / `regkeyeffectiverights53_object` | canonical hive enum, nullable `key`, and trustee SID |
| `windows.ntuser` | `windows-definitions-schema.xsd` / `ntuser_object` | `key` plus nullable `name`; profile/traversal controls remain separate |

The OVAL object entities are string entities with the source operation set
`equals`, `not equal`, `case insensitive equals`, `case insensitive not equal`,
and `pattern match`, except that the registry hive is the mapping's canonical
enum and therefore uses native `equals` only. The contract input records the
source-to-native crosswalk separately from native grammar:

`equals → equals`, `not equal → not_equal`, `case insensitive equals →
case_insensitive_equals`, `case insensitive not equal →
case_insensitive_not_equal`, and `pattern match → matches_regex`.

Native Objects therefore use `matches_regex`; `pattern_match` is not emitted or
accepted as a native selector key. Variables and lists retain their existing
`value_match` cardinality rule. Null is structural selection, not an empty
string or wildcard: file/NTUSER names select their higher-level directory/key,
and registry-rights `key` selects its higher-level hive.

## Validation and compatibility

Generated artifacts were refreshed only from
`schema/native-selector-contracts.json` and the existing mapping catalog:

```text
python tools/generate_native_selector_schema.py --check
python tools/generate_docs.py --check
python -m unittest discover -s tests -v
```

The batch tests cover every resolved selector with positive values, all allowed
native operators, variables/lists, nullability, wrong types, empty lists,
generic operator leakage, legacy `pattern_match`, and unknown selector keys.
Existing converted examples continue to validate, including the approved
registry and Linux partition examples. No scanner implementation, editor pack,
VS Code behavior, source crosswalk, or 0.4.0 baseline artifact was changed.

## Explicitly unresolved

* Filesystem lookup case behavior remains dependent on the effective containing
  directory, filesystem, and selected Windows API namespace. The schema does
  not add a global case switch or silently lowercase a path.
* OVAL traversal restrictions that depend on a non-equality operation remain in
  the capability mapping and are not encoded as editor behavior in the selector
  grammar.
* Runtime collector equivalence, provider permissions, SID resolution, and
  regex-engine behavior are not claimed by schema validation. They require
  scanner/provider qualification before becoming implementation guarantees.
