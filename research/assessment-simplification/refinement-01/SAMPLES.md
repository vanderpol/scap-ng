# Twelve sample refinements

**Experimental continuation.** Each linked dossier contains the exact Rule/version,
original Check Text, complete configuration graph, separate applicability,
unchanged before Assessment, two methods and concrete outcome matrix. Those
artifacts remain part of this study, not historical architecture authority. The
source reproduction in this directory reconfirmed all extracted XML bytes.
The observations below separate this session's experiments from inherited tests.

## Sources and coverage

All five packages are available at NIWC revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5`. Package hashes and fetch URLs are in
[source-reproduction.json](evidence/source-reproduction.json); each family's
`../samples/<family>/source-generation.json` identifies the exact package.

| Family | Pinned package version | Cases |
| --- | --- | --- |
| RHEL9 | V2R9, enhancedV13, SCAP 1.4 | SV-258179, SV-257889, SV-258236 |
| Windows Server2025 | V1R1, enhancedV1, SCAP 1.4 | SV-278028, SV-278138, SV-278001 |
| Windows DNS | V2R3, enhancedV8, SCAP 1.4; source Benchmark identifies Server2022 DNS | SV-259350, SV-259345, SV-259374 |
| Apache2.4 UNIX server | V3R2, enhancedV2, SCAP 1.4 | SV-214228, SV-214268 |
| Apache2.4 UNIX site | V2R6, enhancedV2, SCAP 1.4 | SV-214292 |

The DNS package is not asserted to be a Windows2025-specific revision. Its
supported administrative API on Server2025 needs validation. No requested source
family is missing. Target systems and PowerShell are unavailable; this limits
execution evidence, not source analysis. No additional platform was needed to
demonstrate a distinct problem. Fourteen reached Test types remain supported
under the pinned schemas and governance overrides. No deprecated Test is being
proposed; for example, deprecated `windows.accesstoken` would require the
established supported `windows.userright` replacement in corrected source.

## RHEL9 audit: SV-258179

[Dossier and Check Text](../dossiers/SV-258179.md),
[full XML](../evidence/rhel_9/SV-258179/source-oval.xml),
[graph](../evidence/rhel_9/SV-258179/graph.json),
[before](../samples/rhel_9/assessments/automated/niwc.rhel_9.SV-258179.automated.assessment.yaml),
[after](tables/SV-258179.yaml).

Requirement: audit extended-attribute changes for eligible user and root actions,
including architecture/system-call coverage. The manual procedure checks loaded
rules; the automated source reads the persisted file. These are distinct truths.

New experiment resolves the full constant/concat selector chain and compares all
24 Tests, including regex behaviors, instance and existence, rather than only
regex strings. Sixteen Tests use `all`; eight default to `some`. Four templates
make duplicated predicates reviewable without inventing parsed audit semantics.
Two b64-named root predicates still select b32. Fixing those rows changes the
contract, demonstrated by a regression. Parsing audit records could eventually
make review easier but would need ordering, syscall-list and runtime/persisted
scope semantics; no parser equivalence was established here.

Source collection/error/missing/multiple-match parameters are exercised on
synthetic observations. These do not establish the source regex engine's behavior
on a real audit file. Organizational Inputs cannot choose rows or syscall names.

## RHEL9 home files: SV-257889

[Dossier and Check Text](../dossiers/SV-257889.md),
[full XML](../evidence/rhel_9/SV-257889/source-oval.xml),
[graph](../evidence/rhel_9/SV-257889/graph.json),
[after sketch](../proposals/home-file-permissions.proposal.yaml).

Requirement: protect interactive/root initialization files from forbidden access.
Account selection, UID/home Filters, relative Sets, directory exclusion and
permission bits are substantive. Root requires a match; non-system selection
permits empty collection. Source downward recursion follows symlinks at depth 1;
new filesystem exclusion defaults would change the source contract.

Refinement: the optional authoring-table tool is unsuitable for dynamically
selected accounts. Retain shared account Objects, named Variables and native
file Tests. The inherited 4,096-mode enumeration rejects numeric `mode <= 0740`
(0604 violates forbidden other-read). It supports permission booleans, not a new
permission Test. A reusable selection library MAY reduce boilerplate, but SHALL
expand to explicit Sets/Filters/traversal. No implementation or target traversal
test was added for this case. Remote mounts, permission failures, symlink loops
and missing homes still require native collector fixtures.

## RHEL9 crypto: SV-258236

[Dossier and Check Text](../dossiers/SV-258236.md),
[full XML](../evidence/rhel_9/SV-258236/source-oval.xml),
[graph](../evidence/rhel_9/SV-258236/graph.json),
[before](../samples/rhel_9/assessments/automated/niwc.rhel_9.SV-258236.automated.assessment.yaml),
[after](tables/SV-258236.yaml).

Requirement: system-wide FIPS crypto configuration. Published automation checks
eleven canonical symlink targets and one regular NSS file, rather than all manual
utility checks or every displayed backend. New table expansion preserves all 12
path/field/value and existence contracts. Canonical target is resolved target,
not raw link text. Scanner acquisition is unchanged in concept and unexecuted.

A new counterexample rejects collecting all backends as one population with
global `some`: eleven good Items can hide the missing twelfth. Stable row IDs,
per-row Tests and visible NSS override retain necessary semantics. The table
generalizes to publisher-fixed expectation matrices; native filesystem behavior
and policy completeness do not simplify away.

## Windows FTP paths: SV-278028

[Dossier and Check Text](../dossiers/SV-278028.md),
[full XML](../evidence/ms_windows_server_2025/SV-278028/source-oval.xml),
[graph](../evidence/ms_windows_server_2025/SV-278028/graph.json),
[after sketch](../proposals/ftp-site-paths.proposal.yaml).

Requirement: FTP roots must avoid prohibited system areas; FTP-installed
applicability is separate. Source uses binding Filters, system environment paths,
site-derived commands and four no-prohibited-match Tests. Query failure returning
no output is not evidence of zero FTP sites. Configured path, expanded environment
path and resolved junction target are three different facts.

The DNS experiment supports the design of a fixed structured administrative
query here, but does not implement IIS acquisition. Rows SHOULD identify sites,
bindings and path status; unknown environment values SHALL remain unknown/error.
An organization may select a constrained expected value, never a command or Test.
Use existing native comparisons where adequate; a `path-under` predicate needs
platform case/separator/root semantics before becoming a feature. Boundary
`C:\WindowsOld` versus `C:\Windows`, quoted site names, two sites and junctions
remain in the inherited case matrix. Target execution and path relation are open.

## Windows AD rights: SV-278138

[Dossier and Check Text](../dossiers/SV-278138.md),
[full XML](../evidence/ms_windows_server_2025/SV-278138/source-oval.xml),
[graph](../evidence/ms_windows_server_2025/SV-278138/graph.json),
[after sketch](../proposals/ad-file-rights.proposal.yaml).

Requirement: restrict effective access to AD data/log/SYSVOL directories on domain
controllers. Three registry-derived path Variables, principal Filters and nine
effective-rights Tests cannot become a literal ACL allowlist. SID/group/token
resolution, inheritance and deny/allow ordering remain collector work.

The crypto missing-row counterexample applies to directory/principal coverage.
A future finite table MAY remove repeated authored Tests while preserving each
directory's existence and the exact Filter graph. This emitter intentionally
does not support dynamic AD selections. Preserve `windows.fileeffectiverights53`
and familiar Object/State/Test names. Missing directory, unresolved SID and denied
collection need distinct outcomes. No effective-rights engine, Windows expansion
or access-token test was implemented; inherited synthetic matrices were rerun.

## Windows registry ACLs: SV-278001

[Dossier and Check Text](../dossiers/SV-278001.md),
[full XML](../evidence/ms_windows_server_2025/SV-278001/source-oval.xml),
[graph](../evidence/ms_windows_server_2025/SV-278001/graph.json),
[after sketch](../proposals/registry-ace-records.proposal.yaml).

Requirement: restrictive HKLM ACLs with domain-controller/member principal
differences and the application-package SID exception. Source string projection
and whitelist checks are not a proof of the complete default ACL. Display-only
numeric rights may be filtered out; retain that observation without inventing
target prevalence or repairing source behavior.

Typed ACE observations SHOULD retain numeric masks, explicit access type,
inheritance/propagation and registry key identity. This is separate from effective
rights. Decoder lessons apply: malformed/missing records are protocol failures;
empty and null DACL are different values, not empty-success. A stronger required-
ACL comparison requires a distinct Assessment. Existing role/applicability facts
remain authored assessments. No registry adapter or complete ACL equivalence was
implemented. Unresolved principals and key access failures remain target cases.

## DNS RR completeness: SV-259350

[Dossier and Check Text](../dossiers/SV-259350.md),
[full XML](../evidence/ms_windows_server_dns/SV-259350/source-oval.xml),
[graph](../evidence/ms_windows_server_dns/SV-259350/graph.json),
[after sketch](../proposals/dns-record-completeness.proposal.yaml),
[new fixed query](dns-query.ps1), [decoder/model](dns_records.py).

Requirement: selected signed forward zones need DNSSEC RRs, with source
server-wide caching/all-integrated bypasses and distinct classified-network
applicability. Native per-zone records remove command-building/projection chains.
The prototype retains server-wide exceptions and evaluates mixed inventories
without silently excluding integrated zones one by one.

All256 two-zone signed/RR Boolean combinations were exercised, along with missing
keys, partial inventories, failed queries, duplicate keys/properties, malformed
counts and truncation. Three favorable types on three unrelated zones do not
satisfy per-zone completeness. This disproves flattening, not the source OVAL:
its Variable-instance scope remains unexecuted. The fixed script is unexecuted;
its session identity does not guarantee atomic inventory. Locale/module/privilege,
record support and race outcomes remain open.

## DNS durations: SV-259345

[Dossier and Check Text](../dossiers/SV-259345.md),
[full XML](../evidence/ms_windows_server_dns/SV-259345/source-oval.xml),
[graph](../evidence/ms_windows_server_dns/SV-259345/graph.json),
[after sketch](../proposals/dns-key-duration.proposal.yaml).

Requirement: KSK/ZSK signature validity meets stated bounds, subject to source
bypasses. Source projects `Days*24+Hours`, drops minutes/seconds and catches
exceptions as zero. A typed duration in seconds is readable and precise but is a
changed method at the upper boundary. The inherited boundary fixture at 48h+1s
distinguishes whole-hour projection from exact duration.

RR decoder status handling cannot silently replace this source's error-to-zero
behavior. A compatibility adapter would need an explicit legacy projection;
stronger duration/status behavior needs distinct identity. Key type/id/zone and
missing KSK versus ZSK SHOULD remain visible. No new duration operator is yet
required: typed integer units can express reviewed bounds. No key-query adapter
or target duration test was added; inherited synthetic boundaries were rerun.

## DNS interfaces: SV-259374

[Dossier and Check Text](../dossiers/SV-259374.md),
[full XML](../evidence/ms_windows_server_dns/SV-259374/source-oval.xml),
[graph](../evidence/ms_windows_server_dns/SV-259374/graph.json),
[after sketch](../proposals/interface-records.proposal.yaml).

Requirement: static IPv4 addressing with mask/prefix/gateway. Source selects Up
adapters, permits none and uses SuffixOrigin=Manual. Checking all offline adapters
or replacing that signal with DHCP/PrefixOrigin is an intent refinement.

Per-interface/address records may simplify four command projections without a
general join. ifIndex alone is insufficient when one interface has multiple
addresses: an address key and explicit gateway relation are needed. Zero online,
missing gateway, unrelated favorable values, prefix 0/32 and query failures are
covered by inherited matrices/models. As with RR scope, source correlation is
not presumed broken. `variable.value` already helps count-wrapper boilerplate.
No network adapter, signal substitution or core join was implemented.

## Apache KeepAlive: SV-214228

[Dossier and Check Text](../dossiers/SV-214228.md),
[full XML](../evidence/apache_server_2-4_unix_server/SV-214228/source-oval.xml),
[graph](../evidence/apache_server_2-4_unix_server/SV-214228/graph.json),
[after sketch](../proposals/apache-keepalive.proposal.yaml),
[new acquisition library](apache_occurrences.py).

Requirement: explicit KeepAlive settings/bounds. Source discovery/config/include
scripts and 18 Variables obscure four policy Tests. A shared explicit-occurrence
interface reduces repeated acquisition authoring. It retains conflicting Off/On
occurrences and leaves an absent directive absent, even if Apache has a default.

New fixtures exercise literal includes, spaces, context/order, repeated Includes,
two installations, cycles/budgets and native absence/access failure. Missing
IncludeOptional is skipped only with explicit absence evidence. Conditional/glob
syntax, variable expansion and continuations fail explicitly. ServerRoot changes
are not implemented; a new failing root-change fixture
prevented an incorrect old-root include selection and drove explicit rejection.
Effective settings
require a distinct, more expensive interpreter; no runtime equivalence is claimed.

## Apache cookie flags: SV-214268

[Dossier and Check Text](../dossiers/SV-214268.md),
[full XML](../evidence/apache_server_2-4_unix_server/SV-214268/source-oval.xml),
[graph](../evidence/apache_server_2-4_unix_server/SV-214268/graph.json),
[after sketch](../proposals/apache-cookie.proposal.yaml).

Requirement: applicable session cookies carry required flags, preserving
source enablement/applicability. Existing per-Item States already correlate flags;
there is no demonstrated need for a new join. Shared occurrence acquisition MAY
reuse KeepAlive discovery without merging contexts or installations.

New nested include fixture retains `session;HttpOnly;Secure` as one quoted
argument in its VirtualHost context. It does not execute the complete original
cookie predicate or resolve effective Session enablement. A separate HttpOnly
match and Secure match from unrelated cookies must not satisfy one cookie.
Inherited cookie matrices were rerun. Grammar beyond the restricted parser,
module enablement, conditional sections and target scope remain open.

## Apache default documents: SV-214292

[Dossier and Check Text](../dossiers/SV-214292.md),
[full XML](../evidence/apache_server_2-4_unix_site/SV-214292/source-oval.xml),
[graph](../evidence/apache_server_2-4_unix_site/SV-214292/graph.json),
[after sketch](../proposals/apache-default-documents.proposal.yaml).

Requirement: prevent unintended directory listings/default-document exposure.
Source selects root-level case-insensitive index.html at two discovered root
groups; it does not visit every descendant or compute DirectoryIndex/Options.
Keep native file existence Tests and obtain DocumentRoot records from shared
configuration acquisition. New two-installation fixture prevents Cartesian
combination of unrelated roots; no file scanning occurs in the parser.

Recursing every directory is a coverage change, not an equivalent shortening.
Native collectors SHALL retain remote exclusions, links, permissions and partial
collection. Index.HTML selection may differ from Unix serving behavior. Existing
root/descendant counterexamples were rerun; no Apache server or native filesystem
collector was executed. A full effective DirectoryIndex interpreter remains
unproven and outside this bounded implementation.
