# Windows all_exist: read-only owner decision packet

2026-10-25; [authorization](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6396984623).
No new normalization, conversion admission, package generation or coverage
promotion. The two cases remain unverified. Existing RHEL pins and Oracle
SV-271844 are unchanged. This is source/conversion evidence, not scanner acceptance.

The complete Test attributes, Object/State trees, XCCDF/catalog/Definition
closure, original ZIP/XML hashes and existing-helper diagnostic matrix are in
[windows-all-exist-decisions.json](v04-object-processing/windows-all-exist-decisions.json).
The original XML remains in the unchanged pinned fixtures windows-01.json and
windows-15.json under tests/fixtures/v04-proof-expansion. The analysis also
verified their closures against the complete original SCAP ZIPs.

## Windows 11 SV-253259

Original Rule `xccdf_mil.disa.stig_rule_SV-253259r1210282_rule`, Definition
`oval:mil.disa.stig.windows11:def:253259`, Test
`oval:mil.disa.stig.win:tst:25325900` version 1:
`check_existence="all_exist"`, `check="all"`, no explicit state_operator.
Object `oval:mil.disa.stig.win:obj:25325900` version 1 uses namespace
`root\\cimv2\\security\\microsoftvolumeencryption` and WQL:

```sql
SELECT protectionstatus FROM win32_encryptablevolume
```

State `oval:mil.disa.stig.win:ste:25325900` version 1 compares a record result
field `protectionstatus` with string `1`. Preserve its original attributes and
defaults; do not reinterpret it as an integer comparison.

The population consists of provider-defined query rows, not a literal list of
expected drive identities. The policy comment says all fixed drives, but the
query has **no WHERE clause or fixed-drive filter**. The original source alone
does not establish that these rows exhaust every intended fixed drive. Do not
invent a filter, synthetic missing-drive Item or new obligation. Empty results
fail both existence checks; multiple returned rows must each satisfy the State.
An omitted expected drive cannot be inferred from the actual rows alone.

Owner decision needed: whether to approve a source-pinned, complete-collection,
actual-row interpretation with this explicit policy-coverage limitation, or
require separately reviewed expected-drive obligations. Recommendation: keep
blocked pending that population decision and the incomplete-result review below.

## Windows Server 2025 SV-278208

Original Rule `xccdf_mil.disa.stig_rule_SV-278208r1181330_rule`, Definition
`oval:mil.disa.stig.windows2025:def:278208`. Two separate version-1 Tests, each
`check_existence="all_exist"`, `check="all"`, no explicit state_operator:

| Test | State | Original value pattern |
| --- | --- | --- |
| `oval:mil.disa.stig.win:tst:25344600` | `oval:mil.disa.stig.win:ste:25344600` | `^D(oD\|OD) N(otice\|OTICE) (and\|AND) C(onsent\|ONSENT) B(anner\|ANNER)$` |
| `oval:mil.disa.stig.win:tst:25344601` | `oval:mil.disa.stig.win:ste:25344601` | `^U\.?S\.? D(EPARTMENT\|epartment) (OF\|Of\|of) D(EFENSE\|efense) W(ARNING\|arning) S(TATEMENT\|tatement)$` |

Both States also require source registry type `reg_sz`. Both Tests reference
the same version-1 Object `oval:mil.disa.stig.win:obj:25344600`:
`HKEY_LOCAL_MACHINE`, key
`SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System`, name
`LegalNoticeCaption`. Original string attributes/defaults are preserved in the
machine packet. There are no source Variables, Sets, behaviors or explicit view
selection on this Object. Do not invent a registry-view override.

These are alternative caption checks combined by the original Definition's OR;
they are **not two expected registry Items**. The literal identity makes missing
value evidence more constrained than the WMI population. One complete present
Item can pass the appropriate alternative; a missing value/empty population
fails both. Multiple Items for this fixed identity would require an explicit
identity/view/deduplication explanation, not an unreviewed assumption. A mixed
exists+DNE population is outside a proposed single-identity/no-synthetic-DNE
profile, but remains an unrestricted OVAL counterexample.

Owner decision needed: whether to approve these two exact Tests under a
source-pinned complete single-identity actual-Item contract. Recommendation:
review separately from WMI and resolve incomplete-result handling first. No
admission is implemented here.

## Result evidence and newly exposed reference discrepancy

For each Test separately the tool exercises 2,064 existing-helper algebraic
inputs: six result states, zero/one/two existing Items, mixed DNE/error/not-collected
counts and six collection flags. Not every cross-product is admissible System
Characteristics evidence: for example a complete-success profile cannot contain
error/not-collected Items. The matrix is a diagnostic, not a new evaluator.
There are 317 helper-output differences per Test; this is **not** a count of
317 admissible semantic counterexamples.

All 43 complete/no-DNE/no-error/no-not-collected rows agree. More generally, on
a complete actual-Items-only population, both existence checks mean at least
one Item and both apply the identical `check="all"` State aggregation. This
conditional statement does not establish collector completeness or unrestricted
OVAL equivalence.

| Evidence | Existing helper all_exist | Existing helper at_least_one_exists | Interpretation |
| --- | --- | --- | --- |
| Complete, empty | false | false | No vacuous success |
| Complete, one exists, State true | true | true | Conditional passing case |
| Complete, two exist, States true/false | false | false | Preserve every-Item comparison |
| Complete, one exists + one DNE, existing State true | false | true | Retained unrestricted existence counterexample; outside actual-Items profile |
| Collection error | error | error | Do not discard collection diagnostics |
| Collection not collected | unknown | unknown | Do not claim successful collection |
| Incomplete, one exists, State false | unknown | false | **Reference discrepancy requiring review**, below |

The pinned OVAL 5.12.3 `oval-results-schema.xsd`, TestType documentation,
incomplete-collection exception 3a says: **“If the check attribute evaluation
results in "false", then the OVAL Test result must be "false"”.**
Minimal original-source-backed counterexample: either source Test above,
incomplete collection, one existing Item, no DNE/error/not-collected Items,
State result false, `check="all"`. Existence aggregation on the observed Item
is true; clause 3a appears to require false. The existing repository helper
instead unconditionally returns unknown for incomplete `all_exist` before
checking that false comparison. This is a helper/source-text discrepancy, not
evidence that OVAL itself requires unknown in this case. The new diagnostic
test records both values and checks the exact pinned source quotation.

**Stop condition:** owner review is needed before correcting that established
reference behavior or using incomplete evidence to admit either new source.
No production helper, approved RHEL normalization, result schema or runtime
semantics were changed. A complete-only proof cannot justify silently treating
partial/error evidence as complete. Any later normalization must preserve all
six comparison results and collection error/unknown handling explicitly.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/test_v04_windows_all_exist_decisions.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/audit_v04_windows_all_exist_decisions.py \
  --inputs-dir /workspace/.onboarding/package-acceptance/inputs \
  --output /tmp/windows-all-exist-decisions.json
```

Omit `--inputs-dir` only for fixture-only reproduction; the output explicitly
records whether original ZIP verification ran. No converter is invoked. The
five tests preserve both current unsupported proof outcomes and the negative
counterexamples. No scanner-runtime equivalence is claimed.
