from tools.plan_variable_normalization import classify, projection_lowering


def projection_var(usage="single_use_object_selector", consumer_kind="object_selector"):
    return {
        "variable":"oval:test:var:1",
        "shape":"pure_object_projection",
        "root_operator":"object_component",
        "datatype":"string",
        "projection":{
            "object":"oval:test:obj:source",
            "field":"subexpression",
            "record_field":None,
            "datatype":"string",
        },
        "usage_class":usage,
        "consumers":[
            {
                "kind":consumer_kind,
                "consumer":"oval:test:obj:target",
                "entity":"path",
                "var_check":"all(default)",
                "operation":"equals(default)",
                "datatype":"string(default)",
            }
        ],
        "lineage":[
            {
                "source_object":"oval:test:obj:source",
                "field":"subexpression",
            }
        ],
    }


def test_p1_projection_lowering_is_explicit_and_preserves_consumer_semantics():
    v=projection_var()
    result=classify(v)
    assert result["disposition"]=="candidate_inline_flattened_projection"
    assert result["automatic_normalization"] is False

    lowering=result["p1_lowering"]
    assert lowering["value_source"]=={
        "projection":{
            "object":"oval:test:obj:source",
            "field":"subexpression",
        }
    }
    assert lowering["projection_datatype"]=="string"
    assert lowering["consumer"]=={
        "kind":"object_selector",
        "id":"oval:test:obj:target",
        "entity":"path",
        "operation":"equals(default)",
        "datatype":"string(default)",
        "variable_match":"all(default)",
    }
    assert lowering["required_provenance"]["source_variable_id"]=="oval:test:var:1"


def test_record_field_is_preserved_in_projection_lowering():
    v=projection_var()
    v["projection"]["field"]="record"
    v["projection"]["record_field"]="path"
    lowering=projection_lowering(v)
    assert lowering["value_source"]["projection"]=={
        "object":"oval:test:obj:source",
        "field":"record",
        "record_field":"path",
    }


def test_direct_variable_test_is_not_p1_projection_elimination():
    v=projection_var(
        usage="single_use_direct_variable_test",
        consumer_kind="direct_variable_test",
    )
    result=classify(v)
    assert result["disposition"]=="keep_named_projection_for_direct_test"
    assert result["automatic_normalization"] is False
    assert "p1_lowering" not in result


def test_variable_object_source_is_not_p1_projection_elimination():
    v=projection_var(
        usage="single_use_variable_object_source",
        consumer_kind="variable_object_source",
    )
    result=classify(v)
    assert result["disposition"]=="review_projection"
    assert result["automatic_normalization"] is False


def test_multi_use_projection_stays_named():
    v=projection_var()
    v["usage_class"]="multi_use"
    v["consumers"].append({
        "kind":"state_expected_value",
        "consumer":"oval:test:ste:2",
        "entity":"value",
        "var_check":"all(default)",
        "operation":"equals(default)",
        "datatype":"string(default)",
    })
    result=classify(v)
    assert result["disposition"]=="keep_named_projection_for_reuse"
