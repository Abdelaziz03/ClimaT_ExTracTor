from colpali_2_0.extract import RawElement, _assign_hierarchy


def test_assign_hierarchy_selects_smallest_container() -> None:
    elements = [
        RawElement("outer", 0, "box", (0, 0, 100, 100)),
        RawElement("middle", 0, "box", (10, 10, 90, 90)),
        RawElement("inner", 0, "text", (20, 20, 30, 30), text="hello"),
    ]

    hierarchy = _assign_hierarchy(elements)
    assert hierarchy["inner"]["parent_id"] == "middle"
    assert "inner" in hierarchy["middle"]["children_ids"]
