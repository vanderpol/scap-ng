# Windows NTUSER collection — scanner implementation reference

**Status:** retained implementation guidance, not SCAP-NG authoring schema.
**Source:** [OVAL 5.12.3 Windows system characteristics XSD, `ntuser_item`](https://github.com/OVAL-Community/OVAL/blob/v5.12.3/oval-schemas/windows-system-characteristics-schema.xsd).
**Pinned source:** `OVAL-Community/OVAL` tag `v5.12.3`, Git blob SHA `8fc2fd4dbfc52f0b00666f7637a5e9fac34c5d4d`.
**Preservation policy:** keep this guide and pinned upstream link with the capability. Do not delete it during schema generation, and do not replace the upstream documentation with a paraphrase when resolving implementation ambiguity.

## OVAL implementation notes to retain

OVAL's `ntuser_item` documents recommended—not mandated—collection methods:

1. Locate candidate user profiles using Windows ProfileList and the corresponding ProfileImagePath. Its notes include SID-based filters for identifying human profiles and excluding service accounts. Check actual scope and applicability rather than mechanically relying on sample SID patterns.
2. For users with a loaded profile, obtain per-user registry content through the user's hive under HKEY_USERS, as appropriate.
3. For users without a loaded profile, inspect their `NTUSER.DAT` safely. Avoid opening the live original in a way that locks the file and prevents the user from logging in. Use suitable operating-system APIs, safe access methods, or temporary snapshots as appropriate.
4. Report the observed key, value name, user SID, username, account type, logged-on status, and other supported Item fields with correct optional, absent, and error semantics.

The XSD includes detailed annotations about the above procedures and per-field interpretations. **This document is an index/summary, not a substitute for those annotations.** Consult the pinned `ntuser_item` XSD during scanner implementation, and retain an archival, checksum-verified copy in the implementation test environment for offline builds.

## Collection semantics versus mechanisms

- **Normative capability behavior:** which users/registry values are in scope, Item identity, field types and statuses, and how unavailable or partial evidence is represented.
- **Implementation choices:** Windows APIs, offline hive parsing, privilege handling, caching, snapshots, safe filesystem access, and efficiency.

Alternative collection mechanisms are allowed when equivalent. Scanner developers must not weaken the required collection population because an implementation recipe is difficult to follow.

## Minimum scanner conformance cases

Test loaded and unloaded profiles; local and domain user accounts; service accounts; profiles with missing or inaccessible `NTUSER.DAT`; access-denied and partial collections; absent versus nil registry value names; profile unload or load transitions; and multiple profiles with identically named registry keys. Verify errors are not silently reported as absent or passing evidence.

## Follow-up gate

Before implementing or promoting `windows.ntuser`, compare this checklist against all `ntuser_item` annotations and the corresponding OVAL definitions Object/State documentation, and capture the source XSD version/hash in executable tests. This retained guide must be reviewed with any future OVAL version update.
