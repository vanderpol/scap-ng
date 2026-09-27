# Published NIWC SCAP 1.4 Migration Prototypes

**Iteration:** 001  
**Authoritative research source:** `niwc-atlantic/scap-content-library/Current`  
**Pinned revision:** `8c8e5dff860af6b1290ee9273a282db24278f8d5`

Only content extracted from the pinned NIWC public `Current/` publication tree may be used as real-world migration evidence in this directory.

Earlier prototypes sourced from development/experimental repositories were removed so they cannot be confused with published SCAP 1.4 evidence.

## Source requirement

Every future case SHALL record:

- NIWC repository revision;
- exact `Current/<published-zip>` path;
- SHA-256 of the published ZIP;
- internal datastream/component identity;
- XCCDF Rule identifier;
- OVAL Definition identifier(s);
- source-component digest where practical.

A case is not admitted into this corpus merely because an equivalent-looking definition exists elsewhere.

## Workflow

```text
NIWC Current signed ZIP
        |
        v
safe extraction + component inventory
        |
        v
faithful SCAP 1.4 semantic IR
        |
        +----------------------+
        |                      |
        v                      v
original NG YAML      Ansible-inspired NG YAML
        \                      /
         \                    /
          v                  v
            canonical NG semantics
```

Both YAML forms are generated/rendered from the same semantic IR.

## Current status

The corpus is intentionally empty after the evidence-boundary reset. It will be repopulated from the pinned NIWC public corpus using the automated corpus mining/conversion tooling.
