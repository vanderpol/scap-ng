# Pinned OVAL documentation quality

This review distinguishes **Missing explanation**, **Unclear explanation**, and **Incorrect or inconsistent explanation**. The first category follows the owner wording; the other two are working categories for this batch. Scope is the pinned XSD annotations, including their field/type relationships, not a claim that all OVAL publications omit a topic.

Each finding has a full source quotation, exact XPath, file digest and immutable commit in the [audit ledger](oval-documentation-quality.json). Recommendations are proposals, not new native requirements.

| Finding / category | Specific source limitation | Proposed SCAP-NG improvement |
| --- | --- | --- |
| `registry-overview` — Missing explanation | The Object overview annotation is empty; useful nil/default-value guidance exists only on child fields. | Add a short native overview and link child selector cases; keep null, empty name and registry-view contracts separate. |
| `service-evidence` — Missing explanation | "Specifies when the service should be started" gives purpose but no local collected-value comparison example. | Show SERVICE_DISABLED versus SERVICE_AUTO_START with explicit Items; distinguish startup configuration from current_state. |
| `rpm-evidence` — Missing explanation | The overview lists fields and refers readers elsewhere; it has no local authoring/evidence/outcome example. | Start with a typed architecture comparison; link version/epoch/EVR details separately instead of implying generic version ordering. |
| `file-behavior-order` — Unclear explanation | The "double negative" warning does not demonstrate which entries are added back or how behavior and selector scopes compose. | Give a bounded worked collection example and explicit selector/traversal/filter boundaries after the native contract is approved. |
| `file-acl-meaning` — Unclear explanation | The prose alternates between having an ACL and having an ACL matching standard permissions; the name alone does not explain the distinction. | Define the extended-ACL flag with a small decision table; distinguish recorded ACL metadata from effective access. |
| `shell-empty-output` — Unclear explanation | Item prose says to create an Item with does-not-exist status, while Object prose places does-not-exist on stdout; the status owner needs clarification. | Specify collection, Item and field statuses independently with an empty-stdout fixture after owner review. |
| `firmware-copy-error` — Incorrect or inconsistent explanation | The firmware-password Test overview describes File Vault disk encryption. | Use firmware-password subject matter derived from matching fields/Item documentation; retain the source error in provenance. |
| `sestatus-copy-error` — Incorrect or inconsistent explanation | The SELinux status Test overview describes counts of profiles and processes, mirroring AppArmor subject matter. | Describe SELinux configuration/status fields; do not transfer the incorrect purpose statement. |
| `registry-rights-copy-error` — Incorrect or inconsistent explanation | The registry-key rights overview says it checks Windows files. | Name registry keys and trustees explicitly; keep access-mask/view questions separate. |

The source is often useful and concrete: UNIX file access-time documentation specifies seconds since 1970-01-01 UTC, RPM epoch documentation includes actual formatted `rpm` queries, and shellcommand preserves important safety warnings. Retain those strengths. Better navigation, typed evidence examples and explicit contract status improve usability without silently adopting legacy runtime behavior.
