# Experimental feature contracts, version 1

These are proposals, not changes to the established schema, converter or scanner contract. The YAML files are research notation; generic `required_key_coverage`, `record_identity`, `collection_contract`, table expansion and proposed collector capabilities are not accepted v0.1.0 fields. They SHALL NOT be fed to production tooling as ordinary content. A readable sketch is not a complete collector implementation.

## Finding 1: finite authoring tables before adding runtime features

Repeated finite requirements MAY be authored as rows and expanded **at publication time** to existing named Objects, States, Tests and evaluate logic. This is reusable tooling, not a runtime loop, a new Test family or input-dependent test selection. Organizational Input SHALL NOT add/remove rows or choose templates. Tables SHALL be publisher-owned, finite, typed and immutable for a published assessment revision.

`phase: authoring_expansion` and `research.required_rows` identify this experiment. `rows` preserves each row's existence, match and capability; it is not a list of values whose global existence is sufficient. Expansion SHALL preserve per-row resource/variable instances, collection behaviors and source anomalies. A duplicate generated ID SHALL be rejected. Legitimately duplicate predicates MAY survive with distinct stable Test identity. Expanded logical IDs SHALL be deterministic and provenance SHALL map them to rows. Output/evidence caps SHALL NOT truncate the required row list or change truth.

The audit sketch has **four** source-preserving regex templates and 24 rows, not a corrected 24-way security matrix. `${syscall}` and `${arch}` are compile-time literal substitutions from a closed vocabulary; regex syntax SHALL NOT be accepted from runtime inputs. The `auid` row field describes which fixed template is selected; it does not modify commands. The current bounded experiment compares every expanded regex byte-for-byte against the original OVAL graph. It does not implement a general macro language or the entire textfilecontent collector. Distinct `all`/`some` existence and per-row `instance`/collection semantics require faithful expansion before deployment.

The crypto sketch supplies eleven canonical symlink target rows and one regular-file row. Each row SHALL still use the existing capability and require its own object. No policy-aware crypto collector is needed. A table is less verbose, but retaining eleven expected target values is necessary security information.

## Finding 2: typed records often make a general join unnecessary

OVAL already has record fields and per-Item State aggregation. Existing native record evaluation can express AND of predicates on the same Item. Apache cookie flags therefore do **not** justify inventing a new correlation operator. A typed collector returning zone/key, interface/address or installation/context records may eliminate text projection and repeated command construction without changing general language semantics.

For proposed acquisition, an Item SHALL include a stable key and individually typed observed fields. Keys identify observations, not legacy source IDs. `record_identity: key` declares grouping; it SHALL NOT sort two arrays and zip them or perform an implicit Cartesian join. `collection_contract: typed-status-per-key-v1` is a research output contract: collection carries discovered-key scope, per-key status and completeness, distinct from observed values.

`required_key_coverage: true` means each key discovered by the acquisition scope must have an evaluated record. Missing keys from a **complete** acquisition can establish absence; missing keys from partial/unknown acquisition cannot. The prototype unique-record helper returns error for duplicate keys; this is only suitable for unique keys. Legitimate multiplicity SHALL use composite keys (zone + key type + key ID; interface + address + address family; installation + context + cookie/directive occurrence). Deduplicating records without a capability identity rule is forbidden.

The synthetic helper has the bounded result domain true/false/error/unknown/not_evaluated and AND precedence false, error, unknown, not_evaluated, true. This is not a replacement for full OVAL existence/collection charts; source flag `not applicable`, all-zero State populations and variable instances remain governed by the maintained evaluator contract. `empty_result` in sketches states an experimental scope policy, not a new universal empty-AND default. Unknown collection SHALL NOT be converted to an empty successful collection. A verified violation MAY remain false when another record is unknown; a partial all-good collection SHALL NOT prove true. Missing expected record fields are error; explicitly unknown fields are unknown. Schema validity alone cannot prove these rules.

A field predicate is applied to one record before item quantification. `all` SHALL quantify over all required record instances. `one`, `any`, `none`, State/variable quantification, Sets and Filters remain supported; this experiment does not replace them. Key extraction, filtering and set algebra SHALL preserve identity, status and completeness, including complement relative to the selected universe. Existing OVAL Filter defaults (exclude) and Set defaults (UNION), and filtering before the enclosing Set operator, remain explicit migration semantics.

## Finding 3: a join is justified only by an explicit changed contract

Original OVAL concat functions over multi-valued components may produce Cartesian products. A correlated keyed join produces different values. The Apache root/config demonstration gives four Cartesian paths versus two keyed paths. A converter SHALL NOT silently substitute the keyed form. Authors MAY propose it as a separately reviewed acquisition correction when installations are genuinely related by key.

A future general join would require explicit inner/left semantics, key datatypes/case rules, multiplicity, missing-side statuses, identity, filtering order and memory/collection budgets. None of those are settled here. Prefer collecting one typed record where the product query naturally supplies it. There is no evidence in this study requiring a general join in the core language yet.

## Domain collector boundaries

