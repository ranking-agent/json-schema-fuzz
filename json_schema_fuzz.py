"""JSON schema fuzzer."""
import random


def random_integer(schema):
    """Generate random integer."""
    return random.randint(0, 10)


def random_object(schema):
    """Generate random JSON object."""
    properties = schema.get("properties", dict())
    required = schema.get("required", [])
    object = dict()
    for key, value in properties.items():
        if key in required or random.randint(0, 1):
            object[key] = generate_json(value)
    return object


def generate_json(schema):
    """Generate random JSON conforming to schema."""
    type = schema.get("type", None)
    if type == "integer":
        return random_integer(schema)
    elif type == "object":
        return random_object(schema)
    else:
        raise NotImplementedError()
