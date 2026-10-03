# Full requirement reading log

Receiving SHA `c802b9dac9a0b7c846e18389c24ea417d15d7b74`, 2026-10-03.
Manual reading of complete Check Text, not keyword classification or an OVAL
execution proof. Ordinals refer to extracted source order. Entries are recorded
after each full batch is read; extraction alone is not recorded as reading.

## RHEL 9, 1–50 (read)

SV-257777–SV-257827, with the source's numbering gaps retained. Patterns:
vendor support/current patch policy; exact banners; service state vectors;
boot entries/default boot configuration; runtime sysctl plus persisted settings;
module-disabling directives; file ownership; package presence and signatures.

Important boundaries: 257778 requires external advisory/installed-package evidence,
organizational frequency and IAVA overrides, not merely update-history presence.
257779 requires exact banner equality. 257781/257792/257803/257804–808/257812–818
contain approvals/operational exceptions or cross-rule conditions that cannot be
silently flattened. 257782 excludes kernel-FIPS systems. 257787 excludes UEFI.
257792/793/795/796 and 257809 require multiple configured/runtime layers; 257809
explicitly fails conflicting persisted results. 257818 distinguishes disabled,
inactive and masked; command/example wording must not dictate incorrect native
service-state semantics. 257819 needs authoritative vendor fingerprints/versioned
reference data, not a plausible key label. 257820–822 allow an approved alternative
verification process; absent settings alone are not the whole requirement.
257823's broad rpm file verification is inherited manual guidance, not blanket
permission to outsource scanner file acquisition/scanning. 257825 has connectivity
applicability. In package absence checks, command nonzero can mean confirmed
absence, while access/tool errors must remain distinct.

Concept refinement: reusable *state-vector* queries (enabled/active/masked),
separate runtime/persisted assertions, exact/normalized text contracts, scoped
approval evidence, authoritative reference-data freshness. Most literal tests
do not need a new language primitive; preserve native filesystem acquisition.

## RHEL 9, 51–100 (read)

SV-257828–SV-257878. Package absence/presence with approved operational/MFA/NFS/
GUI exceptions, repository inventory, TFTP package/config dependency, followed by
mount separation and option-set requirements. 257835 explicitly says absent TFTP
is not applicable; secure ExecStart is only relevant when present. 257838 has an
approved alternative MFA exception. 257849 distinguishes missing autofs from
active/permitted service states and operational approval.

Mount requirements need exact mount identity and live-versus-persisted source:
257843–848 require separate filesystems; 257850–852 fail when home has no separate
mount. Audit path is the configured path, not necessarily the manual example.
257854–856 quantify configured NFS entries; 257857–859 select removable media.
257862 excludes BIOS and additionally vfat, even though its example is vfat.
Preserve that source ambiguity rather than silently repairing policy. Options
nodev/nosuid/noexec are membership facts, not substring success across unrelated
mounts. Mount metadata queries are distinct from searching filesystem contents.

Concept refinement: a keyed mount requirement matrix with per-target existence,
source layer and typed option membership; reusable package inventory with explicit
exceptions. This is likely authoring/data reuse over existing methods, not a
general join or shell traversal. Remote-mount metadata can be assessed without
traversing its files. No target/mapping equivalence demonstrated.

## RHEL 9, 101–150 (read)

SV-257879–SV-257928. New distinct problem: 257879 needs a backing-device ancestry
relationship for every persistent filesystem except boot/efi, with a LUKS crypt
ancestor and explicit external/hypervisor/storage-array encryption evidence.
A crypt device somewhere in the inventory is insufficient. 257881 quantifies
non-root local mount options. The remainder is native file permission/ownership
populations, known-path metadata and package-default integrity.

257882/883/884 describe mode 755 but the manual command tests only writable bits;
do not blindly substitute a full twelve-bit allowance from the title. Preserve
the distinction between policy wording, manual predicate and automated graph.
257888 checks owner/group/mode against package defaults with a specific RPM output
filter; full package verification is not automatically the same scope. 257890's
interactive-user heuristic explicitly may miss privileged interactive users.
Selection differs between -L traversal, regular '*.so*' files, directories and
known paths. 257919/921/923 permit required system group owners, not only root;
257928 additionally permits application owners while its illustrative UID filter
does not establish that authorization. Absent/missing file and suppressed access
errors cannot be treated as compliant search results.

