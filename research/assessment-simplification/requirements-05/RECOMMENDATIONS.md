# Easier methods suggested by reading both complete STIGs

**Experimental proposals, not accepted NG syntax or executable content.** The
source versions and exact original Check Text for every cited rule are pinned in
[README](README.md) and the two evidence JSON files. RHEL anchors below use
002.009.013; Windows anchors use 001.001.001. The reading is complete; full OVAL
closure and target execution for the additional examples have not been performed.
“Existing approach” here means the source's Check Text procedure, not a claim
that its automated OVAL graph implements every procedural requirement.

The key shift is to give authors understandable **Objects and questions**:
“each user's own home,” “the device backing this filesystem,” “the setting for
this user,” “the last active rule.” A library can handle collection details, but
the scope, exceptions and meaning of the question must remain visible.

All examples below are human views/pseudocode. They MAY become an editor over
existing native content, an optional compiler recipe, or a directly evaluated
operation if an existing-method gap is demonstrated. They do not currently compile.
No new runtime/schema feature is justified merely because its example is concise.

## 1. A settings table that makes absence visible

**Windows SV-278080, SV-278091, SV-278109 and SV-278181.** The original procedures
repeat hive/path/name/type/value instructions. Some require explicit presence;
others accept absence because the stated default is secure. CachedLogonsCount is
stored as REG_SZ but needs a numeric comparison. This necessary distinction is
easy to lose in a general “secure settings” shorthand.

```text
Object: the selected machine's registry

Setting                         Stored type    Requirement       If absent
NoLockScreenSlideshow           DWORD          equals 1          finding
NoDataExecutionPrevention       DWORD          equals 0          acceptable
CachedLogonsCount               STRING         integer <= 4      finding

Each setting retains its full hive, path and registry view.
CachedLogonsCount applies only to domain-joined member servers.
```

The actual stored table would include full paths, per-row applicability binding,
parsed datatype and error policy. The illustration omits those long paths only
for presentation, not from semantics. Prefer a direct editor for existing
windows.registry Objects/States/Tests. A table expander is optional and needs
per-row native source mapping. Missing-value allowances SHALL NOT be inherited
from adjacent rows. Unsupported parse/type SHALL remain unresolved/error according
to the eventual contract, not be coerced to zero.

**Acceptance cases to execute later:** absent slideshow value → finding; absent
DEP value → acceptable; denied access to DEP → collection error, not acceptable;
CachedLogonsCount string '4' → acceptable, '5' → finding, 'four' → invalid numeric
observation. Exact behavior for malformed/undefined values needs the source graph
and supported collector contract. DriverLoadPolicy's listed values versus its
“7 is a finding” sentence remain an explicit source question.

**Generalizes:** many Windows registry rows and simple typed configuration values.
Low scanner cost if existing capability suffices; moderate expander/UI maintenance.
Does not replace running-behavior or Windows ACL checks.

## 2. Say “only,” “includes,” and “nobody” as different set requirements

**Windows SV-278166, SV-278168, SV-278170, SV-278184 and SV-278249.** Existing
procedures export/review user-right lists. “Only Administrators may have a grant”
excludes outsiders; “Guests must be denied” requires inclusion while allowing
additional denials; DC deny-service requires an empty assignment.

```text
Object: effective user-right assignments on this server

Add workstations to domain: only Administrators may be assigned.
Deny network access on a DC: assignments include Guests.
Deny service logon on a DC: nobody is assigned.
Create symbolic links: only Administrators may be assigned,
  plus Virtual Machines when the Hyper-V role is installed.
```

Use supported userright_test-derived collection/evaluation or a focused existing
query. Do not support deprecated accesstoken_test. Stable SIDs identify principals;
localized names are display. Domain and root-domain SIDs need authoritative
resolution. Applicability remains separate Assessment logic. Organizational Input
MAY provide delegated constrained authorized identities, never executable choices.

**Cases:** {Guests,another-denied-group} satisfies includes Guests but fails
equals Guests; {Administrators,Users} fails only Administrators; confirmed empty
grant list satisfies a subset-only condition, but a separately required membership
would fail; empty DC deny-service passes, unreadable assignment fails to establish
that fact. Hyper-V principal on a non-Hyper-V server is an extra grant. On domain
members SV-278184 accepts SID-113 OR SID-114 but also requires the domain/admin and
Guests denials. An unresolved domain SID must not match an unrelated SID by suffix.

