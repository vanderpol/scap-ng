# Draft Test reported elements 0.4.0

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Reporting selection only. Authors SHALL select all, compared, or an explicit field list. This is not redaction or an Object selector.

## Advanced constraints

[Local constraints](../advanced/reported-elements.md) and [complete JSON Schema](../../../proposed-schema/documentation/reported-elements.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