Concept refinement: device-ancestry assertions, compatible native file-population
reuse, expected metadata maps, typed authorized-owner sets and independent evidence
for package baselines. Runtime caching may share compatible acquisition work while
authored Object identities/scopes and each Rule's policy remain separate.

## RHEL 9, 151–200 (read)

SV-257929–SV-257981. Public-directory sticky bits, local owner/group validity,
device labeling with virtualization exceptions, firewall zones/allowlists,
chrony/DNS/interface configuration, network sysctl values and SSH prerequisites.
257929's sample output has sticky set even though its search predicate selects
missing sticky: treat example output as illustrative/inconsistent, not normative
evidence. 257930/931 quantify every local mounted filesystem and resolve account
IDs; remote exclusions and access errors must be native scanner facts. 257932
explicitly permits device_t for certain VM devices and may need a wider native
device population than /dev.

257938 is absent from this version; no fabricated ordinal/Rule. 257937 requires
active interface zone associations plus runtime/permanent DROP targets, whereas
the example query selects the default zone. A favorable default-zone value is
not all-zone proof. 257940 needs authoritative PPSM CLSA/CAL allowlists with
ports/protocols/services, not only configuration literals. 257945 requires maxpoll
<=16 and an authoritative DoD server; interpreting exponent units matters.
257948 allows a single HA cloud DNS endpoint by explicit applicability, not a
generic count exception. 257949 is a good fixed configuration-query candidate
(NetworkManager --print-config), preserving section identity and approved alternate
resolver evidence. 257950 depends on active IPsec plus approved connections.
257951 allows approved extra postfix restrictions; 257953 accepts demonstrated
alternative notification evidence. 257971–976 have IPv6-disabled applicability.
257981's banner-path discovery command is inherited guidance; native acquisition
must handle referenced files, and execution of sshd debugging is not endorsed here.

Concept refinement: keyed active/configured state vectors, delegated constrained
policy-data sets with authority/provenance, typed configuration-section selection,
account/device identities and explicit evidence for contextual exceptions. File
searches in the Check Text remain scanner operations regardless of shell examples.

## RHEL 9, 201–250 (read)

SV-257982–SV-258036. SSH explicit directives, crypto algorithm allowlists,
configuration/host-key metadata, followed by GNOME value/overrideability pairs,
dconf database freshness, USB blocking and approved alternatives.
257989/991 use only-approved set semantics with nonmissing directive presence;
do not interpret a reordered/list subset as exact-text equality without inspecting
the source. 257994's text requires both data and time RekeyLimit operands, rather
than making the sample 1G/1h automatically exact publisher thresholds. 257996
explicitly inspects file configuration plus sshd -T runtime output. Other SSH
Checks explicitly require uncommented presence; runtime default success alone is
not equivalent. File/key discovery is native; 258001 notes nonstandard key paths.

GNOME pairs distinguish value and writability. Queries need explicit principal/
profile/session context; one root gsettings result cannot silently stand for every
interactive user. 258015 derives a lock directory from the actual system database,
not a literal local database. 258023 rejects idle-delay zero, not just values >600;
258025 allows <=5 lock delay. 258027's writable picture-uri test is a manual proxy,
not full proof of a blank screen. 258028 checks each database mtime against related
keyfile mtimes; its find/stat script is forbidden as a proposed shell filesystem
search. Native metadata/relationships must implement it. A timestamp criterion is
not content equality. 258035/036 accept demonstrated alternative USB blocking and
exclude VMs with no physical/virtual USB: absent package/service alone is insufficient.

Concept refinement: value+enforcement facts, named observation context, native
derived-artifact freshness comparisons, multi-operand settings and clear alternative
manual/automated evidence routes. Shared observation schemas could serve separate
Rules without collapsing their identities or silently choosing a favorable source.

## RHEL 9, 251–300 (read)

SV-258037–SV-258095, retaining source gaps. USB/radio evidence, default versus
existing account policy, interactive-account/home/primary-group relationships,
temporary-account expiration, duplicate IDs, faillock, shell settings, SELinux,
sudo authorization and initial PAM structure.