**Generalizes:** package/protocol/algorithm/principal lists. Set operators already
exist in the larger language; these may be readable recipes rather than new
operators. Main risk is confusing all-required, no-extra and exact equality.

## 3. Choose the fact: configured, running, and enforced

**Windows SV-278090 and SV-278190; RHEL SV-258005–SV-258028 GNOME family.** VBS
checks explicitly say registry settings alone are insufficient. The existing
procedure queries Win32_DeviceGuard and examines Running/security-property arrays.
GNOME checks distinguish values from whether users can override them.

```text
Object: DeviceGuard runtime status on this domain member
Require virtualization-based security is Running.
Require its required security properties include Secure Boot.
Require its running security services include Credential Guard.

Object: selected users' GNOME idle policy
Require timeout is between 1 and 600 seconds.
Require users cannot change the enforced timeout.
```

These are illustrations spanning independently identified Rules, not one merged
Rule. Query DeviceGuard through an existing supported capability or fixed
shellcommand/CIM query; don't invent a new security-service language to avoid a
simple API call. GNOME principal/profile acquisition still needs a scope contract.

**Cases:** registry enabled but runtime stopped → finding; running VBS with
properties {1,2,3} meets Secure Boot, {1,3} does not; a query failure is error,
not stopped or not applicable. GNOME timeout 600 with writable=true fails the
separate lock requirement; 0 means disabled and fails the numeric requirement;
root-only query cannot establish every selected user's enforcement.

**Generalizes:** service startup/live state, sysctl persisted/runtime, effective
versus explicit settings. Mostly observation-contract work; scanner cost varies.

## 4. Compare each Object with its own related Object

**RHEL SV-258052 and SV-258053.** The source account/home procedures derive home
directories and compare ownership/group. Instead of parallel lists and generated
Variable chains, let authors describe whose relationship is being checked.

```text
For each selected local interactive user:
  The user's home directory exists.
  That home directory's group ID equals that user's primary group ID.
```

Selection SHALL keep the STIG's actual interactive-user scope/exclusions visible;
UID >=1000 alone is not a universal interactive-user definition. Acquire accounts
and home metadata with native scanners. First investigate existing Object
components/Variables/records; a relationship operator is experimental until those
methods demonstrably cannot preserve the keyed association readably.

**Cases:** Alice GID1000/home1000 and Bob GID1001/home1001 → satisfied; Alice home
GID1001 remains a finding even though Bob's account has GID1001. Missing Alice
home fails its existence clause; permission-denied home metadata is error; duplicate
account identity is unresolved, not “choose the favorable one.” The source home's
link-following/filesystem scope must be preserved, not invented from this sketch.

**Generalizes:** certificate-to-account mappings, share-to-directory, log-to-path,
setting-to-profile, DNS zone-to-records. Readability gain plausible, collector and
join-completeness costs unmeasured; no target equivalence claim.

## 5. Describe backing-device ancestry rather than grep for encryption

**RHEL SV-257879; Windows SV-278009.** RHEL's lsblk procedure asks whether
persistent filesystems have LUKS protection, excluding /boot and /boot/efi and
allowing documented alternate encryption. Unrelated crypt devices prove nothing
about an unencrypted filesystem.

```text
For every in-scope persistent filesystem except the source's boot exceptions:
  Its backing-device ancestry includes a LUKS encryption layer,
  or approved evidence establishes the permitted external encryption alternative.
```

“Ancestry” needs stable graph identity, layered/LVM/multipath relationships, cycle
handling, traversal completeness and which path/layer combinations provide actual
coverage. This sketch SHALL NOT assume one encrypted branch makes a multi-device
filesystem safe. Investigate current storage Objects and a bounded metadata query
first. Shellcommand MAY query storage metadata; it SHALL NOT discover files by
searching filesystem trees. External encryption evidence is not inferred from a
VM flag or an arbitrary supplied boolean.

