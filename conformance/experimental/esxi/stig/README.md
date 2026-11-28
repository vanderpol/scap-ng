# DISA ESXi 8.0 V2R5 and experimental OVAL 6.0

The source is the ESXi manual XCCDF member in the DISA October 2026 vSphere
bundle. [Source pins](source.json) bind the archive and exact member bytes.
The [crosswalk](coverage.json) accounts for all 76 manual checks, including
48 with candidate projections into 12 OVAL 6.0 Test families and 28 held
with recorded reasons. Every family retains its experimental or proposed
adoption status.

The Host Acceptance Level check reads a host-wide value. That field is
available in the proposed host acceptance family, while the experimental
VIB family carries individual package metadata. The unlock-time check
gives conflicting directions at 900 seconds in its procedure and finding
condition. Its expected outcome remains held.

The experimental [Assessment](release-checks.assessment.yaml) and
[independent expectations](expected.json) cover account lock threshold,
password history and shell access for the dcui account. Typed complete
populations exercise exact equality, inclusive boundaries, empty
populations and observed false cases. Source-wide Rule decisions,
transition to automatic checks, and VMware collection remain unqualified.
The [current RI admission receipt](ri-hold.json) records
`object_capability_unsupported` for all three Tests.

```sh
python conformance/tools/audit_esxi_stig.py --check \
  --archive /path/to/U_VMW_vSphere_8-0_Y26M10_STIG.zip
```

- [DISA October 2026 archive](https://dl.dod.cyber.mil/wp-content/uploads/stigs/zip/U_VMW_vSphere_8-0_Y26M10_STIG.zip)
- [Canonical OVAL 6.0 ESXi scope](https://github.com/vanderpol/scap-ng/issues/86)
- [RI ESXi implementation tracking](https://github.com/vanderpol/scap-ng-ri/issues/202)
