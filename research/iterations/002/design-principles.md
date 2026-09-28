# Iteration 002 Design Principles

## OVAL-aligned capability naming

The default SCAP-NG capability name is:

    <oval-family>.<oval-test-basename>

Examples:

| OVAL namespace | OVAL test | NG capability |
| --- | --- | --- |
| unix | file_test | unix.file |
| windows | registry_test | windows.registry |
| linux | rpminfo_test | linux.rpminfo |
| solaris | package_test | solaris.package |
| macos | plist511_test | macos.plist511 |
| independent | textfilecontent54_test | independent.textfilecontent54 |

The suffix `_test` is removed because NG capabilities are not modeled as
OVAL XML tests.

### Versioned test names

Do not automatically remove numeric/version suffixes such as `53`, `54`,
`55`, or `511`.

If two OVAL test generations have materially different data models or
semantics, the NG capability name keeps the distinguishing suffix until a
reviewed NG-native unification proves lossless.

### Deprecated tests

An OVAL name does not become an NG capability merely because it existed.

Effectively deprecated tests remain migration blockers unless later OVAL
governance explicitly reinstated them. When a supported replacement exists,
native NG uses the supported family/test vocabulary.

## Why preserve OVAL family namespaces

OVAL's family boundaries encode real collection differences.

Examples include:

- Unix file ownership/mode/type semantics versus Windows SID/ACL/security
  semantics;
- Linux RPM package information versus Debian package information;
- Windows Registry and WMI, which have no Unix equivalent;
- Solaris-specific package/system concepts;
- macOS property-list and authorization concepts.

SCAP-NG should benefit from that accumulated experience rather than flattening
all platforms into generic collectors and then rebuilding platform-specific
fields inside them.

## What NG is free to simplify

Reusing OVAL capability names does **not** require retaining:

- OVAL XML;
- definition/test/object/state element layering;
- opaque OVAL IDs;
- XML namespace URIs;
- OVAL variable/component syntax when a clearer NG transform is equivalent;
- XCCDF check-content references.

The capability vocabulary and data semantics can remain familiar while the
authoring language becomes substantially smaller.

## Applicability

Applicability is an ordinary NG assessment used in an applicability role.

Therefore the same OVAL-aligned capability vocabulary applies equally to:

- compliance checks;
- inventory/platform checks;
- feature/package applicability;
- role-based applicability;
- configuration-based applicability.

A scanner implements capabilities such as `unix.file` or
`windows.registry`. It does not need special knowledge that a particular
combination means "Linux Mint", "Windows 11 workstation", or another platform.

## Design review rule

When defining a native NG capability:

1. Find the corresponding supported OVAL family/test when one exists.
2. Start with that family/test basename as the NG name.
3. Reuse the mature OVAL data-model lessons.
4. Simplify the author-facing syntax.
5. Change or merge the capability only when there is concrete evidence that
   the NG model remains semantically complete and portable.
