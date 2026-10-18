# 0.4 readability research — where Apache and DNS actually hurt

**18 October 2026 · Research issue [#235](https://github.com/vanderpol/scap-ng/issues/235). Non-normative.** No scanner/compiler/schema design is changed by this note.

## Source-backed measurements, not guesses

Inspected the *complete English-first* YAML embedded in [Apache SV-214228](FULL-05-apache.md) and [DNS SV-259345](FULL-04-dns.md). These are **authoring source graph measurements**, not execution durations or duplicate native provider counts.

| Source example | Named local Variables | References from one named Variable to another | Longest Variable-only prerequisite chain | Final checks |
| --- | ---: | ---: | ---: | ---: |
| Apache UNIX `SV-214228` | **18** | **19** | **9 named Variable nodes** | **4** |
| DNS Server `SV-259345` | **3** | **0** | **1 named Variable node** | **5** |

DNS's three command-building Variables **all reference the same named forward-zone Object**. It has a *shared-acquisition plus command-transformation* readability problem, not an 18-Variable cascade.

For Apache the two major branches, derived from the actual authoring names and expressions, are:

### Apache path A — base config + Include/IncludeOptional path discovery

```text
gather-unique-apache-http-installation-paths-object
  → apache-base-install-directories-unix-variable
  → httpd-root-apachectl-v-variable
      → filepath-httpd-root-variable ─────┐
  → server-config-file-apachectl-v-variable
      → relative-server-config-file-variable
          → filepath-http-conf-file-variable
              → shell-command-check-all-include-include-optional-files-variable
              → all-included-conf-files-from-include-refernces-in-httd-conf-variable
              → merged-included-conf-files-from-include-refernces-in-httd-conf-variable
              → httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
                  → KeepAlive checking command
                  → MaxKeepAliveRequests checking command
```

This is a **conceptual dependency outline, not complete edges**: `filepath-http-conf-file` also depends on the parsed HTTPD_ROOT and SERVER_CONFIG_FILE components. The complete YAML retains the exact expressions, regular expressions, shell behavior, merge delimiter, sorting and order.

### Apache path B — *actually loaded* config list

```text
gather-unique-apache-http-installation-paths-object
  → apache-path-httpd-or-apache2-variable
  → command-gather-httpd-apache2-list-all-loaded-configuration-files-variable
  → all-loaded-configuration-filepaths-variable
  → merged-list-all-loaded-config-files-variable
      → KeepAlive checking command
      → MaxKeepAliveRequests checking command
```

The two discovery routes are **not obviously redundant**: one follows the config and Include chain, the other parses active/loaded files. Combining them without independent source/evidence proof could lose an important distinction between a file being present and a file being loaded.

## Three specific authorability problems to resolve

1. **Author writes command plumbing instead of the check.** The author must mentally evaluate `concat`, shell collection, regex extraction, merge/sort and path derivation across up to nine named Variable nodes before reaching the four final predicates. Renaming `variables` to `sources` alone changes none of this.
2. **Related checks cannot clearly reuse an authored *collection recipe*.** Both Apache directives consume the same two derived config-file sets. DNS has three independent commands derived from one zone list. We should be able to declare the upstream collection once and express the dependent transformations visibly and type-safely without hidden loops or duplicate shell execution.
3. **Optional versus required evidence is fragile.** Apache's optional included-config predicates use `when_present_...` comparisons, while main config checks require results. The difference between zero command-result Items, absent stdout fields, empty paths, uncollected configs and failures must remain visible. DNS similarly distinguishes a successfully executed command with no zone-output values from having no collected command Item.

## Competing simplification directions to test

**Candidate A — navigation, without a language change.** Keep the current named Object/Variable semantics and automatically show a human-readable dependency tree beside the YAML. This is safest, but the auditor still writes all 18 names, commands and transforms; it does not fulfill the author's ease-of-creation goal by itself.

**Candidate B — one typed, composable acquisition expression in the *one* authoring language.** A named collection can explicitly consume another collection, transform its values and then collect dependent Items, with a typed source identity at each stage. The author would name important reused outputs such as *all loaded config paths* and *base config + include paths*, not every transient concat/regex/merge intermediate. **This is a design goal, not a new `derive/pipe/gather` syntax authorization.** Do not draft keywords first; define exact dataflow, empty/error/provenance and item-parent correlation contracts, then see which YAML shape is shortest to explain correctly.

**Candidate C — do nothing but improve helper/editor UX.** Worth retaining as a control: when source composition turns out not to preserve arbitrary OVAL commands, a transparent editor on the existing graph may outperform a misleading one-line shorthand.

## Objective acceptance gate before proposing syntax

Select **one** real Apache path and **one** real DNS zone-derived command from the complete linked sources. For each, show a *full* current and candidate definition (no omitted Variables or hidden scripts); the transformations must preserve selected Items, ordering, regex matches, strings versus arrays, error-if flags, completeness and provenance. Verify zero/one/many sources, missing source, collector error and partial collections independently. Ask a new auditor to explain and author the chain **without the design rationale**.

A winning candidate should reduce either **independently named transients or reference-hop count** and novice author errors, not merely characters. If an abstraction makes *absence* or *error* outcomes harder to reason about, reject it even if YAML is much shorter.

**Status:** dependency analysis complete; composition grammar, semantic lowering and independent human review remain open. Do not treat the hand-drawn outlines or a smaller count as executable equivalence.
