# Issue #14 selector contract batch 02: high-usage string selectors

This draft is stacked on draft PR #17 and keeps PRs #15, #16, and #17
unmerged pending owner approval.

## Priority and coverage

The repository does not contain the bulk converted STIG corpus, so the
capability-catalog counts are usage proxies rather than scanner-execution
claims. This batch selects high-usage, single-field or all-string capabilities
whose pinned OVAL object type and existing mapping are unambiguous.

| Capability | Usage proxy | Resolved selectors |
|---|---:|---|
| `windows.service` | 12 | `service_name` |
| `unix.shadow` | 10 | `username` |
| `unix.password` | 8 | `username` |
| `unix.interface` | 7 | `name` |
| `linux.dpkginfo` | 6 | `name` |
| `linux.systemdunitproperty` | 3 | `unit`, `property` |
| `linux.selinuxboolean` | 3 | `name` |
| `linux.systemdunitdependency` | 2 | `unit` |
| **Batch total** | **51** | **9 selectors** |

Coverage moves from 19 resolved / 122 unresolved to **28 resolved / 113
unresolved of 141**.

## Source and semantic boundary

The existing mappings pin each capability to its OVAL 5.12.3 definitions
schema and object. The reviewed object entities are `EntityObjectStringType`:

- `windows.service.service_name`
- `unix.shadow.username`
- `unix.password.username`
- `unix.interface.name`
- `linux.dpkginfo.name`
- `linux.selinuxboolean.name`
- `linux.systemdunitdependency.unit`
- `linux.systemdunitproperty.unit` and `property`

Each retains the five source string operations through the separate crosswalk:
`equals`, `not equal`, `case insensitive equals`, `case insensitive not
equal`, and `pattern match` map to native `equals`, `not_equal`,
`case_insensitive_equals`, `case_insensitive_not_equal`, and `matches_regex`.
Native selectors never accept the source spelling `pattern_match`.

The batch does not infer account-name, service-name, interface, package,
SELinux, or systemd provider behavior from string syntax. State fields remain
separate from object selectors, and collection errors remain errors rather
than absence.

## Reconciliation safeguard

The generator now reconciles every generated selector inventory against the
resolved contract source and validates every declared batch count. The emitted
`docs/metadata/native-selector-audit.json` records the generated total,
resolved/unresolved totals, source resolved count, and per-batch declared versus
actual selector counts. Tests assert these reconciliations and fail if a future
report claims a different total.

## Validation

```text
python tools/generate_native_selector_schema.py --check
python tools/generate_docs.py --check
python -m unittest discover -s tests -v
```

The 18-test suite includes positive, negative, boundary, variable/list,
unknown-key, generic-operator, and legacy-spelling checks for both batches.
Existing examples, generated artifacts, and the 0.4.0 provenance boundary
remain intact.

## Unresolved

Runtime collector equivalence, platform/provider case behavior, account and
service authority resolution, regex engine qualification, and scanner proof
remain outside this schema-only batch.
