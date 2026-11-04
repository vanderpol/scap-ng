# Organizational Input authoring demonstration

These constructed Rule/Benchmark/applicability wrappers reference the canonical
[optional Assessment](../windows-optional-organizational-input.assessment.yaml).
They demonstrate policy wiring, not an original SCAP Benchmark conversion or a
scanner result. Assessment identity resolves through the selected source graph.

The Rule omits `organizational_input_requirements`. A compiler derives the
complete map from its explicit Input-to-Parameter binding and Assessment
references. Authors edit the Input declarations, requirements, guards and binding;
they do not have to write source-pointer strings. An explicitly supplied map must
match the complete derived reference multiset. Packaged Rules always contain the
map, including `{}` when no organization-resolved dependency exists.

Native uses contain `kind: value|presence` and an RFC6901 `source_path` relative
to the selected Assessment body. Pointers identify actual Input references,
including the presence guard. Wrong kind, target, Input/Parameter identity,
duplicates, missing or unexpected locations reject during semantic compilation
and package verification; JSON Schema alone does not prove those graph checks.
OVAL source State terms remain source-fidelity/provenance concepts and are not native 0.4 authoring fields.