**Cases:** ext4→LVM→LUKS gives a protected chain; ext4→plain disk plus an unrelated
LUKS disk does not; unknown backing edge leaves protection unproven; a filesystem
with encrypted and unencrypted data-bearing branches requires an explicitly
validated coverage rule, not this sketch's automatic pass. Boot exceptions are
source-specific; VM without approved encryption evidence remains unresolved/failing
according to the actual alternative's contract.

**Generalizes:** storage, resource containment and parent-chain properties.
High implementation/compatibility cost until product graph semantics are defined.

## 6. Compare partition identity, not spelling or drive letters

**Windows SV-278143.** Existing Check Text reads the NTDS database path from
registry, enumerates organization-created shares and compares logical partitions.
Administrative shares are excluded, but hidden user shares ending '$' are included.

```text
Object: the configured directory database file
Object: all organization-created user-data shares, including hidden shares
For each such share:
  Its resolved logical partition differs from the database's logical partition.
```

Native acquisition resolves partition identity, mount points and junctions.
Fixed administrative queries may obtain registry/share metadata; shellcommand
does not search the filesystem. Distinguish collection exclusions from assessment
exceptions, and source-defined logical-partition identity from physical disk ID.

**Cases:** different textual paths on the same logical partition → finding;
different partitions on one physical disk can satisfy this check; Payroll$ is
still in scope; C$ system share is excluded by actual share classification;
unresolved junction or incomplete share inventory does not establish separation.

**Generalizes:** relational resource identity. Requires native metadata semantics
and testable scope; a simple string-prefix compiler is rejected.

## 7. Make “for which user?” part of the Object

**Windows SV-278240 and RHEL's GNOME policy family.** HKCU in a service-run scanner
can refer to the service account. It does not automatically mean every user who
uses attachments. The original HKCU check accepts absent SaveZoneInformation or
DWORD2, rejects DWORD1, but does not fully specify the scanned user population.

```text
For each publisher-defined in-scope user profile:
  Observe that user's Attachments policy.
  SaveZoneInformation is absent with a complete observation, or equals DWORD 2.
```

The user population is an unresolved source/author question, not a silent new
all-users requirement. Profile identities, unloaded hives, inaccessible profiles,
new-user defaults and scanner credentials need explicit contracts. Prefer scoped
existing registry/profile Objects before adding a global “all users” primitive.

**Cases:** scanner service value2/user Alice value1 → Alice finding; one complete
absent user value passes that user's source condition; inaccessible Bob hive does
not count as absent; empty selected population needs explicit applicability and
existence behavior. GNOME system/profile/per-user policy precedence is a different
collector contract, despite similar readable questions.

**Generalizes:** user-scoped settings and identity-specific policy. High collection
cost; helps prevent misleading scope claims but is not proven automation yet.

## 8. Ask about order, not merely the presence of words

**RHEL SV-258095/258096, SV-258229 and SV-270180.** The procedures respectively
require PAM preauth placement, audit '-e 2' last among noncomment lines, and a
terminal fapolicyd deny-all rule with permissive=0.

```text
In each required PAM stack:
  The required preauth step occurs before the required pam_unix step.
In the persisted audit rule source:
  The last noncomment rule enables immutable mode.
In the compiled fapolicyd rule sequence:
  Enforcement is nonpermissive and the terminal rule denies all remaining access.
```

Each grammar/include/substack/compiled-source view is distinct. Native scanners
acquire all required files/includes; a parser preserves sequence and source mapping.
“Before” needs clarification for repeated modules/branches: never guess first/last
winner. Try existing text/record/order expressions; reviewed recipes may hide their
mechanics. New directly evaluated sequence operations need domain conformance.

**Cases:** preauth after pam_unix → finding; '-e 2' followed by another active
rule → fails last-rule condition even if token exists; trailing comments don't
change last noncomment rule; deny-all followed by allow violates terminal placement;
unreadable included PAM stack leaves effective order unproven. Equivalent fapolicyd
deny/deny_log/deny_audit actions must retain the source's accepted alternatives.

**Generalizes:** order-sensitive configuration. Moderate/high parser cost; unsafe
generic regex-to-sequence normalization is rejected.

