# ESXi host accounts — `esx.host_account`

**Status:** draft 0.2.0 native contract with synthetic observations. No live
VMware collector or complete comparator conformance is established.

## Object and acquisition

Target one identified ESXi host. `select.account_name` is a required, nonnull
string predicate; the Object retains its capability and can be reused by Tests
and Variables. Named Objects, shared Sets/filters and compatible States use the
[shared behavior](shared-behavior.md). A Test consumes the selected Object.

The source illustrates `Get-VMHostAccount`; it does not mandate PowerCLI.
Collectors SHALL acquire account data from the assessed host/context, not the
scanner host's account database. An acquisition error SHALL NOT be represented
as a successful empty account population. When names coincide across domains,
retain each account observation and its domain; do not merge by name alone.
The source does not provide a domain Object selector: comparison/filtering may
use the domain State field without inventing an additional selector.

## State and Item field reference

All five fields are scalar, optional observations and available for comparison.
Omitted/nonexistent/uncollected/error values are not empty strings or false.

| Native field | Datatype | Meaning | Source field |
| --- | --- | --- | --- |
| `account_name` | string | Account name on the assessed host. | `account_name` |
| `domain` | string | Domain to which this account belongs. | `domain` |
| `description` | string | Descriptive account information. | `description` |
| `shell_access_enabled` | boolean | Whether the account has ESXi shell access. | `shell_access_enabled` |
| `role` | string | Granted host-account role; no closed role enum. | `role` |

Present collected string payloads SHALL be JSON strings; shell-access payloads
SHALL be JSON Booleans. The Boolean false differs from an unavailable value.
No resolved UID/SID or effective-permission assertion is inferred from these
fields. Host-account `role` is observed data, distinct from a policy Rule's role.

## Tests, reporting and examples

[Standalone examples](../../../tests/esx-host-0.2.0/README.md) select synthetic
`audit-user` and require shell access false. False satisfies this requirement;
true fails it. These are fixture expectations, not universal security policy.
Compared reporting retains the compared field and required account/domain
identity supplied by recorded field-use evidence. Default `all` also reports
available description/role fields; confidentiality uses redaction independently
of `reported_elements`. No account data was collected from a real host.

## Provenance and gaps

[Mapping](../../../schema/v0.2.0/capability-mappings/experimental/esx.host_account.json)
adapts `host_account_test/object/state/item` from the [pinned new-Test XSDs](../../../third_party/oval-6.0-new-tests/README.md).
Descriptions also appear in generated schemas. Native syntax reuses NG
primitives; existing 5.12.3 behavior and 0.1.0 mappings are unchanged.

Live acquisition, permission-denied behavior, account/domain correlation,
Variable/Set/filter execution and independently reviewed vendor results remain
open in #128/#131. Classification: Adapted fields/types, Inherited licensed
source, Common native reference/content, Evidence/Audit synthetic fixtures.
