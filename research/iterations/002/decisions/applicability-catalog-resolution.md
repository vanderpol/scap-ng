# Benchmark Applicability Catalog Resolution

**Status:** working design decision  
**Iteration:** 002  
**Scope:** Benchmark-scoped applicability catalogs and Rule applicability references

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Decision

A Benchmark MAY declare one applicability catalog as an explicit source
dependency.

Example:

    benchmark:
      id: disa.rhel9.stig
      applicability: applicability.yaml

      rules:
        - policy/RHEL-09-211010.yaml
        - policy/RHEL-09-211015.yaml

The applicability catalog maps stable applicability condition identifiers to
the Assessment Methods that determine those conditions.

Example:

    applicability:
      linux.gnome-installed:
        assessment: ../../shared/assessments/linux/gnome/installed.yaml

      linux.fips-enabled:
        assessment: ../../shared/assessments/linux/crypto/fips-enabled.yaml

A Rule SHALL reference applicability conditions by identifier only.

Example:

    rule:
      id: RHEL-09-000000
      when:
        - linux.gnome-installed

The Rule SHALL NOT repeat the applicability catalog path or the applicability
condition's Assessment Method path.

## Resolution semantics

A Rule applicability identifier SHALL resolve against the applicability catalog
declared by the Benchmark containing that Rule.

The effective Rule applicability is:

    Benchmark platform condition
    AND
    Rule-specific applicability condition

A Rule with no `when` property inherits only the Benchmark platform condition.

A processor SHALL NOT infer an applicability Assessment Method from:

- the applicability identifier;
- a filename or directory convention;
- a platform name;
- scanner implementation knowledge.

The author-controlled applicability catalog is authoritative for the
condition-to-Assessment relationship within that Benchmark.

## Validation

A conformant build/validation process SHALL reject:

- a Rule applicability identifier not defined by the Benchmark's declared
  applicability catalog;
- duplicate applicability identifiers within a catalog;
- an applicability entry whose Assessment reference cannot be resolved;
- an applicability entry whose referenced file is not a valid Assessment
  object;
- ambiguous resolution of an applicability identifier.

Unused applicability entries SHOULD produce a warning rather than an error.

## Rationale

Rule-level applicability conditions are commonly reused by many Rules. Repeating
the same condition-to-Assessment mapping in every Rule is redundant and creates
a synchronization hazard.

The Benchmark-scoped catalog preserves explicit author control while allowing
Rules to remain concise.

This is intentionally different from Rule compliance Assessment binding, which
usually remains an explicit forward Rule-to-Assessment reference in the Rule
policy object.

## Source organization

A typical Benchmark source tree is:

    rhel9/
      benchmark.yaml
      applicability.yaml
      policy/
        RHEL-09-211010.yaml
        RHEL-09-211015.yaml

Shared Assessment implementations may live outside the Benchmark tree:

    shared/
      assessments/
        platforms/
        linux/
          gnome/
          crypto/
          nfs/

The catalog path is explicitly declared by the Benchmark. No filename such as
`applicability.yaml` has implicit semantic meaning.

## Future specification direction

A future SCAP-NG specification SHOULD define:

- explicit Benchmark declaration of an applicability catalog;
- Rule applicability references by stable condition identifier;
- deterministic catalog resolution;
- the Boolean expression grammar for Rule applicability;
- build-time validation of every referenced condition.

The exact repository layout remains an authoring convention rather than runtime
semantics.
