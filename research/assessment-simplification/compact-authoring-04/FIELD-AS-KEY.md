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
