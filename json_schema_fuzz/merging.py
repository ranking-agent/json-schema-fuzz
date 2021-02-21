"""Merging."""
import copy
from typing import Any, Dict, List


def merge(
    schema_a: Dict[Any, Any],
    schema_b: Dict[Any, Any],
    path: List[Any] = None,
):
    """
    Merge two JSON schemas recursively

    Will raise exception for conflicting values.
    Based on: http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
    """
    if path is None:
        path = []

    # Make a copy of a so that it doesn't get modified in place
    schema_a = copy.deepcopy(schema_a)
    for key in schema_b:
        if key not in schema_a:
            schema_a[key] = schema_b[key]
            continue
        if isinstance(schema_a[key], dict) and isinstance(schema_b[key], dict):
            merge(schema_a[key], schema_b[key], path + [str(key)])
        elif schema_a[key] == schema_b[key]:
            pass  # same leaf value
        elif isinstance(schema_a[key], list) and isinstance(schema_b[key], list):
            # Append lists together
            schema_a[key].extend(schema_b[key])
        else:
            raise NotImplementedError(
                f"Conflicting key {key} encountered in path {path}")
    return schema_a