258038 accepts alternative peripheral-blocking evidence on empty/error usbguard;
that is not permission to turn collection errors into an automatic pass. 258042
requires existing nonsystem passwords to have positive max days <=60, separately
from default login.defs. 258045/061 need uniqueness across all relevant identities;
the group manual `uniq -d` without sorting can miss nonadjacent duplicates. 258047
needs temporary-account classification and an explicit time origin/provisioning
deadline for the 72-hour requirement; account expiration alone does not prove it.
258048/051/052/053 link each user's primary GID/home to actual group/file metadata.
Source heuristics acknowledge privileged interactive users can be missed. 258058
needs a scoped authoritative list of authorized accounts, not arbitrary allow-all
input. 258054/056 reject zero thresholds; 258057 requires zero as indefinite
admin-release lockout. Uniform numeric comparison shortcuts would be wrong.

258068/069 have shell/domain scope and approved domain exceptions. 258072–075
change Rule severity when umask is zero; severity belongs to policy, not technical
truth. 258078 requires current plus persisted SELinux enforcing. 258080 derives a
tally directory and has SELinux/PAM applicability. 258084's example is timeout 0
but explicit failure text rejects negatives/missing/multiple source locations;
interpret title/example/manual predicate separately. 258085 requires three flags
and restricts source-location multiplicity. PAM 258094/095 accepts demonstrated
included/substacked configuration; 258095 requires preauth before pam_unix, not
module presence alone. Shell initialization/PATH content cannot be safely evaluated
as arbitrary privileged scripts merely to infer policy.

Concept refinement: per-record field-to-field comparisons, uniqueness, explicit
time-origin evidence, parser-aware ordered/include relationships and typed scoped
approval/authorization data. Some are existing variable/record semantics presented
more clearly; policy intent versus manual/source anomalies remain separate.

## RHEL 9, 301–350 (read)

SV-258096–SV-258149. PAM include/order/hashing, pwquality/default/existing
password rules, SSSD/CAC/OCSP/PKI, emergency/rescue service configuration,
AIDE coverage/notification and rsyslog destination/driver/block semantics.
258096–098 accept demonstrated include/substack configurations; literal file-only
presence is insufficient. Credit values 258102/103/109/111 exemplify -1 but explicit
finding text rejects positives, leaving zero as an intent/manual boundary. 258114
similarly rejects >3 without explicitly excluding zero. Do not silently strengthen
those source predicates. 258116 requires crypt_style in the defaults section.
258123 requires the certificate_verification entry in [sssd], with alternative
status-checking evidence. 258127 inspects every selected private key; prompt-based
ssh-keygen testing needs noninteractive/error/format/privilege handling and native
key-file discovery. 258128/129 allow one of default or drop-in locations but not
both, a source-location cardinality requirement. 258131 needs a valid DoD-issued
certificate at the specified location; issuer text alone is not cryptographic trust.
258132 requires a certmap section tied to user/domain data. 258133 conditionally
requires expiration=1 when cache_credentials is true; false/absent is explicitly
permitted. Unknown is not known false/absent.

258134–139 accept other integrity tools, require coverage of every selection line
and each audit tool, and separate scheduled execution/notification from installation.
Inherited find/scheduling shell text does not authorize proposed filesystem scans.
258143 joins actual listening sockets/configured listeners with log-aggregation
authorization and alternate-tool applicability. 258146–148 distinguish an omfwd
action block from a module block: identical key/value text in the wrong scope can
fail. 258149 accepts legacy or RainerScript syntax and alternative offloading
evidence. An unqualified keyword search hides the necessary structured context.

Concept refinement: grammar-qualified record selectors, same-block relationships,
exclusive source-location presence, verified trust/reference data and explicit
coverage/scheduling/notification evidence. Avoid conflating configuration evidence
with demonstrated runtime delivery, or technical policy with example commands.

## RHEL 9, 351–400 (read)

SV-258150–SV-258200. Logging facility validation, audit service/actions/capacity,
percent thresholds, configured log-path/group relations, frequency/buffer controls
and broad audit event requirements. 258150's alternate logger local0 probe is not
itself proof of cron facility logging; a bounded behavioral method may be legitimate
for this specific requirement only after event/facility/destination semantics are
validated. No probe or source command was executed.

