""" Operations on schemas """
import copy
import itertools
from typing import Any, Dict, List

from .utils import ALL_TYPES, lcm, listify


def get_from_all(
    dictionaries: List[dict],
    key,
    default=None
):
    """
    Get list of values from dictionaries.
    If it is not present in any dictionary, return the default value.
    """
    values = []
    for dictionary in dictionaries:
        value = dictionary.get(key, None)
        if value is not None:
            values.append(value)
    if len(values) > 0:
        return values
    else:
        return default


def get_index_or_default(
        given_list: list,
        index: int,
        default=None
):
    """ Get index from a list or get a default value """
    try:
        return given_list[index]
    except IndexError:
        return default


def merge_listify(values):
    """
    Merge values by converting them to lists
    and concatenating them.
    """
    output = []
    for value in values:
        if isinstance(value, list):
            output.extend(value)
        else:
            output.append(value)
    return output


def combine_anyof_lists(*values):
    """
    Merge lists of anyOf values so that they all must
    be true. This is done by merging all the permutations
    of the lists.
    """
    values = list(filter(len, values))
    if len(values) == 1:
        return values[0]

    output = []
    for anyof_permutation in itertools.product(*values):
        output.append(merge(*anyof_permutation))
    return output

# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements


def merge(
    *schemas: List[Dict[Any, Any]],
) -> Dict[Any, Any]:
    """
    Merge a list of JSON schemas recursively.

    Merging schemas here means that an instance
    must validate against all provided schemas
    in order to validate against the combined schema.

    This is equivalent to an allOf with the provided schemas.
    """

    # If there is a False, the combined schema must be false
    if any(schema is False for schema in schemas):
        return False

    # Replace True with the empty schema
    schemas = [
        {} if schema is True
        else schema
        for schema in schemas
    ]

    merged_schema = {}

    # Dictionary of properties and how
    # to merge them together
    property_merging_functions = {
        # Combinations
        "allOf": merge_listify,

        # Numbers
        "maximum": min,
        "exclusiveMaximum": min,
        "minimum": max,
        "exclusiveMinimum": max,
        "multipleOf": lcm,
        "notMultipleOf": merge_listify,

        # String
        "minLength": max,
        "maxLength": min,

        # Object
        "required": merge_listify,
        "additionalProperties": lambda values: merge(*values),

        # Array
        "contains": merge_listify,
    }

    # Process properties from dictionary
    for prop, merge_function in property_merging_functions.items():
        values = get_from_all(schemas, prop)
        if values:
            merged_schema[prop] = merge_function(values)

    # Process remaining properties that have more
    # complex merging requirements

    # When merging types use the intersection of the provided
    # lists. The only exception to this is with number because
    # number is an integer.
    type_values = get_from_all(schemas, "type")
    if type_values:
        # Convert to sets
        type_values = [set(listify(type_value)) for type_value in type_values]

        has_integer = any(
            "integer" in type_value for type_value in type_values
        )
        if has_integer:
            # Convert all numbers to integers
            for type_value in type_values:
                if "number" in type_value:
                    type_value.remove("number")
                    type_value.add("integer")

        # Merge using intersection
        merged_schema["type"] = list(
            set.intersection(*type_values)
        )

    any_of_values = get_from_all(schemas, "anyOf")
    if any_of_values:
        merged_schema["anyOf"] = combine_anyof_lists(*any_of_values)

    one_of_values = get_from_all(schemas, "oneOf")
    if one_of_values:

        # Build inverse values for all schemas provided
        inverted_oneof_values = []
        for one_of_list in one_of_values:
            inverted_oneof_values.append([
                invert(s) for s in one_of_list
            ])

        new_anyof_values = []

        # Build permutations where one value is true and the rest are false
        one_of_indexes = [range(len(v)) for v in one_of_values]
        # During this permutation, use the index provided as the one "true"
        # and have the rest of the indexes be false
        for true_indexes in itertools.product(*one_of_indexes):
            # Make a copy of the inverted one_of value
            current_permutation = copy.deepcopy(inverted_oneof_values)

            # Replace inverted values with given values at the true_indexes
            for outer_list_index, _ in enumerate(current_permutation):
                inner_list_index = true_indexes[outer_list_index]
                current_permutation[outer_list_index][inner_list_index] = \
                    one_of_values[outer_list_index][inner_list_index]

            # Merge and save
            denested_schemas = [
                subschema for outer_list in current_permutation
                for subschema in outer_list
            ]
            new_anyof_values.append(merge(*denested_schemas))

        existing_anyof = merged_schema.get("anyOf", [])
        merged_schema["anyOf"] = combine_anyof_lists(
            existing_anyof, new_anyof_values)

    properties_values = get_from_all(schemas, "properties")
    if properties_values:
        merged_schema["properties"] = {}
        all_keys = {
            key
            for d in properties_values
            for key in d.keys()
        }
        for key in all_keys:
            all_values = [d.get(key, {}) for d in properties_values]
            merged_schema["properties"][key] = merge(*all_values)

    has_duplicates_values = get_from_all(schemas, "hasDuplicates")
    if has_duplicates_values and any(has_duplicates_values):
        merged_schema["hasDuplicates"] = True

    unique_items_values = get_from_all(schemas, "uniqueItems")
    if unique_items_values and any(unique_items_values):
        merged_schema["uniqueItems"] = True

    items_values = get_from_all(schemas, "items")
    if items_values:
        if isinstance(items_values[0], list):
            largest_index = max([len(items) for items in items_values])
            merged_schema["items"] = []
            for index in range(largest_index):
                merged_schema["items"].append(
                    merge(*[
                        get_index_or_default(items, index, {})
                        for items in items_values
                    ])
                )
        else:
            merged_schema["items"] = merge(*items_values)

    return merged_schema


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

    if isinstance(schema, bool):
        return not schema

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
    if additional_properties is not None:
        inverted_schemas.append({
            "anyAdditionalProperty": invert(additional_properties),
        })

    any_additional_property = schema.get("anyAdditionalProperty", None)
    if any_additional_property is not None:
        inverted_schemas.append({
            "additionalProperties": invert(any_additional_property),
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

    unique_items = schema.get("uniqueItems", False)
    if unique_items:
        inverted_schemas.append({"hasDuplicates": True})

    has_duplicates = schema.get("hasDuplicates", False)
    if has_duplicates:
        inverted_schemas.append({"uniqueItems": True})

    # Combine all schemas together and return

    # No schemas means this will never be valid
    if len(inverted_schemas) == 0:
        return False

    # To make the output simpler use a condensed output if we
    # only generated one item
    if len(inverted_schemas) == 1:
        return inverted_schemas[0]

    return {"anyOf": inverted_schemas}
