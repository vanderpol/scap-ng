# Current SCAP-NG 0.3 owner review

**Status:** active pre-alpha showcase for the project owner and OVAL Board visitors. There is **no formal 0.3 Board vote or certification** implied by this page.

## Start with one real download

[**Download the six-STIG native authoring ZIP**](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-typed-operators-5796d016b12f/scap-ng-0.3-six-stig-authoring.zip) · [GitHub Release including all six compiled `.scapng` bundles](https://github.com/vanderpol/scap-ng/releases/tag/v0.3.0-six-stig-typed-operators-5796d016b12f) · [SHA-256 manifest](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-typed-operators-5796d016b12f/SHA256SUMS.txt).

The authoring archive contains exactly **one normalized set** of RHEL 9,
Oracle Linux 9, Windows 11, Windows Server 2025, Windows Server DNS and
Apache 2.4 UNIX content, with reusable Assessments under
`authoring/shared/assessments/`. No faithful/candidate clones, per-STIG
authoring ZIPs, conversion evidence sidecars, or Actions-only expiring links.

**New 0.3 authoring direction:** Compared with SCAP 1.4, redundant comparison
datatypes disappear where typed YAML values are sufficient. Rare comparison
algorithms use explicit operators such as `version_greater_than_or_equal`.
**4,532 / 5,267** source datatype declarations (86%) are eliminated in this
conservative projection, with 735 still explicit for uncertain and dynamic
cases. Six independently rebuilt scanner bundles from the old and revised
authoring trees passed **byte-for-byte SHA-256 equivalence** in the
[issue #200 release gate](https://github.com/vanderpol/scap-ng/issues/200).

## What to review

Follow the [short review guide](REVIEW-GUIDE.md) or start with the
[embedded Assessment examples](../../specification/examples/assessments.md).
The [A/B/C/D vocabulary discussion](https://github.com/vanderpol/scap-ng/discussions/213)
remains informal and nonbinding; no Board votes are assumed.

Compilation parity is not independently proven scanner runtime parity.
OVAL 5.12.3 Self-Assertion and special-float conversion gap
[#218](https://github.com/vanderpol/scap-ng/issues/218) remain open.
