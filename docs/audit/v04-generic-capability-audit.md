# Generic conversion architecture: all 100 mappings

Read-only architecture audit under [#251](https://github.com/vanderpol/scap-ng/issues/251),
against `dbaafd7337396573baa7c3b1019f3f7becbccc91`. No converter, approved schema,
capability mapping, source fixture or release gate changed. Conversion coverage
remains 249 source-proved / zero compiled-unproved / 42 blocked original Windows
Server 2025 Rules. This audit enables no additional capability.

## What the counts establish

All **100** supported mapping JSON files were inspected alongside their referenced
original OVAL XSD Object/State declarations. The [CSV](v04-generic-capability-audit.csv)
lists every capability; the [machine packet](v04-generic-capability-audit.json)
records classification, source fields, unmapped fields, datatype gaps and hashes.
XSD field enumeration here covers directly declared fields, not a complete
validator, inheritance resolver or execution of embedded Schematron.

| Disjoint structural class | Count | Conversion approach |
| --- | ---: | --- |
| Ordinary flat selectors and State fields | 60 | Existing generic field-routing and predicate design |
| Ordinary current-system source, no native Object | 17 | Existing generic `test_source.kind: none` design |
| Traversal family | 11 | Shared traversal/behavior interpretation plus field routing |
| Collector parameters/behaviors, excluding the preceding class | 7 | Shared parameter/default/behavior interpreter |
| Record/collector-input family, excluding traversal | 3 | Shared record and input semantics |
| Different Test-source forms | 2 | Fixed-unknown and direct-Variable Test paths |
| **Total** | **100** | **77 ordinary shapes; 23 with additional features** |

These are **structural candidates, not 77 certified complete conversions**.
The direct converter currently loads only **15** capabilities, with bounded
original-source evidence. Eight of those belong to the ordinary classes.
Even enabled capabilities do not support every legal source construct. Among
the 77 ordinary shapes, 21 expose native datatype alternatives beyond the
current literal reader's string/integer/Boolean subset; IOS and IOS-XE interface
metadata omit `field_datatypes`. Common operator, Variable/function, record
absence and existence limitations also prevent an honest universal support count.

## Which capabilities need more than plain field copying

- **Traversal (11):** `file.hash`, `independent.textfilecontent54`,
  `independent.xmlfilecontent`, `independent.yamlfilecontent`,
  `linux.selinuxsecuritycontext`, `unix.file`, `windows.file`,
  `windows.fileeffectiverights53`, `windows.ntuser`, `windows.registry`,
  `windows.regkeyeffectiverights53`. Preserve recursion, filesystem scope,
  path alternatives, per-leaf behavior and Filter/Set boundaries. YAML content
  additionally uses records; text/NTUSER capabilities also have collection controls.
- **Collector behaviors (7):** `independent.shellcommand`, `linux.rpminfo`,
  `linux.rpmverifyfile`, `linux.rpmverifypackage`, `windows.sid`,
  `windows.sid_sid`, `windows.wuaupdatesearcher`. Preserve command-error flags,
  file-path inclusion, verification suppression, group resolution and update scope.
- **Record/input handling (3 here; four total including YAML):**
  `independent.sql512`, `windows.wmi.query`, `windows.cmdlet`. Preserve acquisition
  inputs versus matching, null versus empty, record identity/member errors,
  field-selection versus expected-value matching, and complete record conditions.
- **Test-source variants (2):** `independent.unknown` has no ordinary Object/State
  reference sequence and preserves a fixed unknown result through its capability;
  `variable.value` removes Object indirection in favor of a Test Variable reference.
  Its State `var_ref` cannot be discarded without proving it redundant.

These justify **shared semantic handlers**, not 23 whole-capability converters.
The audit establishes no inherent need for a handwritten converter per ordinary
capability. Source validation in `v04_direct_system_policy.py` and the file-rights
datatype guard are examples that can move into common XSD/Schematron validation,
instead of growing another capability-specific branch.

## Can XSD and metadata drive this?

**Yes, with a small shared engine and reconciled machine-readable metadata.**
Original XSD supplies field structure, types, required/fixed/default distinctions,
nillability, enums and inheritance. Embedded Schematron supplies additional
constraints: the policy nonnegative checks and nil cmdlet record datatype
requirement are concrete examples. Current native schemas and reviewed mappings
supply native names, source kind, collection parameters, approved vocabulary
crosswalks, record structure and acquisition restrictions. State content lowers
to inline structured `require`; this proposes no separate native State layer.

The metadata is not yet a complete executable conversion contract:

- Only **3 of 14** mappings with collection parameters have a native
  `collection_parameter_source_map`. Other routes occur in historical crosswalks
  or behavior descriptions. They need consistent canonical field routing.
- **19** Object crosswalks still contain historical `select.*`/`collect.*` paths.
  Those strings must never become generated authoring wrappers.
- **Seven** traversal crosswalks still map `recurse_file_system.all` to `any`.
  The approved common schema requires `filesystem: all`; the current tested
  text-file helper already preserves it. Do not execute the stale spelling.
- Deprecated State fields found outside ordinary maps generally need explicit
  rejection, not guessed renames or silent removal. The Variable identity field
  is a distinct structural transformation, not a deprecation.

XSD does not establish conversion equivalence by itself. Shared code must preserve
quantifiers, Boolean logic, dynamic values, collection failures, identity and
ordered acquisition boundaries. Approved semantic differences need explicit
reviewed metadata/proof. Do not infer a Windows `all_exist` normalization or repair
malformed source merely because a structurally valid native document can be built.

Recommended sequence: resolve/validate source types and Schematron once; complete
shared datatype/operator handling; normalize field/behavior routing against the
approved native grammar; reuse record, traversal and dependency handlers; then
admit capability mappings in source-backed, independently proved batches. Each
ordinary capability should add mapping data and fixtures, not a new Python module.
Keep the existing source-proof, schema, compiler and independent consumer gates.

Validation for this report: all 100 rows have distinct identities, referenced XSDs
resolve, class counts sum to 100, and the enabled catalog contains 15 entries.
No broad regression suite or corpus conversion was needed for a documentation-only
audit. This is neither scanner parity nor a production-readiness finding.
