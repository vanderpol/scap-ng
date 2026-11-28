# Canonical Set and Filter replay

The replay reads the existing [Assessment](../cases/core/set-filters.assessment.yaml),
[supplied Items](../fixtures/core-set-filters.json) and
[independent expected populations](../expected/core-set-filters.json).
Current RI compiles the authored filters and resolves the Sets through
both its in-memory and streaming implementations. All eight cases
matched the expected member identities in source order.

Four controls preserve distinctions that matter to authors. A difference
with an incomplete right operand carries partial membership and remains
incomplete. Duplicate identities within one operand, an errored filter
field and cancellation produce explicit diagnostics. The
[RI receipt](ri-receipt.json) records both implementations for each case.

The [scale receipt](scale.json) records six pinned streaming test runs.
Union and intersection retained one identity per shared input member.
Difference of the identical operands returned zero Items. Each operator
ran with 100,000 and 1,000,000 Items per operand. RI's two existing shared
resource-budget checks also passed. These runs exercise streaming membership
and resource accounting. Host acquisition, Rule/Assessment execution and
scan-wide concurrency remain separate.

```sh
python conformance/tools/replay_set_filters.py --check \
  --ri /path/to/pinned/scap-ng-ri
```

- [RI pinned streaming scale test](https://github.com/vanderpol/scap-ng-ri/blob/ca4fabfe18f167115ecb455d47728cd3ae36837c/runtimecore/set_scale_test.go)
- [Large execution evidence](https://github.com/vanderpol/scap-ng-evidence/issues/3)
