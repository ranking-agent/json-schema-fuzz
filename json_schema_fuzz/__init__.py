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
    if items != None:
        if isinstance(items, list):
            my_list = []
            for thing in items:
                my_list.append(generate_json(thing))
            return my_list
        else:
            minitems = schema.get("minItems", None)
            maxitems = schema.get("maxItems", None)
            if minitems != None:
                my_min = minitems
            else:
                my_min = 1
            if maxitems != None:
                my_max = maxitems
            else: 
                my_max = 20
            list_length = random.randrange(my_min, my_max)
            
    # minitems = schema.get("minItems", None)
    # maxitems = schema.get("maxItems", None)
    # contains = schema.get("contains", None)
    
    # if items == None:
    #     my_array = []
    
    return

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
