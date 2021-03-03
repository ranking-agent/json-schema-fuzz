"""JSON schema fuzzer."""
from decimal import Decimal
import json
import random
import string

import exrex

from .schema_operations import merge

MAX_REJECTED_SAMPLES = 1000


class RejectionSamplingFailed(Exception):
    """
    Failed to generate sample that satisfies all criteria
    """


def listify(value):
    """ If value is not a list wrap it in a list """
    if isinstance(value, list):
        return value
    else:
        return [value]


def random_integer(schema):
    """Generate random integer."""

    multiple_of = schema.get("multipleOf", Decimal(1))

    default_min = Decimal(1 * multiple_of)
    default_max = Decimal(100 * multiple_of)

    minimum = max(
        schema.get("minimum", default_min),
        schema.get("exclusiveMinimum", default_min) + 1
    )
    maximum = min(
        schema.get("maximum", default_max),
        schema.get("exclusiveMaximum", default_max) - 1
    )

    not_multiple_of = schema.get("notMultipleOf", [])
    if not isinstance(not_multiple_of, list):
        not_multiple_of = [not_multiple_of]

    for _ in range(MAX_REJECTED_SAMPLES):
        # Generate new value
        value = random.randint(minimum, maximum)

        # Verify
        if value % multiple_of != 0:
            continue
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

    smallest_interval = Decimal(10 ** -decimal_digits)

    minimum = max(
        schema.get("minimum", default_min),
        schema.get("exclusiveMinimum", default_min) - smallest_interval
    )
    maximum = min(
        schema.get("maximum", default_max),
        schema.get("exclusiveMaximum", default_max) + smallest_interval
    )
    multiple_of = schema.get("multipleOf", None)

    not_multiple_of = schema.get("notMultipleOf", [])
    if not isinstance(not_multiple_of, list):
        not_multiple_of = [not_multiple_of]

    for _ in range(MAX_REJECTED_SAMPLES):
        float_value = random.uniform(float(minimum), float(maximum))
        value = Decimal(
            str(round(float_value, decimal_digits))
        )

        # Verify
        if multiple_of and value % multiple_of != 0:
            continue
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
    """ Parse schema from string and gneerate random JSON data """
    schema = json.loads(
        schema_str,
        parse_int=Decimal,
        parse_float=Decimal,
    )
    return generate_json(schema)


def generate_json(schema):
    """Generate random JSON conforming to schema."""

    # Merge allOf subschemas into the base schema
    all_of = schema.get("allOf", [])
    for subschema in all_of:
        schema = merge(schema, subschema)

    if "type" not in schema:
        raise NotImplementedError(f"No type available in schema: {schema}")
    possible_types = listify(schema["type"])
    chosen_type = random.choice(possible_types)

    if chosen_type == "number":
        return random_number(schema)
    elif chosen_type == "integer":
        return random_integer(schema)
    elif chosen_type == "object":
        return random_object(schema)
    elif chosen_type == "boolean":
        return random_boolean(schema)
    elif chosen_type == "string":
        return random_string(schema)
    elif chosen_type == "array":
        return random_array(schema)
    else:
        raise NotImplementedError()
