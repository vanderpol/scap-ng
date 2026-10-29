# IOS XE: content defects, validator conflicts and converter limits

Investigation requested by the owner on 2026-10-29 under
[#251](https://github.com/vanderpol/scap-ng/issues/251).
[Exact original excerpts and validator diagnostics](v04-iosxe-content-investigation-20261029.json).
No source repair, schema change, validator relaxation or scanner execution.

## Source and attribution

The four reported Router NDM validation failures occur in
`U_Cisco_IOS-XE_Router_NDM_V3R5_STIG_SCAP_1-4_Benchmark-enhancedV18-signed.zip`,
NIWC revision `8c8e5dff860af6b1290ee9273a282db24278f8d5`, ZIP SHA-256
`82e2d4bf65abc53bb6da01874944c555efae51dbc98d80e6e42423d1025e7efa`.
The adjacent JSON is authoritative for the pin and individual source hashes.
All four active XCCDF automated checks point to the `-oval2.xml` component and
`oval:navy.navwar.niwcatlantic.scc.iosxe:*` Definitions/Variables. These findings
are attributable to the pinned NIWC enhanced artifact; origin in DISA's original
content has not been established. A matching Rule title or presence of another
older embedded component is not proof of that attribution.

## What the four failures establish

| Rule | Requirement | Pinned Schematron failure | Interpretation |
| --- | --- | --- | --- |
| SV-215807r1186318 | Concurrent management sessions | Integer VTY count consumed by concat | Validator/function-casting conflict; content bug not established from this failure alone |
| SV-215812r1137875 | Management information flow | Two concat expressions consume integer VTY count | Same conflict |
| SV-215833r961068 | Five-minute management inactivity timeout | Integer count consumed by concat; regex_capture consumes an int-declared text Variable | Same concat conflict plus a stronger textual-datatype content defect candidate |
| SV-215854r1156415 | At least two authentication servers | Integer VTY count consumed by concat | Same conflict |

The concat expressions use an integer count to build a regex repetition
quantifier, for example a string prefix ending in `{`, the numeric count, and a
string suffix such as `,}`. Their apparent intent is ordinary count-to-string
formatting. The pinned Schematron asserts that a Variable referenced by concat
must have `datatype="string"`, and therefore rejects these references.

However, the **same pinned OVAL schema** says in `FunctionGroup`:

> If the data being worked on is not of the correct type, a cast should be
> attempted before reporting an error. For example, if a concat function
> includes a registry component that returns an integer, then the integer
> should be cast as a string in order to work with the concat function.

Consequently, a failed assertion is certain; the conclusion that every
count-to-concat use is invalid intended OVAL behavior is not. The example names
a registry component, while the assertions restrict Variable references, so
the exact scope of permitted casting needs standards review. Do not turn an
apparent validator/specification inconsistency into an unconditional content-bug
report, or silently remove the assertion. These closures remain rejected by the
current original-source acceptance gate.

## SV-215833 has additional text/integer problems

Original Variable `...:var:21583304` is declared `datatype="int"`, commented
"Split the configuration into separate lines", and contains:

```xml
<split delimiter="\n">
  <object_component object_ref="...:obj:21583303" item_field="config_line"/>
</split>
```

Original Variable `...:var:21583307` is also declared `datatype="int"` and
captures text with `regex_capture pattern="\s+exec-(.*)"` from that Variable.
For a representative `exec-timeout 5 0` configuration line, the capture would
be `timeout 5 0`, which is not an integer. This is a constructed illustration
of the original expression, not an observed scanner result. OVAL `VariableType`
requires each returned value to comply with the declared datatype or report an
error. That gives a stronger content defect candidate than an integer count
being formatted as a string.

The split delimiter is also literally two characters, backslash and `n`
(Unicode 92, 110), not a newline character in XML. OVAL documents split as using
a delimiter string. Whether the intended source relied on scanner-specific
escape interpretation is unverified; this is an additional portability/authoring
question, not a claim of measured runtime failure.

Suggested upstream review: check the declarations of the text-bearing Variables,
the actual captured text expected by their consumers, and the delimiter's intended
lexical value. Separately resolve the concat casting/Schematron contradiction.
No candidate correction has been applied or claimed semantically equivalent.

## Other IOS XE findings are separate

| Source | Automated Rules | Current disposition |
| --- | ---: | --- |
| Router NDM enhancedV18 | 37 | 32 independently static-proved; four original validation failures above; one count-function converter limit |
| Router RTR enhancedV18 | 6 | All six independently static-proved |
| Switch NDM enhancedV6 | 37 | Foreign-namespace catalog bindings; requested Definitions are present |

Router `SV-215838r1015295`, redundant authoritative NTP sources, counts collected
`global_command` values through an int-declared `count` Variable. Its blocker is
unsupported SCAP-NG conversion of count, not an identified content defect.

All 37 Switch NDM Rules are affected by `ds:uri` entries in the SCAP namespace
instead of XML Catalog `cat:uri`; the exact Definition/component-ref chain
exists. The catalog XSD permits foreign extensions, which does not give those
entries standard catalog semantics. Its `ms.dns` Rule-ID prefix is another
provenance anomaly; IDs alone do not establish incorrect executable logic.
See the [population/catalog packet](v04-population-binding-resumption-20261029.md).

The 38 Router Rules were previously blocked by absent independent IOS XE
field crosswalks. Implementation `b70802028075850cf5f4397c50249813f86a7b14`
adds those crosswalks for unchanged approved line/global mappings. All 66 Tests
in three pinned source-component fixtures prove, six focused regressions pass,
and all 38 DRAFT authoring/program hashes retain parity. All nine exact-commit
hosted workflows pass, including **3,314 maintained tests: 3,313 passed, zero
failures/errors, one existing skip**. This does not establish scanner-runtime
equivalence or complete policy migration.
