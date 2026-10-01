# Parameters and Organizational Input

**Status:** pre-alpha normative draft

## 1. Parameter

A Parameter represents typed policy data that exists independently of any one Assessment execution.

SCAP-NG does **not** retain XCCDF `Value` as a native construct. Valid XCCDF
`Value` content is migrated into Parameters and policy/input bindings.

A Parameter SHALL define:

- stable semantic identity;
- data type;
- human-readable description;
- whether resolution is publisher-defined or organization-defined;
- publisher value/default when one exists;
- cardinality;
- validation constraints needed to determine whether a supplied value is
  valid.

SCAP-NG SHALL NOT restrict Parameters to a single text string.

The type system SHOULD support the typed values and cardinalities legitimately
needed as Assessment inputs, including strings, booleans, numbers, versions,
paths as data values, lists/sets, and structured records. Parameter typing
SHOULD align with the Assessment input type system rather than creating a
separate XCCDF-compatible type island.

## Parameter versus Assessment Variable

A Parameter and an Assessment Variable are different concepts.

A **Parameter** is policy-layer data resolved before Assessment execution. Its effective value may come from the Benchmark publisher, a publisher Profile,
or—only when intentionally unresolved by the publisher—from Organizational
Input, an API, or interactive input according to the rules below. Native
Tailoring SHALL NOT override Parameter values.

An **Assessment Variable** is part of the Assessment's executable/dataflow graph
and may derive values from literals, other Variables, Objects/Items, functions,
or explicitly bound external inputs.

An Assessment SHALL consume a Parameter only through an explicit typed input
binding. Binding a Parameter to an Assessment Variable or other declared input
SHALL NOT make the Parameter part of the executable Assessment graph.

Policy resolution SHALL freeze effective Parameter values before ordinary
Assessment execution. Assessment execution SHALL NOT mutate the effective
policy Parameter value.

## 2. Tailoring versus Organizational Input

SCAP-NG SHALL distinguish Tailoring from Organizational Input.

**Tailoring** changes only the native policy surfaces explicitly permitted by
the Tailoring specification, such as Rule selection and published Assessment
selection. It SHALL NOT replace an already-resolved publisher Parameter value.

**Organizational Input** supplies expected policy state intentionally left
unresolved by the publisher.

Supplying required Organizational Input SHALL NOT by itself mark a Rule as
tailored.

A user SHALL NOT be required to create a Tailoring artifact merely to provide
required Organizational Input.

## Organizational Input priority and lifecycle

Organizational Input is a first-class policy-resolution mechanism, not a
Tailoring convenience.

A Benchmark publisher SHOULD use Organizational Input when the requirement
itself explicitly delegates a value to the deploying organization, site,
mission, system owner, or other authorized authority and no universal publisher
value can be asserted.

An Organizational Input declaration SHOULD identify:

- stable Parameter identity;
- expected datatype and cardinality;
- human-readable prompt/description;
- validation constraints;
- whether a value is required before the dependent Assessment can run;
- provenance/authority metadata expected for the supplied value;
- whether the value may be reused persistently across runs or must be supplied
  per Assessment Request.

The supplied value SHALL be validated before execution and SHALL become part of
the frozen effective policy context for the run. Results SHALL preserve enough
provenance to distinguish who/what supplied the value and under which
organizational authority.

Organizational Input SHALL NOT be used to override a concrete publisher
requirement. If the publisher says X, supplying Y is not Organizational Input;
it is a different policy.

## Publisher Profile Parameter refinement

A publisher Profile MAY resolve a publisher-defined Parameter differently from
the Benchmark baseline, including selecting a different publisher value and,
when required by migrated semantics, a different publisher-defined validation
constraint set.

Only publisher-controlled Benchmark/Profile layers MAY alter Parameter
constraints. Organizational Input SHALL provide values within the effective
constraints and SHALL NOT redefine datatype, cardinality, bounds, patterns,
allowed values, or other validation semantics. Tailoring SHALL NOT provide or
override Parameter values.

