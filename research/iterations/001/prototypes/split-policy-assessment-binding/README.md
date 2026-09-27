# Split Policy / Assessment / Binding Prototype

In this candidate architecture:

- policy rules contain authoritative requirement text and the default manual procedure;
- assessments contain reusable technical collection/assertion logic;
- bindings associate an exact policy rule with an assessment and parameters.

Policy-only rules require no assessment or binding.

The scanner-facing published SCAP-NG bundle would still be self-contained: policy, bindings, and all transitive assessment dependencies are compiled into one signed package. Scanner operators are not expected to install policy and automation separately.

This layout optimizes reuse and provenance separation but introduces mapping/reference management that must be justified by tooling and validation.
