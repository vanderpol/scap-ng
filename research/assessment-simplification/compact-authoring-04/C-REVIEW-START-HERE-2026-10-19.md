# SCAP-NG 0.4-C — first source-converted Assessments to review

**19 October 2026 · [Research #245](https://github.com/vanderpol/scap-ng/issues/245) · Experimental human authoring, not an accepted specification or scanner-conformant result.**

**Start with [macOS plist511](./oval-self-assertion-c-review/macos-plist511.research.yaml)**, then [PAN-OS config](./oval-self-assertion-c-review/panos-config.research.yaml). Compare each with its pinned original OVAL XML. They are **actual source-derived C `from`/`must` files, compiled by the C research compiler and structurally compared with the source-compatible A Test**; not speculative sketches.

### Review these actual original-source conversions

| Converted C file | Pinned original OVAL 5.12.3 XML | What to look for |
| --- | --- | --- |
| [macOS plist XPath with a Boolean value](./oval-self-assertion-c-review/macos-plist511.research.yaml) | [Original OVAL](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/macos/macos-def_plist511_test.xml) | **Best first review:** a substantive selector and a typed Boolean field check |
| [PAN-OS XPath and hostname match](./oval-self-assertion-c-review/panos-config.research.yaml) | [Original OVAL](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/panos/panos-def_config_test.xml) | Tests a real collected string condition |
| [AIX package/fileset selection](./oval-self-assertion-c-review/aix-fileset.research.yaml) | [Original OVAL](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/aix/aix-def_fileset_test.xml) | Shows duplicate selector-versus-requirement text worth questioning |
| [Juniper CLI output presence](./oval-self-assertion-c-review/junos-show.research.yaml) | [Original OVAL](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/junos/junos-def_show_test.xml) | Simple observation existence |
| [Cisco ASA CLI line existence](./oval-self-assertion-c-review/asa-line.research.yaml) | [Original OVAL](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/asa/asa-def_line_test.xml) | Simple command selector |
| [macOS install history presence](./oval-self-assertion-c-review/macos-installhistory.research.yaml) | [Original OVAL](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/macos/macos-def_installhistory_test.xml) | Simple existence, intentionally broad selector |
| [macOS disk information presence](./oval-self-assertion-c-review/macos-diskinfo.research.yaml) | [Original OVAL](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/macos/macos-def_diskinfo_test.xml) | Simple existence, intentionally broad selector |

All seven originated in the pinned [OVAL Community Self-Assertion@e3538595c5083b9c34d937a81d319234df9bbfaa](https://github.com/OVAL-Community/SCAP-Self-Assertion/tree/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content) corpus. These seven files were reproduced from the successful [original-source native C compiler workflow, run 39325259986](https://github.com/vanderpol/scap-ng/actions/runs/39325259986). The [source-independent compiler and coverage manifest](../../../tools/research_c_original_oval_to_authored_c.py) recorded **7 of 162 source-compatible Definitions converted to C**, with **155 still unsupported by this narrow native C compiler**; there are **five additional original invalid/deprecated Definition blockers**. All **785 original Tests** remain counted in the source review manifest. The 162/167 source OVAL roundtrip result is an **existing 0.3/A capability**, not a C authoring success count.

### What each `from` / `must` file proves—and doesn't

For the macOS plist check, original OVAL declares one Test + one Object + one State; the new C representation contains the same file/XPath selector and requires **every eligible Item** to report `value_of: true`, with original at-least-one existence preserved by the C compiler. The original Test comment, exact Definition ID and pinned XML location are in each file header.

The source-independent C compiler enforces the supported field capability mappings and confirms the lowered typed Test preserves the selected source Test's selector, operation, value, existence and matching. It does **not** execute a target collector or prove every scanner/OVAL evaluation outcome. Other original constructs are deliberately rejected rather than lost; advanced source Set/Filter/Variable/foreach and most compound multi-Test Definitions still need authoring conversion.

### More challenging C research examples to read *after* the seven real source conversions

- [Real Windows 11 seven-check account-rights/role composition](./c-source-exact-windows-rdp-rights.research.yaml) — two shared observations, a role-dependent logic tree, source-backed **read-only C research view**, not one of the seven converted Self-Assertion Definitions. Does its `require` tree convey enough without hiding evidence?
- [Apache derived value with private observation](./c-derived-apache-version.research.yaml) — demonstrates `observation` and derived values instead of a separate authored Object; this is a narrowly source-reconstructed Apache example, not the complete complex Apache Assessment.

### Short feedback that would actually help

Please focus on **whether the evidence being gathered (`from`) and the requirement (`must`) are immediately clear**, whether `any_item`/`every_item` is clearer than current OVAL `check_existence`+`check`, and whether any part appears to hide essential dataflow or ownership of values. For the complex Windows/Apache examples, consider whether observations and derived values meaningfully reduce mental effort. There is no 0.4-C schema freeze decision being requested.

**Development continues:** [source-gate report](./C-OVAL-SELF-ASSERTION-SOURCE-GATE-2026-10-19.md) · [Original source conversion compiler](../../../tools/research_c_original_oval_to_authored_c.py) · [Research issue #245](https://github.com/vanderpol/scap-ng/issues/245). Newer multi-Test compiler research exists, but the 7-of-162 number here reflects the latest *completed, independently reproduced full corpus run* at the time this page was prepared.
