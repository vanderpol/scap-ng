# Scanner-Facing Package Prototype

Iteration 001 assumes that source organization and runtime distribution are different concerns.

Regardless of whether the combined-rule or split policy/assessment/binding source model is selected, an **automated published benchmark is one self-contained signed package**.

A scanner operator should not have to install a policy package and a separately versioned automation package.

## Candidate bundle

Tentative extension: `.scapng`

Conceptual structure:

```text
META-INF/
  manifest.json
  signature.cose

benchmark.json
rules/
assessments/
bindings.json
profiles/
provenance/
```

The exact content directories depend on the architecture decision. A compiler may also choose a normalized internal arrangement if the specification permits it.

## Integrity model

The preferred research direction is:

1. canonicalize each normative JSON member as required;
2. hash each normative member;
3. list all member digests in `META-INF/manifest.json`;
4. sign the canonical manifest;
5. reject unlisted normative members, missing members, duplicate paths, or digest mismatches.

The signature therefore covers the complete logical benchmark without depending on incidental ZIP compression bytes.

The exact signature technology and ZIP profile remain open questions.