## 9. State a derived artifact's freshness against its own inputs

**RHEL SV-258028.** The source compares dconf database timestamps with related
keyfiles. A shell find script is unnecessary and disallowed for our native approach.

```text
For each selected dconf database:
  Its modification time is not earlier than any of its related source keyfiles.
```

Native Object acquisition preserves database-to-keyfile association and scope.
The operation is an existing typed comparison plus max/quantification candidate;
investigate Variables/functions before proposing a new freshness operator.
Timestamp resolution/time basis and absent database/source behavior need contracts.

**Cases:** DB mtime100, its source times90/100 → satisfies timestamp condition;
one source101 → finding; another database's source200 cannot make this DB stale;
missing DB fails existence, unreadable source leaves freshness unproven. A fresh
timestamp on wrong compiled contents passes this timestamp predicate but does not
prove content correctness. Do not claim a stronger cryptographic build guarantee.

**Generalizes:** compiled/generated configuration and caches. Likely modest
evaluation cost; acquisition and clock/filesystem semantics remain necessary.

## 10. Select a configuration record, not a matching line anywhere

**RHEL SV-258146–SV-258148 and SV-258123.** Source examples qualify
rsyslog forwarding action versus module blocks and security options in particular
sections. Same key/value in a different block does not satisfy the selected action.

```text
For every selected omfwd forwarding action:
  Its queue is LinkedList, uses the required storage policy,
  and saves queued messages on shutdown as required by the respective Rule.
```

This aggregates a human view across separate Rules; it is not a merged policy.
Use grammar-specific records with parent IDs and explicit duplicate behavior,
not a generic configuration parser that treats every key as interchangeable.
Preserve defaults/explicit presence according to each original check. Native
acquisition owns include discovery; a parser works on acquired content.

**Cases:** LinkedList in a module block but omfwd queue missing → not established;
two actions with one bad queue → finding where all selected actions are required;
two attributes on different actions cannot combine into one compliant action;
unreadable include → incomplete scope, not a vacuous pass.

**Generalizes:** INI sections, Apache contexts, SSH Match blocks and service instances.
Library contracts needed per grammar; high risk from undocumented scope broadening.

## 11. Treat dates and procedural evidence as real requirements

**RHEL SV-258047; Windows SV-278013/278014, SV-277990 and SV-278106.** Temporary
accounts have a 72-hour lifecycle, emergency accounts have a crisis-resolution
condition, service-password rotation also follows knowledgeable staff departure,
and a security log needs a week's environment-specific capacity.

```text
For each identified temporary account:
  Its automatic expiry is within 72 hours of the authoritative lifecycle start.
For each emergency account:
  Apply the source's expiry/crisis-resolution requirement and documented exception.
For each manually managed application credential:
  Rotation satisfies the annual deadline and required departure-triggered rotation.
```

The start of 72 hours is not supplied fully by account-expiry metadata alone.
Creation/provisioning evidence cannot be replaced by last password change. Calendar
year versus fixed days, timestamp truncation/timezones, “Never,” and source query
filter completeness need attention. Log capacity depends on workload/offload;
the Windows 5GB and RHEL 10GB examples SHALL NOT become fixed universal requirements.

Existing focused administrative queries can provide account timestamps. Separate
manual or authenticated external observations provide process/classification
facts; a signed approval record alone does not prove the technical condition it
approves. Publisher Assessment choices MAY describe valid automated/manual methods;
Organizational Input SHALL NOT select commands or which Tests execute.

**Cases:** expiry at start+72h versus +72h+1s requires explicit precision contract;
unknown lifecycle start cannot prove the deadline; staff departure yesterday with
unchanged password fails event-triggered rotation despite an age of only ten days;
an ongoing crisis needs its documented exception, not automatic NA; direct-server
audit logging has the source capacity exception, a mere configured destination
does not prove actual direct writing.

**Generalizes:** lifecycle/deadline checks and operational controls. Evidence
integration may cost more than language changes; forced automation is rejected.

## 12. Keep discovery native; use existing shellcommand for suitable queries

