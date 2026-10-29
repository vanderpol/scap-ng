# Observed source oddities and improvement opportunities

Prepared 2026-10-29 for the project owner. Tracking:
[#251](https://github.com/vanderpol/scap-ng/issues/251) and
[#255](https://github.com/vanderpol/scap-ng/issues/255).

**The highest-impact producer-side opportunity is the catalog generator:**
992 automated Rules across 21 packages have complete embedded check content,
but their new catalog entries use the wrong namespace for standard URI bindings.
Several smaller, repeatable authoring problems are also suitable for generator
checks. The integer-to-concat failures need a standards decision before they
should be called content bugs. SV-215833 deserves a focused authoring review.

This report covers all oddity classes identified by the existing pinned
65-benchmark conversion and follow-up investigations. It is not a new exhaustive
semantic audit of every original check, and it makes no scanner-runtime claims.
No source content, validator, schema, compiler or scanner was changed to produce
it. Suggested areas of control are hypotheses for you to confirm, not assumptions
about which artifacts you own.

## How to use this report

The companion **affected-rules.csv** is the working list. Filter `finding_ids`
for an O-number below, then use the exact source filename, Rule ID, original
diagnostic and pinned source link. It includes 3,024 distinct Rules: all 2,981
currently blocked automated Rules, five additional manual Rules with the Switch
ID anomaly, and 38 IOS XE Rules whose tooling limitation is now resolved.

**findings.json** retains the detailed classification and 71 original closure
validation records. The PDF is a printable copy of this report. All three are
included in the accompanying report package; the source originals are also
preserved in the complete DRAFT archive.

Finding counts overlap. For example, one Rule can have a wrong reference type,
a deprecated Object, and a bad pattern operation. Counts are affected Rules,
not unique source nodes or guaranteed conversion gains.

## Where you may be able to improve the producing pipeline

| Priority | Finding | Observed reach | Likely place to investigate |
| --- | --- | --- | --- |
| First | O01: foreign namespace on catalog URI entries | 992 automated Rules, 21 packages | Catalog/XML element creation |
| First | O02: stale standard catalog references | 20 dangling entries in 20 packages; 979 of those 992 Rules share these packages | Enhancement/repackaging graph construction |
| First | O03: missing record datatype | 11 investigated Rules | Cmdlet Object generator |
| First | O04: pattern paths with prohibited recursion behavior | 7 investigated Rules | File acquisition templates |
| First | O05: missing/incompatible operation on pattern entities | 11 investigated Rules | Regex acquisition templates |
| First | O06: Test-level absence with a State reference | 4 investigated Rules | Test construction/requirement modeling |
| First | O07: wrong Object/State/Filter family | 4 investigated IIS Site Rules | Test family and reference generation |
| Review | O11/O12: IOS XE text-as-int and delimiter | SV-215833 | Timeout-check Variable pipeline |
| Review | O08: deprecated constructs | 162 observed Rules, including 151 primary effective-Test exclusions | Supported-content maintenance |
| Review | O09: nonstandard sqlext packages | 137 automated Rules in four SQL Server packages | Extension publishing/compatibility |
| Cleanup | O13: Switch IDs carry ms.dns prefix | All 42 Rules in the IOS XE Switch NDM package | Identifier/provenance template |

The small validation counts above are observed counts within investigated
closures, not a claim that the other content is free of the same pattern.

## O01/O02 — catalog entries and stale references

Every one of the 992 requested Definitions is present in exactly one embedded
OVAL component. The intended source chain is also present: URI entry, matching
component-ref, component, exact Definition ID. The problem is the entry's QName:

```xml
<!-- Observed extension element: SCAP namespace -->
<ds:uri name="...-oval2.xml" uri="#..._cref_...-oval2.xml"/>

<!-- Standard XML Catalog entry, shown as an improvement target -->
<cat:uri name="...-oval2.xml" uri="#..._cref_...-oval2.xml"/>
```

`ds` denotes `http://scap.nist.gov/schema/scap/source/1.2`.
`cat` denotes `urn:oasis:names:tc:entity:xmlns:xml:catalog`.
This is a namespace-URI issue, not a choice of prefix spelling. Changing a
prefix while keeping the SCAP namespace would not fix the standard binding.

The catalog XSD allows foreign elements with `namespace="##other"` and
`processContents="skip"`. These entries can therefore pass structural XSD
validation while contributing no standard XML Catalog URI mapping. This is why
an XSD-only packaging check can miss the problem.

Twenty affected packages also retain one older standard catalog entry whose
component-ref points to a missing old component. The remaining affected package,
Windows 2012/2012 R2 DC, has a usable old catalog but lacks standard bindings
for its new foreign entries. The 979 figure is affected Rules sharing the 20
stale-entry packages; it does not mean 979 distinct dangling entries.

**Improvement:** create new entries using the XML Catalog namespace, then check
every standard URI binding, component-ref target, selected check href and
Definition ID after repackaging. Reconcile stale entries with the intended final
component graph. Keep publisher signatures and provenance coherent when issuing
a corrected package. Do not silently rewrite previously signed/frozen archives.

No missing requested Definition or relative-path normalization defect was found
in this 992-Rule cohort. Correct bindings may expose additional content or
converter blockers; 992 is not a promised unlock count.

## O03 — nil cmdlet parameters still need the record datatype

Eleven investigated Windows Rules fail the original assertion that a
`cmdlet_object` parameters entity must have datatype `record`. The relevant
templates emit a nil parameters entity without the required record type.

```xml
<!-- Observed shape -->
<parameters xsi:nil="true"/>

<!-- Type annotation to review; intended nil semantics must stay intact -->
<parameters datatype="record" xsi:nil="true"/>
```

Nil does not waive the datatype constraint. The affected sources span Windows
10, Windows 11, and Server 2016/2019/2022/2025. Review the common generator rather
than patching eleven unrelated checks by hand. The exact Objects and Rules are
listed under O03 in the CSV.

## O04 — path patterns and recursion behaviors conflict

Seven investigated Rules combine a pattern-match path entity with `max_depth`
and/or `recurse_direction`, which the pinned original Schematron prohibits.
Examples include .NET SV-225229 and Windows 11 SV-253280, with analogous checks
in Windows 10 and Server 2016/2019/2022/2025.

**Improvement:** determine whether the intended search is represented by the
path regex or by traversal from a selected directory, then author a permitted
form. Simply dropping recursion could change the collection population. A useful
generator check is to reject this combination before the signed package is built.

## O05 — pattern entities have incompatible or omitted operations

Eleven investigated Rules fail assertions requiring a pattern entity's operation
to be `pattern match`. They occur in Firefox Windows, .NET, Oracle Linux
7/8/9 and RHEL 8/9. Some original assertions report the same node under both
shellcommand/textfilecontent54 descriptions; the count is distinct Rules, not
the number of assertion messages.

**Improvement:** verify that the entity really contains a regex and explicitly
emit `operation="pattern match"` where the capability requires it. Keep this
separate from comparisons on returned State fields. Do not globally replace
`equals` operations on arbitrary string entities.

## O06 — Test-level none_exist also references a State

Four investigated Rules violate the original rule that a Test with
`check_existence="none_exist"` must not reference a State:

- Oracle Linux 9 SV-271451r1137691.
- RHEL 9 SV-257789r1137691.
- IIS 8.5 Server SV-258446r928857.
- IIS 8.5 Site SV-258445r928856.

**Improvement:** resolve the intended condition. "No selected Items exist" and
"selected Items exist but none match a State" are different requirements.
Removing the State or changing existence without that review can change meaning.
Field-level absence is also a different scope; see O20 below.

## O07 — Object, State and Filter types do not agree

IIS 8.5 Site SV-214451r879567, SV-214452r879568, SV-214463r879643 and
SV-214495r879587 contain original family/reference validation failures.
The diagnostics include `appcmd_test` references that do not resolve to the
required `appcmd_object`/`appcmd_state` family and Filter States of the wrong type.
Some of these Rules also contain deprecated content.

**Improvement:** validate the typed reference graph, not just ID existence.
Every referenced node must have the kind and capability family required by its
consumer. A rename of the XML element alone is not a proven correction: different
capabilities can return different fields and have different collection behavior.

## O08/O09 — deprecated constructs and nonstandard SQL extensions

The primary ledger excludes 151 Rules for effectively deprecated Tests. Detailed
validation of the 71 investigated closures finds 11 additional Rules with
deprecated Objects, States, Tests or attribute values, giving **162 distinct
observed Rules** in O08. This is an overlap-aware inventory of different kinds
of deprecation; it is not 162 deprecated Test types. Examples include legacy
Windows user/access-token/WMI constructs and deprecated Test `check` values.

**Improvement:** keep a versioned support inventory, including explicit later
OVAL reinstatement decisions, and migrate deprecated constructs only to reviewed
semantic replacements. Do not treat every historical `deprecated_info` annotation
as current deprecation if a recorded reinstatement applies. Do not turn old
`check="none exist"` into an arbitrary modern quantifier without checking intent.

Four SQL Server packages use nonstandard `independent.sqlext` content: SQL Server
2016 Database/Instance and SQL Server 2022 Database/Instance. Their 137 automated
Rules are held at the package-extension boundary. This does not establish that
their checks are logically incorrect.

**Improvement:** if maintaining that extension, publish its versioned grammar,
collector/result semantics and compatibility requirements alongside the content.
Using a standard SQL capability is an option only where equivalence is reviewed;
do not assume that changing the element name preserves behavior.

## IOS XE findings: authoring concerns versus standards conflicts

The four Router NDM validation failures below occur in the pinned NIWC enhanced
`oval2` component with `oval:navy.navwar.niwcatlantic.scc.iosxe:*` identities.
The active XCCDF checks point to that component. Attribution to DISA's original
content has not been established.

### O10 — integer-to-concat is a disputed validation boundary

SV-215807r1186318, SV-215812r1137875, SV-215833r961068 and
SV-215854r1156415 insert an integer count into string construction. Their apparent
intent is to format a count inside a regex repetition quantifier. The pinned
Schematron rejects Variable references inside concat unless the referenced
Variable is declared string.

The same schema's FunctionGroup prose says a cast should be attempted before
reporting an error, and explicitly illustrates an integer cast to string for
concat. Its example names a registry component, whereas the failing assertions
restrict Variable references. That exact scope needs standards review.

**Improvement opportunity:** reconcile the casting prose and validator, and test
the intended count-to-regex pipeline. These are confirmed assertion failures;
three of the Rules should not be labeled confirmed content bugs on that basis
alone. Do not change count datatypes or remove assertions just to obtain a pass.

### O11/O12 — SV-215833 has stronger authoring concerns

Variable `...:var:21583304` is declared `int` but described as splitting the
configuration into lines. Variable `...:var:21583307` is also declared `int` and
uses `regex_capture pattern="\s+exec-(.*)"` on that text. A representative capture
from `exec-timeout 5 0` would be `timeout 5 0`, not an integer. That example is
constructed from the expression; no live scanner result is claimed.

The split delimiter is the literal two-character XML string `\n` (code points
92 and 110), not a newline character. OVAL documents a delimiter string. Reliance
on scanner-specific escape interpretation is unverified.

**Numeric captures are valid.** This same Rule has a separate HTTP-timeout
Variable `...:var:21583310` declared `int`, using
`regex_capture pattern="ip http timeout-policy idle (\d+)"`. A capture such as
`5` is a valid integer value for numeric comparison with 300. That branch is
not the text-datatype concern. The concern is confined to intermediate Variables
21583304 (split configuration text), 21583307 (capture `timeout 5 0`) and
21583305 (merge timeout lines), each declared `int`. The `(5|4|3|2|1)` group
in the later State regex checks the merged text; it does not change what the
preceding `regex_capture` Variable returns.

**Improvement:** review those text-bearing intermediate declarations, all
downstream consumers, and the delimiter's actual lexical value. Keep numeric
capture Variables numeric where their captured values are integer-representable.
Add examples with multiple configuration lines and nonmatching/empty output.
This is a stronger content-defect candidate than formatting an integer count as
string, but no source correction or runtime equivalence is established.

### O13 — Switch IDs look copied from DNS content

All 42 Rules in IOS XE Switch NDM enhancedV6 use an `ms.dns` Rule-ID prefix;
37 are automated and five are manual/OCIL-only. This is a confirmed provenance
or template anomaly, not proof that the associated checks evaluate DNS logic.

**Improvement:** review the identifier template for future output. Treat existing
IDs as published identities: changing them requires updating references and
maintaining migration/provenance records rather than casual renaming.

Router SV-215838r1015295's NTP-server `count` is a separate converter limitation
(O17). The 37 Switch automated Rules are in the catalog group O01. The remaining
38 Router Rules have now passed independent static verification (O23); their
earlier failure was our missing reader crosswalk, not a demonstrated source bug.

## Valid source constructs that should not be changed to appease conversion

| Finding | Primary affected Rules | What is actually unresolved |
| --- | ---: | --- |
| O14: Test all_exist | 1,184 | Missing expected populations, error/unknown/incomplete evidence and native existence semantics |
| O15: check imports/exports | 381 | Source-bound external/organizational input and binding recovery |
| O16: multiple aggregation components | 30 | Collection-expression/cardinality/dependency semantics |
| O17: count/split/substring | 33 | Function support: 15 count, 15 split, three substring |
| O18: acquisition comparison/datatype | 2 | Case-insensitive command and version-typed module acquisition |
| O19: non-integer ordered comparison | 10 | Converter's integer-only expansion boundary; original closures validated |
| O20: comparator-bearing field absence | 9 | Absence-versus-comparison normalization requires source-intent review |
| O21: source fields missing from crosswalk | 2 | rpmverifyfile ghost_file/configuration_file field representation |
| O22: Variable-source attributes/function chain | 2 | Valid Solaris source attributes and subsequent split support |

These are conversion/contract boundaries, not an instruction to simplify valid
OVAL. Secondary blockers overlap, and most blocked content has not received
independent semantic verification. The listed construct can be supported by
OVAL while still needing SCAP-NG implementation or contract work.

For O14, a complete successful population of actual Items makes all_exist and
one_or_more agree, but a positive Item does not establish complete accounting of
all expected targets. The real Amazon Linux 2023 SV-274101 example selects seven
audit-tool paths through a Variable. Preserve missing-target, error, unknown and
incomplete distinctions; do not globally replace the source token.

For O18, the two validated originals are .NET SV-225226r961041 (case-insensitive
command acquisition) and Windows 10 SV-220812 (version-typed module acquisition).
Do not erase the operation or cast version to string merely to fit a target.

For O20, examples require an absent stdout/stderr field but also carry a literal
`.*` comparator. That may be redundant authoring, but field absence is not the
same as "a field exists and no values match". The prior owner-approved exact
normalization remains bounded; it is not permission for a global rewrite.

For O21, the affected valid originals are RHEL 7 SV-214799r991589 and Oracle
Linux 7 SV-221653r1015161. Dropping ghost/configuration-file filters could change
which files are assessed. This needs mapping review, not source deletion.

## Practical checks for future published content

If these are within your control, the most useful additions to the producing
pipeline would be:

1. **A semantic reference-closure check after enhancement and packaging.** Resolve
   every selected check href through standard catalog entries to the expected
   Definition, and verify component-ref targets and typed Object/State/Filter
   references. Flag foreign catalog-like elements separately from real mappings.
2. **Original XSD and Schematron checks with per-Rule attribution.** Record exact
   diagnostics; distinguish invalid content, deprecated content and known
   standards/validator conflicts. A green XSD-only run is insufficient.
3. **Template checks for the recurring patterns above.** Record datatypes on nil
   cmdlet parameters, path-pattern/recursion combinations, required pattern
   operations, forbidden none_exist/State combinations, and meaningful ID prefixes.
4. **Small Variable/function examples with expected values and failures.** Include
   count-to-string formatting, text captures, literal delimiters, empty output,
   missing inputs, unknown and errors. Keep observed scanner results distinct
   from static validation or illustrative examples.
5. **A support and extension inventory.** Identify effective deprecations and
   reinstatements, and provide the normative contract for vendor extensions.
6. **Versioned corrections.** Reissue corrected source with new identity/version
   and checksums as appropriate, preserving earlier signed artifacts and a
   concise explanation of what changed and whether evaluation meaning changed.

This report recommends checks; it does not install a new CI gate or change the
existing source-validation policy.

## Evidence and accounting

Pinned production inputs: `niwc-atlantic/scap-content-library` revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5`. Implementation/recovery record:
`vanderpol/scap-ng` at `2e5eaec0caf031d792ea6dd996a649e48a91c24d`.
The report reuses existing ledgers and validation records; it does not rerun
the 65-source conversion.

- 65 benchmarks, 8,892 original Rules, 7,239 automated attempts.
- Separate published static proof total: 4,258 primary automated Rules.
- Residual automated blockers: 2,981. Manual/OCIL-only Rules preserved: 1,653.
- The original complete DRAFT still labels 52 candidates UNVERIFIED; their later
  static proofs are published separately. Neither label implies live runtime parity.
- The 71 detailed closure records combine 32 recorded exclusions and 39 additional
  investigations. They are not a validity census of all 7,239 automated Rules.

Durable supporting records:

- [Complete original-preserving DRAFT](https://github.com/vanderpol/scap-ng-evidence/tree/57032484aa098d18fecf69fe186b2ef753473245/runs/v04-converter/2026-10-29-all-65-complete-draft-stage-one).
- [Separate 52-proof checkpoint](https://github.com/vanderpol/scap-ng-evidence/tree/5b1b027623cd454b263aa60e16122bba503566a9/runs/v04-converter/2026-10-29-stage-two-52-static-proofs-b70802028).
- [Full population/catalog/IOS XE investigation](https://github.com/vanderpol/scap-ng-evidence/tree/5b1b027623cd454b263aa60e16122bba503566a9/runs/v04-converter/2026-10-29-population-catalog-iosxe-investigation).
- [IOS XE exact original excerpts](v04-iosxe-content-investigation-20261029.json).
- [Population/casting/catalog decision packet](https://github.com/vanderpol/scap-ng/issues/255#issuecomment-6508115066).

The accompanying CSV and JSON provide the affected source filenames, Rule IDs,
hashes, confidence and suggested control area for every indexed Rule. Corrections
to NIWC-enhanced artifacts should not be attributed to DISA originals without a
separate authoritative-source comparison.




## Appendix A — all 21 catalog-affected packages

| Pinned package | Automated Rules | Stale standard entry |
| --- | ---: | --- |
| [Active Directory Domain V3R6 / enhancedV2](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Active_Directory_Domain_V3R6_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip) | 17 | Yes |
| [Active Directory Forest V3R2 / enhancedV2](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Active_Directory_Forest_V3R2_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip) | 4 | Yes |
| [Apache Server 2-4 UNIX Server V3R2 / enhancedV2](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Apache_Server_2-4_UNIX_Server_V3R2_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip) | 22 | Yes |
| [Apache Server 2-4 UNIX Site V2R6 / enhancedV2](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Apache_Server_2-4_UNIX_Site_V2R6_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip) | 6 | Yes |
| [Apache Server 2-4 Windows Server V3R3 / enhancedV2](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Apache_Server_2-4_Windows_Server_V3R3_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip) | 23 | Yes |
| [Apache Server 2-4 Windows Site V2R2 / enhancedV2](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Apache_Server_2-4_Windows_Site_V2R2_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip) | 5 | Yes |
| [Apple macOS 13 V1R5 / enhancedV7](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Apple_macOS_13_V1R5_STIG_SCAP_1-4_Benchmark-enhancedV7-signed.zip) | 102 | Yes |
| [Apple macOS 14 V2R3 / enhancedV7](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Apple_macOS_14_V2R3_STIG_SCAP_1-4_Benchmark-enhancedV7-signed.zip) | 152 | Yes |
| [Apple macOS 15 V1R4 / enhancedV8](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Apple_macOS_15_V1R4_STIG_SCAP_1-4_Benchmark-enhancedV8-signed.zip) | 157 | Yes |
| [Apple macOS 26 V1R1 / enhancedV5](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Apple_macOS_26_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV5-signed.zip) | 157 | Yes |
| [Cisco IOS-XE Switch NDM V3R5 / enhancedV6](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Cisco_IOS-XE_Switch_NDM_V3R5_STIG_SCAP_1-4_Benchmark-enhancedV6-signed.zip) | 37 | Yes |
| [Cisco IOS Router NDM V3R6 / enhancedV6](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Cisco_IOS_Router_NDM_V3R6_STIG_SCAP_1-4_Benchmark-enhancedV6-signed.zip) | 29 | Yes |
| [Cisco IOS Switch NDM V3R6 / enhancedV6](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_Cisco_IOS_Switch_NDM_V3R6_STIG_SCAP_1-4_Benchmark-enhancedV6-signed.zip) | 29 | Yes |
| [F5 NGINX V1R1 / enhancedV1](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_F5_NGINX_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV1-signed.zip) | 22 | Yes |
| [MS Exchange 2019 Edge Server V2R2 / enhancedV1](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_MS_Exchange_2019_Edge_Server_V2R2_STIG_SCAP_1-4_Benchmark-enhancedV1-signed.zip) | 55 | Yes |
| [MS Exchange 2019 Mailbox Server V2R3 / enhancedV1](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_MS_Exchange_2019_Mailbox_Server_V2R3_STIG_SCAP_1-4_Benchmark-enhancedV1-signed.zip) | 51 | Yes |
| [MS IIS 10-0 Server V3R6 / enhancedV18](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_MS_IIS_10-0_Server_V3R6_STIG_SCAP_1-4_Benchmark-enhancedV18-signed.zip) | 25 | Yes |
| [MS IIS 10-0 Site V2R14 / enhancedV19](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_MS_IIS_10-0_Site_V2R14_STIG_SCAP_1-4_Benchmark-enhancedV19-signed.zip) | 33 | Yes |
| [MS OneDrive V2R4 / enhancedV12](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_MS_OneDrive_V2R4_STIG_SCAP_1-4_Benchmark-enhancedV12-signed.zip) | 12 | Yes |
| [MS Windows 2012 and 2012 R2 DC V3R6 / enhancedV13](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_MS_Windows_2012_and_2012_R2_DC_V3R6_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip) | 13 | No |
| [MS Windows Server DNS V2R3 / enhancedV8](https://github.com/niwc-atlantic/scap-content-library/blob/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current/U_MS_Windows_Server_DNS_V2R3_STIG_SCAP_1-4_Benchmark-enhancedV8-signed.zip) | 41 | Yes |

## Appendix B — smaller source-validation groups to review

Full versioned Rule IDs are shown below; the CSV retains the complete XML IDs,
source hashes, messages and original-source links. The IOS XE casting rows are
standards-conflict candidates, not unconditional content-bug findings.

| Finding | Pinned source | Rule IDs |
| --- | --- | --- |
| O03 | MS Windows 10 V3R7 / enhancedV17 | SV-220698r991589, SV-220699r991589 |
| O03 | MS Windows 11 V2R10 / enhancedV18 | SV-253255r1210279, SV-253256r1210280 |
| O03 | MS Windows Server 2016 V2R8 / enhancedV19 | SV-224827r991589, SV-224865r991589 |
| O03 | MS Windows Server 2019 V3R9 / enhancedV19 | SV-205848r991589, SV-205856r991589 |
| O03 | MS Windows Server 2022 V2R10 / enhancedV19 | SV-254246r1210256, SV-254283r991589 |
| O03 | MS Windows Server 2025 V1R1 / enhancedV1 | SV-278031r1182046 |
| O04 | MS DotNet Framework 4-0 V2R8 / enhancedV15 | SV-225229r1188309 |
| O04 | MS Windows 10 V3R7 / enhancedV17 | SV-220723r991589 |
| O04 | MS Windows 11 V2R10 / enhancedV18 | SV-253280r991589 |
| O04 | MS Windows Server 2016 V2R8 / enhancedV19 | SV-224842r991589 |
| O04 | MS Windows Server 2019 V3R9 / enhancedV19 | SV-205852r991589 |
| O04 | MS Windows Server 2022 V2R10 / enhancedV19 | SV-254261r1210262 |
| O04 | MS Windows Server 2025 V1R1 / enhancedV1 | SV-278008r1211146 |
| O05 | MOZ Firefox Windows V6R8 / enhancedV13 | SV-251550r961194 |
| O05 | MS DotNet Framework 4-0 V2R8 / enhancedV15 | SV-225228r1043178, SV-225232r1050651, SV-225233r1117179, SV-225234r1188289, SV-225237r1043178 |
| O05 | Oracle Linux 7 V3R3 / enhancedV16 | SV-221655r958390 |
| O05 | Oracle Linux 8 V2R9 / enhancedV19 | SV-248528r958390 |
| O05 | Oracle Linux 9 V1R4 / enhancedV5 | SV-271689r1091779 |
| O05 | RHEL 8 V2R8 / enhancedV22 | SV-230226r1069298 |
| O05 | RHEL 9 V2R9 / enhancedV13 | SV-270174r1044831 |
| O06 | MS IIS 8-5 Server V2R7 / enhancedV13 | SV-258446r928857 |
| O06 | MS IIS 8-5 Site V2R9 / enhancedV13 | SV-258445r928856 |
| O06 | Oracle Linux 9 V1R4 / enhancedV5 | SV-271451r1137691 |
| O06 | RHEL 9 V2R9 / enhancedV13 | SV-257789r1137691 |
| O07 | MS IIS 8-5 Site V2R9 / enhancedV13 | SV-214451r879567, SV-214452r879568, SV-214463r879643, SV-214495r879587 |
| O10 | Cisco IOS-XE Router NDM V3R5 / enhancedV18 | SV-215807r1186318, SV-215812r1137875, SV-215833r961068, SV-215854r1156415 |
| O11 | Cisco IOS-XE Router NDM V3R5 / enhancedV18 | SV-215833r961068 |
| O12 | Cisco IOS-XE Router NDM V3R5 / enhancedV18 | SV-215833r961068 |

## Appendix C — original primary blocker accounting

This is the disjoint stage-one primary disposition table, not the overlapping
O-number finding inventory. Later validation findings are additive evidence; 
the frozen DRAFT ledger has not been rewritten.

| Primary disposition | Automated Rules |
| --- | ---: |
| Assessment contracts | 1,630 |
| Catalog bindings | 992 |
| Effective deprecated original Tests | 151 |
| Nonstandard sqlext packages | 137 |
| Recorded original validity/deprecation exclusions | 32 |
| Further converter/source investigation | 39 |
| Total blocked automated Rules | 2,981 |

O08 includes 151 primary effective-Test exclusions plus 11 additional distinct
Rules with observed original deprecation diagnostics. O02 shares Rules with
O01. O10 shares SV-215833 with O11/O12. These findings must not be summed.
The 1,653 manual/OCIL-only Rules are preserved content, not automatic defects.
