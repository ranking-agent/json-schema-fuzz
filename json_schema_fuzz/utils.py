""" Utility functions and constants for fuzzer module """
import json
import math
import random
from decimal import Decimal
from typing import List

ALL_TYPES = ["object", "number", "array",
             "string", "null", "boolean", "integer"]


def custom_json_loads(input_string):
    """ Load JSON using Python's decimal type for numbers """
    return json.loads(
        input_string,
        parse_float=Decimal,
        parse_int=Decimal,
    )


def listify(value):
    """ If value is not a list wrap it in a list """
    if isinstance(value, list):
        return value
    else:
        return [value]


def gcd(num_a, num_b):
    """
    Calculate the Greatest Common Divisor of a and b.

    Same implementation as math.gcd except this one
    works with decimals.
    """
    while num_b:
        num_a, num_b = num_b, num_a % num_b
    return num_a


def lcm(
        numbers: List[int]
) -> int:
    """
    Find least common multiple of a list of numbers
    """
    current_product = 1
    current_gcd = 1
    for num in numbers:
        current_gcd = gcd(current_gcd, num)
        current_product *= num
    return current_product // current_gcd


def random_multiple_in_range(start, stop, multiple):
    """
    Sample a random multiple of a number within a specified range (inclusive)

    Supports decimal values
    """

    first_multiple = math.ceil(start / multiple) * multiple
    last_multiple = math.floor(stop / multiple) * multiple

    num_multiples = int((last_multiple - first_multiple) / multiple)

    instance_multiple = random.randint(0, num_multiples)

    instance_value = multiple * instance_multiple + first_multiple
    return instance_value
