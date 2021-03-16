"""JSON schema fuzzer."""
import random
import string
from decimal import Decimal

import exrex

from .schema_operations import merge
from .utils import (ALL_TYPES, custom_json_loads, listify,
                    random_multiple_in_range)

MAX_REJECTED_SAMPLES = 1000


class RejectionSamplingFailed(Exception):
    """
    Failed to generate sample that satisfies all criteria
    """


def get_minimum_maximum(schema, schema_type):
    """
    Pull minimum and maximum from a schema

    Returns None if the value is not provided
    """

    if schema_type == "integer":
        exclusive_added_value = 1
    else:
        exclusive_added_value = 0

    minimum = schema.get("minimum", None)
    exclusive_minimum = schema.get("exclusiveMinimum", None)
    minimum = max(
        minimum if minimum is not None else Decimal("-Infinity"),
        exclusive_minimum + exclusive_added_value if
        exclusive_minimum is not None else Decimal("-Infinity")
    )
    if minimum == Decimal("-Infinity"):
        minimum = None

    maximum = schema.get("maximum", None)
    exclusive_maximum = schema.get("exclusiveMaximum", None)
    maximum = min(
        maximum if maximum is not None else Decimal("Infinity"),
        exclusive_maximum - exclusive_added_value if
        exclusive_maximum is not None else Decimal("Infinity")
    )
    if maximum == Decimal("Infinity"):
        maximum = None

    return minimum, maximum


def random_integer(schema):
    """Generate random integer."""

    multiple_of = schema.get("multipleOf", Decimal(1))

    minimum, maximum = get_minimum_maximum(schema, "integer")

    default_range = 100 * multiple_of

    if minimum is not None and maximum is None:
        maximum = minimum + default_range
    elif maximum is not None and minimum is None:
        minimum = maximum - default_range
    elif minimum is None and maximum is None:
        # Use default range
        minimum = -default_range
        maximum = default_range

    minimum, maximum = int(minimum), int(maximum)

    not_multiple_of = schema.get("notMultipleOf", [])
    if not isinstance(not_multiple_of, list):
        not_multiple_of = [not_multiple_of]

    for _ in range(MAX_REJECTED_SAMPLES):
        # Generate new value
        value = random_multiple_in_range(
            minimum,
            maximum,
            multiple_of
        )

        # Verify
        is_multiple_of = [value % num == 0 for num in not_multiple_of]
        if any(is_multiple_of):
            continue
        return int(value)
    raise RejectionSamplingFailed()


def random_number(schema):
    """Generate random number."""

    minimum, maximum = get_minimum_maximum(schema, "number")

    multiple_of = schema.get("multipleOf", None)

    # Sample continuously if not given multiple_of
    if not multiple_of:
        if minimum is not None and maximum is None:
            maximum = minimum + 100
        elif maximum is not None and minimum is None:
            minimum = maximum - 100
        elif minimum is None and maximum is None:
            # Use defualt range
            minimum = -100
            maximum = 100

        # We don't have to worry about notMultipleOf
        # because it's a continuous sample (infintesimal odds)
        return Decimal(
            random.uniform(float(minimum), float(maximum))
        )

    default_range = 100 * multiple_of

    # Use multiple_of to sample
    if minimum is not None and maximum is None:
        maximum = minimum + default_range
    elif maximum is not None and minimum is None:
        minimum = maximum - default_range
    elif minimum is None and maximum is None:
        # Use defualt range
        maximum = default_range
        minimum = -default_range

    not_multiple_of = schema.get("notMultipleOf", [])
    if not isinstance(not_multiple_of, list):
        not_multiple_of = [not_multiple_of]

    for _ in range(MAX_REJECTED_SAMPLES):
        value = random_multiple_in_range(
            minimum,
            maximum,
            multiple_of,
        )

        # Verify
        is_multiple_of = [value % num == 0 for num in not_multiple_of]
        if any(is_multiple_of):
            continue
        return value
    raise RejectionSamplingFailed()


def random_object(schema):
    """Generate random JSON object."""

    properties = schema.get("properties", dict())
    required = schema.get("required", [])

    object = dict()
    for key, value in properties.items():
        if key in required or random.choice([True, False]):
            object[key] = generate_json(value)
    return object


def random_boolean(schema):
    """Generate random JSON boolean."""
    return random.choice([True, False])


def random_string(schema):
    """Generate random string."""

    min_length = schema.get("minLength", 0)
    max_length = schema.get("maxLength", min_length + 50)

    for _ in range(MAX_REJECTED_SAMPLES):
        # Generate new value
        pattern = schema.get("pattern", None)
        if pattern is not None:
            # Use exrex to generate pattern
            value = exrex.getone(pattern)
        else:
            # Use random.choices
            lowercase_letters = string.ascii_lowercase
            length = random.randint(min_length, max_length)
            value = "".join(random.choices(lowercase_letters, k=length))

        if min_length <= len(value) and len(value) <= max_length:
            return value
    raise RejectionSamplingFailed()


def random_array(schema):
    """Generate random array.
    Default min and max length are set to 0 and 10, respectively.
    """
    items = schema.get("items", {})
    maxitems = schema.get("maxItems", 10)
    minitems = schema.get("minItems", 0)

    length = random.randint(minitems, maxitems)
    output_array = [generate_json(items) for _ in range(length)]
    return output_array


def generate_json_from_string(schema_str):
    """ Parse schema from string and generate random JSON data """
    schema = custom_json_loads(schema_str)
    return generate_json(schema)


# pylint: disable=too-many-return-statements
def generate_json(schema):
    """Generate random JSON conforming to schema."""

    # Merge allOf subschemas into the base schema
    all_of = schema.get("allOf", [])
    for subschema in all_of:
        schema = merge(schema, subschema)

    possible_types = listify(schema.get("type", ALL_TYPES))

    instance_type = random.choice(possible_types)

    if instance_type == "number":
        return random_number(schema)
    elif instance_type == "integer":
        return random_integer(schema)
    elif instance_type == "object":
        return random_object(schema)
    elif instance_type == "boolean":
        return random_boolean(schema)
    elif instance_type == "string":
        return random_string(schema)
    elif instance_type == "array":
        return random_array(schema)
    elif instance_type == "null":
        return None
    else:
        raise NotImplementedError()
