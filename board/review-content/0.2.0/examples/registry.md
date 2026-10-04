# Windows registry: address matching with one satisfying Item

Compare [selected source](../sources/registry.xml), [Assessment](../content/registry.assessment.yaml),
[provenance](../provenance/registry.json), and [expectations](../expected/registry.json).
Human status: **pending-review**. Provenance: Inherited selected criterion.

Scope: criterion `oval:org.mitre.oval.test:tst:1020` within Definition
`oval:org.mitre.oval.test:def:38`. It selects the `CurrentVersion` value at
`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion`.

Before: Test `tst:1020` → Object `obj:1020` / State `ste:1020`.
After: `test-windows-version-address → windows-version-entry / expected-version-address`. The versioned mapping changes the hive
literal to `local_machine`. It preserves the State's case-insensitive key
comparison as `equal_ci` and the exact name comparison as `equal`.

`check_existence: some` requires an existing Item. `check: one` requires exactly
one Item satisfying the **whole State**; this is not `check_existence: one`.
Those quantifier scopes are deliberately left distinct.

The synthetic single Item has the correct hive and name and a lower-case key;
it satisfies the case-insensitive State, so the result is true. Confirmed absence
is false. Denied registry acquisition is error. Registry selector execution,
registry virtualization/view selection and live permissions are not tested here.
No deprecated windows_view behavior is added to native content.

The source State does **not** compare the registry value's data. This sample
therefore makes no claim about Windows edition, OS version or a security setting.
The file name `CurrentVersion` must not tempt readers to infer an absent value Test.

Mechanical comparison: [converter output](../mechanical/registry.assessment.yaml)
now comes from the maintained lower/align/mapping API path, with a source-ID-keyed
local naming plan. The readable native file only shortens titles and, where
applicable, uses Constant `value` syntax. Executable selectors, State predicates,
quantifiers and criteria are identical between forms. No manual semantic fix is
applied. File/registry mapping calls are explicitly case-scoped; their general
automatic converter readiness remains unchanged.
