# SCAP-NG 0.4.1 `for_each` Object expansion

`for_each` is an active 0.4.1 Object feature. The syntax is defined by
[`capability-common.schema.json` `foreach_binding`](../../../schema/capability-common.schema.json#/$defs/foreach_binding)
and the generated capability Object overlays. Runtime/compiler obligations are
recorded in the [native contract](../../contracts/0.4.1-foreach.md).

```yaml
shared_objects:
  source-files-object:
    object_title: Source file paths
    capability: unix.file
    filepath: {equals: /etc/passwd}

tests:
  dependent-test:
    capability: unix.file
    object:
      for_each: {item: source, in: source-files-object}
      filepath: {from: source.full_path}
```

The source is one named shared Object. The dependent Object is expanded once
per source Item, and a selector may bind from one visible Item field using the
[`foreach_selector_binding`](../../../schema/capability-common.schema.json#/$defs/foreach_selector_binding)
form. Multiple source Objects are never implicitly combined into a Cartesian
product. Chaining is admitted only when the compiler preserves lineage and
resource bounds.

Schema validation cannot resolve the source ID, verify Item field existence or
prove collection completeness. Implementations must fail closed for unresolved,
missing, multi-valued or invalid bindings and must retain source Item lineage,
status and evidence completeness in Results.
