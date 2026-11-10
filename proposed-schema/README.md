# Proposed schema-derived documentation

These are proposed documentation annotations, not a release or a replacement for
`schema/`. All frozen 0.4.0 assertions and acceptance boundaries remain intact.
Descriptions live in actual JSON Schema resources under `documentation/`.
The reference and editor metadata are generated transports, not prose sources.

## Regenerate

Python 3.12 and the pinned dependencies in `requirements-dev.txt` are required.
No OVAL checkout, network access, editor installation or scanner is required.

```sh
python -m pip install -r requirements-dev.txt
python tools/generate_documentation.py
```

That one generation command discovers all capability and shared schemas and
writes the platform indexes, basic/advanced references, exact-context editor
help, coverage, gap and duplicate-description ledgers, and an integrity manifest
under `docs/reference/`. To reject missing or stale output:

```sh
python tools/generate_documentation.py --check
python -m unittest discover -s tests -v
```

## Maintain

1. Edit the proposed schema's `description`, not generated Markdown or metadata.
   Keep the basic meaning short; a second paragraph can record supported caveats.
2. Reuse an existing description owner with a schema `$ref`, or a passive
   `x-doc-description-ref` when adding an assertion-bearing reference could change
   validation. These links are explicit; the renderer never borrows parent prose.
3. A capability declares its identity and Object/Item/Require schema pointers in
   `x-doc-capability` and `x-doc-roles`. Item and Require reference the same
   `$defs/meanings`; add a result field once. Inline Object fields are discovered
   from `x-doc-validation-ref` and combined with capability-specific annotations.
   Add a new capability schema and its declarative Test association; no renderer
   code changes are needed. A regression test exercises discovery of a new
   capability and field.
4. Regenerate, inspect the tables and ledgers, and run the commands above.
   CI rejects stale output, broken associations/references and new missing
   descriptions. `coverage-debt.json` records existing exact-pointer debt; reduce
   it as descriptions are researched. Do not enlarge it to bypass a missing-field
   failure without documenting why that contract cannot safely be described.
5. Preserve semantic holds. Validation structure is compared with all 35 frozen
   schema roots; 170 accepted/rejected syntax witnesses run against both trees.
   Schema validation does not test collection, evaluation or scanner equivalence.

## Integration annotations

| Annotation | Purpose |
| --- | --- |
| `x-doc-origin` | Original frozen schema resource |
| `x-doc-capability`, `x-doc-platform`, `x-doc-roles` | Capability identity and role pointers |
| `x-doc-role` | Role of an inline schema view; Object fields follow its native validation reference |
| `x-doc-description-ref` | Explicit link to one description owner; adds no assertion |
| `x-doc-validation-ref` | Existing validation shape, separate from a field-meaning annotation |
| `x-doc-datatypes`, `x-doc-comparison-datatypes`, `x-doc-values` | Native mapping declarations; **not** new payload restrictions |
| `x-doc-declared-shape` | Collection-parameter declaration; distinguished from what validation enforces |
| `x-doc-source`, `x-doc-review`, `x-doc-status` | Source identity, editorial receipt and documentation status |
| `x-doc-availability`, `x-doc-contract`, `x-doc-gap-proposal` | Discrepancies, unresolved behavior and draft wording |
| `x-doc-expand`, `x-doc-scope` | Keep shared controls/libraries out of basic tables and identify inactive or unreferenced schema contexts |

These are proposed, passive schema annotations. Types, required keys, enums,
default annotations and validation structure come from the actual schemas.
Mapping-only parameter/datatype declarations remain explicitly nonasserting;
this work does not settle the previously held datatype questions.

`tools/documentation_artifacts.py` loads the offline transport only with an
externally supplied manifest SHA-256, verifies source/output hashes, and resolves
exact capability/role/path or schema-pointer help. Missing or stale packs fail
closed. Schema help carries its context scope so inactive migration shapes and
unreferenced helpers are distinguishable from declared grammar. It does not provide raw YAML-language-service integration or prove a
VS Code host result. Production editor pins are unchanged.

JSON Schema `examples` remain available at their source pointers. Issue #42 can
extend the generic rendering with paired, evidence-qualified Pass/Fail examples;
no example execution or scanner-equivalence claim is introduced here. The
manifest binds schemas, provenance, debt and generated output for later versioned
artifact packaging; this PR performs no packaging or release publication.
