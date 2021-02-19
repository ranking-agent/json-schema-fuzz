"""Merging."""
import copy
from typing import Any, Dict, List


def merge(
    a: Dict[Any, Any],
    b: Dict[Any, Any],
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
    a = copy.deepcopy(a)
    for key in b:
        if key not in a:
            a[key] = b[key]
            continue
        if isinstance(a[key], dict) and isinstance(b[key], dict):
            merge(a[key], b[key], path + [str(key)])
        elif a[key] == b[key]:
            pass  # same leaf value
        elif isinstance(a[key], list) and isinstance(b[key], list):
            # Append lists together
            a[key].extend(b[key])
        else:
            raise NotImplementedError(
                f"Conflicting key {key} encountered in path {path}")
    return a
