# 0.4-C complete Apache example: one authoring model, unchanged 0.3 execution

**19 October 2026 · [issue #245](https://github.com/vanderpol/scap-ng/issues/245) · Experimental, not a normative language, not a deployed scanner assessment.**

## What is now independently compilable

The exact original full [Apache SV-214268 source Assessment](../../requirements-first-language/contract-candidate/corpus/source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml) has **five automated Tests and nineteen chained, computed Variables**, including an explicit named shared acquisition plus four private acquisitions inside source variable expressions. Those values feed subsequent shell commands that inspect loaded Apache configuration files, Session directives, the HttpOnly/Secure SessionCookieName attributes and the session cookie module.

The new **[complete source-independent C hybrid compiler](../../../tools/research_c_apache_hybrid_authoring.py)** converts a human-facing Assessment with:

- One named shared `observation` (a source-backed command acquisition).
- Nineteen `derived_values` steps containing typed field reads, captures, concatenations, distinct/merge operations, and `use` references to prior results. They are **not all passive comparison values**: steps explicitly parameterize further shell command acquisitions, preserving causal dependencies.
- Five human-named `checks`, each with a `from` acquisition and a `must` requirement distinguishing existence, matching and per-field predicates.
- One `require: and` tree preserving the original five-Test order and identifiers, with original Test descriptions, command strings, filters, regexes, and original field matching retained.

**No source A Variables, Tests, original shared Objects or compiled output graph are supplied to the C compiler.** It independently reconstructs them from this C input. The source importer is only used to *present an initial editable research view* and, separately, to verify full deep equality on the returned A-compatible Assessment.

### What authors can read (excerpt from full generated YAML)

```yaml
checks:
  if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify:
    source_id: if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify-test
    description: If the SessionCookieName directive exists in other loaded configuration files, verify it is configured with HttpOnly
    from:
      independent.shellcommand:
        description: Gather all SessionCookieName data from all loaded conf files
        collect:
          command:
            use: shell_command_to_check_sessioncookiename_in_all_loaded_conf_files
          shell: bash
          pattern: SessionCookieName .+
          error_if_exit_status_not_0: false
          error_if_stderr_exists: false
    must:
      items_exist: one_or_more
      items_match: every
      fields:
        - field: stdout_line
          exists: optional
          matches: every
          matches_regex: (?i)HttpOnly
        - field: stdout_line
          exists: optional
          matches: every
          matches_regex: (?i)Secure
      fields_join: and
```

**The two optional field checks are not silently changed into required matches.** The Test-level existence condition remains independent. A semantic rewrite of optional field handling would require its own reviewer decision.

## Verification, not claims

[Original-source and generated C proof — Actions run 39337906612](https://github.com/vanderpol/scap-ng/actions/runs/39337906612) verifies:

| Full original Apache source property | Result |
| --- | --- |
| Original Tests reconstructed exactly | **5/5** |
| Local Variable definitions reconstructed exactly | **19/19** |
| Named shared acquisition preserved | **1/1** |
| `must` field/existence and State matching | All Test structures exactly equal |
| C `use` dependencies feeding further acquisitions | Original typed `variable` edges restored |
| Missing/duplicate Test, changed command, changed match/existence, changed field, graph cycles, source hash/pin drift | Negative tests reject |
| Scanner execution and six-state differential equivalence | **Not proven** |

The [generator](../../../tools/generate_c_apache_full_hybrid.py) produces a **15.6 KB standalone C YAML Assessment** plus a SHA-256/proof JSON from the checked-in source fixture, using:

```bash
PYTHONPATH=tools python tools/generate_c_apache_full_hybrid.py --output c-apache-source-review
```

The pinned successful CI run packages `apache-sv214268-five-checks-nineteen-derived-values.research.yaml` and `proof.json` as the `c-original-apache-full-hybrid-research-not-scanner-parity` artifact; artifacts have a finite GitHub retention period. Re-run the above generator for reproducible bytes using [source revision `88213df`](https://github.com/vanderpol/scap-ng/commit/88213df6796b35554295afb908f0ff98bf0f2f79). **SHA-256 of generated YAML:** `795908c3a263c1572f5a5be1cd75be9af7349f546da32267bdf375aad4ae013d`. **SHA-256 of pinned source fixture:** `e020339a22ddf4daaca6db5e37c6251d78f32a9d467c84b64a76ccc174166ef5`.

**312 focused C tests passed** at [Actions run 39337906612](https://github.com/vanderpol/scap-ng/actions/runs/39337906612), including seven new complete Apache regression cases.

## Follow-up: independently audited value grouping is *not* a textual readability win

The [source-backed folding audit](../../../tools/research_c_variable_folding_safety.py) identified **four** genuine single-consumer, pure-value steps eligible for *presentation* grouping. It deliberately excluded other single-use steps that feed commands/selectors and all shared/reused nodes.

The new [bounded grouping adapter](../../../tools/research_c_apache_grouped_values.py) nests exactly those four steps inside their consumers and restores each original Variable on compilation. [CI run 39338548987](https://github.com/vanderpol/scap-ng/actions/runs/39338548987) passed **319 focused tests**, including adversarial changes to source scope and acquisition behavior. The generated review artifact contains *both* complete forms, with matching source-graph proofs.

| Metric on actual generated Apache YAML | All 19 named | 4 grouped, 15 named |
| --- | ---: | ---: |
| Top-level derived-value declarations | 19 | 15 |
| Total YAML lines | 428 | 428 |
| UTF-8 bytes | 15,596 | 16,179 |
| Native Variables reconstructed | 19 | 19 |
| Original Test/command semantics changed | No | No |

**Decision: do not automatically adopt this grouping as cleaner authoring.** It saves four *top-level names*, but no lines, and adds 583 bytes by nesting metadata. It may be useful as a collapsible graphical *presentation*, but that requires an actual comprehension study and avoids hiding the four downstream command-driving dependencies.

The next promising experiment is to separate compiler-owned source provenance (legacy source IDs/titles/types) from *author-edited* transformations without losing reproducibility, and then compare the complete source-linked example with a real author-facing editor. Do not count invisible/expanded declarations as eliminated work until a non-OVAL author can meaningfully navigate them.

## Independent assessment

**This is a real C authoring gain beyond `must` renaming.** A reviewer can follow a derived value into the specific command it parameterizes and then the evidence/requirement it supports. The full graph remains exactly OVAL-compatible; we didn't build a new shell collector or Set evaluator.

**Not yet sufficient:** Every one of the 19 derived values remains a separately authored step in this experiment. Four previous source-backed audit candidates may be safe to group in a UI, while four single-use steps that drive dynamic collection must **not** be casually folded away. The next change should benchmark readability of *actual* generated YAML and test carefully bounded source-preserving grouping/inline expansions. Also compare real execution outcomes on complete, empty, incomplete, error, unknown and NA evidence before making scanner-parity claims.

For source-backed **actual original OVAL 5.12.3** Set/Filter/constant authoring, use the separate [seven-Test UNIX Self-Assertion hybrid proof](C-HYBRID-MUST-OVER-ORIGINAL-OVAL-SET-2026-10-19.md). This Apache fixture is a converted STIG Assessment derived from SCAP source and is **not** one of the 20 fully native C-converted Self-Assertion Definitions; do not combine the counts.
