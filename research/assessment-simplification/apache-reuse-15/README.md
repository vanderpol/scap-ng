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

Module extraction proof status: **executable research prototype added; full-corpus run pending.**

## Recommendation

Prototype **source-time observation modules with typed exports** for 0.3.0
research.

Use Apache discovery as the first proving case because it has unusually high
repetition and Variable complexity. Keep runtime shared-collection execution as
a separate later optimization.

Before promotion, run the complete 22-Assessment Apache corpus through a module
extraction/re-expansion proof and require the flattened graph to match the
faithful source graph for the bounded helper subgraph.
