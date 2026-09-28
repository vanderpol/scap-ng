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

### Historical numeric/version suffixes — OVAL Board decision

Names such as `fileeffectiverights53`, `textfilecontent54`,
`user_sid55`, and `plist511` often encode the OVAL release in which a
replacement or semantic correction was introduced.

SCAP-NG should not prejudge whether those historical suffixes remain part of
the native capability name.

For iteration 002:

- preserve the source-derived supported test basename when demonstrating or
  up-converting content so no semantic distinction is accidentally hidden;
- do not treat that spelling as final NG syntax;
- document whether the suffixed and unsuffixed generations have materially
  different data/result semantics;
- present the naming choice to the OVAL Board.

The Board may choose, for example, to retain `macos.plist511` for explicit
lineage, or establish a new NG baseline such as `macos.plist` if only the
corrected semantics are admitted into NG.

The same decision applies consistently across historical numeric suffixes.

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

## Platform, applicability, and compliance

All three use the same NG assessment language, but they have different
authoring roles.

- **Platform** identifies the product/OS target of a benchmark, such as
  `windows.11`, `windows.server-2025`, `rhel.9`, or `oracle-linux.9`.
- **Applicability condition** is an additional reusable fact about a target,
  such as `windows.member-workstation`, `windows.domain-controller`,
  `linux.gnome-installed`, or `linux.fips-enabled`.
- **Compliance assessment** determines whether the actual security requirement
  is satisfied.

A benchmark supplies the platform. Rules inherit it and add only the extra
applicability conditions they need.

A scanner implements capabilities such as `unix.file`, `windows.registry`,
or `windows.wmi`. Content authors combine those capabilities to establish
platform identity and reusable applicability conditions.

## Design review rule

When defining a native NG capability:

1. Find the corresponding supported OVAL family/test when one exists.
2. Start with that family/test basename as the NG name.
3. Reuse the mature OVAL data-model lessons.
4. Simplify the author-facing syntax.
5. Change or merge the capability only when there is concrete evidence that
   the NG model remains semantically complete and portable.
