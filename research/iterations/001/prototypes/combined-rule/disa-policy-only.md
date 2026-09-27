# DISA Policy-Only View — Combined-Rule Candidate

This file describes the minimum intended DISA authoring burden under the combined-rule candidate.

DISA would author the policy fields it already maintains. Automation is simply absent.

A conceptual rule contains:

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

No separate OCIL-style question is required.

If automation is later incorporated into the same rule by the benchmark automation publisher, an `assessment` member is added to the resolved automated form. The major architectural question is how this occurs while preserving policy provenance and avoiding difficult generalized overlay semantics when policy and automation originate from different organizations.

See `content/windows/policy-only.yaml` and `content/linux/policy-only.yaml`.
