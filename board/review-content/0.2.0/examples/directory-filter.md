# Directory selection and an exclusion filter

Status: **pending-review**. [Native Assessment](../content/directory-filter.assessment.yaml),
[mechanical conversion](../mechanical/directory-filter.assessment.yaml),
[original selected closure](../sources/filter.xml), [provenance](../provenance/directory-filter.json),
[independent synthetic cases](../expected/directory-filter.json).

Pinned Self-Assertion `unix/oval-def_set-unix.xml`, Definition
`oval:org.mitre.oval.test:def:276`, selected criterion `tst:451`. This is a
criterion fragment, not the complete source Definition. Exact IDs, versions,
comments and schema families remain in provenance and the extract.

The executable Object selects the directory `/opt/support/txt` with a nil
filename, `recurse_direction="none"`, and local filesystems. It does **not** scan
its descendants. The source comments mention Windows paths and a three-member
set; those comments contradict this UNIX selector. Conversion preserves the
selector, values and behavior rather than silently correcting the content.

| OVAL construct | Native representation / effect |
| --- | --- |
| `obj:189`, literal path and nil filename | `support-directory-object`, `directory` plus `name: null` |
| `var:134`, two constant paths | `excluded-directories-variable`, two string values |
| `ste:746`, path Variable and `var_check="only one"` | `excluded-directory-state`, `variable_match: one` |
| `obj:373`, one referenced Object and EXCLUDE filter | `filtered-support-directory-object`, UNION operand with filter |
| `ste:196` | `support-directory-state`, directory equals `/opt/support/txt` |
| `tst:451`, `only_one_exists`, `all` | `test-filtered-support-directory`, existence `one`, check `all` |

For the unchanged source, a complete selected directory Item survives exclusion:
its path equals **neither** Variable value. The filtered population contains one
Item, which matches the final State, producing `true`. Confirmed absence is
`false`; a collection failure is `error`; no collection is `unknown`.

Two explicitly native edge variants change the publisher Constant in the
fixture, not through Organizational Input. Listing the directory once excludes
it and yields `false`. Listing it twice makes **exactly one** equality false;
the Item survives and the result is `true`. These distinguish `one` from `any`
and `all`. They do not claim that the unchanged upstream source removes an Item.

Mechanical and native files execute the same graph. Native refinement replaces
inaccurate explanatory titles and uses the supported Constant `value` form
instead of `expression.literal`. Source comments stay in provenance. The bounded
helper combines preselected synthetic Items and filters; it does not acquire
directories or demonstrate live scanner traversal. Scanner-native filesystem
selection remains responsible for local filesystem exclusions and efficiencies.

The earlier [owner/Variable-chain filter seed](filter.md) remains a separate
native supporting example. It is not a conversion of this source criterion.
