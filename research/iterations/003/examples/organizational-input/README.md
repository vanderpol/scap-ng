# Organizational Input worked example

**Status:** pre-alpha **integration research fixture**, not an end-to-end scanner validation.
The Assessment now uses the *supported* `linux.partition` capability and a
consumer-local Object/State. Direct `value.input` binding remains a separate
unproven evaluator/compilation capability (issue #193).

An illustrative publisher delegates the allowed filesystem types for the
`/home` mount to the organization. The organization approves `ext4` and
`xfs`. The Assessment selects the `/home` partition and checks its reported
`fs_type` against the approved values. These values are fictitious, not DISA
requirements. This scenario does not claim the organization may override a
publisher-defined requirement.

1. `benchmark-parameter.yaml`: unresolved typed Parameter `approved_filesystem_types`.
2. `rule-fragment.yaml`: binds Parameter to Assessment `approved-filesystem-types-input`.
3. `home-filesystem.assessment.yaml`: independent `linux.partition` Test with
   `fs_type` State consuming the approved input directly.
4. `site.organizational-input.yaml`: organization-approved values and attribution.
5. `assessment-request.yaml`: explicit request-time Input Set reference.
6. `resolved-context.yaml`: illustrative resolved binding and missing-input result.

Files are illustrative fragments and a research Assessment, **not** a complete
schema-valid Benchmark/Rule package. Missing approved input yields
`not_evaluated` with `missing_organizational_input`. The Input Set cannot
change collector selectors, operations or executable Tests. The proposed
`in` comparison is research only; this fixture retains explicit
`equals` and `variable_match: one_or_more` semantics.

Template generation is the publisher/build's primary responsibility for
predeclared organization inputs; scanner-generated templates for arbitrary
Rule/State Tailoring remain a separate Board research topic (#196).
