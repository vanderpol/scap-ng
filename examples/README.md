# Curated pre-alpha 0.4 Assessment examples

These four examples are **byte-for-byte copies** of current selected source
Assessments, renamed only for navigation. They illustrate different language
constructs and are validated against the local `assessment.schema.json` in CI.

| File | What it illustrates | Source scope |
| --- | --- | --- |
| [Windows lock screen](windows-server-2025-lock-screen.assessment.yaml) | Inline Registry Object and shared Test-wide field cardinality | Pinned converted Rule |
| [Linux /home nosuid](linux-home-nosuid.assessment.yaml) | Linux selector and native requirement | Owner-approved 0.4 sample |
| [Optional organizational Input](windows-optional-organizational-input.assessment.yaml) | Explicit Input guard and not-evaluated reason | Focused authoring demonstration |
| [Windows SYSVOL permissions](windows-server-2025-sysvol-permissions.assessment.yaml) | Variable expression and shellcommand acquisition | Pinned source conversion, not a permissions-scanner claim |

Examples are not independent scanner runs, live observations, global sharing
qualifications or proof promotions. **Do not use any supplied example as
evidence that a target host complies.**

Exact original paths and pinned source commit: [provenance](../docs/PROVENANCE.md).

