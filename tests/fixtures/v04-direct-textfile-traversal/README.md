# Original text-file traversal Objects

The XML is byte-exact original Self-Assertion content pinned at
`e3538595c5083b9c34d937a81d319234df9bbfaa`;
[provenance](provenance.json) records its path and SHA-256.

Original Objects `oval:org.mitre.oval.test:obj:12` and `:734` specify downward
traversal with depths 1 and -1. Their acquisition dependency closures pass the
original XSD/Schematron and independently match the native Object terms; -1 is
represented by native `max_depth: unlimited`. The original default traversal includes
symlinks and directories; regex flags and Item creation are separate parameters.

The **whole original document is not declared valid**: it retains an unrelated
deprecated notes element and a Test using `none_exist` with a State reference.
Those original diagnostics and source bytes are preserved. Node-scoped checks
are limited to the two Object closures, with no source repair.

These are **two Object proofs, not two converted original Tests**. The original
Tests use `all_exist`, whose population contract remains unsupported. A new
negative regression confirms that boundary. Compiled-package checks use an
explicitly constructed native Test/Benchmark wrapper for each Object; this
wrapper is not a source Test translation or production Rule proof.

Positive/negative regressions compose recursion with regex flags, Item creation,
filesystem scope, Sets and ordered Filters. Mutations change depth, symlink
selection, flags, scope and filter order. Native Boolean/integer aliases and
malformed traversal payloads are rejected. Original upward recursion, path/
behavior Schematron violations, deprecated view attributes and unknown data
remain unsupported.

Production Rule proof coverage is checked separately by the maintained six-
source acceptance gate against the pinned original NIWC archives. No scanner
file access, traversal execution or runtime status equivalence is claimed by
these Object terms or compiled-package checks.

```bash
PYTHONPATH=.:tools python -m unittest test_v04_direct_textfile_traversal test_v04_direct_textfile
```