258155 says a week's capacity depends on activity and immediate central offload;
10GB is a typical example, not a universal fixed threshold. 258156/158 express
remaining-space percentages corresponding to utilization, with >=25% warning
threshold versus exact 5% administrative threshold and alternative evidence.
258165–167 derive each audit log's path/group/directory from actual config; do not
hardcode /var/log/audit because it is an example. 258168 is inclusive 1..100.
258173 only explicitly flags returned backlog values <8192; missing-result behavior
requires source/manual-intent analysis. 258174 is a suitable focused postconf/postmap
query candidate, with correct source-map identity and alias absence/error distinctions.

Audit 258176 adds inter-field comparisons uid!=euid and gid!=egid with elevated
effective IDs. 258188 adds EPERM/EACCES outcomes. Path execution rules use -S all,
path, perm=x and auid domains. Other rules quantify syscall/architecture combinations.
The earlier auid-only symbolic coverage prototype does not implement all these
conditions and must not be presented as covering this full audit section.
Key labels, ordered filtering, loaded/persisted scope and missing rules still
need explicit contracts; favorable token presence is not security coverage proof.

Concept refinement: explicit time/activity bases, typed relative thresholds,
configured-resource links, error-aware fixed utility queries and carefully bounded
behavioral observations. New event predicates expose the restricted audit model's
limits rather than justify replacing all audit checks with it.

### RHEL 9, ordinals 401–445: remaining audit and cryptographic requirements

Read all 45 complete check texts. 258201–213 largely repeat path-execution audit
coverage, but 258214 inspects persisted shutdown rules, not loaded rules. 258216
shows both architectures while its finding wording only rejects no matches;
resolve the full automated/manual contract before tightening cardinality. Watch
rules 258217–225 vary path and actor constraints. 258221's title says /etc/opasswd
but its check says /etc/security/opasswd. 258227 allows a documented availability
exception to panic-on-audit-failure. 258229 requires -e 2 as the LAST noncomment
line: finding that line anywhere is insufficient. 279936 adds crond_t subject
type and distinct effective/login user conditions beyond the earlier audit model.

258236 lists THIRTEEN cryptographic backend paths in its manual check, including
openssl_fips.config. The previously selected automated graph/model used twelve.
This discrepancy needs reconciliation; do not silently expand the earlier model
and claim equivalent conversion. NSS is a regular file exception to the symlink
pattern; approved subpolicies still require correctly resolved backend links.
258241 allows FIPS or FIPS:<subpolicies>, and also inspects CURRENT.pol for allowed
hashes, prohibited algorithms and RSA minimum size. A successful --show query
alone does not establish compliance. 258232/242 have service/package applicability.
258231 excludes inactive password fields; hash prefix is not account applicability.

270174 requires the exact GNOME banner with formatting/newline considerations.
270177/178 are SSH CLIENT cryptographic settings, distinct from server settings.
270180 requires fapolicyd permissive=0 AND a terminal deny-all rule; accepted
terminal actions include deny, deny_log and deny_audit. Sequence placement matters.
272488 permits an independently verified alternative notification service.
272496 correlates each designated sudo administrator with its own SELinux role
and type; separate favorable matches cannot satisfy this requirement.

Concept refinement: terminal/ordered predicates, scoped typed crypto-policy
inspection, paired same-record constraints and explicit source disagreements.
Full RHEL reading is complete (445/445). This establishes requirements coverage,
not full OVAL dependency closure or scanner equivalence for all 445 rules.

### Windows Server 2025, ordinals 1–50: inventory, accounts, permissions and roles

Read all 50 complete check texts; reread 18–20 after output truncation. 277982
requires authoritative patch deadlines, not merely patch-agent installation.
277983/985/987/988/989/990/991 depend on hardware approvals, identity-to-person
and duty relationships, organizational policies, departure events or exceptions.
Local metadata alone cannot prove these. 277986 combines enabled SID-500 password
age <=60 days with LAPS policy AND successful operation, with standalone LAPS
exception. 277990 annual rotation also requires rotation on knowledgeable staff
departure: a recent timestamp does not satisfy that event condition by itself.

