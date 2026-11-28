# OVAL 5.12.3 and native YAML file-content boundaries

The [expectation manifest](expected.json) defines the file bytes, selected
YAMLPath, permission preconditions and expected outcomes. The UNIX and
Windows OVAL sources each contain four independent Definitions. The
corresponding native YAML Assessments preserve the typed record and exact
key spelling.

| Fixture | Pinned OpenSCAP UNIX Object flag | UNIX Definition |
| --- | --- | --- |
| Readable empty mapping | does not exist | false |
| Readable document without the selected path | does not exist | false |
| Malformed YAML | error | error |
| Valid YAML with read permission denied | error | error |

The expected OVAL Test disposition follows the collection flag and existence
requirement. For example, uncollected evidence produces unknown. The
[OpenSCAP receipt](openscap-unix.json) records each selected Definition, Test
and Object rather than an adjacent unselected Definition. OpenSCAP 1.4.2
advertises OVAL 5.11.1. Both XML sources passed external validation with
the pinned OVAL 5.12.3 XSD and embedded Schematron.

The current [converter replay](converter.json) matched all eight native Test
payloads exactly, including the paths, YAMLPath, cardinalities and record key.
The [RI admission receipt](ri-hold.json) records selected Test holds before
acquisition on both documents. The [Studio model receipt](studio.json) covers
both exact native documents. Windows collection and native scanner
outcomes remain unqualified.

```sh
python conformance/tools/replay_oval_yaml_boundaries.py --oscap /path/to/oscap --check
```

To replay conversion, pass both XML paths to
`conformance/tools/qualify_oval_conversion.py` with the converter revision,
schema checkout and source commit recorded in the converter receipt. Supply
`--boundary-expectations` with this directory's expected.json and
`--receipt` with converter.json.

- [OVAL 5.12.3 Object flags and Test result rules](https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/oval-results-schema.xsd#L504)
- [RI YAML file-content collector gap](https://github.com/vanderpol/scap-ng-ri/issues/305)
