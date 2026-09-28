# Three-Format Reuse Example Index

These six examples are generated from **measured exact OVAL semantic reuse** in
the four published anchor benchmarks. Each group contains the same technical
assessment represented in all three candidate YAML forms.

Open the same group in each column when comparing formats; do not compare
different examples across formats.

| Example | Published policy rules | Combined rule + overlays | Split policy / assessment / binding | Ansible-inspired |
| --- | --- | --- | --- | --- |
| Windows Secure Boot | Win11 `SV-253257`; Server 2025 `SV-278032` | [shared base + overlays](../generated/four-anchor-reuse/reuse-views/groups/exact-001-0dc983f8ec70/combined-rule/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-001-0dc983f8ec70/split-policy-assessment-binding/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-001-0dc983f8ec70/ansible-inspired/) |
| Linux hardware RNG service | RHEL9 `SV-257782`; OL9 `SV-271511` | [shared base + overlays](../generated/four-anchor-reuse/reuse-views/groups/exact-002-1abb613998c7/combined-rule/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-002-1abb613998c7/split-policy-assessment-binding/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-002-1abb613998c7/ansible-inspired/) |
| Windows DoW Root CA | Win11 `SV-253427`; Server 2025 `SV-278192` | [shared base + overlays](../generated/four-anchor-reuse/reuse-views/groups/exact-003-250d31ca794b/combined-rule/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-003-250d31ca794b/split-policy-assessment-binding/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-003-250d31ca794b/ansible-inspired/) |
| Windows account lockout duration | Win11 `SV-253297`; Server 2025 `SV-278033` | [shared base + overlays](../generated/four-anchor-reuse/reuse-views/groups/exact-004-469de3fc5eac/combined-rule/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-004-469de3fc5eac/split-policy-assessment-binding/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-004-469de3fc5eac/ansible-inspired/) |
| Linux xattr audit syscalls | RHEL9 `SV-258179`; OL9 `SV-271536` | [shared base + overlays](../generated/four-anchor-reuse/reuse-views/groups/exact-005-a49afca9eefc/combined-rule/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-005-a49afca9eefc/split-policy-assessment-binding/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-005-a49afca9eefc/ansible-inspired/) |
| Linux systemd-journald | RHEL9 `SV-257783`; OL9 `SV-271739` | [shared base + overlays](../generated/four-anchor-reuse/reuse-views/groups/exact-006-da10d697e0f8/combined-rule/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-006-da10d697e0f8/split-policy-assessment-binding/) | [shared assessment + bindings](../generated/four-anchor-reuse/reuse-views/groups/exact-006-da10d697e0f8/ansible-inspired/) |

## Suggested review order

For reviewers unfamiliar with Linux, start with **Windows Secure Boot**, then
**account lockout duration**, then the larger **DoW Root CA** example.

For Linux, start with **hardware RNG service** or **systemd-journald**. The
**xattr audit syscall** group is deliberately the stress case: its migrated
assessment contains 24 tests and 17 variables and preserves the known source
anomaly rather than silently repairing it.

## What to compare

For each group, inspect:

- how easily the independent policy identities remain visible;
- how clearly the shared technical assessment is identified;
- whether every affected policy can be discovered from the source;
- how much source navigation is required;
- whether an assessment change has an obvious impact set;
- whether policy-specific values can be specialized without mutating shared
  technical semantics;
- whether provenance and version ownership are understandable;
- whether the source structure would remain usable at the measured corpus
  fan-out of 6, 12, or 13 benchmarks.

The canonical semantic fingerprint is the control: the three views are intended
to differ in authoring organization, not technical behavior.