277992 inspects effective AppLocker deny-default category policy, or another
approved tool. 277993 explicitly requires TPM 2.0 and readiness. 277997 covers
local volumes, accepts NTFS/ReFS/CSVFS, excludes recovery/EFI partitions. 277998–
278001 use context-specific ACE rights and inheritance/propagation, special
principals and domain-controller variants; Windows ACLs cannot be reduced to the
POSIX mode allowance prototype or a sorted list of permission names. Registry
permissions also allow a named exceptional SID. 278002 limits standard principals
on shared printers only; excludes nonshared PDF/XPS and special application owners.
278007 requires BOTH share and filesystem access restriction to approved users.

278003 excludes enabled builtin administrator/application accounts and approved
necessary inactive accounts; Never-login is explicit, distinct from collection
error. 278004 treats AD blank Passwordnotrequired as finding, unlike an unknown
collection. 278005 has different domain/local exclusions including krbtgt.
278008 explicitly searches all drives for p12/pfx but has approved application
and noncertificate exceptions: extension alone is a candidate, not necessarily
proof. Native scanner discovery is required; no PowerShell filesystem search.
278009 permits documented hypervisor/storage encryption evidence. 278011 has
installed-role inventory compared with approved required roles, not a universal
allowlist. 278013/014 temporary/emergency lifecycle needs a defined time origin
and crisis-resolution evidence, including the ongoing-crisis exception.

278015/019–022/026 distinguish installed from Available/Removed; unsupported or
failed queries are not absence. 278016 FTP role exception; 278017/018 title mentions
organizational need but check does not state its approval procedure. 278018 tests
Bluetooth startup automatic, not any hardware existence. 278023–025 present
alternative SMB1 absence versus BOTH server/client disablement, not any one of
three sufficient predicates. Keep applicability Assessments distinct, avoiding
circular rule-result dependencies. 278027/028 per-site FTP configuration/scope.
278029 time source varies with domain/PDC-emulator role. 278030 unresolved SIDs
require actual identity invalidity: temporary domain disconnection is not orphan
proof. 278033 accepts lockout duration 0 as admin-only release, otherwise >=15.

Concept refinement: authorization-aware identity records, role-scoped expectations,
real ACL semantics, event-linked evidence, typed inventory queries via existing
shellcommand where suitable, and explicit alternatives/conditional subrequirements.

### Windows Server 2025, ordinals 51–95: numeric policy and audit matrices

Read all 45 check texts. 278034 lockout bad count is 1..3, whereas 278033 permits
zero. 278037 maximum password age 1..60; 278036 history >=24 despite title's 24.
278039 permits an external four-character-type filter only when it requires the
builtin option disabled; otherwise enable fallback. No universal boolean shortcut.
278041/042 require actual offload process/cadence, interconnected real time versus
standalone weekly. A configured destination alone is weaker evidence. 278043–045
resolve actual event-log paths rather than assume defaults. 278046 executable ACL
is NA on Core; only TrustedInstaller may modify/full-control Event Viewer.

278047–078 repeat audit subcategory success/failure expectations with a prerequisite
that subcategory policy overrides legacy categories. A table can remove repeated
instructions while retaining independent Rule identities, actual capability and
stable subcategory identifiers (localized strings are display, not identity).
278064/065 allow Not Configured for VM/NAS excessive events; do not generalize to
all audit rows. 278066 says 'Audit Audit Policy Change' in its example; record the
wording anomaly rather than resolve to an invented different subcategory.
Existing supported Windows audit-policy collectors or fixed AuditPol query should
be investigated before a new auditing language/runtime. Detailed audit-policy
presence alone does not prove effective auditing if override is disabled.

### Windows Server 2025, ordinals 96–145: explicit registry contracts and actual behavior

Read all 50 texts. Many are simple typed registry comparisons and need a readable
registry recipe/editor, not a new assessment runtime. Preserve hive/path/value,
REG_DWORD/REG_SZ and explicit missing-value outcome. 278091/109–111/118/122 accept
missing names due to stated defaults; neighbors generally FAIL on absence.
Unknown/permission-denied is not missing. 278091 finding sentence rejects 7 but
listed acceptable values are 1,3,8 or absent; undefined values need source-contract
resolution. 278104 similarly names valid download modes and rejects internet 3;
do not silently accept every other integer. 278087 UNC values require both parsed
properties on EACH of two share patterns, allow extra entries, domain-joined only.

