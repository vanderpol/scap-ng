# Item inclusion and verified observation-copy examples

These synthetic cases extend the standalone ownership result examples from
`../assessment-results-0.2.0/`. They exercise result materialization, not target
collection, collection-cache reuse authorization, or production STIG conversion.

Two file Items are available; only `file-config` contributes to the Test.
`expected-results/scopes.json` specifies the independent scope/count oracle:

- `all` (default): retain both available Items and both Object references.
- `consumed`: retain `file-config`, omit the unused Item, and record the original
  available and included/omitted counts. The original collection status and
  completeness flags retain their acquisition meaning.

Test references, per-Item results, Variable `item_refs`, and actual field-use
records all contribute to the mandatory consumed set. Field selection happens
later in the optional derived Item report; canonical consumed Items keep their
full typed observation fields.

`source.assessment-result.json` is a fixed UTF-8 synthetic source artifact.
`expected-results/imported-items.json` records its exact SHA-256 byte pin and the
expected copied Item. The import assigns `local-file`, preserves UID 1001 and
its lookup metadata, and records source execution/binding/completeness. This
snapshot was generated from the helper and is checked against pinned source
bytes; the scope oracle is independently specified.

```sh
PYTHONPATH=tools python tools/test_item_materialization_v02.py
```

On PowerShell set `$env:PYTHONPATH = 'tools'`, then run the Python command without
the Unix environment prefix. All checks operate offline. A digest pin verifies
bytes, not producer trust, source accuracy, freshness, signatures, or permission
to reuse a collection. Those remain responsibilities of the importing producer.
