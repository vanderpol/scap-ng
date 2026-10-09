# Selection, filtering, and local predicates (0.3.0)

**Status:** accepted authoring direction for 0.3.0; schema/compiler/converter implementation and semantic equivalence validation are tracked in [#208](https://github.com/vanderpol/scap-ng/issues/208). The frozen 0.2.0 schema is unchanged.

## Three distinct jobs

| Construct | Meaning | Evaluates |
| --- | --- | --- |
| Object `select` / `collect` | Which resources to query, and with what acquisition parameters? | Collector inputs and selector semantics |
| Object/Set-operand `filters` | Which **observed Items** remain in this Object's resulting population? | A comparison on fields of each collected Item |
| Test `states` | Do the resulting Items satisfy the requirement? | Local comparisons on each applicable Item; Test existence/match rules still apply |

**A Filter is not merely an alternate spelling of a selector or a compliance State.**
Selectors determine acquisition; Filters operate on the Item population after
acquisition and *before* the enclosing Set operation and Test. A capability
may not expose a particular observed Item field as a collection selector at
all. Filtering on owner, mode, actual configuration value or other observed
fields must remain expressible independently.

An implementation MAY fuse or push down a Filter into acquisition for
performance **only when the complete observable behavior is equivalent**,
including Item membership, missing/error states, completeness, provenance and
evaluation outcomes. An optimizer SHALL NOT use a pushdown that merely returns
the right Boolean on ordinary successful examples.

## Native local authoring

An Object/Set-operand Filter SHALL contain its include/exclude action and
local predicate directly. It SHALL NOT reference a separately named State.
Its comparison language is the same typed predicate expression used for Test
conditions; there is no independent Filter comparison language or new truth
function. A Filter's effective capability comes from the Object/Set operand
whose collected Items it evaluates.

**No Filter or State title is required or emitted in native authoring.**
The predicate's consumer location, explicit action, field, operation and value
are normally self-documenting. Do not copy historical `state_title`, source
OVAL `comment`, or a new `filter_title` into executable inline predicate fields.
Preserve historical State identifiers, titles and comments in the separate
migration provenance ledger. Authors MAY use ordinary YAML comments to explain
non-obvious purpose or subtle source semantics; comments SHALL NOT affect
comparison, evaluation, schema validity, or result identity. In particular, a
missing human title SHALL NOT cause generation of an artificial State ID.

For example, an abbreviated illustration:

```yaml
tests:
  library-file-ownership-test:
    capability: unix.file
    object:
      capability: unix.file
      set:
        operator: union
        operands:
          - object: system-library-files-object
            filters:
              - action: exclude
                field: owner_uid
                value: 0
                operation: equals
                datatype: integer
                match: all
                existence: one_or_more
    existence: none
    match: all
    reported_elements: all
```

Here, a nonempty violation population fails the Test: the Filter excludes
correctly owned files. The `none` Test existence quantifier tests the
**filtered** population, not the raw acquisition. A real full Assessment
also needs metadata, `evaluate`, and the declaration of the referenced
Object.

Tests similarly express expectations directly:

```yaml
states:
  - field: owner_uid
    value: 0
    operation: equals
    datatype: integer
    match: all
    existence: one_or_more
```

The Test retains the sole Test capability declaration. A Filter attached to a
shared Object takes its capability from that Object; a same-capability Set
operand inherits its own referenced/inline Object's capability, not
necessarily that of the outer Test or a surrounding lexical map.
Capability mismatches SHALL fail validation. Native authoring SHALL NOT need
named/reused State registries, State references, a redundant `state:` wrapper,
or capability declarations inside local predicates. Shared Objects remain
first-class when acquisition identity or reuse matters.

## Semantics that SHALL remain intact

1. Each Filter action SHALL be explicit: `include` or `exclude`. A legacy
   omitted OVAL action imports as its effective `exclude` behavior; omission
   is not a native default.
2. Filters apply to each relevant Object/Set operand **before** the enclosing
   `union`, `intersection`, or `difference`. Preserve action order and
   existing multiplicity/Item-identity semantics; do not arbitrarily
   rearrange filters or move them across Set operators.
3. Predicate field, datatype, operation, value or typed value source, observed
   `match`, field `existence`, expected `value_match`, redaction,
   record/list fields, and nested logical expression are preserved exactly.
   Native logical grouping SHALL not introduce implicit AND/OR semantics.
4. Filter evaluation is not interchangeable with Test evaluation: a
   non-Boolean Filter-State match is a collection/evaluation **error** in the
   retained OVAL processing model, whereas a corresponding ordinary Test
   comparison can propagate a distinct non-Boolean Test status. Incomplete
   and missing collections also retain their defined status.
5. Test `existence`, Test `match`, `states_match`, and `evaluate` retain
   their original scope and truth behavior. Filtering cannot make a stopped
   or incomplete scan appear complete.
6. State references shared by multiple Tests/Filters may be **duplicated as
   immutable local predicates** in native source. Repeated conditions and
   operand positions must be preserved even where payloads are identical,
   because cardinality operators such as `one`/`odd` can be sensitive to
   multiplicity. This change does not duplicate a shared Object acquisition.
7. Source State identities, authorship/comments where present and the precise
   source-to-local-use mapping belong in separate migration provenance.
   Diagnostic/evidence references use unambiguous lexical paths or generated
   stable identities, not required author-maintained State names.

## Lossless forward conversion

OVAL 5.12.3 and earlier SCAP-NG versions may reference a named State from
several Tests and Filters. The converter SHALL resolve the full reachable
State graph and inline each effective State payload at the use site. Every
comparison and quantifier remains intact. Nested Filter/Set use sites retain
their location. Unreferenced States need not appear in runnable source but
remain available in migration evidence when exact source reconstruction is
required.

A separate reversible migration ledger MAY restore source State IDs/titles
and graph layout for a structural equivalence check; that ledger is
**non-executable** and is not required to scan native content.

A converter SHALL fail with a precise diagnostic for unresolved references,
mismatched capabilities, ambiguous wrapper collisions, unsupported predicates,
or any unproven semantic rewrite. A schema-valid source and mechanical
re-expansion alone do **not** demonstrate all runtime six-state equivalence.
Conformance also requires differential execution/semantic fixtures, including
errors and partial collections. Release scope and implementation gates are in
[#208](https://github.com/vanderpol/scap-ng/issues/208).

## Why keep Filters separate?

Combining `select` and `filters` would require specifying which comparison
fields are legal collector inputs, when filtering occurs relative to Sets and
`for_each`, how item-level errors propagate, and which evidence is retained.
That adds complexity rather than removing it. Keeping both phases is simpler
and supports independent collector-performance optimizations.

**Authoring rule:** request resources with `select`; narrow the observed Item
population with `filters`; express the compliance expectation with Test
`states` or explicit Test existence/matching.
