# Reusable observation modules for repeated authoring dataflow

**Status:** research proposal; no schema or accepted language change.

## Problem

The Apache 2.4 production content demonstrates a concentrated authoring-reuse
problem. The 22 automated Apache Server Assessments are only 1.63% of the
representative six-benchmark sample, but contain 282/451 Variables (62.53%).

Representative Rules repeat essentially the same discovery graph:

1. locate the Apache/httpd installation;
2. derive the `apachectl` command;
3. obtain `HTTPD_ROOT`;
4. obtain `SERVER_CONFIG_FILE`;
5. form the primary configuration path;
6. discover Include/IncludeOptional paths;
7. locate the httpd/apache2 executable;
8. run/interpret `DUMP_INCLUDES`;
9. derive loaded configuration-file paths;
10. merge/configure those values for the Rule-specific query.

SV-214228, SV-214268, and SV-214292 contain the same first ten discovery
Variables and the same loaded-configuration discovery chain. Their meaningful
differences begin primarily at the directive-specific query.

Copying those Objects/Variables into every standalone Assessment creates
maintenance risk without adding policy meaning.

## Full Apache corpus reuse census

Pinned Apache 2.4 UNIX Server conversion, 22 automated STIG Rule Assessments:

- **18** Variable definitions recur with identical payloads;
- those account for **233 repeated Variable occurrences**;
- **9** Object definitions recur with identical payloads;
- those account for **96 repeated Object occurrences**;
- the Apache installation-path Object appears unchanged in **22/22** Rules;
- the Apache executable-path Variable appears unchanged in **21/22** Rules;
- the main root/config/include discovery chain appears unchanged in **16/22**
  Rules;
- loaded-config discovery appears unchanged in **17/22** Rules.

This establishes a real maintenance/reuse problem rather than a hypothetical
language convenience. The repeated graph is concentrated in acquisition and
path discovery; Rule-specific directive logic varies afterward.

Census workflow:
`Apache authoring reuse research`, run `37614226049`.

## Proposed concept: source-time observation module

Add an **authoring-only reusable module** that owns acquisition/dataflow and
exports typed observations. It is not an Assessment and does not produce a
compliance truth result.

Conceptual source:

```yaml
module:
  id: scap-ng.apache.httpd.discovery
  version: 1

  # Private implementation. Current implementation could initially preserve
  # the exact converted shell/Variable graph.
  objects:
    ...
  variables:
    ...

  exports:
    httpd_executable:
      from: variable.apache-path-httpd-or-apache2
      datatype: string
      cardinality: zero_or_more

    httpd_root:
      from: variable.filepath-httpd-root
      datatype: string
      cardinality: zero_or_more

    primary_config:
      from: variable.filepath-http-conf-file
      datatype: string
      cardinality: zero_or_more

    included_configs:
      from: variable.all-included-conf-files
      datatype: string
      cardinality: zero_or_more

    loaded_configs:
      from: variable.all-loaded-configuration-filepaths
      datatype: string
      cardinality: zero_or_more
```

A consuming Assessment explicitly imports it:

```yaml
assessment:
  imports:
    apache:
      source: ../../modules/apache/httpd-discovery.module.yaml
      expected_id: scap-ng.apache.httpd.discovery
      expected_version: 1

  tests:
    keepalive:
      capability: independent.textfilecontent54
      object:
        for_each:
          item: config_path
          in: apache.primary_config
        select:
          full_path:
            from: config_path
          pattern:
            value: '^\\s*KeepAlive\\s+(.+)$'
            operation: match
            datatype: string
      ...
```

The exact syntax is deliberately provisional. The important contract is the
scope and compilation behavior.

## Scope rules

- Module internals are private.
- Consumers may reference only declared exports.
- An import is explicit and namespaced; no ambient/global Variables exist.
- Every export declares datatype and cardinality.
- Export status/completeness/provenance must be preserved.
- Imports are statically resolvable and version checked.
- Cycles are invalid.
- A module cannot change Rule selection, organizational policy, or consumer
  evaluation merely by being imported.

