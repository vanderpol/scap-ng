# User-Supplied Inputs / Organizational Values

**Status:** working design decision for OVAL Board review  
**Iteration:** 002  
**Scope:** split policy / assessment source model

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Core distinction

SCAP-NG SHALL distinguish **Tailoring** from **Organizational Input**.

- **Tailoring** changes an already-resolved publisher policy decision.
- **Organizational Input** supplies a value the publisher intentionally left
  unresolved because the organization must define it.

Supplying a required Organizational Input is not, by itself, Tailoring and
SHALL NOT cause a rule to be reported as publisher-policy-modified.

A user SHALL NOT be required to create a Tailoring artifact merely to execute
a Profile containing unresolved organizational Parameters.

Example:

    publisher value: password_minimum_length = 15
    local value:     password_minimum_length = 18

This is Tailoring.

By contrast:

    publisher value: approved_time_sources = unresolved
    local value:     [ntp1.example.mil, ntp2.example.mil]

This is Organizational Input.

## Parameter definition, Assessment Method, and Assessment Request

SCAP-NG SHOULD distinguish three responsibilities.

1. The **Benchmark/policy layer** defines the semantic Parameter: identity,
   description, type constraints, whether it is publisher-defined or
   organization-defined, and any publisher value/default.
2. The **Assessment Method** declares a typed expected-state input slot that it
   consumes. It does not contain local organizational values.
3. The **Assessment Request** (run manifest) binds a Benchmark/Profile and
   optional Tailoring and supplies or references Organizational Input values.

Conceptually:

    benchmark parameter:
      approved_time_sources:
        type: set<string>
        requirement: organizational
        required: true

    rule binding:
      assessment_input: expected_sources
      parameter: approved_time_sources

    assessment method:
      inputs:
        expected_sources:
          type: set<string>
          role: expected_state

    assessment request:
      organizational_inputs:
        approved_time_sources:
          - ntp1.example.mil
          - ntp2.example.mil

An Assessment Request MAY embed Organizational Input values directly or
reference a separately managed Organizational Input set. Interactive scanner
entry, an API, or another authorized input mechanism MAY populate the same
logical bindings at run time.

## Policy-data isolation

Values originating from Profiles, Tailoring, Organizational Input, interactive
input, APIs, or external input files SHALL be treated solely as typed policy
data.

Such values MAY participate as operands representing expected state.

Such values SHALL NOT:
- select or replace an Assessment Method;
- alter collection targets or collection behavior;
- supply commands, scripts, SQL, XPath, shell fragments, interpreter input, or
  other executable/query language;
- choose collectors, plugins, operations, comparison operators, or privileges;
- otherwise alter scanner execution semantics.

The assessment schema SHOULD make parameter references legal only in
State-equivalent expected-value positions.

This is intentionally stricter than historical OVAL, where external variables
could participate in broader object/component structures.

## Typed values

SCAP-NG SHALL NOT limit Organizational Input to a single text string.

The type system SHOULD support, at minimum, consideration of:
- string;
- boolean;
- integer / decimal;
- version;
- path as a data value, not a collection target;
- list<T>;
- set<T>;
- map<K,V>;
- structured record/object.

Validation MAY include allowed values, numeric ranges, uniqueness, and
field-level requirements. Expression-bearing values require separate security
review because a regex or similar mini-language is executable semantics, not
merely passive data.

## Missing required Organizational Input

A required Organizational Input with no effective value SHALL NOT be guessed.

Unless a declared policy default applies, an assessment dependent on the
missing value SHALL return a result that clearly identifies unresolved policy
input, such as `not_evaluated` / `not_checked`, according to the final NG
result vocabulary.

Content MAY explicitly declare an empty/default value when an empty value has
real policy meaning. Missing required input SHALL NOT silently become empty.

## Provenance

The source of every effective Parameter value SHALL be retained.

At minimum, result provenance SHOULD distinguish:
- publisher Benchmark value;
- publisher Profile value;
- Tailoring override;
- persistent Organizational Input set;
- interactive run-time entry;
- API/integration supplied value;
- declared default.

A Rule result SHALL indicate when a Tailoring action modified publisher policy.
A Rule result SHALL separately indicate when Organizational Input was required
to complete an otherwise unresolved publisher requirement.

These states are semantically different and SHALL NOT be collapsed into a
single `tailored=true` indicator.

## SCAP 1.4 analog

| SCAP-NG concept | SCAP 1.4 analog | Relationship |
| --- | --- | --- |
| Parameter | XCCDF Value + OVAL external variable contract | expanded and strongly typed |
| Organizational Input | XCCDF interactive Value / check-export / OVAL external variable | separated from Tailoring |
| Tailoring override | XCCDF Tailoring/Profile set-value/refine-value | direct descendant with stronger provenance |
| Assessment Method input | OVAL State/external-variable use | restricted to expected-state operands |
| Assessment Request | no single direct analog | new orchestration artifact |

## Open questions for Board review

- Final primitive/structured type set.
- Final missing-input result vocabulary.
- Whether a standalone Organizational Input Set is normative or only a
  reusable serialization used by Assessment Requests.
- Required privacy/redaction behavior for locally sensitive values.
- Exact schema restrictions for safe State-equivalent parameter references.
