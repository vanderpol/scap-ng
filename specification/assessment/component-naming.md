# Named component IDs

**Status:** accepted SCAP-NG 0.3 authoring convention. This does not change the frozen 0.2 baseline.

Named internal Assessment components use meaningful lowercase kebab-case IDs ending in the component type.

| Component | Required form | Example |
| --- | --- | --- |
| Object | `<meaningful-name>-object` | `forward-zones-object` |
| State | `<meaningful-name>-state` | `root-owned-state` |
| Variable | `<meaningful-name>-variable` | `home-directories-variable` |
| Test | `<meaningful-name>-test` | `home-directory-permissions-test` |
| Input | `<meaningful-name>-input` | `minimum-password-length-input` |
| named Observation export | `<meaningful-name>-export` | `httpd-config-paths-export` |

Example:

```yaml
assessment:
  shared_objects:
    forward-zones-object:
      capability: windows.dns.zone
      select:
        zone_type: forward

  variables:
    home-directories-variable:
      ...

  tests:
    zone-signing-test:
      object: forward-zones-object
      states:
        - dnssec-enabled-state

  evaluate:
    test: zone-signing-test
```

## Rules

- Use full component words. Do not use legacy abbreviations such as `obj`, `ste`, `var`, or `tst`.
- The type suffix is part of the logical ID and appears at the **end** so repository searches such as `-object`, `-variable`, and `-test` are useful.
- The meaningful portion describes intent, not implementation mechanics, source XML IDs, hashes, or arbitrary sequence labels.
- Inline/private components do not receive artificial IDs merely to satisfy this convention.
- References use the complete component ID unchanged.
- When deterministic disambiguation is required, place the discriminator before the type: `forward-zones-2-object`, not `forward-zones-object-2`.
- A shared Object still ends in `-object`. Scope belongs to its declaration context; do not encode `shared` redundantly in the ID.
- Assessment IDs, Rule IDs, and filenames are separate concerns and are not required to mirror internal component IDs.
- Source OVAL identities remain in migration provenance rather than native IDs.

## Conversion

SCAP 1.4 conversion SHALL preserve source identity in migration evidence while emitting native names that follow this convention.

A 0.3 normalizer MAY convert older native presentation forms such as `test-example` and `state-example` to `example-test` and `example-state` when every reference can be rewritten deterministically and collision-free.

The frozen 0.2 review content is not renamed by this convention.