This follows the same principle emerging from locality research:
**containment means private scope; an explicit exported identity means reusable
scope.**

## Compilation

The first implementation should be intentionally conservative:

1. resolve the module source;
2. validate its ID/version/export contract;
3. namespace its private graph for the importing Assessment;
4. lower each export reference to the ordinary Object/Variable graph;
5. emit a self-contained compiled Assessment/package;
6. record the resolved module ID/version/content digest in build provenance.

The module therefore adds **no new scanner runtime semantics**.

A scanner does not fetch modules. A signed package remains self-contained.

### Standalone development/review

Provide a compiler/normalizer mode conceptually equivalent to:

```
scap-ng flatten assessment.yaml --output standalone.assessment.yaml
```

This materializes imported module internals into one ordinary Assessment source
file. Teams can therefore keep one-file review/debug artifacts while maintaining
the repeated discovery logic once in source.

## Why not a shared Assessment?

An Assessment produces technical truth. Apache discovery produces observations.
Using an Assessment only to transport Variables/Items would conflate:

- Assessment-result dependencies;
- authoring reuse;
- shared collection execution;
- Item materialization.

Those remain distinct problems.

Future runtime collection reuse may allow multiple module consumers to share one
collection execution, but authoring modules should not depend on that feature.
Compile-time expansion is sufficient to solve the copy/paste problem safely.

## Why exports should not expose internal Variable names

The consumer should depend on `apache.loaded_configs`, not on a chain such as
`merged-list-all-loaded-config-files-variable`.

That permits the module implementation to evolve later from shell command +
regex/concat/merge plumbing to a proven typed Apache discovery collector without
rewriting every Rule. A module-version change can make any semantic change
explicit.

## Relationship to foreach/locality

The concepts compose naturally:

- module: reuse discovery across Assessments;
- `foreach`: consume a returned multi-value observation locally;
- Test-local Object/State: keep Rule-specific acquisition/assertion beside the
  Test;
- named Variables: remain for genuinely complex Rule-local dataflow.

A likely Apache native-authoring pattern is therefore:

```
shared module -> exported config paths
              -> local foreach over paths
              -> local text/config Test
              -> local expectation
```

rather than copying a dozen Variables into every Rule.

## Guardrails

Do not introduce:

- implicit module search paths;
- mutable network imports at scanner runtime;
- unversioned imports;
- arbitrary templating/Jinja;
- module parameters that can construct executable commands from organizational
  input;
- silent merging of exports from multiple installations;
- automatic replacement of source Cartesian-product behavior with keyed joins.

The Apache source already demonstrates that multi-installation and include
semantics can matter. A reusable module must preserve those semantics unless a
separately reviewed native collector intentionally changes them.

Module extraction proof status: **passed on the pinned full Apache corpus.**

The first bounded prototype extracts 4 Objects + 11 Variables into
`scap-ng.apache.httpd.discovery`. Fifteen of the 22 Rule Assessments match the
complete module shape. All 15 flatten back to the original converted Assessment
with exact structural equality.

Only two exports are consumed outside the module in those 15 Rules:

- `httpd_executable` — 21 external references;
- `primary_and_included_configs` — 18 external references.

The prototype export surface has therefore been reduced to exactly those two.
`httpd_root` and `primary_config` remain private implementation details.

Proof workflow: `Apache authoring reuse research`, run `37614728886`.

## Shared inventory Assessment alternative

A potentially cleaner alternative is to reuse the existing Assessment artifact
rather than introduce a separate source-time `module` document type.

Conceptually:

