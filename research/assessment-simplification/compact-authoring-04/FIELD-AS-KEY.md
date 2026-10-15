# 0.4 research: direct State field names versus field/value wrappers

**Not adopted.** No 0.3 specification or Board Discussion #213 changes. [Research issue #227](https://github.com/vanderpol/scap-ng/issues/227) / [broader authoring issue #225](https://github.com/vanderpol/scap-ng/issues/225).

## Why revisit the wrapper?

Object selection already names a resource field directly (`select.mount_point`). State comparison currently introduces an extra, indirect `field:` property. The field-key representation would make collection and expectation sides visually parallel.

**Actual RHEL 9 SV-257851 mount option check** (metadata omitted):

```yaml
# 0.3 canonical, unchanged
states:
  - field: mount_options
    value: nosuid
    operation: equals
    existence: one_or_more
    match: one_or_more
```

```yaml
# Proposal A: field key, with explicit original comparison attributes
states:
  - mount_options:
      value: nosuid
      operation: equals
      existence: one_or_more
      match: one_or_more
```

```yaml
# Proposal B: field key + independently proposed comparison alias
states:
  - mount_options:
      equals: nosuid
      existence: one_or_more
      match: one_or_more
```

The second proposal combines two **independently tested** transformations. `mount_options: nosuid` alone is **not** recommended: an untyped bare scalar does not specify the comparison operator, entity existence, or matching quantifier.

## Does field-as-key conflict with static-Variable arrays or quantifier shorthand?