**Windows SV-278008, SV-285321/285322 and SV-278192–194.** Original procedures
search all drives for p12/pfx and enumerate SSH keys; certificate-store checks use
the Cert: PowerShell provider. Those are different acquisition problems.

```text
Object: scanner-discovered in-scope certificate-installation candidates
Require no prohibited installation file remains, preserving application exceptions.

Object: scanner-discovered SSH host-key files for this installation
Require each file's source-defined Windows access policy.

Object: local machine Trusted Root certificate-store entries
Require the applicable authorized, valid, unexpired DoW roots.
```

The scanner SHALL own all filesystem searches, including one-directory searches,
and retain remote filesystem exclusions, traversal efficiencies, permissions,
links/junctions and completeness. No find/Get-ChildItem filesystem shell recipe.
A fixed Cert: provider or DeviceGuard/AuditPol administrative query MAY use existing
shellcommand; it does not need a new language feature merely to return typed facts.
Organizational Inputs SHALL remain constrained values, never command interpolation.

**Cases:** pfx extension with documented noncertificate application use is not
automatically prohibited; denied directory means absence unproven; excluded remote
scope must be reported, not misrepresented as all drives; a valid-looking CN with
untrusted identity does not establish an authorized root; one valid certificate
does not cover all publisher-required identities; cert-query failure is error.

**Generalizes:** file inventory versus service/provider metadata. Native scanner
capabilities already carry substantial necessary complexity. Reuse them.

## Comparison and next experiments

No readability/effort reduction percentages are claimed: no author trial occurred.
The removal of repeated instructions and explicit identities makes these promising,
but terseness alone is insufficient evidence.

| Approach | Expected author benefit | Scanner/tool cost | Main compatibility risk | Next evidence |
| --- | --- | --- | --- | --- |
| Registry and right-assignment tables | Less repetition; clear absence/set meaning | Low runtime, moderate tooling | Per-row contracts flattened | Lower one bounded table to existing native graph; independent source cases |
| Running/enforced observation recipes | Correct fact easy to name | Existing query plus typed contract | Configured mistaken for operating | DeviceGuard target observations, including unsupported/error |
| Keyed own-object relationships | Natural “its” comparisons | Existing Variables first, relation tool if needed | Wrong-parent witness/partial inventory | Home GID or NTDS-share identities with complete source graph |
| Storage ancestry | Express security coverage directly | High unless metadata capability suffices | Partial/encrypted branch mistaken for all data | Layered and multi-device targets before language adoption |
| Principal contexts | Makes affected user explicit | High collection scope cost | Runner HKCU mistaken for all users | Define publisher population, loaded/unloaded hive fixtures |
| Sequence and scoped records | Avoids token-presence false assurance | Moderate/high grammar work | Includes/order/default behavior changed | PAM/rsyslog/fapolicyd source-contract cases |
| Derived freshness | Clear relation to selected sources | Modest evaluation; native acquisition | Wrong sources/precision or overclaim | dconf per-database metadata cases |
| Mixed automated/manual evidence | Honest coverage for real requirement | Evidence workflow integration | Approved/documented substituted for verified | Explicit independent evidence and expiry contracts |
| Existing focused shellcommand | Removes unnecessary legacy complexity | Low new-language cost; target testing required | Exit/localization/error and query scope | Fixed typed API adapters, no filesystem traversal |

Recommended next bounded tasks: a Windows registry table with both absence
contracts and a user-right subset/containment/empty view; then one genuine new
relationship (home GID) and one actual-runtime observation (DeviceGuard). Resolve
complete source graphs for those selected experiments, and compare old/new on the
same targets before claiming equal scanner results. Retain direct native editing,
pinned helper/compiler versions and source maps so content authors can work around
implementation defects. No mandatory second language is proposed.

Full reading also limits earlier claims: crypto manual 13 versus automated 12
resources; audit interfield, exit-code, subject-type and terminal-state cases exceed
the prior restricted auid model; Windows ACL/SACL semantics cannot inherit the
POSIX allowance proof; explicit SSH directives and rekey dimensions cannot be
silently converted to effective/default-only observations. New capabilities stay
experimental, supported rare capabilities stay retained, deprecated Tests stay
unsupported, and provenance remains separate from executable semantics.
