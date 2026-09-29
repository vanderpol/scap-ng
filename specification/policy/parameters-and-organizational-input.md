# Parameters, Tailoring Values, and Organizational Input

**Status:** pre-alpha normative draft

## 1. Parameter

A Parameter represents typed policy data.

A Parameter SHALL define:

- stable semantic identity;
- data type;
- human-readable description;
- whether the value is publisher-defined or organization-defined;
- publisher value/default when one exists;
- validation constraints needed to determine whether a supplied value is
  valid.

SCAP-NG SHALL NOT restrict Parameters to a single text string.

The type system SHOULD support scalar and structured values needed by real
policy, including strings, booleans, numbers, versions, paths as data values,
collections, and structured records.

## 2. Tailoring versus Organizational Input

SCAP-NG SHALL distinguish Tailoring from Organizational Input.

**Tailoring** changes an already-resolved publisher policy decision.

**Organizational Input** supplies expected policy state intentionally left
unresolved by the publisher.

Supplying required Organizational Input SHALL NOT by itself mark a Rule as
tailored.

A user SHALL NOT be required to create a Tailoring artifact merely to provide
required Organizational Input.

## 3. Assessment input binding

An Assessment Method MAY consume a Parameter only through an explicitly typed
input binding.

Parameter values SHALL be usable only as policy/expected-state data.

## 4. Policy-data isolation

Values supplied through a Benchmark, Profile, Tailoring artifact,
Organizational Input set, interactive entry, API, or external input file SHALL
NOT:

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

## 7. Value provenance

Results SHALL preserve the source of effective Parameter values sufficiently to
distinguish at least:

- publisher Benchmark value;
- publisher Profile value;
- Tailoring override;
- persistent Organizational Input;
- interactive run-time input;
- API/integration supplied input;
- declared default.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Policy Resolution](policy-resolution.md) · [Contents](../README.md) · [Next: Assessment Method →](../assessment/assessment-method.md)

<!-- spec-nav:end -->
