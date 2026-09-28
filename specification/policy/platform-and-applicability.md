# Platform Specification and Applicability

**Status:** pre-alpha normative draft

## 1. Separation of roles

SCAP-NG SHALL distinguish:

1. **Platform** — product or operating-system identity;
2. **Applicability condition** — an additional reusable condition determining
   whether a Rule is relevant within the Platform population;
3. **Compliance Assessment** — whether the Rule requirement is satisfied.

All three MAY use the same underlying Assessment language, but they serve
different policy roles.

## 2. Platform

A Platform identifies a product or operating-system family/version targeted by
a Benchmark.

Examples include:

    windows.11
    windows.server-2025
    rhel.9
    oracle-linux.9

A role, feature, package, or configuration condition such as domain controller,
GNOME installed, FIPS enabled, or NFS mounted SHOULD be represented as
applicability rather than encoded into a composite Platform when the concepts
are separable.

## 3. Explicit Platform assessment binding

A Benchmark SHALL explicitly bind its Platform identities to the Assessment
Methods that determine those identities.

Illustrative authoring form:

    platforms:
      any_of:
        - id: rhel.9
          assessment: ../../shared/assessments/automated/platforms/rhel-9.assessment.yaml
        - id: almalinux.9
          assessment: ../../shared/assessments/automated/platforms/almalinux-9.assessment.yaml
        - id: rocky-linux.9
          assessment: ../../shared/assessments/automated/platforms/rocky-linux-9.assessment.yaml

The exact serialization remains subject to schema review.

A processor SHALL NOT infer the Platform Assessment from:

- the Platform identifier;
- a filename;
- a directory;
- a CPE name;
- an operating-system string;
- scanner-specific knowledge.

## 4. Applicability catalog

A Benchmark MAY explicitly reference one applicability catalog.

The catalog maps stable applicability condition identifiers to the Assessment
Methods that establish those conditions.

A Rule SHALL reference applicability conditions by identifier rather than
repeating Assessment paths.

A Rule applicability identifier SHALL resolve against the applicability
catalog declared by its containing Benchmark.

An unresolved applicability identifier SHALL be a validation error.

## 5. Effective Rule applicability

Effective Rule applicability is:

    Benchmark Platform
    AND
    Rule-specific applicability

A Rule with no Rule-specific applicability condition inherits only the
Benchmark Platform condition.

## 6. Rule `when` expressions

A Rule MAY use `when` to compose named applicability conditions.

`when` MAY support Boolean composition such as `all_of`, `any_of`, and
`not`.

`when` SHALL NOT become a second Assessment language.

Collection, query, command execution, comparison against target state, and
other Assessment implementation logic SHALL reside in Assessment Methods.

## 7. Legacy composite platforms

A SCAP 1.4 migration tool SHOULD separate legacy platform expressions into
Platform identity and reusable applicability conditions only when semantic
equivalence is exact.

When exact decomposition cannot be established, fidelity SHALL take precedence
over normalization and the source condition SHALL be preserved for review
without silently inventing reusable semantics.
