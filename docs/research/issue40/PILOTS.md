# Two bounded schema-driven previews

**Unapproved annotation preview in memory only.** The same inspector used by PR #39 reads types, occurrence bounds and local references here. No per-schema renderer is introduced. These pages are generated from native schemas plus exact proposed annotation operations, not hand-maintained guide text.

## Assessment core: comparison Require

`https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement`

**Before:** One complete Test requirement: item_requirement gives explicit existence and satisfaction counts; conditions follow as fields/and/or/one/xor. Field cardinality must be explicit.

**Proposed:** Comparison requirement with independent Item counts, a complete shared field-count policy and one field condition or Boolean condition group.

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| `item_requirement` | object | 1..1 | Explicit Item existence and satisfaction quantifiers; the two decisions remain independent. |
| `field_requirement` | object | 1..1 | Required shared values_found/values_matching pair for comparison Tests. The editor may offer these defaults but must serialize the complete pair. A closer complete pair overrides it; no runtime default. |
| `fields` | object | conditional | One complete condition; distinct fields are combined with logical AND. |
| `and` | array | conditional | Undocumented here; shared/structural proposal requires review. |
| `or` | array | conditional | Undocumented here; shared/structural proposal requires review. |
| `one` | array | conditional | Undocumented here; shared/structural proposal requires review. |
| `xor` | array | conditional | Undocumented here; shared/structural proposal requires review. |

Counts are contextual: the Item/field parent policies are required for comparison; selection of `fields` versus Boolean groups remains conditional. Existence-only requirements use their separate shared schema. Unsupported/indeterminate constraints are reported, not guessed.

## Shared concat family

`https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/concat`

| Signature element | Schema shape / bounds | Contract |
| --- | --- | --- |
| `concat(components…)` | 2..n ordered entries | Concatenate at least two ordered component expressions, taking the Cartesian product of multivalued components; native casting and unavailable-component status mappings require explicit confirmation. |
| component | Shared expression `$ref`; recursive nesting allowed by grammar | Arguments are syntax-validated; conversion/status obligations remain **provisional**. |
| return datatype | Not encoded at this function syntax node | Owner must confirm the native return/conversion/status contract; no runtime result is inferred from validation. |

**Before:** Concatenate two or more components in order. Multiple values produce the Cartesian product of component values. Components follow inherited source casting rules when a string conversion is required; incompatible values produce an error. A missing or nonexistent component yields the inherited source status; Error, Incomplete, Not Collected, and Not Applicable statuses are not silently converted to strings.

**Proposed:** Concatenate at least two ordered component expressions, taking the Cartesian product of multivalued components; native casting and unavailable-component status mappings require explicit confirmation.

Signature notation above is descriptive; native source uses the named `concat` key. Minimal schema example (not executed):

```json
{
  "concat": [
    {
      "literal": "a"
    },
    {
      "literal": "b"
    }
  ]
}
```

The syntax still rejects fewer than two components. Annotation previews preserve the entire validation assertion tree; positive/negative witnesses are checked before and after. No arithmetic, substring or inactive function-call grammar is added.

Historical concat basis: pinned OVAL 5.12.3 `ConcatFunctionType`, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`; source attribution is review evidence, not automatic native semantics.
