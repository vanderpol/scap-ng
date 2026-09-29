# SCAP-NG -> OVAL Round-Trip Prototype

This tool regenerates OVAL 5.12.3 from the machine-readable stress fixtures in
`research/iterations/003/examples/oval-ng-roundtrip-stress/`.

It is intentionally fail-closed:

- only implemented fixture constructs are accepted;
- unsupported node types/functions are errors;
- it does not claim to be a general SCAP-NG compiler;
- generated IDs are new deterministic research IDs, because semantic comparison
  must not depend on legacy IDs.

Current support covers enough surface for the first stress corpus:

- Tests/Checks with check/check_existence;
- independent textfilecontent54, linux partition, and linux
  inetlisteningservers Collections;
- named Collection Sets using UNION;
- Collection Filters referencing States;
- selector/predicate operations and datatypes;
- variable references and var_check;
- constant Variables;
- local Variables;
- object_component;
- variable_component;
- concat;
- arithmetic;
- count;
- behaviors used by the fixtures.

Usage:

    python tools/scap_ng_roundtrip_v003/ng_to_oval.py \
      research/iterations/003/examples/oval-ng-roundtrip-stress/rhel-audit-log-partition.json \
      -o /tmp/rhel-audit-log-partition.xml

Next steps are XSD/Schematron validation and an independent semantic normalizer
that compares original OVAL with regenerated OVAL.


## Conformance development workflow

Active round-trip/conformance development is performed on a pull-request branch
so PR-triggered GitHub Actions runs, jobs, logs, and generated artifacts are
visible through the GitHub integration.

The branch workflow is not a semantic requirement of SCAP-NG; it is only a
development/testing mechanism. The authoritative test requirements remain the
XSD/Schematron validation and semantic round-trip comparisons described above.