278090 explicitly warns registry settings alone do NOT establish VBS operation:
actual DeviceGuard status must be Running and RequiredSecurityProperties contain
Secure Boot 2, optionally DMA 3. This is a strong counterexample to collapsing
behavioral requirements into configuration checks. 278092 excludes domain
controllers. 278096/097 split battery and plugged-in contexts. 278105–107 exempt
direct audit-server writers; Security size is environment-dependent week capacity,
not universally the 5GB example. 278108 applies only to unclassified systems.
278125–129 distinguish client and service paths even with identical value names.
A table shorthand SHALL retain each row's path, type, applicability, absence and
comparison semantics; it SHALL NOT inherit a convenient global missing policy.

### Windows Server 2025, ordinals 146–195: directory objects and scoped sets

Read all 50 texts; reread 163–173 to recover the truncated middle. 278133–137
require the named Default Domain Policy, not arbitrary local/effective settings;
minutes/hours/days differ, zero explicitly forbidden for service/user ticket
lifetimes but not explicitly addressed in renewal/skew finding language. 278138
resolves NTDS file locations from registry; 278139 resolves SYSVOL share location
then inspects FIRST directory level. Example paths are not source constants.
278140–142 distinguish directory property/extended rights, standard principals,
object classes, inherited permissions, Exchange and approved distributed-admin
exceptions. Severity changes with authentication data presence, a Rule reporting
concern rather than silently changed technical truth.

278143 correlates user-share and NTDS database logical PARTITION identities;
hidden user shares ending '$' remain in scope, unlike administrative system shares.
A suffix filter is incorrect. 278144 role/application necessity and 278145 network
classification/Type-1 crypto require authoritative organizational evidence.
278146 is an actual anonymous LDAP search probe outside root DSE: network or TLS
failure is not expected authorization denial; risk mitigation affects severity.
278147 permits two focused query methods, requires present MaxConnIdleTime <=300.

278148–153 are SACL audit coverage with success/failure, inheritance, property GUIDs,
object-type and descendant scopes. They are distinct from DACL restriction checks
and audit subcategory settings. Some source notes permit adding duplicate identical
success entries; do not turn a display count into a new universal cardinality law.
278159 certificate existence and 278160 issuer approval differ; Component CIO CA
still a CAT II finding, not an automatic pass. 278161 checks UPN formatting with
alternate-token organizational formats; formatting does not prove CA issuance.
278162 any enabled AD user without required smartcard is finding, no invented
application-account exclusion from neighboring rules. 278165–167/175 grant lists
are subset-of allowed principals; 278168/169/171/174 denial lists must CONTAIN
Guests, not equal Guests. 278170 requires EMPTY deny-service assignments on DCs.
278165 application exception additionally requires vendor evidence and account
password controls. 278176 krbtgt password age <=180 days, distinct from humans.
278177 requires member-server admin responsibility and replacing Domain Admins.
278178 notes scanner credential limitations; temporary scan-time weakening must
not be misreported as compliant steady state.

Concept refinement: typed subset/containment/empty operators, GUID-based directory
permission/audit records, explicit named policy scope, resource-to-resource joins,
and provenance for process/approval evidence. Supported userright_test, NOT
currently deprecated accesstoken_test, is the relevant OVAL family to investigate.

### Windows Server 2025, ordinals 196–235: sets, certificate stores and delegated text

Read all 40 check texts. 278181 CachedLogonsCount is REG_SZ but numeric <=4;
registry storage type and parsed comparison datatype are separate. 278182 states
an explicit SDDL string; replacing string equality with effective-ACL semantics
would be a different method requiring validation. 278184 requires Guests plus
root/domain admin SIDs and either local-account SID 113 OR local-admin SID 114 on
domain members. Domain SID resolution is relational, not wildcard match '*512'.
278186 title excludes all extra deny-service principals, but check only requires
two on domain systems; record title/check discrepancy. Standalone requires empty.
278190 requires actual SecurityServicesRunning contains 1: registry LsaCfgFlags
is explicitly insufficient. 278192–194 certificate-store paths are Cert: provider
queries, NOT filesystem searches; a narrowly fixed shellcommand is legitimate.
Typed certificate collector is also an option. Root/interoperability/CCEB stores,
issuer/subject fields, expiration and classified applicability differ. Names are
examples, not permanent exhaustive authoritative trust lists. 278194 alternate
instruction's CN wording references DoD Interoperability despite CCEB target;
flag before claiming a normalized identity predicate is source-equivalent.