```yaml
assessment:
  id: shared.apache.httpd.discovery
  version: 1
  mode: automated
  class: inventory
  purpose: assessment

  objects:
    # private Apache discovery acquisition
    ...

  variables:
    # private Apache discovery/dataflow
    ...

  exports:
    httpd_executable:
      variable: apache-path-httpd-or-apache2-variable
      datatype: string
      cardinality: zero_or_more

    primary_and_included_configs:
      variable: httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
      datatype: string
      cardinality: zero_or_more
```

A consumer would reference only the typed exports:

```yaml
dependencies:
  apache:
    assessment: ../../shared/apache-httpd-discovery.assessment.yaml
    expected_id: shared.apache.httpd.discovery
    expected_version: 1
    purpose: assessment

tests:
  keepalive:
    object:
      for_each:
        item: config_path
        in: apache.primary_and_included_configs
      ...
```

The existing Apache extraction proof makes this attractive: the 15-Assessment
proof class needs only two public outputs, `httpd_executable` and
`primary_and_included_configs`. The other extracted Variables remain private
implementation details.

### What would have to change

Current Assessment dependencies expose another Assessment's final technical
result. Current Item-reuse research can import collected Items from a producer
Object. Neither contract currently exports arbitrary Variable values.

Therefore this alternative requires one new concept regardless of syntax:
**typed observation exports from an Assessment**.

The contract should preserve:

- datatype and cardinality;
- value-production status, including zero values versus error/unknown;
- collection completeness inherited from source Objects;
- provenance back to producer Objects/Variables and source Items;
- same-target and binding identity;
- versioned, statically resolved export names;
- cycle detection;
- materialization/provenance sufficient for standalone consumer results.

Consumers SHALL NOT receive ambient access to the producer's internal Objects or
Variable names. Only declared exports cross the boundary.

### Result versus observation dependency

The producer's final Assessment truth and its exported observations are separate
products.

A consumer may depend on the producer result when policy/evaluation actually
needs that truth. Merely consuming `apache.primary_and_included_configs` does
not mean the consumer inherits the producer's pass/fail outcome.

This distinction avoids turning a discovery result into policy truth while still
allowing the producer to be a legitimate inventory Assessment.

### Runtime advantage

Unlike a compile-time-only module, a shared executable Assessment creates a
natural place for scanners to schedule Apache discovery once per target and
reuse the resulting observations across many Rule Assessments.

A compiler may still support flattening for standalone review/debugging, but
runtime reuse becomes an optimization of the same explicit dependency graph
rather than a separate feature.

### Current preference

This shared-Assessment alternative is now the preferred research direction over
introducing a separate module artifact **if** typed observation exports can be
specified cleanly without weakening standalone Assessment/result semantics.

The key research question is no longer whether Apache discovery is reusable; the
production proof established that. The question is whether Assessment exports
can unify:

1. source authoring reuse;
2. runtime shared acquisition/dataflow; and
3. explicit typed/provenanced observation consumption

without conflating those observations with Assessment truth.

No schema change is implied by this research note.

## Recommendation

Prototype **typed observation exports from a shared inventory Assessment** as
the first 0.3.0 reuse direction.

Apache is the proving case because the production corpus has unusually high
repetition and the extraction/re-expansion proof already establishes a bounded
shared discovery subgraph. Reuse the existing Assessment artifact if that can
cleanly carry both its own technical result and separately typed exported
observations.

Keep the source-time `module` design as a fallback if Assessment exports would
force artificial truth semantics, weaken standalone results, or otherwise make
the Assessment contract less coherent.

Before promotion:

1. define export status/cardinality/completeness/provenance semantics;
2. prototype producer and consumer syntax over the proven Apache subgraph;
3. prove flattening/re-expansion against the faithful converted Assessments;
4. prove same-target/binding and cycle rules; and
5. demonstrate that a scanner can schedule the shared producer once without
   changing consumer Test results or evidence semantics.

Runtime collection caching remains a separate optimization; the authored
dependency/export contract must be correct even when an implementation executes
the producer more than once.
