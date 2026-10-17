# Item creation choices inside the 201 Test-level all_exist cases

**Research only; no collector or authoring schema changed.**

The historical six-STIG Test existence choice and collection Item creation behavior are separate.

## Observed capability/behavior combinations

| Capability | Item creation behavior | Count |
| --- | --- | ---: |
| `independent.textfilecontent54` | `all_object_elements_fullfilled` | 132 |
| `linux.partition` | `<not specified>` | 6 |
| `linux.rpminfo` | `<not specified>` | 7 |
| `unix.file` | `<not specified>` | 6 |
| `unix.password` | `<not specified>` | 2 |
| `unix.shadow` | `<not specified>` | 1 |
| `unix.symlink` | `<not specified>` | 1 |
| `unix.sysctl` | `<not specified>` | 26 |
| `variable.value` | `<not specified>` | 1 |
| `windows.ntuser` | `key_and_name_exist` | 3 |
| `windows.registry` | `<not specified>` | 6 |
| `windows.wmi.query` | `<not specified>` | 10 |

## Windows NTUSER source Tests

- `authoring/ms_windows_11/assessments/automated/SV-253293.automated.yaml` — The system must notify the user when a Bluetooth device attempts to connect. — Item creation `key_and_name_exist`
- `authoring/ms_windows_11/assessments/automated/SV-253425.automated.yaml` — 'Do not suggest third-party content in Windows spotlight' is set to 'Enabled' — Item creation `key_and_name_exist`
- `authoring/ms_windows_11/assessments/automated/SV-253477.automated.yaml` — 'Turn off toast notifications on the lock screen' is set to 'Enabled' — Item creation `key_and_name_exist`

## Interpretation

- `windows.ntuser`: creating an Item for an existing `ntuser.dat` even if its requested value is missing is conceptually sound, but it changes what Items are selected compared with key/name-only creation.
- `independent.textfilecontent54`: `filepath_exists` and `all_object_elements_fullfilled` select different Item populations.
- Under the proposed native rule, missing fields on a real resource are recorded as absent fields, rather than adding phantom missing Items.
- Changing the Item creation choice during migration must be evaluated for both source Test results and the evidence it emits. An exact YAML roundtrip does not establish this.

## Limits

- OVAL source behavior is not necessarily native Item identity policy.
- Many capabilities do not expose a named item_creation setting.
- A collection option that preserves existing file Items can change the tested Item population; it is not a safe blind rewrite of all_object_elements_fullfilled.
- The number of returned Items is different from the number of explicitly enumerated expected resource identities.
- Each absent/error/not_collected source outcome still requires six-state preservation.
