# Generic OVAL six-state boundary ledger — NOT Assessment execution

**Generated from the repository reference truth tables.** No scanner, real system data or candidate field-presence alias lowering was involved.

| Generic input | Model outcome | Contract |
| --- | --- | --- |
| `OR(True,Error)` | **true** | Inherited OVAL OR |
| `AND(False,Error)` | **false** | Inherited OVAL AND |
| `ALL Items(False,Error)` | **false** | Generic Item matching |
| `At least one Item(True,Error)` | **true** | Generic Item matching |
| `Incomplete, known True, ALL` | **unknown** | Generic collected-object helper |
| `Incomplete, known False, ALL` | **false** | Generic collected-object helper |
| `Incomplete, known True, AT LEAST ONE` | **true** | Generic collected-object helper |
| `Collection flag Error` | **error** | Generic collected-object helper |
| `Collection flag Not Collected` | **unknown** | Generic collected-object helper |

**Unverified:** absent/unreadable Apache fields; Linux/DNS inherited field-policy overrides under partial data; WMI record semantics across six statuses; repeated DNS field values.

[Back to generated preview index](INDEX.md).
