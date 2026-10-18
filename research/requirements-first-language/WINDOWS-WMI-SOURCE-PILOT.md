# B source-compatible Windows WMI query pilot (issue #237)

**Research-only, fixture-executable support — not original SCAP 1.4 parity and not a native Windows scanner.**

The published converted SCAP-NG 0.3 source case [Windows 11 SV-253265](contract-candidate/corpus/source-specimens/windows-wmi-query-0-a5018a53e0f6.source.yaml) checks that a WMI query for fixed disks with non-NTFS filesystems returns **no Items**. B now has a bounded compiler-owned representation for state-free `windows.wmi.query` Tests, retaining the original WQL and namespace verbatim.

The [source lowerer](../../tools/research_b_source_wmi_lowering.py) accepts only a single direct automated Test with source `existence: none` or `one_or_more`, source `match: all`, no States, no Variables, no Shared Objects, and a bounded read-only SELECT query. Unsupported forms are rejected, not approximated. This is an **internal compiler IR**, not a second authored language.

The [snapshot adapter](../../tools/research_b_wmi_query_snapshot.py) accepts externally obtained WMI query snapshots with explicit acquisition identity, collection status and raw rows. It **does not execute WMI** or assert that a query was evaluated correctly on Windows; snapshot correctness is an external acquisition obligation. Its stable row indices are sufficient for *count-only fixture checks* but are not a proof of OVAL WMI Item identity semantics.

The [B evaluator](../../tools/research_native_contract_evaluator.py) applies pinned generic OVAL Test truth tables after validating the query identity and Item shape. For the pinned `none_exist` Test:

| Evidence | Research Test result |
| --- | --- |
| Complete collection, no result rows | true |
| Complete collection, one or more non-NTFS rows | false |
| Incomplete collection, zero rows | unknown |
| Incomplete collection, at least one row | false |
| Collection error | error |
| Not collected | unknown |
| Not applicable | not applicable |
| Wrong namespace/query or duplicate Item identity | error |

The [regressions](../../tools/test_research_b_source_wmi.py) exercise these cases, source identity, unsupported State processing and invalid queries. CI publishes its observed status alongside the existing State/Boolean source tests in [source-runtime-ci.md](contract-candidate/corpus/source-runtime-ci.md).

**Still missing**: an independently tested real Windows WMI/CIM collector, complete WQL namespace/membership semantics, source Original OVAL WMI object and item flags, Windows permission/access-denied behavior, source SCAP 1.4 XML import/differential proof, vendor scanner conformance, and complete compiled six-STIG bundles. All converted source Tests remain classified *source parity unverified*. In particular, no absent-row result can be trusted unless the collector truly ran the original query to completion.

Track [#237](https://github.com/vanderpol/scap-ng/issues/237) for B engineering; defer any A lessons to [#236](https://github.com/vanderpol/scap-ng/issues/236).
