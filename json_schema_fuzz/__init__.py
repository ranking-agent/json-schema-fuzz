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
    pattern = schema.get("pattern", None) # check if string is restricted to a regex pattern
    if pattern == None:
        lowercase_letters = string.ascii_lowercase
        word_length = random.randrange(1, 20)
        new_word_list = random.choices(lowercase_letters, k=word_length)
        new_word = "".join(new_word_list)
        return new_word
    else:
        return exrex.getone(pattern)
    


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
    else:
        raise NotImplementedError()