This rule provides the native target for legacy XCCDF `refine-value` semantics
without retaining XCCDF selector machinery as a native language feature.

## Publisher requirement versus organization-authored policy

When a Benchmark publisher defines a concrete Parameter value as part of the
requirement, that value is part of the publisher's policy. A native Tailoring
artifact SHALL NOT substitute a different expected value while continuing to
present the result as evaluation against the publisher's policy.

If an organization intentionally adopts a different requirement, it SHALL
publish or otherwise identify a distinct organization-authored policy/Benchmark
(or a future standardized derived-policy artifact) with its own provenance and
identity. Evaluation against that local policy is not a tailored evaluation of
the unchanged publisher requirement.

This preserves a simple audit rule: a result claiming evaluation against a
publisher Benchmark/Profile uses that publisher's resolved Parameter values.
Differences in expected values are visible as differences in policy identity,
not hidden inside Tailoring.

This rule does not apply when the publisher deliberately leaves the expected
value unresolved for the organization. In that case, Organizational Input
supplies the missing value without creating a different policy requirement.

## 3. Assessment input binding

An Assessment Method MAY consume a Parameter only through an explicitly typed
input binding.

Parameter values SHALL be usable only as policy/expected-state data.

## 4. Policy-data isolation

Values supplied through a Benchmark, Profile, Organizational Input set,
interactive entry, API, or external input file SHALL NOT:

- select or replace an Assessment Method;
- alter collection targets or collection behavior;
- supply commands, scripts, SQL, XPath, shell fragments, or interpreter input;
- select collectors/plugins;
- select comparison operators;
- alter privileges;
- otherwise modify executable Assessment semantics.

This restriction is a security boundary.

## 5. Missing required input

A required Organizational Input with no effective value SHALL NOT be guessed.

Unless an explicit policy default applies, an Assessment dependent on missing
required input SHALL NOT produce an ordinary pass or fail result.

The final standardized not-evaluated/not-checked vocabulary remains under
design.

## 6. Assessment Request

An Assessment Request SHOULD identify the Benchmark/Profile being assessed and
bind any Tailoring and Organizational Input needed for that run.

Organizational Input MAY be embedded in the request or referenced from a
separately managed input set.

## XCCDF Value migration

Valid XCCDF 1.2 `Value` semantics SHALL be migrated without requiring a native
XCCDF-style Value object.

The migration mapping is:

- XCCDF `Value` -> SCAP-NG Parameter;
- unselected/base XCCDF value -> Benchmark Parameter value/default;
- XCCDF datatype and constraints -> Parameter datatype/cardinality/constraints;
- `prohibitChanges` -> migration provenance describing whether legacy XCCDF permitted value mutation; native SCAP-NG does not use this flag to permit Tailoring Parameter overrides;
- `check-export` -> explicit typed Assessment input binding;
- Profile `set-value` / `set-complex-value` -> publisher Profile Parameter
  value binding;
- Profile `refine-value` -> resolved publisher Profile Parameter value and
  effective constraint set;
- legacy Tailoring value changes -> a distinct organization-authored policy/Benchmark (or an explicitly defined future derived-policy artifact), not a native Tailoring Parameter override.

Legacy selector names and source IDs MAY be retained in migration provenance,
but native execution SHALL depend on the resolved Parameter semantics rather
than XCCDF selector tags.

When an XCCDF cluster operation targets multiple Values, migration tooling SHALL
resolve and expand the operation deterministically to the affected native
Parameters while retaining provenance of the source cluster operation.

A legacy construct that cannot be represented without loss SHALL fail migration
explicitly rather than silently coercing the value.

## 7. Value provenance

Results SHALL preserve the source of effective Parameter values sufficiently to
distinguish at least:

- publisher Benchmark value;
- publisher Profile value;
- organization-authored policy value, when evaluating a separately published local Benchmark;
- persistent Organizational Input;
- interactive run-time input;
- API/integration supplied input;
- declared default.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Policy Resolution](policy-resolution.md) · [Contents](../README.md) · [Next: Assessment Method →](../assessment/assessment-method.md)

<!-- spec-nav:end -->
