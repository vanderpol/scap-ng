# SV-278217 lossless-authoring implementation checkpoint

**Status:** research prototype, not yet merged into the normative 0.3 compiler. The current [readable SV-278217 example](README.md) is the test case. The experimental expansion is intentionally strict.

## Expansion contract under test

| Authored shorthand | Canonical value |
| --- | --- |
| `hive: {equals: local_machine}` | native hive `local_machine`, comparison `equals`, string |
| `key: {equals: 'SYSTEM\\CurrentControlSet\\Control\\Lsa'}` | equality against the exact Registry key, string |
| `name: {equals: RestrictAnonymous}` | equality against the Registry value name, string |
| `type: {equals: dword}` | Registry item `type` equals `dword` |
| `value: {equals: 1}` | same item `value` equals integer `1` |
| `match: all`, `existence: one_or_more` | explicit state quantifiers, not defaults |

**What is rejected:** string `'1'` where integer is required; unspecified Registry type; missing existence; unrecognized operation; bare selector string implying equality; `REG_MULTI_SZ` shortcut before element semantics are defined.

An isolated Python prototype verified seven positive/negative tests. **The proof was local, not CI, not full JSON Schema validation and not a scanner test**; do not report completed end-to-end conversion or pass the Board gate.

## Next integration steps

1. Make a formal authoring-input schema distinct from the canonical Assessment format, and ensure the authoring schema itself catches missing fields.
2. Expand only well-defined shorthand from the capability mapping. Prove the canonical output validates against the 0.3 registry capability schema and semantic validator. Some legacy predicate names, notably cardinality/State shape, still require reconciliation.
3. Wire expansion into the normalizer/compiler (never into runtime scanner), create goldens for Registry DWORD / string / absent / unreadable, and match original canonical results.
4. Move logical identity resolution (issue #199) into the same compilation pass.
5. Keep SV-278029 as the flagship integration test and leave proposed NTP parsing unresolved until proven from existing capabilities.
