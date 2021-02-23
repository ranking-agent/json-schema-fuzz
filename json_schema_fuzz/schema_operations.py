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


ALL_TYPES = ["object", "number", "array", "string", "null", "boolean"]


def invert(
    schema: Dict,
):
    """
    Return the inverse of a schema.

    The inverse is a a schema that will validate true
    for anything that validates false on the original
    schema.
    """
    inverted_schemas = []

    type = schema.get("type", None)
    if type:
        inverted_schemas.append({"type": ALL_TYPES - type})

    # Combinations

    all_of = schema.get("allOf", None)
    if all_of:
        inverted_schemas.append({"anyOf": [invert(s) for s in all_of]})

    any_of = schema.get("anyOf", None)
    if any_of:
        inverted_schemas.append({"allOf": [invert(s) for s in any_of]})

    one_of = schema.get("oneOf", None)
    if one_of:
        # !(a XOR b) == (!a AND !b) OR (a AND b)
        inverted_schemas.append({
            "anyOf": [
                {
                    "allOf": [invert(s) for s in one_of]
                }, {
                    "allOf": one_of
                }
            ]
        })

    # Strings

    min_length = schema.get("minLength", None)
    if min_length:
        inverted_schemas.append({'maxLength': min_length - 1})

    max_length = schema.get("maxLength", None)
    if max_length:
        inverted_schemas.append({'minLength': max_length + 1})

    pattern = schema.get("pattern", None)
    if pattern:
        # Use a tempered greedy token that will match anything not matched
        # by the original regex
        # https://stackoverflow.com/questions/164414/how-to-inverse-match-with-regex
        inverted_schemas.append({'pattern': f"^(?:(?!{pattern}).)*$"})

    # Numbers

    multiple_of = schema.get("multipleOf", None)
    if multiple_of:
        inverted_schemas.append({"notMultipleOf": multiple_of})

    minimum = schema.get("minimum", None)
    if minimum:
        inverted_schemas.append({"exclusiveMaximum": minimum})
    maximum = schema.get("maximum", None)
    if maximum:
        inverted_schemas.append({"exclusiveMinimum": maximum})
    exclusive_minimum = schema.get("exclusiveMinimum", None)
    if exclusive_minimum:
        inverted_schemas.append({"maximum": exclusive_minimum})
    exclusive_maximum = schema.get("exclusiveMaximum", None)
    if exclusive_maximum:
        inverted_schemas.append({"minimum": exclusive_maximum})

    # Objects

    properties = schema.get("properties", None)
    if properties:
        inverted_schemas.append({
            "properties": {k: invert(v) for k, v in properties.items()},
            "anyOf": [{"required": [k]} for k in properties.keys()],
        })

    required = schema.get("required", None)
    if required:
        inverted_schemas.append({
            "anyOf": [{"disallow": [k] for k in properties.keys()}],
        })

    additional_properties = schema.get("additionalProperties", None)
    if additional_properties:
        inverted_schemas.append({
            "anyAdditionalProperties": invert(additional_properties),
        })

    # Arrays

    items = schema.get("items", None)
    if items:
        if isinstance(items, list):
            item_conditions = []
            for index, item_schema in enumerate(items):
                item_conditions.append({
                    "items": [{}] * index + [invert(item_schema)]
                })
            inverted_schemas.append(
                {"anyOf": item_conditions + [{"maxItems": len(items)}]})
        else:
            inverted_schemas.append({"contains": invert(items)})

    contains = schema.get("contains", None)
    if contains:
        inverted_schemas.append({"items": invert(contains)})

    unique_items = schema.get("uniqueItems", None)
    if unique_items:
        inverted_schemas.append({"hasDuplicates": unique_items})

    # Combine all schemas together and return

    combined_schema = {}
    for inverted_schema in inverted_schemas:
        merge(combined_schema, inverted_schema, in_place=True)
    return combined_schema
