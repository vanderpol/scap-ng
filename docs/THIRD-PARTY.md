# Third-party attribution and licensing boundary

This staging import includes project-owned schemas, native capability mapping
metadata, and a small set of curated source-derived authoring examples.

- The top-level Apache-2.0 license is **not** a claim to relicense OVAL, DISA,
  NIST, NIWC or other third-party source material cited in mapping provenance
  or examples. Preserve source identifiers, notices and provenance.
- No original SCAP 1.4 benchmark, OVAL XML corpus, external source archive,
  historical package binary, research fixture bundle or published proof asset
  has been copied into this staging repository.
- Each curated example traces to an exact file in the original Git repository;
  its semantics must not be represented as independently runtime-proved.
- Before any public 0.4.0 distribution, complete the project-wide provenance,
  copyright, notices and release-packaging review.

## OVAL documentation research boundary

The 5.12.3 OVAL Windows `ntuser` XSD contains extensive field and scanner
implementation annotations. Its source file includes a Government
License/Disclaimer that requires reproduction alongside a copy or modification
of the original XSD. To keep ownership boundaries clear, our generated
documentation uses original summaries, pinned upstream links, and an offline
audit of annotation counts and hashes; **it does not copy the original XSD
prose**. All translated scanner notes remain unreviewed implementation
candidates, not frozen SCAP-NG rules. Verbatim incorporation, if ever desired,
requires a separate reviewed notices/attribution decision.

