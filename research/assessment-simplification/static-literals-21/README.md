# Static literal collections versus Variables

**Status:** research only; not accepted 0.3 semantics.

Tracked by [#169](https://github.com/vanderpol/scap-ng/issues/169) and
[#185](https://github.com/vanderpol/scap-ng/issues/185).

## Design question

Should SCAP-NG require a named Variable for fixed author-supplied values, or
should Objects, States, and Variable expressions accept native literal values
and literal collections directly?

## OVAL serialization background

OVAL Object and State entities are XML simple-content elements. A simple entity
holds one lexical value. If `var_ref` is present, OVAL Schematron requires the
entity body to be empty and requires `var_check`.

An OVAL `constant_variable`, by contrast, allows one or more `value` children.
The OVAL 5.12.3 documentation says Variable values are treated as though they
were inserted where the Variable is referenced.

For constant/static values, this means a Variable often supplies cardinality
that the XML entity representation cannot express directly. SCAP-NG should
preserve the semantics without automatically preserving that serialization
workaround.

Dynamic Variables remain a different concept. Object-derived values, `concat`,
`merge`, `regex_capture`, `split`, arithmetic, Variable-to-Variable graphs, and
external/Organizational Input bindings represent real runtime dataflow and
remain first-class.

## Six-benchmark evidence

The current modernized six-benchmark candidate contains 29 named constant
Variables:

- 11 list-valued constants;
- 18 scalar constants.

### List-valued constants

All 11 are consumed only as literal value sets in Object or State entities:

| Scope | Constant Variables | Consumer references |
| --- | ---: | ---: |
| Object only — what to collect | 8 | 19 |
| State only — what must match | 3 | 7 |
| Shared across Object and State | 0 | 0 |

Reuse is small and local to one Assessment:

| References within the Assessment | Constant Variables |
| ---: | ---: |
| 2 | 9 |
| 3 | 1 |
| 5 | 1 |

Examples include fixed system-directory lists and regex lists in Objects, and
fixed Windows permission sets in States.

This supports separate Object and State locality: the same constant value set
is not being reused across collection scope and expectation scope in this
sample.

### Scalar constants inside dynamic Variables

The remaining 18 scalar constants are used as operands of genuine derived
Variable expressions such as `concat`. The derived Variable still represents
runtime computation and should remain a Variable; the fixed scalar operand does
not need its own named constant Variable.

Illustrative direction:

```yaml
variables:
  derived_path:
    kind: local
    expression:
      concat:
        - literal: /etc/dconf/db/
        - variable: database_name
        - literal: .d/locks
```

not three separate named constant Variables solely to provide the prefix and
suffix.

## Proposed native rule

1. Object and State entities MAY consume a typed literal collection directly.
2. The value comparison quantifier remains explicit. A literal array does not
   silently mean `any`.
3. Dynamic Variables remain named when they represent runtime dataflow.
4. Fixed scalar operands MAY appear directly inside dynamic Variable
   expressions.
5. A named constant value set remains available when reuse or an intentional
   domain name improves readability; it is not required by serialization.

Illustrative Object value set:

```yaml
path:
  value:
    - /lib
    - /lib64
    - /usr/lib
    - /usr/lib64
  datatype: string
  operation: equals
  value_match: only_one
```

Illustrative State value set:

```yaml
permission:
  value:
    - read
    - execute
  datatype: string
  operation: equals
  value_match: all
```

Names above are illustrative; exact vocabulary remains subject to the existing
OVAL/NG vocabulary rules.

## Semantic requirement

Native arrays must preserve OVAL `var_check` semantics. Source content uses
multiple quantifiers, including `all`, `at least one`, and `only one`, with
different comparison operations. A bare array with implicit OR semantics would
not be a lossless conversion.

## Complexity/value assessment

This approach adds a native value shape, but no scheduling, iteration,
collection fan-out, artifact identity, result type, or cross-Assessment
dependency. It therefore has a substantially smaller semantic/runtime surface
than constructs intended for dynamic collection-derived values.

## Promotion proof required

Before any schema change:

1. prove Object list-value round-trip independently;
2. prove State list-value round-trip independently;
3. preserve datatype, operation, and value quantifier exactly;
4. test empty, singleton, duplicate, invalid/mixed datatype, record, and
   six-state/error cases;
5. prove literal operands inside `concat`/other supported functions without
   removing the dynamic Variable node;
6. retain named constants when deliberate reuse is clearer than repetition;
7. measure the full corpus only at the next intentional milestone checkpoint.

## Current recommendation

Continue the bounded proof. If the edge cases remain exact, make native literal
collections the default conversion for static values and reserve named
Variables for real dataflow, external input, or intentional reuse.