278197/198 identify builtin accounts despite rename; names alone are unstable.
278204 requires registry presence even though 30 is default. 278206 timeout 1..900.
278207 legal notice preserves entire exact required text. 278208 permits an
organization-defined noncontravening caption but explicitly requires manual review
for such titles; do not label every nonstandard caption an automated failure or
an arbitrary Organizational Input string an automatic pass. Its referenced
WN25-SO-000150 actually addresses smartcard removal, an apparent cross-reference
anomaly. 278209 allows documented operational alternative requiring actual manual
locking policy. Client/server signing paths differ despite identical value names.
278218 EveryoneIncludesAnonymous is a prerequisite cited by earlier default ACL
rules; default ACL evidence alone is incomplete without that condition.

### Windows Server 2025, ordinals 236–270: masks, user context and exception-bearing rights

Read all 35 check texts. 278223/227/228 specify exact numeric cryptographic masks;
'contains these bits' could accept forbidden bits and is not equivalent without
source/runtime proof. 278226 wording 'at least negotiate' contrasts with exact
registry value 1: document before accepting stronger-looking 2. 278232–239 UAC
NA on Server Core; don't apply that exclusion to neighboring non-UAC rules.
278234 accepts admin consent OR credentials on secure desktop (2 or 1).
278240 is HKCU, accepts absent or 2 but fails 1. Scanning only the service runner's
HKCU cannot establish all relevant users' compliance; source population is not
fully specified here and needs author/scanner contract, unloaded hive collection
and per-profile errors. This is Windows evidence for principal-scoped Objects.

278241/242/246/248/256 empty assignment requirements are not interchangeable with
subset-of lists. 278242/243/244/246/247/250/252/253/254/256/257 permit specified
application exceptions with vendor need, ISSO evidence and password controls;
several demand highly privileged password protection too. 278245/248/249/251/255
lack that generic exception: table defaults must not grant it to every row.
278249 permits Virtual Machines SID S-1-5-83-0 only when Hyper-V role exists.
278257 also permits an organizational Auditors group. A constrained authorized
principal list cannot by itself prove vendor necessity and required companion
controls. Supported user-right collection plus same-principal exception evidence
is preferable to reviving deprecated accesstoken_test or arbitrary command inputs.

### Windows Server 2025, ordinals 271–291: final rights and cross-platform SSH

Read all 21 complete texts. 278258/259 subset-of Administrator grants; 278261/262
application exceptions retained. 279918/920–923 introduce further subcategory rows;
Sensitive Privilege Use repeats earlier success/failure requirements, but equal
intention alone does not prove complete Assessment reuse. 285313 title says must
implement OpenSSH while check is NA if not installed; preserve/check that mismatch
before strengthening applicability. Client-only versus server installation needs
source-graph analysis. 285314 includes actual banner display BEFORE access plus
explicit uncommented Banner directive; path presence alone does not prove content
or display behavior. 285315 approved alternate MFA is applicability exception.
285317 requires both rekey dimensions, not exact 1G/1h merely from example.
285319 finding language <=600 does not explicitly reject zero, despite SSH zero
meaning disabled; flag inferred-intent question, do not silently repair.
285320–322 ask default ACLs, with public keys as restrictive as private keys here.
285321/322 contain PowerShell filesystem discovery pipelines; proposed native
scanners SHALL own those searches even when limited to one directory. 285323
requires explicit noncommented GSSAPI no; effective default alone is not enough.

Concept refinement: reuse cross-platform requirement patterns without merging
Unix/Windows collector semantics, retain explicit directives where required,
separate behavioral evidence from text proxies, and native file discovery from
legitimate certificate-provider/API queries. Complete Windows reading is now
291/291. Total reading coverage: 736/736 rules in two pinned published benchmarks.
