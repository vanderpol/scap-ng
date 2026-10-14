# 0.3 quick review — real STIG authoring in ten minutes

**Audience:** project owner and OVAL Board visitors. These are pre-alpha examples, not a request to ratify 0.3 or a claim of scanner runtime conformance.

**Download:** [one six-STIG native authoring ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-typed-operators-5796d016b12f/scap-ng-0.3-six-stig-authoring.zip) · [release with six compiled scanner bundles](https://github.com/vanderpol/scap-ng/releases/tag/v0.3.0-six-stig-typed-operators-5796d016b12f).

Open the ZIP; all native source paths begin with `authoring/`.

| Time | Review | Real file in the ZIP |
| --- | --- | --- |
| 2 min | **Rule → Assessment selection** by logical ID; automated or manual default, no redundant `default` entry | `authoring/rhel_9/rules/SV-257851.rule.yaml` |
| 2 min | **Simplified comparison**: rare OVAL version type represented by `version_greater_than_or_equal` instead of separate `datatype` | `authoring/apache_server_2-4_unix_server/assessments/automated/SV-214273.automated.yaml` |
| 2 min | **Local acquisition, variables, checks and decision logic** in a complete Assessment | Same Apache Assessment, then any Windows or Linux automated Assessment |
| 2 min | **Reusable shared acquisition/Assessment** stored separately without relative-path authoring links | `authoring/shared/assessments/linux/accounts/interactive-users-dir-assigned-in.assessment.yaml` |
| 2 min | **Scanner-facing package**: open one `.scapng` archive from the same GitHub Release and inspect its manifest and canonical typed Assessment JSON | Six `.scapng` release assets |

The old and new source forms **compiled into byte-for-byte identical six-STIG
bundles** in the publication gate; see [#200](https://github.com/vanderpol/scap-ng/issues/200).
In the authoring ZIP 4,532 of 5,267 originally authored datatype declarations
are omitted; 735 are retained in noninferable cases. This metric counts
occurrences rather than unique STIG Rules.

## Important limits

The full supported SCAP 1.4/OVAL 5.12.3 **lossless forward-conversion**
requirement is unchanged. Compilation identity only demonstrates that removing
redundant syntax did not change the current canonical scanner packages; it
does not establish independent OVAL runtime comparator conformance, target
data collection, or Board approval. The specialized nonfinite-float gap is
tracked in [#218](https://github.com/vanderpol/scap-ng/issues/218).

For richer examples, see the [short Assessment showcase](../../specification/examples/assessments.md),
[0.3 schema](../../schema/v0.3.0/README.md) and the
[informal vocabulary discussion](https://github.com/vanderpol/scap-ng/discussions/213).
