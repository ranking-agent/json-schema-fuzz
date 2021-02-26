""" Operations on schemas """
import copy
import itertools
import math
from typing import Any, Dict, List


def remove_allOf(schema):
    """
    For a given schema merge in allOf
    until it is removed entirely
    """

    while True:
        all_of = schema.get("allOf", [])
        if len(all_of) == 0:
            break
        for subschema in all_of:
            merge(schema, subschema, in_place=True)

    # Remove allOf now that it is empty
    schema.pop("allOf", None)


def lcm(numbers):
    """
    Find least common multiple of a list of numbers

    TODO replace with math.lcm after updating to Python 3.9
    """
    product = 1
    gcd = 1
    for num in numbers:
        gcd = math.gcd(gcd, num)
        product *= num
    return product // gcd


def get_val_or_none(dictionaries, key):
    """
    Get list of values from dictionaries.
    If it is not present in any dictionary, return None.
    """
    values = []
    for dictionary in dictionaries:
        value = dictionary.get(key, None)
        if value:
            values.append(value)
    if len(values) > 0:
        return values
    else:
        return None


def merge(
    *schemas: List[Dict[Any, Any]],
) -> Dict[Any, Any]:
    """
    Merge a list of JSON schemas recursively.

    Merging schemas here means that all schemas
    must be true for result schema to be true.
    """

    merged_schema = {}

    # Combinations

    all_of_values = get_val_or_none(schemas, "allOf")
    if all_of_values:
        merged_schema["allOf"] = list(
            itertools.chain(*all_of_values)
        )

    any_of_values = get_val_or_none(schemas, "anyOf")
    if any_of_values:
        merged_schema["anyOf"] = []
        for anyof_permutation in itertools.product(*any_of_values):
            merged_schema["anyOf"].append(merge(*anyof_permutation))

    # Numbers

    minimum_values = get_val_or_none(schemas, "minimum")
    if minimum_values:
        merged_schema["minimum"] = max(minimum_values)
    exclusive_minimum_values = get_val_or_none(schemas, "exclusiveMinimum")
    if exclusive_minimum_values:
        merged_schema["exclusiveMinimum"] = max(exclusive_minimum_values)

    maximum_values = get_val_or_none(schemas, "maximum")
    if maximum_values:
        merged_schema["maximum"] = min(maximum_values)
    exclusive_maximum_values = get_val_or_none(schemas, "exclusiveMaximum")
    if exclusive_maximum_values:
        merged_schema["exclusiveMaximum"] = min(exclusive_maximum_values)

    multiple_of_values = get_val_or_none(schemas, "multipleOf")
    if multiple_of_values:
        merged_schema["multipleOf"] = lcm(multiple_of_values)

    not_multiple_of_values = get_val_or_none(schemas, "notMultipleOf")
    if not_multiple_of_values:
        merged_schema["notMultipleOf"] = []
        # notMultipleOf values might be list or number
        for not_multiple_of_value in not_multiple_of_values:
            if isinstance(not_multiple_of_value, list):
                merged_schema["notMultipleOf"].extend(not_multiple_of_value)
            else:
                merged_schema["notMultipleOf"].append(not_multiple_of_value)

    # Strings

    min_length_values = get_val_or_none(schemas, "minLength")
    if min_length_values:
        merged_schema["minLength"] = max(min_length_values)

    max_length_values = get_val_or_none(schemas, "maxLength")
    if max_length_values:
        merged_schema["maxLength"] = min(max_length_values)

    return merged_schema


ALL_TYPES = ["object", "number", "array", "string", "null", "boolean"]


# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
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
                {"anyOf": item_conditions + [{"maxItems": len(items) - 1}]})
        else:
            inverted_schemas.append({"contains": invert(items)})

    contains = schema.get("contains", None)
    if contains:
        inverted_schemas.append({"items": invert(contains)})

    unique_items = schema.get("uniqueItems", None)
    if unique_items:
        inverted_schemas.append({"hasDuplicates": unique_items})

    # Combine all schemas together and return

    # To make the output simpler use a condensed output if we
    # only generated one item
    if len(inverted_schemas) == 1:
        return inverted_schemas[0]
    else:
        return {"anyOf": inverted_schemas}
