# Apache multi-file configuration: native policy vs original SCAP-derived checks

**17 October 2026. Research #235 (authoring), #229 (source parity). Not a normative 0.4 change, Apache parser, or completed scanner.**

This research starts from the complete [334-line SCAP 1.4-derived Apache research Assessment](../assessment-simplification/english-first-04/canonical-operators/apache.canonical.research.yaml), not just the English description. The current two-assertion native sketch in [examples/05-apache-directives.yaml](examples/05-apache-directives.yaml) must NOT be labeled source-equivalent.

## Original source structure

The original Assessment has **18 declared derived Variables** and a four-test AND. Every Test uses an independent shellcommand object and **requires at least one Item**. The four Tests separately evaluate:

| Original Test | Command source files | Item cardinality | Required comparison |
| --- | --- | --- | --- |
| KeepAlive primary/Includes | Primary httpd.conf/apache2.conf and files derived from Include statements | at_least_one | Each stdout_line must match regex for KeepAlive On |
| KeepAlive loaded files | Files discovered through server -t -D DUMP_INCLUDES | at_least_one | Every PRESENT stdout_line must match regex for KeepAlive On |
| MaxKeepAliveRequests primary/Includes | Primary config and direct Include paths | at_least_one | All collected subexpressions >= 100 |
| MaxKeepAliveRequests loaded files | Files discovered through DUMP_INCLUDES | at_least_one | Every PRESENT subexpression >= 100 |

The source's last two comparator fields differ between an unconditional comparator and a when-present comparator. However, optional compared **entity values** do not waive the requirement for an **Item**. A shellcommand with zero Items does not satisfy at_least_one, even if the check description begins with "If ... defined."

All four source collections explicitly set both exit-code and stderr automatic-error flags to false. An exit code other than zero, by itself, does **not** establish that the source check returned Error. Do not substitute a generic "command failure means Error" rule.

The two file discovery paths also differ. The primary+Include file list is derived from grep of Include/IncludeOptional statements; the loaded-file list comes from the Apache -t -D DUMP_INCLUDES command and regex extraction. The original includes shell pipeline output captures, unique/merge and document ordering. There is no basis for assuming the two populations are identical.

## Provable traps before source conversion

**One loaded-source Test with zero Items.** A native provider might expose a complete configuration containing KeepAlive On and MaxKeepAliveRequests 150. But the original also requires an Item from EACH of two separately evaluated "other loaded" command Tests. Flattening four shell observations into two effective settings has lost enough information that the native evaluator cannot reconstruct whether all four Tests satisfied their collection cardinalities. This is a **structural information-loss counterexample**, not an assertion about what every real shellcommand probe outputs.

**Directive name prefix:** the original grep patterns include case-insensitive starts-with expressions for KeepAlive. These can select a literal line beginning KeepAliveTimeout, whereas a typed provider selecting the exact directive token KeepAlive would ignore it. These are different evidence populations. Whether it changes final compliance depends on subsequent State comparisons, which require independent source-level test fixtures.

**Different configuration files can disagree.** Apache configuration may include KeepAlive On in one file and KeepAlive Off in another. A provider returning only the final effective setting erases the conflicting source record, whereas the original compares multiple command-returned lines with an all-compliance requirement. Conversely, a simple provider that checks all raw directives might reject otherwise inactive or overridden config. Neither is automatically source-faithful.

**Source regex vs typed numeric parse:** the original MaxKeepAliveRequests probe obtains a regex subexpression, which is not the same as validating the entire directive value as a well-typed integer. A provider that rejects "100garbage" before comparison would differ from a regex that captured the numeric prefix 100. This is a *potential* mismatch; verify exact source capture semantics before claiming an outcome.

**Optional stdout entity values:** an Item existing without stdout_line may satisfy a when-present predicate, but an entirely missing shellcommand Item fails at_least_one. This distinction is lost in a simplistic "directive may be absent" paraphrase.

## Prototype native data capability

The [read-only Apache provider](../../tools/research_provider_apache_directives.py) and its [v0.1 contract](providers/apache.config_directives.v0.1.yaml) parse a deliberately small, static subset of files. It follows static Include and IncludeOptional, bounded glob matches, and nested includes; it reports observed KeepAlive/MaxKeepAliveRequests tokens, unmodified value text, source file and source line.

Crucially, it retains duplicate/conflicting directives, tracks file identity, and marks the evidence **incomplete** when an Include cannot be read or resolved, a context container is seen, macros or continuations cannot be interpreted, a file/include cycle occurs, or configured limits are hit. It does **not** run Apache, parse all its contexts, distinguish active configurations, or infer effective directive values.

[Isolated fixture tests](../../tools/test_research_provider_apache_directives.py) cover primary/include file provenance, conflicting values, optional vs required missing Includes, cycles, duplicate references, path escapes, unsupported contexts, dynamic macros, caps, raw strings, lookalike directive names and invalid lines. [Source contract tests](../../tools/test_research_apache_source_contract.py) pin the 18 Variables, four Test IDs, four per-Test at_least_one requirements, optional field predicates, and source exit/stderr flags.

No benchmark test runs this provider against production Apache instances. The contract remains *fixture-test only*.

## What auditors should write in a genuinely native check

A greenfield requirement might say:

~~~yaml
require:
  and:
    - apache.directive:
        name: KeepAlive
        equals: "On"
    - apache.directive:
        name: MaxKeepAliveRequests
        at_least: 100
~~~

But the provider MUST explain which HTTP server installation is selected, which loaded context the values apply to, what an absent directive means, duplicate/conflicting source configuration, unsupported Apache features and whether it exposes raw or effective values.

**A converted source-faithful Assessment may not be able to use this two-line abstraction.** It might need four separate scoped source requirements and a compatibility evaluation path. That is acceptable if ordinary humans author native content and the converter preserves original security behavior without inventing a false equivalence claim.

A middle-ground native requirement could check four scoped populations *if that is truly the intended policy*, with a typed file source and a positive minimum of one per population. That is still a different artifact from the literal original source because the original operates on shellcommand Items and optional stdout/subexpression fields.

## Research conclusion

**The hard issue is not just file inclusion. It is what counts as an observed Item, how source output becomes a compared field, and whether absence of stdout is allowed inside a required command Item.**

Reusable typed providers can reduce authoring complexity without creating a STIG-specific verdict function, but must expose raw evidence and diagnostics. Replacing four command graphs with two normalized settings before proving equivalence would repeat the original OVAL-in-YAML mistake in reverse: it would make content prettier by silently deleting semantics.

**No Gemini request yet.** Once the four-source scope and provider/evidence contract can be presented with adversarial fixtures, an independent review should ask whether a novice auditor can AUTHOR an unambiguous policy, not whether two YAML spellings look nicer.
