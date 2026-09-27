# DISA Policy-Only View — Split Candidate

This file describes the minimum intended DISA authoring burden under the split policy/assessment/binding candidate.

DISA authors only policy rules:

```yaml
rule:
  id: ...
  title: ...
  severity: ...
  references: ...
  discussion: ...
  check: ...
  fix: ...
```

The scanner treats `check` as the default manual assessment procedure.

There is no assessment object and no binding for a policy-only rule.

An automation publisher later creates assessment and binding objects during automation development. The final scanner-facing benchmark is then built as one self-contained signed package containing the exact policy plus the matching automation.

The scanner operator never installs policy and automation separately.

See the policy files under `content/windows/policy/` and `content/linux/policy/`.
