# SCAP-NG 0.4 examples

Four curated Assessments illustrate current authoring syntax. They are validated against the local 0.4 Assessment schema in CI.

| Example | Demonstrates |
| --- | --- |
| [Windows Registry](windows-server-2025-lock-screen.assessment.yaml) | Compact inline Object, Item and Field requirements |
| [Linux /home nosuid](linux-home-nosuid.assessment.yaml) | Mount selection and matching |
| [Optional organizational Input](windows-optional-organizational-input.assessment.yaml) | Input presence guard and `not_evaluated` fallback |
| [Windows SYSVOL permissions](windows-server-2025-sysvol-permissions.assessment.yaml) | More complex expression and shellcommand acquisition |

Start with Windows Registry or Linux. The permissions example is a source conversion, **not** proof of native permissions-scanner support. The optional Input example demonstrates Assessment-level `input_provided` branching, **not** a complete Rule-level organizational Input dependency mapping; the latter has an [open 0.4 contract gap](https://github.com/vanderpol/scap-ng/issues/8).

These examples illustrate syntax; they do not establish runtime behavior, independently prove conversion equivalence, or demonstrate that any host complies. For original source paths and pinned provenance, see [provenance](../docs/PROVENANCE.md).

Historical conversion evidence is managed separately in [SCAP-NG evidence](https://github.com/vanderpol/scap-ng-evidence), but its obsolete October 30 draft corpus has been retired from current project navigation. **There is not yet a current-schema-qualified downloadable 65-benchmark library.** See the [publication and retirement tracker](https://github.com/vanderpol/scap-ng-evidence/issues/1). Do not treat historical DRAFT content as current authoring examples or independently proved Assessments.
