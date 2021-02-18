"""JSON schema fuzzer."""
import random
import string

import exrex

from .merging import merge


def random_integer(schema):
    """Generate random integer."""
    return random.randint(0, 10)


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
    pattern = schema.get("pattern", None)
    if pattern is None:  # check if string is restricted to a regex pattern
        lowercase_letters = string.ascii_lowercase
        word_length = random.randrange(1, 20)
        new_word_list = random.choices(lowercase_letters, k=word_length)
        new_word = "".join(new_word_list)
        return new_word
    else:
        return exrex.getone(pattern)


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


def generate_json(schema):
    """Generate random JSON conforming to schema."""

    # Merge allOf subschemas into the base schema
    all_of = schema.get("allOf", [])
    for subschema in all_of:
        schema = merge(schema, subschema)

    type = schema.get("type", None)
    anyof = schema.get("anyOf", None)
    if type is not None:
        if type == "integer":
            return random_integer(schema)
        elif type == "object":
            return random_object(schema)
        elif type == "boolean":
            return random_boolean(schema)
        elif type == "string":
            return random_string(schema)
        elif type == "array":
            return random_array(schema)
        else:
            raise NotImplementedError()
    elif anyof is not None:
        return generate_json(random.choice(anyof))
    else:
        raise NotImplementedError()
