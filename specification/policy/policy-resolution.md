# Policy Resolution and Evaluation Order

**Status:** pre-alpha normative draft

This section defines how Benchmark, Profile, Tailoring, Organizational Input,
Platform, Rule applicability, and Assessment Methods compose into one
deterministic execution request.

## 1. Inputs to policy resolution

An Assessment Request identifies:

- an exact compiled Benchmark package;
- optionally, one publisher Profile;
- optionally, one Tailoring artifact compatible with that Benchmark/Profile;
- required Organizational Input values or references, each explicitly bound to the request.

A scanner SHALL NOT choose a Profile or Tailoring artifact implicitly based on
filename, directory, target identity, or local implementation convention.

## 2. Resolution order

A processor SHALL conceptually resolve policy in this order:

1. load and validate the exact Benchmark/package;
2. establish Benchmark Rule membership and default-enable every member Rule;
3. resolve the selected publisher Profile and its ancestors;
4. apply Profile Rule deselections and publisher Parameter bindings;
5. resolve and apply Tailoring layers;
6. resolve explicitly bound Organizational Input Sets and other authorized run-time policy data;
7. validate every supplied value against the bound Benchmark Parameter declaration;
8. freeze the effective Rule-selection, Assessment-selection, Parameter, and Organizational Input state for the run;
9. evaluate the Benchmark Platform expression;
10. for each effectively selected Rule, evaluate its Rule applicability
   expression;
11. execute the applicable Rule's selected Assessment Method(s);
12. emit results that identify the resolved policy state used.

An implementation MAY optimize this processing order internally, but such
optimization SHALL NOT change observable semantics.

## Explicit Organizational Input binding

An Organizational Input Set SHALL be applied only when it is explicitly bound
by the Assessment Request or by an external orchestration system that produces
an equivalent explicit request.

A scanner SHALL NOT infer or select an Organizational Input Set from:

- target hostname or address;
- target inventory;
- organization or intended-scope metadata;
- filenames or directory layout;
- ambient environment variables;
- local scanner convention.

Intended-scope metadata MAY assist operators and orchestration systems, but it
does not itself bind policy data to a run.

A bound Input Set SHALL identify the exact Benchmark identity/version for which
its values were authored. A mismatch SHALL fail policy resolution.

When a required organization-resolved Parameter is still unresolved after all
explicitly bound inputs have been processed, dependent Assessments SHALL be
reported `not_evaluated` (or the final standardized equivalent) with a
structured `missing_organizational_input` reason rather than pass, fail, or
not-applicable.

## 3. Selection before applicability

Rule selection SHALL be resolved before Rule applicability.

A Rule disabled by Profile/Tailoring is not part of the effective policy
selection and need not have its applicability evaluated.

A selected Rule whose applicability evaluates false remains part of the policy
selection and SHALL be represented as not applicable.

These states SHALL remain distinguishable in results.

## 4. Policy data before applicability/assessment

Effective Parameter and Organizational Input values SHALL be resolved before
executing any applicability or compliance Assessment that consumes them.

Missing required values SHALL NOT be guessed.

A missing required value SHALL NOT be converted into a false applicability
result or ordinary compliance failure.

## 5. Platform gate

The Benchmark Platform expression is the outer execution gate.

If the Platform expression is false, Rule compliance Assessments SHALL NOT be
executed.

If Platform evaluation is indeterminate/error, Rule compliance SHALL NOT
proceed as though the Platform were either true or false.

## 6. Rule applicability gate

For each selected Rule, its `when` expression is evaluated after the
Benchmark Platform has been established.

If `when` is true, the compliance Assessment may execute.

If `when` is false, the Rule is not applicable and its compliance Assessment
SHALL NOT execute.

If `when` is indeterminate/error, the Rule SHALL NOT receive an ordinary
pass/fail/not-applicable outcome based on guessed semantics.

## 7. Immutable execution context

Once execution begins, the effective policy context for that run SHALL be
immutable.

A scanner SHALL NOT pick up changed Tailoring, Organizational Input, shared
Assessment source, or Benchmark source midway through a run.

Compiled package identity plus resolved run inputs SHALL be sufficient to
identify the policy context used.

## 8. Result requirements

Results SHALL identify enough resolved policy state to answer:

- which Benchmark/version was used;
- which Profile, if any, was selected;
- which Tailoring, if any, was applied;
- which Rules were effectively selected;
- which Parameter/Organizational Input sources affected evaluation;
- whether each selected Rule was applicable;
- which Assessment Method produced the compliance result.

Results MAY use compact references when the immutable package and Tailoring
artifacts are available, but historical interpretation SHALL NOT depend on
mutable current source.


## 9. Check selection

A Rule MAY expose one or more named **Assessment selections**. Each selection
SHALL resolve to an Assessment Method or other assessment implementation
permitted by this specification.

When more than one selection is exposed, the Rule MAY identify a default
selection. Selection names are extensible identifiers; implementations SHALL
NOT assume that only `automated` and `manual` are valid names.

A Profile or Tailoring layer MAY select an exposed Rule Assessment selection
when the governing policy permits that choice. Selection changes which
published Assessment evaluates the Rule; it SHALL NOT rewrite the referenced
Assessment implementation.

Effective resolution is therefore:

    Benchmark -> Rule -> selected Assessment

Assessment selection SHALL be resolved and frozen with the effective policy
before applicability and compliance execution.

Different selection identifiers MAY resolve to the same Assessment Method when
the Rule intentionally exposes multiple names for equivalent technical
behavior. Shared implementation SHALL NOT erase selection identity; results
SHALL still record the effective selection.

If an explicitly requested selection does not exist for the Rule, resolution
SHALL fail. A processor SHALL NOT silently substitute the default selection or
another available choice.

Results SHALL identify the effective Rule Assessment selection and Assessment
Method used when alternatives exist.

### Authoring links versus scanner resolution

In native 0.3 source, a Rule-owned Assessment selection SHALL identify the
Assessment by **stable logical ID**. A matching Assessment must be found
unambiguously within the declared compilation source scope; when multiple
versions are eligible, the author SHALL select a specific version. Missing,
duplicate, incompatible and escaped references cause compilation failure.
Authors SHALL NOT maintain a separate Assessment index. Existing converter
outputs may temporarily use source-relative paths as a migration input only;
the compiler normalizes them to logical IDs. The package manifest binds those
IDs to immutable members, and scanners SHALL NOT infer filenames. See [Source, Compilation,
Packaging, and Integrity](../package/package-and-integrity.md#5-explicit-source-references-versus-compiled-manifest-resolution)
for the normative source-resolution, integrity and failure contract.


<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Profiles and Tailoring](profiles-and-tailoring.md) · [Contents](../README.md) · [Next: Parameters and Organizational Input →](parameters-and-organizational-input.md)

<!-- spec-nav:end -->
