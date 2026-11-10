# Compatibility resource name for native field-result.schema.json

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Resource URI retained for local reference continuity; only the current native wire is accepted. Legacy payloads are preserved under tests/fixtures/v04-native-results/pre-migration-schemas and immutable history, never silently migrated.

## Advanced constraints

[Local constraints](../advanced/entity-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/entity-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
