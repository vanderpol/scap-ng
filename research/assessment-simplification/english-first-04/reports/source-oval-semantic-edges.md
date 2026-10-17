# Non-cardinality edge cases in six original OVAL STIG streams

**Research-only source inventory, no schema change.**

Source pinned to `niwc-atlantic/scap-content-library` at `8c8e5dff860af6b1290ee9273a282db24278f8d5`.
Element counts use original DISA and NIWC OVAL IDs and are unique per
package, not de-duplicated across Linux packages that reuse an identical ID.

## Distribution by author and feature family

### DISA

**criteria_operator**

| Source feature | Instances |
| --- | ---: |
| `AND (default)` | 2412 |
| `OR` | 129 |
| `AND` | 66 |

**definition_extension**

| Source feature | Instances |
| --- | ---: |
| `extend_definition` | 1267 |

**definition_negation**

| Source feature | Instances |
| --- | ---: |
| `negate` | 22 |

**object_filter**

| Source feature | Instances |
| --- | ---: |
| `exclude (default)` | 111 |
| `include` | 44 |
| `exclude` | 18 |

**object_set**

| Source feature | Instances |
| --- | ---: |
| `UNION` | 107 |
| `UNION (default)` | 50 |
| `COMPLEMENT` | 8 |

**object_variable_reference**

| Source feature | Instances |
| --- | ---: |
| `var_ref` | 111 |

**state_entity_check**

| Source feature | Instances |
| --- | ---: |
| `all` | 20 |
| `at least one` | 20 |
| `none satisfy` | 6 |

**state_operation**

| Source feature | Instances |
| --- | ---: |
| `pattern match` | 164 |
| `equals` | 153 |
| `greater than or equal` | 51 |
| `less than or equal` | 35 |
| `case insensitive equals` | 22 |
| `greater than` | 20 |
| `less than` | 12 |
| `case insensitive not equal` | 9 |
| `not equal` | 8 |

**state_var_check**

| Source feature | Instances |
| --- | ---: |
| `all` | 4 |
| `at least one` | 4 |

**state_variable_reference**

| Source feature | Instances |
| --- | ---: |
| `var_ref` | 16 |

**test_check**

| Source feature | Instances |
| --- | ---: |
| `all` | 1734 |
| `at least one` | 79 |
| `none satisfy` | 5 |

**test_existence_explicitness**

| Source feature | Instances |
| --- | ---: |
| `explicit` | 1128 |
| `default_unspecified` | 690 |

**test_state_reference**

| Source feature | Instances |
| --- | ---: |
| `with_state` | 1201 |

**variable_function**

| Source feature | Instances |
| --- | ---: |
| `variable_component` | 128 |
| `object_component` | 83 |
| `literal_component` | 35 |
| `concat` | 34 |
| `regex_capture` | 14 |
| `count` | 10 |
| `split` | 10 |
| `unique` | 6 |
| `arithmetic` | 2 |

**variable_type**

| Source feature | Instances |
| --- | ---: |
| `local_variable` | 91 |
| `constant_variable` | 30 |


### NIWC/NAVWAR

**criteria_operator**

| Source feature | Instances |
| --- | ---: |
| `AND (default)` | 142 |
| `OR` | 30 |
| `AND` | 22 |

**definition_negation**

| Source feature | Instances |
| --- | ---: |
| `negate` | 5 |

**object_filter**

| Source feature | Instances |
| --- | ---: |
| `exclude` | 41 |
| `include` | 15 |
| `exclude (default)` | 13 |

**object_set**

| Source feature | Instances |
| --- | ---: |
| `UNION` | 2 |
| `UNION (default)` | 1 |

**object_variable_reference**

| Source feature | Instances |
| --- | ---: |
| `var_ref` | 185 |

**state_check_existence**

| Source feature | Instances |
| --- | ---: |
| `none_exist` | 42 |
| `any_exist` | 31 |
| `only_one_exists` | 20 |
| `at_least_one_exists` | 11 |

**state_entity_check**

| Source feature | Instances |
| --- | ---: |
| `all` | 77 |
| `none satisfy` | 22 |
| `at least one` | 14 |
| `only one` | 2 |

**state_operation**

| Source feature | Instances |
| --- | ---: |
| `pattern match` | 142 |
| `equals` | 51 |
| `less than or equal` | 16 |
| `case insensitive equals` | 10 |
| `greater than or equal` | 9 |
| `greater than` | 7 |
| `not equal` | 5 |
| `less than` | 4 |
| `case insensitive not equal` | 3 |

**state_var_check**

| Source feature | Instances |
| --- | ---: |
| `at least one` | 9 |
| `all` | 1 |

**state_variable_reference**

| Source feature | Instances |
| --- | ---: |
| `var_ref` | 17 |

**test_check**

| Source feature | Instances |
| --- | ---: |
| `all` | 269 |
| `only one` | 32 |
| `at least one` | 21 |

**test_existence_explicitness**

| Source feature | Instances |
| --- | ---: |
| `explicit` | 304 |
| `default_unspecified` | 18 |

**test_family**

| Source feature | Instances |
| --- | ---: |
| `shellcommand_test` | 191 |

**test_state_reference**

| Source feature | Instances |
| --- | ---: |
| `with_state` | 270 |

**variable_function**

| Source feature | Instances |
| --- | ---: |
| `variable_component` | 265 |
| `literal_component` | 255 |
| `concat` | 228 |
| `object_component` | 160 |
| `regex_capture` | 113 |
| `unique` | 17 |
| `count` | 2 |
| `substring` | 2 |

**variable_type**

| Source feature | Instances |
| --- | ---: |
| `local_variable` | 367 |
| `constant_variable` | 26 |


## Interpretation and recommendation

This inventory shows **usage, not necessity**. The native grammar should
only expose a specialized keyword if a readable composition or typed capability
cannot express the actual requirement correctly. Original Test/State/Set/Variable
meaning remains an import conformance concern until equivalent lowering is proven.

A zero or low count in these six STIGs does not justify dropping an OVAL 5.12.3
feature from generic conversion: OVAL Self-Assertion and other benchmarks
can exercise it. Conversely, a feature common in inherited DISA 1.3-origin
content does not establish that it belongs in the new authoring vocabulary.

## Limits

- The six selected STIG archives are not the full 65-benchmark corpus and not the OVAL Self-Assertion test suite.
- Native 0.4 authoring is a separate 1,375-Test population; do not equate source and native counts.
- All counts derive from original XML declared attributes and IDs; defaults are labeled only where inspected.
- A State entity's operation is counted at State-element occurrence level; a repeated attribute can count multiple times within one State.
- Low-use operators may have important security consequences; no support is removed by this census.
