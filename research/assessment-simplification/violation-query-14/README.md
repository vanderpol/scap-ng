# Violation-query modernization research

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**

## Question

Should OVAL content that collects only noncompliant Items and then requires
`none_exist` be rewritten as a positive statement such as "all target Items
satisfy State X"?

Representative RHEL 9 Rules:

- SV-257918 — system commands owned by root;
- SV-257919 — system commands group-owned by a system group;
- SV-257920 — library files owned by root;
- SV-257921 — library files group-owned by root;
- SV-257922 — library directories owned by root; and
- SV-257923 — library directories group-owned by a system group.

The manual procedures use the same violation-query mental model: run `find`
for objects that violate the requirement; any output is a finding.

## Corpus signal

In the maintained converted RHEL 9 corpus:

- **41** automated Assessments contain `existence: none_exist`;
- **12** contain both `none_exist` and at least one `action: exclude` Filter;
- the six Rules above form one especially uniform `unix.file` family; and
- the same textual conjunction was not found in the maintained Windows Server
  2025 automated corpus.

The other six RHEL matches are heterogeneous, so this is a recurring idiom but
not one security-domain concept.

## Faithful source shape

Condensed SV-257918:

```yaml
collect:
  capability: unix.file
  select:
    path:
      value:
        variable: system-command-directories
    filename:
      operation: pattern match
      value: .*
  filters:
    - action: exclude
      match:
        field: user_id
        operation: equals
        value: 0
    - action: exclude
      match:
        field: type
        operation: equals
        value: symbolic link
    - action: exclude
      match:
        field: type
        operation: equals
        value: directory
  behaviors:
    recurse_direction: down

assert:
  existence: none_exist
```

The first Filter removes compliant Items. The remaining collected Items are
violations, and `none_exist` means pass only when no violation remains.

## Tempting positive form

A human-oriented form would be easier to read:

```yaml
target:
  capability: unix.file
  # same directory/type scope

require:
  each:
    field: user_id
    operation: equals
    value: 0
```

That says the requirement directly, but it is **not** automatically equivalent
to the source graph across all OVAL results.

## Executable result proof

Focused fixtures:

- `tools/research_violation_query_semantics.py`
- `tools/test_research_violation_query_semantics.py`

For Boolean State results, the two interpretations agree.

| Collection | Requirement observations | Violation query | Positive universal |
| --- | --- | --- | --- |
| complete | no target Items | true | true |
| complete | all true | true | true |
| complete | any false | false | false |
| incomplete | only true seen | unknown | unknown |
| incomplete | any false seen | false | false |

The counterexample is Filter-State failure behavior.

SCAP-NG's retained OVAL processing model treats a non-Boolean Filter State
result as a collection/evaluation **error**. Ordinary State aggregation
preserves `unknown`, `not evaluated`, or `not applicable`.

Therefore:

| Requirement State | Violation query | Positive universal |
| --- | --- | --- |
| unknown | **error** | unknown |
| not evaluated | **error** | not evaluated |
| not applicable | **error** | not applicable |
| error | error | error |

There is also an incomplete-stream counterexample: a seen violating Item plus
another Item whose Filter State is unknown makes the source Object/Test
`error`, while a universal check can already be decisively `false`.

One counterexample is enough to reject an independent automatic rewrite.

## Decision

**Do not rewrite this OVAL idiom into ordinary positive Test semantics.**

The six-file family does not justify another 0.3.0 evaluation primitive.

If a positive authoring spelling is ever added, it should be presentation
shorthand whose normative meaning **desugars to the existing violation-query
graph**:

1. collect the target Items;
2. exclude Items whose requirement State is true;
3. preserve Filter non-Boolean error behavior; and
4. assert `none_exist`.

That preserves zero-item vacuity, incomplete-collection behavior, Item evidence,
and source error semantics.

For 0.3.0, the simpler recommendation is to rely on the existing locality work:

- inline private Filter States next to the Object;
- use meaningful labels such as `violations` / `compliant-items` in examples;
- keep `none_exist` explicit; and
- avoid adding a new semantic operator unless author feedback shows the
  remaining form is still materially difficult to understand.

## Before/after conclusion

The readability problem is mostly presentation, not missing evaluation power.

A concise, localized violation query is already close to the STIG manual's
mental model: "find noncompliant files; there must be none." Turning it into a
separate universal-quantification semantic would add risk without enough
benefit.

## Human status

**pending-review**

Recommendation: no new semantic feature for this family in 0.3.0.
