from __future__ import annotations
from dev_qol_toolkit import json_utils

def test_flatten_and_unflatten_roundtrip():
    src = {"a": {"b": [1, {"c": 2}]}}
    flat = json_utils.flatten_json(src)
    assert flat == {"a.b.0": 1, "a.b.1.c": 2}
    back = json_utils.unflatten_json(flat)
    assert back == src