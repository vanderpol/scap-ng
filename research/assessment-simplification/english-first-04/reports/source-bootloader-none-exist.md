# Bootloader none_exist + State: original OVAL investigation

**Research only.** Pinned original NIWC-enhanced SCAP 1.4 ZIPs. No source or normative 0.4 change.

## Counts

- Original bootloader candidate Tests: **4**
- Original OVAL Tests with explicit `none_exist` + State: **2**
- Bootloader candidates using that combination: **2**

## Original source candidates

### `oval:mil.disa.stig.ind:tst:25778700` (rhel_9)

- Original author namespace: `DISA`
- Test existence: `all_exist`; match: `all`
- Comment: /etc/grub2.cfg:superusers exists and has a name.
- Referenced Objects: `oval:mil.disa.stig.ind:obj:25778700`
- Referenced States: `oval:mil.disa.stig.ind:ste:25778700`
- Located via: object selector

### `oval:navy.navwar.niwcatlantic.scc.rhel9os:tst:25778901` (rhel_9)

- Original author namespace: `NIWC/NAVWAR`
- Test existence: `none_exist`; match: `all`
- Comment: Verify the boot loader password is not set to root, admin, or adminstrator.
- Referenced Objects: `oval:navy.navwar.niwcatlantic.scc.rhel9os:obj:25778901`
- Referenced States: `oval:navy.navwar.niwcatlantic.scc.rhel9os:ste:25778901`
- Located via: object selector

### `oval:mil.disa.stig.ind:tst:25778700` (oracle_linux_9)

- Original author namespace: `DISA`
- Test existence: `all_exist`; match: `all`
- Comment: /etc/grub2.cfg:superusers exists and has a name.
- Referenced Objects: `oval:mil.disa.stig.ind:obj:25778700`
- Referenced States: `oval:mil.disa.stig.ind:ste:25778700`
- Located via: object selector

### `oval:navy.navwar.niwcatlantic.scc.rhel9os:tst:27145101` (oracle_linux_9)

- Original author namespace: `NIWC/NAVWAR`
- Test existence: `none_exist`; match: `all`
- Comment: Verify the boot loader password is not set to root, admin, or adminstrator.
- Referenced Objects: `oval:navy.navwar.niwcatlantic.scc.rhel9os:obj:27145101`
- Referenced States: `oval:navy.navwar.niwcatlantic.scc.rhel9os:ste:27145101`
- Located via: object selector


## Required disposition

Compare the original Test/State references to the single native 0.4
`verify-boot-loader-root-admin-adminstrator` Assessment and test both
complete zero Items and incomplete/error outcomes. Do not silently erase
a State, turn `none_exist` into `none match`, or claim 100% conversion.

## Limitations

- The original OVAL XML is direct evidence about original Test/State shape.
- A source-to-native identity join is still needed to prove which original Test maps to the exact native ID.
- Other original Test instances may be omitted from the curated native authoring set.
- If original source includes none_exist plus a State, the source itself uses a form prohibited by OVAL 5.12.3 Schematron; migration must error or explicitly resolve with a reviewed equivalence proof.
- If original source omits a State but native has one, inspect the converter for accidental State attachment.
