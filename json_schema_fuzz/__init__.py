"""JSON schema fuzzer."""
import json
import math
import random
import string
from decimal import Decimal

import exrex

from .schema_operations import merge
from .utils import ALL_TYPES, listify, random_multiple_in_range

MAX_REJECTED_SAMPLES = 1000


class RejectionSamplingFailed(Exception):
    """
    Failed to generate sample that satisfies all criteria
    """


def random_integer(schema):
    """Generate random integer."""

    multiple_of = schema.get("multipleOf", Decimal(1))

    default_min = Decimal(1 * multiple_of)
    default_max = Decimal(100 * multiple_of)

    minimum = max(
        schema.get("minimum", default_min),
        schema.get("exclusiveMinimum", default_min) - 1
    )
    # Python ranges are exclusive on the maximum
    maximum = min(
        schema.get("maximum", default_max) + 1,
        schema.get("exclusiveMaximum", default_max)
    )

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
    default_min = Decimal(1)
    default_max = Decimal(100)
    decimal_digits = 4

    smallest_interval = 10 ** Decimal(-decimal_digits)

    minimum = max(
        schema.get("minimum", default_min),
        schema.get("exclusiveMinimum", default_min) - smallest_interval
    )
    maximum = min(
        schema.get("maximum", default_max),
        schema.get("exclusiveMaximum", default_max) + smallest_interval
    )
    multiple_of = schema.get("multipleOf", smallest_interval)

    not_multiple_of = schema.get("notMultipleOf", [])
    if not isinstance(not_multiple_of, list):
        not_multiple_of = [not_multiple_of]

    possible_values = list(
        multiples_in_range(
            minimum,
            maximum,
            multiple_of,
            precision=decimal_digits
        )
    )

    for _ in range(MAX_REJECTED_SAMPLES):
        value = random.choice(possible_values)

        # Verify
        is_multiple_of = [value % num == 0 for num in not_multiple_of]
        if any(is_multiple_of):
            continue
        return float(value)
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
    schema = json.loads(
        schema_str,
        parse_int=Decimal,
        parse_float=Decimal,
    )
    return generate_json(schema)


# pylint: disable=too-many-return-statements
def generate_json(schema):
    """Generate random JSON conforming to schema."""

    # Merge allOf subschemas into the base schema
    all_of = schema.get("allOf", [])
    for subschema in all_of:
        schema = merge(schema, subschema)

    if "type" in schema:
        possible_types = listify(schema["type"])
    else:
        possible_types = ALL_TYPES

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
