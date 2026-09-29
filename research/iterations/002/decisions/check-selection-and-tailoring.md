# Check Selection and Tailoring

**Status:** accepted iteration-002 design decision

## Decision

In the split policy/assessment model, a Benchmark Rule references policy and
does not directly select an Assessment implementation.

Policy SHALL expose one or more named check alternatives when a Rule has
multiple valid assessment implementations. Each alternative is identified by a
**check selector** and resolves to an Assessment Method.

Effective resolution is:

    Benchmark Rule -> Policy -> selected check -> Assessment

Policy MAY identify a default check. Selector names are extensible and are not
limited to `automated` and `manual`.

Profile/Tailoring policy MAY select an exposed check selector. Selection chooses
among published alternatives; it does not rewrite executable assessment logic.

An explicit selector that does not resolve SHALL cause policy resolution to
fail. Implementations SHALL NOT silently fall back to the default or another
check.

## Why this is required

XCCDF can expose selectable check alternatives, and tailoring can use selector
semantics to choose which check is performed. Existing content can use this,
for example, to choose a manual check instead of an automated check.

A split model in which Benchmark only knows policy and policy resolves directly
to one Assessment would lose this behavior. The named-check layer preserves the
behavior without coupling Benchmark Rules directly to executable files.

## Migration requirement

Stage-1 SCAP 1.4 conversion SHALL preserve check-selection semantics.

Conversion SHALL be semantically lossless or SHALL fail explicitly. A converter
SHALL NOT silently:

- discard a selectable check;
- choose a different selector;
- fall back to a default selector;
- replace an unsupported automated check with a manual check;
- weaken or strengthen the source evaluation semantics.

New legacy constructs discovered while converting the reference STIG corpus
SHOULD become permanent migration/conformance regression tests.

## Example

Policy:

    checks:
      - selector: automated
        assessment: assessments/example.assessment.yaml
      - selector: manual
        assessment: assessments/example-manual.assessment.yaml
    default_check: automated

Tailoring:

    check_selectors:
      EXAMPLE-01-000001: manual

The tailored Rule resolves to the `manual` alternative. If `manual` is not
exposed by the governing policy, resolution fails.

## Related specification sections

- `specification/policy/policy-resolution.md`
- `specification/policy/profiles-and-tailoring.md`
- `specification/migration/scap-1.4-migration.md`
- `specification/crosswalk/scap-1.4-concept-crosswalk.md`
- `specification/core/conformance.md`
