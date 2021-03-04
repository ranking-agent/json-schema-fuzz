""" Utility functions and constants for fuzzer module """
import math
import random
from typing import List

ALL_TYPES = ["object", "number", "array",
             "string", "null", "boolean", "integer"]


def listify(value):
    """ If value is not a list wrap it in a list """
    if isinstance(value, list):
        return value
    else:
        return [value]


def lcm(
        numbers: List[int]
) -> int:
    """
    Find least common multiple of a list of numbers

    TODO replace with math.lcm after updating to Python 3.9
    """
    product = 1
    gcd = 1
    for num in numbers:
        gcd = math.gcd(gcd, num)
        product *= num
    return product // gcd


def random_multiple_in_range(start, stop, multiple, precision=0):
    """
    Sample a random multiple of a number within a specified range (inclusive)

    Supports decimal values using the precision parameter
    """

    first_multiple = round(start / multiple, precision) * multiple
    last_multiple = round(stop / multiple, precision) * multiple

    num_multiples = (int(last_multiple - first_multiple) / multiple)

    instance_multiple = random.randint(0, num_multiples)

    instance_value = multiple * instance_multiple + first_multiple
    return instance_value
