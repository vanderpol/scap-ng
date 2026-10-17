# Apache: make 18 Variables understandable before replacing them

**October 16, 2026 · Design experiment for [#235](https://github.com/vanderpol/scap-ng/issues/235); not an approved capability or source-equivalent Assessment.** Derived from the complete [Apache UNIX SV-214228 source and proposed authoring comparison](FULL-05-apache.md). The six stage groupings below are a *human reading map* of the source graph, not a claim that the commands are interchangeable.

## The real dependency graph, grouped by purpose

The source Assessment has **18 command-building/local Variables and four Tests**. Those Variables are not 18 independent compliance conditions. They belong to two different configuration-file discovery paths, followed by two directive checks in each path.

| Stage | What the auditor needs to understand | Variables |
| --- | --- | ---: |
| 1. Find the installation | Discover Apache base directories and an executable path | 2 |
| 2. Locate the main configuration | Use \`apachectl -V\` to resolve \`HTTPD_ROOT\`, \`SERVER_CONFIG_FILE\` and their joined path | 5 |
| 3. Resolve *declared* includes | Find and combine \`Include\` / \`IncludeOptional\` references with the main configuration path | 4 |
| 4. Discover *loaded* files | Run the Apache executable with \`-t -D DUMP_INCLUDES\`, extract and combine reported paths | 3 |
| 5. Test \`KeepAlive\` | Build two separate directive searches, one per file-discovery path | 2 |
| 6. Test \`MaxKeepAliveRequests\` | Build two separate directive searches, one per file-discovery path | 2 |
| **Total** | **Six understandable stages, still 18 exact source Variables** | **18** |

\`\`\`mermaid
flowchart TD
    A["Discover Apache installation paths"] --> B["apachectl -V: main configuration path"]
    A --> C["Apache executable: DUMP_INCLUDES"]
    B --> D["Main file + declared Include paths"]
    C --> E["Files reported as loaded"]
    D --> F["Required KeepAlive / MaxKeepAliveRequests checks"]
    E --> G["Additional loaded-file KeepAlive / MaxKeepAliveRequests checks"]
    F --> H["All four checks required"]
    G --> H
\`\`\`

The two branches are **not interchangeable**. A source with a configured \`IncludeOptional\` or conditional include can have different *declared* paths from *actually loaded* paths. Collapsing them into "read the Apache config" could erase source intent, especially on failure and partial collection.

## Four original checks, not one simplified claim

These are the four actual source Tests, summarized without changing their composition:

| Test | File path branch | Requirement |
| --- | --- | --- |
| Required \`KeepAlive\` | Main + declared includes | A qualifying directive must be found and match \`On\` |
| Additional \`KeepAlive\` | Loaded files | Field evaluation is *when present*; missing-value behavior remains distinct |
| Required \`MaxKeepAliveRequests\` | Main + declared includes | Required numeric directive check |
| Additional \`MaxKeepAliveRequests\` | Loaded files | Separate check over additional loaded files |

The complete source defines the exact stdout patterns, numeric bounds, Item/field existence and status flags; **read the [full Apache comparison](FULL-05-apache.md) for those conditions**. It combines all four with \`evaluate.all_of\`. The source's title about limiting simultaneous session requests must not be interpreted as permission to simplify this to a single effective-value check.

## The first *real* redesign opportunity

A reusable native Apache collector could produce two explicitly named sets of file occurrences—**declared configuration references** and **runtime-loaded files**—without the author writing command-string construction chains. It must *not* hide their difference.

**Conceptual typed-source shape (not executable; new capabilities and modes require specification):**

\`\`\`yaml
sources:
  apache-installations:
    inspect: apache.installations

  declared-directives:
    inspect: apache.configuration
    collect:
      installations_from: apache-installations
      file_scope: main_and_declared_includes
      view: raw_occurrences

  loaded-directives:
    inspect: apache.configuration
    collect:
      installations_from: apache-installations
      file_scope: runtime_loaded
      view: raw_occurrences

checks:
  required-keepalive:
    from: declared-directives
    require: ... # exact original existence, line/pattern and match semantics

  additional-keepalive:
    from: loaded-directives
    require: ... # original when-present semantics
\`\`\`

This follows the *same* \`sources → checks → evaluate\` grammar being investigated elsewhere. The two other \`MaxKeepAliveRequests\` checks, collection failure flags and full metadata are deliberately not invented in this conceptual sketch. \`installations_from\`, \`file_scope\` and \`view\` are **potential capability parameters**, not approved 0.4 vocabulary.

## The collector contract is the hard part

A source-backed implementation and comparison must establish:

1. Which Apache installation(s), executable(s), roots and main configuration files are discovered—including none, multiple installations, and incompatible binaries.
2. How \`Include\`, \`IncludeOptional\`, globs, relative paths, recursion, cycles and conditions are interpreted; distinguish textual include references from runtime-loaded paths.
3. Whether it exposes **raw line occurrences** or effective directive values, with file path, line number, source branch, order and include ancestry. A parsed effective value cannot silently replace the source's \`grep\` behavior.
4. What happens on missing files, malformed configuration, permission errors, command exit/stderr and partially collected results. Preserve failure status and evidence, not just pass/fail.
5. Whether the four original Test/State cardinalities and full \`all_of\` result match for no/multiple records, mixed values and the six technical outcomes.

**Fail-closed criterion:** if any branch cannot reproduce original collection or evidence semantics, use the existing generic shellcommand/Variable path for that Assessment. A shorter file alone is not a compatibility argument.

## What this iteration improves, and what it does not

- **Improves understanding now:** 18 Variables can be understood as *two parallel discovery paths → four directive checks*; the reader sees why there are four checks, rather than assuming redundant tests.
- **Could reduce authoring complexity later:** a rigorously implemented native Apache capability might replace command-building steps with two reusable, observable collections.
- **Not yet proven:** numerical reduction in source operations, full scanner outcomes, evidence fidelity, runtime savings or human authoring results. Those require a native implementation and differential tests.

**Next proof target:** build the explicit branch-level provenance report against the pinned [SV-214228 YAML](FULL-05-apache.md), then compare an Apache collector against the exact four command-based source checks. Do *not* revise 0.4 normative schemas or the original research examples based on this diagram alone.
