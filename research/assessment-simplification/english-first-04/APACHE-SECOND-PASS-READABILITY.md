# Apache 0.4 — second-pass readability limit: why *not* inline everything

**18 October 2026. Research issues [#235](https://github.com/vanderpol/scap-ng/issues/235), [#227](https://github.com/vanderpol/scap-ng/issues/227).** Reviewed the entire Apache UNIX SV-214228 authoring source, not a fabricated miniature. This is an *authorability* finding, **not a native language adoption, schema update, compiler run, or OVAL result-equivalence claim**.

## A concrete limit discovered

The [complete English-first source](FULL-05-apache.md) contains **18 named Variables** and **19 Variable-to-Variable source references**. Their reference counts are:

| Metric | Actual source observation |
| --- | ---: |
| Variables referenced exactly once | **13** |
| Variables reused at least twice | **5** |
| Longest named-Variable prerequisite chain | **9 nodes** |
| Distinct source Objects used by both discovery paths | **one original process-command collection** |
| Identical named-Variable dependencies across the main/include and actually-loaded paths | **none** |

The five multiply referenced *meaningful sharing points* are:

- `apache-base-install-directories-unix-variable` — base installation directories;
- `filepath-httpd-root-variable` — parsed HTTPD_ROOT directory;
- `filepath-http-conf-file-variable` — resolved main config path;
- `httpd-conf-merged-included-conf-files-from-include-refernces-in-variable` — main plus Include/IncludeOptional paths;
- `merged-list-all-loaded-config-files-variable` — separate, reported **actually loaded** configuration paths.

**The two populations cannot be merged merely because both describe config files.** One follows the configured main file and include references; one is obtained through a different shell query for loaded files. Their membership, availability, source provenance and error semantics are not proved identical.

## Measured comparison of three degrees of inlining

I mechanically substituted existing `concat` expression *text* at its single referencing command site, without editing shell literals, regex expressions, flags or Test predicates. Reversing the replacements using the saved original Variable declarations recreated the complete research YAML exactly. **The substitutions are not standalone, self-describing, typed, scanner-equivalent 0.4 source**.

| Research variant | Named Variables | Non-comment YAML lines | Maximum indentation | Source-review consequence |
| --- | ---: | ---: | ---: | --- |
| Full English-first Apache | 18 | 335 | Not used as a winner metric | Full 18-step source graph; all named expression metadata available |
| [Four final single-use check commands inline](FULL-05-apache-INLINE-COMMAND-CANDIDATE.md) | **14** | **310** | **22 spaces** | Removes four hops from final `collect.command` into separately named, single-use `concat` expressions |
| **Aggressive follow-on trial**, *not published as another 300-line alternate* | **11** | **322** | **26 spaces** | Three deeper nested `collect.command` expressions save names but **add 12 lines**, expand deep source contexts, and discard three more titled Variable declarations |

The aggressive trial inlined exactly these **additional** original single-use command names into their parent inline-shellcommand Objects: `httpd-root-apachectl-v-variable`, `server-config-file-apachectl-v-variable`, `command-gather-httpd-apache2-list-all-loaded-configuration-files-variable`. Its 11-name result was checked reversible using a separately retained edit recipe, **not** compiled or manually accepted. This is a negative control: *fewer Variables can make the full document longer and more nested*.

**Conclusion for this iteration:** Do **not** use “inline every single-use Variable” as the 0.4 design rule. Keeping a named derived source may be more intelligible than expanding it inside an already deeply nested `regex_capture → values → object → collect.command`.

## Two source-backed, independent paths the auditor must be able to explain

This is a **navigation map**, not replacement syntax or an abbreviated claim of exact command behavior:

```text
                                   Original Apache process-command collection
                                      /                               \
MAIN CONFIG + INCLUDE PATHS                                  ACTUALLY LOADED FILES
  installation base (shared Variable)                           apache executable path
  ├─ read HTTPD_ROOT via apachectl -V                            query Apache loaded files
  └─ read SERVER_CONFIG_FILE via apachectl -V                    regex-extract loaded file paths
  resolve main configuration path (shared Variable)              unique + merge paths (shared Variable)
  read Include/IncludeOptional references                         |
  merge/include main configuration paths (shared Variable)         |
           |                                                      |
      +----+------------------+                           +-------+------------------+
      |                       |                           |                          |
  KeepAlive On          MaxKeepAliveRequests>=100    when-present KeepAlive On    when-present MaxKeepAliveRequests>=100
```

That diagram only labels the *source-derived dependencies*; it does not specify new collector behavior. The original four Test predicates distinguish mandatory main/Include checks and loaded-file checks using `when_present_...` field comparison. All four Tests remain under the exact `evaluate.all_of` graph.

The [complete Apache authorability challenge](APACHE-COMPOSITION-AUTHORING-CHALLENGE.md) asks auditors to identify both paths, the actual original shell commands, Item versus field absence and the provenance of each derived file list. **A successful reviewer should be able to explain the two paths directly from authored source, not be forced to trust this prose map.**

## A practical 0.4 language goal, avoiding an unproved `pipe` or `derive`

A winning *single authoring language* should allow:

1. **Clearly named, reusable collection and derived-value outputs** where a value fans out to multiple checks or another source operation. Preserve both Apache config-population identities.
2. **Local expressions at their sole meaningful use**, but only where colocating them improves comprehension instead of burying them under nested Object/record/value machinery.
3. **Explicit type, cardinality, transformation and status propagation** along source edges. No implicit per-file loop, string/list join, shell interpolation or fallback-to-empty.
4. **Separation of source/dataflow shape from what makes a Test pass**. The final four checks must be readable without scanning 18 names; their requirements must still retain exactly what happens for no Item, missing field, incomplete, unknown, error and optional matches.
5. **Fully reversible provenance or an explicit *non-lossless* authoring decision.** The inline research examples omit `title/kind/datatype` declarations; we cannot call them canonical-lossless without deciding how source provenance is preserved.

The **next high-value comparison** is not a fourth enormous YAML dialect. Compare a *typed, explicitly labeled reusable collection stage* with the existing named Variable+Object graph and an editor showing an expanded source chain. Use the existing full Apache content as the truth source and score new auditors on predicting source populations and failure outcomes. If a clearer source view cannot be represented without hiding semantics, retain the existing graph and simplify authoring through guided composition.

## Decision status

- **Survives as a research candidate:** Four leaf command expressions inlined into the checks (14 Variables), pending standalone metadata, type and result preservation; reviewer comprehension is untested.
- **Rejected as a blanket rule:** All-single-use inlining; the three additional deep source commands **increase YAML and nesting** while removing names.
- **Unresolved, do not silently decide:** Whether inline `concat` is admitted as a `collect.command` value, whether per-collection dependency stages become first-class, how source variable declarations/provenance are recovered, and exact zero/one/many/error results.
- **Still required:** A concrete *independent first-read authoring review*, source-backed reversible lowering and differential semantic tests **before** promoting any candidate.

No normative 0.4 change, broad compiler assignment, new scanner feature or 65-STIG job follows from this document.
