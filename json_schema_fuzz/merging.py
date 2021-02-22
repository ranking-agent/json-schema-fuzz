"""Merging."""
import copy
from typing import Any, Dict, List


def merge(
    schema_a: Dict[Any, Any],
    schema_b: Dict[Any, Any],
    path: List[Any] = None,
    in_place: bool = False,
):
    """Merge two JSON schemas recursively."""
    if path is None:
        path = []

    if not in_place:
        # Make a copy of a so that it doesn't get modified in place
        schema_a = copy.deepcopy(schema_a)

    for key in schema_b:
        if key not in schema_a:
            schema_a[key] = schema_b[key]
            continue
        if isinstance(schema_a[key], dict) and isinstance(schema_b[key], dict):
            merge(schema_a[key], schema_b[key],
                  path=path + [str(key)],
                  in_place=True)
        elif schema_a[key] == schema_b[key]:
            pass  # same leaf value
        elif (
                isinstance(schema_a[key], list)
                and isinstance(schema_b[key], list)
        ):
            # Append lists together
            schema_a[key].extend(schema_b[key])
        else:
            raise NotImplementedError(
                f"Conflicting key {key} encountered in path {path}")
    if in_place:
        return None
    else:
        return schema_a