| Proposed acquisition | Observed fields, not a compliance Boolean | Remaining implementation obligation |
| --- | --- | --- |
| `linux.audit_rules` | action/list, architecture, syscall set, auid conditions, rule order, snapshot kind | Kernel versus persisted state, syscall resolution, exclusion/never ordering, unsupported predicates; restricted parser is not a collector |
| `apache.configuration` | installation, source file, line, context, directive occurrence, explicit/effective value | Discovery, recursive Includes, optional absence, scope merging, modules/conditional sections, on-disk versus loaded state, application version |
| `windows.iis.site` | site ID, binding, configured/expanded/resolved physical path | Safe WebAdministration query, environment variables, drive/path semantics and native junction handling |
| `windows.registry.ace` | SID, access mask, ACE type/order, inheritance/propagation flags, registry view | Preserve numeric rights, null/empty DACL distinction, locale-independent IDs; explicit ACL is not effective access |
| `windows.dns.zone` / `windows.dns.signingkey` | zone ID/type/integration/signing; RR type/count; key ID/type/duration | Per-zone errors and completeness, units, cmdlet/product versions, key-role identity |
| `windows.network.interface` | ifIndex/address identity, address/prefix/gateway relation, origin fields | Multiple addresses, IPv4/IPv6, adapter state, query errors and relation cardinality |

`windows.fileeffectiverights53` remains the established OVAL-aligned capability; do not replace it with ACE matching. Native file Objects retain scanner traversal, permission, remote filesystem, symlink/junction and completeness handling. All domain sketches remain unimplemented. Their predicates are visible policy; a `compliant: true` collector is rejected.

`source_groups` in Apache sketches identifies observed groups that the published source queries independently. A one-record summary of those groups is a **changed method**, unless every group's required/optional presence and occurrence rules survives. The initial sketch deliberately demonstrates the design candidate; it is not marked faithful. `*_explicit` distinguishes explicit directives from defaults. Registry default-table and path-relation predicates in sketches are **unresolved domain operations**: their full identity/type semantics must be designed before execution. They SHALL NOT be treated as implemented comparisons merely because the YAML parses.

`filesystem: any` in the home-file sketch is a proposed explicit rendering of the source unrestricted filesystem behavior, not permission to scan remote systems through shellcommand. A future local-only policy changes selected scope and must use a different reviewed assessment choice. Max depth/link semantics still need differential collector tests.

## Bounded shellcommand alternative

Shellcommand MAY acquire structured administrative-query data. It SHALL NOT enumerate/traverse the filesystem for these proposals. No target commands were executed in this study.

A candidate adapter SHALL declare: literal executable and interpreter/version allowlist; fixed arguments or a fixed signed script; requested privilege; permitted product/module versions; native argument binding; explicit timeout and stdout/stderr byte budgets; UTF-8 JSON output with a versioned record schema; locale/timezone handling; completion and per-record query error envelopes. Nonzero exit, decode failure, truncated output or timeout SHALL NOT masquerade as an empty successful record list. Partial observations MAY be retained with incomplete status. Bounded evidence concerns emitted explanation, not lost assessment Items.

Windows candidates: fixed PowerShell administrative scripts using Get-DnsServerZone, Get-DnsServerResourceRecord, Get-DnsServerSigningKey, Get-NetAdapter/Get-NetIPConfiguration or Get-Website, returning named records through ConvertTo-Json with an explicit depth. Use literal script logic, typed argument binding, explicit terminating-error handling and per-key error records. No `Invoke-Expression`, interpolated organizational command strings or filesystem recursion. Module availability/Windows Server 2025 support, privilege, nested JSON depth, multiple output records and nonterminating errors require actual target tests. This contract proposes requirements; no adapter has met them here.

For `update-crypto-policies --check`, a focused invocation is legitimate alongside native links. Exit/output/version/locale behavior still needs official utility documentation and RHEL target testing. Do not infer success from a favorable substring. It SHALL NOT replace canonical path/type checks or traverse directories in shell.

Organizational Input SHALL remain constrained policy values. Classification, where delegated, is a boolean/enumeration consumed by a separate applicability Assessment; it SHALL NOT alter configuration Test selection or script contents. Tailoring selection of publisher-defined assessment choices is a separate mechanism.

## Standards references and limits

Authority for legacy behavior: pinned vendored SCAP 1.4/OVAL 5.12.3 XSDs, including `oval-definitions-schema.xsd`, `oval-results-schema.xsd`, `unix-definitions-schema.xsd`, `windows-definitions-schema.xsd`, `independent-definitions-schema.xsd`, plus the maintained [evaluation contract](../iterations/003/design/assessment-evaluation-semantics.md). Schema provenance: [vendored source pin](../../third_party/scap-1.4-schemas/README.md). This study does not run the upstream Self-Assertion corpus; the existing schema-derived evaluator regressions are separate language evidence.

Official product references retrieved 2026-10-03:

- [Apache core directives](https://httpd.apache.org/docs/2.4/mod/core.html): directive contexts, Includes, defaults and MaxKeepAliveRequests behavior. Default values are not proof of explicit policy settings.
- [Microsoft AccessCheck](https://learn.microsoft.com/en-us/windows/win32/secauthz/how-dacls-control-access-to-an-object): access tokens and ordered ACE processing. The synthetic one-bit example is deliberately narrower.
- [DNS resource records](https://learn.microsoft.com/en-us/powershell/module/dnsserver/get-dnsserverresourcerecord?view=windowsserver2025-ps) and [signing keys](https://learn.microsoft.com/en-us/powershell/module/dnsserver/get-dnsserversigningkey?view=windowsserver2025-ps): administrative acquisition API candidates.
- [Get-NetIPAddress](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-netipaddress?view=windowsserver2025-ps): PrefixOrigin and SuffixOrigin are distinct properties. Their policy relationship must not be assumed.

Live product pages are supplementary design evidence, not pinned OVAL semantic oracles. Their URLs and retrieval date are recorded; no full documentation was copied.
