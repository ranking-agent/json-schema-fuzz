"""JSON schema fuzzer."""
import random
import string

import exrex


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
    # check if string is restricted to a regex pattern
    pattern = schema.get("pattern", None)
    if pattern is None:
        lowercase_letters = string.ascii_lowercase
        word_length = random.randrange(1, 20)
        new_word_list = random.choices(lowercase_letters, k=word_length)
        new_word = "".join(new_word_list)
        return new_word
    else:
        return exrex.getone(pattern)


def random_array(schema):
    """Generate random array."""
    items = schema.get("items", None)
    maxitems = schema.get("maxItems", 10)
    minitems = schema.get("minItems", len(items))
    # for now, we will assume that all listed types are required
    # TODO: modify this function to allow for optional types

    # calculate number of items per type in resulting array
    length = random.randint(minitems, maxitems) # choose a length for outputted array
    num_items = len(items) # number of accepted item type
    pot = length - num_items
    num_each_type = []
    i = 0

    while i < num_items:
        give = random.randint(0, pot)
        number = 1 + give
        num_each_type.append(number)
        pot = pot - give
        i += 1

    item_list = list(items)
    final_array = []

    for item in item_list:
        index = item_list.index(item)
        num = num_each_type[index]
        j = 0
        while j < num:
            final_array.append(generate_json(item))
            j += 1
    return final_array


def generate_json(schema):
    """Generate random JSON conforming to schema."""
    type = schema.get("type", None)
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
