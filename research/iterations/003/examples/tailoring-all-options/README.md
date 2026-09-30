# Tailoring: all documented options

Start with [all-options.tailoring.yaml](tailoring/all-options.tailoring.yaml). It is a comprehensive, fictional authoring example of the current documented Tailoring surface, bound to [benchmark.yaml](benchmark.yaml). The real-source companion is [rhel9-example.tailoring.yaml](tailoring/rhel9-example.tailoring.yaml), bound to the current full RHEL9 Benchmark version `002.009.013` and its `CAT_I_Only` Profile.

This is a worked policy-resolution example. It does not introduce a separate Policy object, change the RHEL9 publication, or claim finalized serialization/NG schema or target execution. The demonstration Benchmark uses manual Assessments; its non-default `document-review` selector shows that selector names are extensible. Parameter data and source bindings are exercised by the example resolver, not a production assessor's expected-state input evaluator.

## Option coverage

| Documented option | Where it is exercised |
|---|---|
| Tailoring identity, version, title and description | Top of the all-options file |
| Exact Benchmark identity/version | `benchmark` binding; mismatched versions fail |
| Base publisher Profile | `profile: site-baseline` |
| Parent Tailoring inheritance | `extends` binds the parent identity, version and explicit relative source path |
| Re-enable a publisher-disabled Rule | `enabled_rules: demo-log-retention` |
| Disable a publisher-selected Rule | `disabled_rules: demo-time-sources` |
| Enable a Group and reverse a parent Tailoring exclusion | `enabled_groups: authentication` |
| Disable a Group | `disabled_groups: sessions` |
| Refine permitted publisher values | `parameters`; integers, a boolean, string, list and record |
| Override a parent value | Password length progresses 12 → 14 → 16 → 18 |
| Select existing named Assessment alternatives | `check_selectors`: `manual` and `document-review` |
| Justify selection and value changes | `selection_justifications`, `parameter_justifications` |
| Author, organization, creation/modification times | `provenance` |
| Approval authority/reference, ticket and exception | `provenance` |
| Effective/expiration dates and overall justification | `provenance`; metadata does not schedule or modify execution |
| Tailoring with no Profile or parent | [no-profile.tailoring.yaml](tailoring/no-profile.tailoring.yaml) |
| Separate Organizational Input | [organizational-input.yaml](organizational-input.yaml); never placed in Tailoring Parameters |
| Bind run inputs explicitly | [assessment-request.yaml](assessment-request.yaml); illustrative request binding only |
| Preserve effective policy and provenance | [resolved-policy.json](resolved-policy.json), [no-profile-resolved-policy.json](no-profile-resolved-policy.json) |
| Real RHEL9 identities, Profile and Assessment paths | [rhel9-resolved-policy.json](rhel9-resolved-policy.json) |

Supported selection lists and mappings remain visible when empty. Publisher Profiles show `disabled_rules: []` when appropriate; they never expose `enabled_rules`. Tailoring can show both because it can reverse inherited deselections. Group operations expand against the exact Benchmark version. Contradictory Group/Rule changes in the same layer fail; parent-to-child overrides are deliberate layering.

These examples express value refinement as typed Parameter overrides. They do not add a direct XCCDF `refine-value` structure or permit changing constraints, operators, collector targets or execution semantics. Unknown selectors fail rather than falling back to a default.

The Group field names, parent reference mapping, Parameter definition/constraint shapes, request/input shapes and detailed provenance/justification layout are **source grammar proposals** illustrating already documented behavior. They are not a newly approved standard. The current draft already illustrates `benchmark`, `profile`, `enabled_rules`, `disabled_rules`, `parameters` and `check_selectors`.

## Expected effective selection

| Rule | Benchmark | Publisher Profile | Parent Tailoring | Site Tailoring |
|---|---|---|---|---|
| Password length | enabled | enabled | disabled | enabled |
| Password history | enabled | disabled | disabled | enabled |
| Log retention | enabled | disabled | disabled | enabled |
| Session timeout | enabled | enabled | enabled | disabled |
| Time sources | enabled | enabled | enabled | disabled |

Organizational Input supplies the approved time-source list separately. In the comprehensive scenario the time-source Rule is excluded; supplying that value does not re-enable it, choose a method or mark it tailored. The no-Profile scenario illustrates a separate selection starting with all five member Rules enabled.

The real RHEL9 example restores `SV-257778`, excludes `SV-257777`, and selects the published manual method for enabled Rule `SV-257784`. It has `parameters: {}` because the pinned RHEL9 source exposes no publisher Parameters. Its resolved selection contains 28 of 445 Rules; the restored/excluded Rules offset each other.

## Reproduce the worked resolution

From the repository root:

```powershell
python -m pip install PyYAML==6.0.3
python tools/resolve_tailoring_example.py `
  --benchmark research/iterations/003/examples/tailoring-all-options/benchmark.yaml `
  --tailoring research/iterations/003/examples/tailoring-all-options/tailoring/all-options.tailoring.yaml `
  --organizational-input research/iterations/003/examples/tailoring-all-options/organizational-input.yaml `
  --output work/tailoring-resolved-policy.json
python tools/test_tailoring_example.py
```

The small resolver validates the examples' bindings and policy boundaries and records per-layer provenance. It does not execute Assessment Requests, evaluate targets, enforce a finalized NG schema, or implement complete missing-input result semantics. Assessment identities come from document contents; Rule filenames do not establish identity. Parent source paths and Assessment paths are explicit and bounded.

Eleven regressions cover the expected five-Rule outcome, no-Profile behavior, actual RHEL9 bindings, mismatched publication, same-layer conflicts, unknown selectors, invalid Parameter values, Organizational Input separation, prohibited execution mutations, parent identity/cycles and filename-independent Rule lookup. All passed locally and on Windows/Linux in [CI run 36783808173](https://github.com/vanderpol/scap-ng/actions/runs/36783808173). See [validation.json](validation.json).

## Rebase is a workflow

Rebase is not an additional executable Tailoring option. To target a new Benchmark version, create a candidate with a new Tailoring revision, bind the exact new publication, and review each existing Rule/Group/Parameter/selector decision. Rebase the parent layer too when necessary. Record old/new bindings and which decisions were retained, removed, mapped or require review in provenance. Existing Tailoring is never silently reused against the new version; the version-mismatch regression verifies that boundary. No automated rebase mapping is claimed here.

Specification basis: [Profiles and Tailoring](../../../../../specification/policy/profiles-and-tailoring.md) and [Parameters and Organizational Input](../../../../../specification/policy/parameters-and-organizational-input.md). Provenance: **Common** authored fictional fixture/resolver; **Inherited** current specification behavior and actual pinned RHEL9 publication; **Evidence/Audit** expected policy snapshots and negative regressions. Example names, approvals and exceptions are fictional and convey no real authorization.
