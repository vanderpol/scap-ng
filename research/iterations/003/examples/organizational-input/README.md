# Organizational Input worked example

**Status:** pre-alpha design fixture

This example demonstrates an organization-defined expected value without
Tailoring the publisher requirement.

Scenario: the publisher requires a system to use the organization's approved
time sources, but cannot publish the actual server names because they are
site-specific.

The flow is:

```text
Benchmark Parameter declaration (unresolved)
        ↓
explicit Rule -> Assessment input binding
        ↓
Organizational Input Set supplies the value
        ↓
Assessment Request explicitly binds that Input Set
        ↓
policy resolution validates + freezes the value
        ↓
Assessment executes against the supplied expected state
```

The important boundaries are:

- the Benchmark declares **what input is required**, its type/cardinality and
  constraints;
- the Assessment declares **what typed input it consumes** without knowing the
  Benchmark Parameter ID;
- the Rule binds the Benchmark Parameter to the selected Assessment input;
- the organization supplies the value in a separate versioned Input Set;
- the Assessment Request explicitly chooses the Input Set;
- scope metadata never causes implicit scanner selection;
- missing required input produces `not_evaluated` with
  `missing_organizational_input`, not pass/fail/not-applicable;
- Organizational Input cannot select Tests, change collection, inject commands,
  or otherwise modify executable Assessment semantics.

All names, people and organizations below are fictional.