**No conflict in the proven source model**, provided three independent quantifier scopes are kept distinct and the compiler lowers in a deterministic order. [Combined 0.4 integration CI](https://github.com/vanderpol/scap-ng/actions/runs/38727447660) verifies six tests using the actual v0.3.0 common JSON Schema, the static-literal folding implementation, field-as-key transformation and `require` alias helper. This is still authoring/structural validation, **not scanner differential testing**.

The **real RHEL 9 SV-257923** `unix.file` Object selector uses the following canonical 0.3 directory array after folding a static Variable:

```yaml
object:
  capability: unix.file
  select:
    directory:
      value:
        - /lib
        - /lib64
        - /usr/lib
        - /usr/lib64
      operation: equals
      datatype: string
      value_match: one
```

`value_match: one` controls each candidate directory's comparison to the **four expected names**. It **cannot** be replaced by a Test or State `require` shorthand.

An **illustrative combined check** (not claimed to be the content of SV-257923) could retain the Object above while adopting:

```yaml
states:
  - owner_uid:
      equals: 0
      require: at_least_one_all_match
require: at_least_one_all_match
```

The **State** preset expands to `existence: one_or_more, match: all` for the `owner_uid` field; the **Test** preset separately expands to that same pair for collected filesystem Items. The expression `equals: 0` is another independently proposed comparison alias.

For RHEL 9 **SV-257851** `mount_options`, the original field pair is `one_or_more/one_or_more`, **not** `one_or_more/all`:

```yaml
states:
  - mount_options:
      equals: nosuid
      require: at_least_one_some_match
```

Here `at_least_one_some_match` is a **research-only shorthand** that precisely expands to `existence: one_or_more` plus `match: one_or_more`. This name and combined compact grammar are not normative 0.4 features. In either check, a field-level preset never changes `value_match`.

### Separate list roles

- `object.select.directory.value: [ ... ]`: a **collection of expected selector values**, previously held by a constant Variable; the associated `value_match` stays explicit.
- `states: [ ... ]`: an **ordered list of distinct State predicates**; a field-key mapping occurs *inside each entry*, retaining repeated fields and logical groups.
- `states[*].field_name.value: [ ... ]`: an **expected State value collection**; its own `value_match` is still required, independent of State `require`, Test `require` and the outer State list.

The source proof additionally uses a constant integer array in an expected State field, a constant string array in an Object selector, a field literally named `value` with an array, and two different Test/State `require` expansions. The exact parsed source Assessment reconstructs after all transformations.

### Important compiler ordering and provenance

The static-Variable normalizer records paths to each replaced `value` node. Changing `field: owner_uid` to the nested `owner_uid:` mapping changes **State path coordinates**. Therefore the compiler must either (a) normalize field-key syntax into canonical State predicates **before** running static-Variable expansion/recording provenance, or (b) run the static fold first and update provenance paths, with inverse operations in reverse order. The integration test deliberately verifies that **re-expanding a path-based proof in the wrong order fails**; expanding `require`, lowering field keys, and only then restoring the static source Variable produces exact source identity.

Existing canonical 0.3 JSON Schema requires `value_match` on both Object and State literal arrays. The new test confirms malformed arrays that omit it are rejected; a field-key rewrite must **not** make that property optional. There is no underlying contradiction—just a required staging/validation contract.

## Published six-STIG proof

The [CI run](https://github.com/vanderpol/scap-ng/actions/runs/38721946322) downloaded the frozen six-STIG 0.3 authoring ZIP and tested a research-only compiler.

- **318/318** automated Assessment source documents expand to exactly the original parsed canonical 0.3 mappings.
- **922/922** State field predicate occurrences lower and re-expand exactly, preserving all keys and value types. This is a **structural source proof**, not differential scanner semantics.
- **119** are legitimate fields literally named `value` (mostly Windows Registry) and were rejected by an overly conservative first prototype. Schema/shape-based disambiguation makes all 119 exactly reversible: `- value: { ...predicate... }` is a **field named value**, while `value: 0` inside the payload is the comparison operand.
- **119** `all` logical branches were traversed and reconstructed as arrays; no AND/OR semantics were inferred or reordered.
- The prototype handles repeated field predicates as **separate list entries**, preserving each evaluation and the enclosing `states_match` expression. A YAML mapping with duplicate keys must **not** replace ordered State lists.

Source code: [prototype](https://github.com/vanderpol/scap-ng/blob/main/tools/research_04_field_key_authoring.py), [fail-closed tests](https://github.com/vanderpol/scap-ng/blob/main/tools/test_research_04_field_key_authoring.py).

## Collision example from real Windows Registry capability

```yaml
# Both `value` keys mean different things at different structural levels:
states:
  - value:          # field identifier: "value"
      value: 0      # expected value
      operation: equals
      existence: one_or_more
      match: all
```

```yaml
# With explicit comparison alias (proposal):
states:
  - value:
      equals: 0
      existence: one_or_more
      match: all
```

The input schema must discriminate canonical longhand (a string `field` property), compact field-key mapping (exactly one field name mapped to a predicate) and logical groups (`all/any/one/odd` mapped to arrays). Thus a field *named* `field` or `all` can be disambiguated **by payload type**, without hard-coded reserved-name exclusions. The capability schema must still define which field names are **valid for the selected Test capability**; arbitrary unknown YAML keys must fail.

## All 65 original OVAL sources: field vocabulary is genuinely diverse

The [65-benchmark source census](https://github.com/vanderpol/scap-ng/actions/runs/38722189621) also succeeded on the pinned NIWC OVAL 5.12.3 source. After excluding macOS, opaque shell-command Tests and unsupported SQL extensions, it found **7,211** native structured State-field occurrences (5,074 distinct original State identities).

| Source attribute shape | Observed structured occurrences |
| --- | ---: |
| Field literally named `value` | **1,335 / 7,211 (18.5%)** |
| Field named `subexpression` | **1,151** |
| Field named `type` | **1,069** |
| State-field uses a Variable reference | **571** |
| Record-valued State field | **286** |
| Original State definitions with repeated direct child field names | **0 observed** |

These are **source OVAL State-field occurrences**, not counts of emitted 0.3 State predicates. Record fields may have nested structures, and Variables must remain fully typed/declared after lowering. We preserve ordered State arrays anyway: more than one independent predicate for the same field can be valid at an Assessment level even if it did not appear as repeated direct State entities in this OVAL census.

**Key finding:** A blanket rule reserving `value` would unnecessarily exclude almost one-fifth of structured source-field occurrences. A *typed* field-key schema distinguishes the field name from the comparison operand by **nesting**, not by banning reserved words.

## Authoring complexity edge cases

- **Repeated same field / different expectations:** retain separate ordered list entries. `states: {field_name: ...}` alone is NOT a universal replacement; duplicate YAML keys collapse or fail.
- **Nested logical groups:** `- any: [ ... ]` remains an operator on the array; a field named `any` has a predicate mapping payload, so the forms can be differentiated. Retain full Boolean/quantifier composition.
- **Record, variable, input, list, typed version and regex predicates:** carry all original properties under the named field; field-key grammar changes no comparison algorithm or type. Never turn complex predicates into bare scalars.
- **No hidden defaults:** `field_name: {value: ...}` by itself is **not** evidence of a defined `operation`, `existence` or `match` unless the canonical source already supplied them. A production authoring grammar must retain the same required-property constraints as the equivalent longhand State.
- **Evidence/redaction and provenance:** comparison metadata is retained unchanged; do not allow dynamic field keys to leak redacted value fields into authoring/result output.

## Should this be a compact feature or the primary 0.4 syntax?

This proposal may be more compelling as a **single 0.4 canonical State syntax**, rather than another mix-and-match alias in a separate compact authoring grammar. That would avoid hidden Easter eggs, provide a cleaner one-grammar experience, and align `select` fields with State fields. **But** it would be a true normative format revision, requiring migration of existing 0.3 content and scanner implementations—not merely an authoring precompiler macro.

Before deciding, compare that option directly with a **schema-discoverable compact YAML front-end** that expands to the unchanged canonical State shape, and with an editor that generates full 0.3. Require capability-specific JSON Schema autocomplete, valid/invalid fixtures, exact re-expansion, and Board review before adopting 0.4.

The separately tracked [65-source OVAL field-name investigation](https://github.com/vanderpol/scap-ng/blob/main/tools/research_04_source_oval_macro_census.py) measures real source field names, collisions and repeated entities; it is not identical to 0.3 source Assessment occurrence counts.
