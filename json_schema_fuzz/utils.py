""" Utility functions and constants for fuzzer module """
import math
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
