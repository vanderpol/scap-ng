from tools.value_projection_semantics_probe import (
    ERROR,
    OK,
    oval_object_component,
    inline_projection,
    prove_inline_projection_equivalence,
    same_item_binding_projection,
)


def test_zero_source_items_is_error():
    assert oval_object_component([], "path") == {"status": ERROR, "values": []}


def test_missing_item_field_is_error_even_when_other_items_have_it():
    items=[
        {"path":["/a"]},
        {"name":["b"]},
    ]
    assert oval_object_component(items, "path") == {"status": ERROR, "values": []}


def test_projection_flattens_values_without_retaining_row_identity():
    items=[
        {"path":["/a","/b"]},
        {"path":["/c"]},
    ]
    source=oval_object_component(items, "path")
    assert source == {"status": OK, "values":["/a","/b","/c"]}
    bound=same_item_binding_projection(items, "path")
    assert bound == [
        {"source_item":0,"value":"/a"},
        {"source_item":0,"value":"/b"},
        {"source_item":1,"value":"/c"},
    ]


def test_record_field_projection_and_missing_record_field():
    items=[
        {"record":[{"name":["alpha"],"value":["1","2"]}]},
        {"record":[{"name":["beta"],"value":["3"]}]},
    ]
    assert oval_object_component(items,"record","value") == {
        "status":OK,"values":["1","2","3"]
    }
    broken=[
        {"record":[{"value":["1"]}]},
        {"record":[{"name":["beta"]}]},
    ]
    assert oval_object_component(broken,"record","value") == {
        "status":ERROR,"values":[]
    }


def test_candidate_inline_projection_is_semantically_identical():
    cases=[
        ([], "path", None),
        ([{"path":["/a"]}], "path", None),
        ([{"path":["/a"]},{"path":["/b","/c"]}], "path", None),
        ([{"path":["/a"]},{"name":["x"]}], "path", None),
        ([{"record":[{"field":["x","y"]}]}], "record", "field"),
    ]
    for items,field,record_field in cases:
        proof=prove_inline_projection_equivalence(items,field,record_field)
        assert proof["equivalent"] is True
        assert proof["source"] == inline_projection(items,field,record_field)
