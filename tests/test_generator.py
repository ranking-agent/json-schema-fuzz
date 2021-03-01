"""Test JSON schema fuzzer."""
import re

from json_schema_fuzz import generate_json


def test_integer():
    """Test generating integers."""
    schema = {
        "type": "integer"
    }
    output = generate_json(schema)
    assert isinstance(output, int)


def test_object():
    """Test generating integers."""
    schema = {
        "type": "object",
        "properties": {
            "a": {
                "type": "integer"
            }
        }
    }
    output = generate_json(schema)
    assert isinstance(output, dict)
    assert isinstance(output.get("a", 0), int)


def test_boolean():
    """Test generating booleans."""
    schema = {
        "type": "boolean"
    }
    output = generate_json(schema)
    assert isinstance(output, bool)


def test_array():
    """Test generating arrays."""
    schema = {
        "type": "array",
        "items": {
            "type": "string"
        }
    }
    output = generate_json(schema)
    assert isinstance(output, list)
    for element in output:
        assert isinstance(element, str)


def test_pattern_string():
    """Test generating a pattern restricted string.

    Test uses a pattern for a simple North American telephone number with an
    optional area code.
    """
    schema = {
        "type": "string",
        "pattern": "^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"
    }
    output = generate_json(schema)
    assert isinstance(output, str)
    assert re.fullmatch(schema.get("pattern"), output) is not None


def test_no_pattern_string():
    """Test generating string with no pattern restriction."""
    schema = {
        "type": "string",
    }
    output = generate_json(schema)
    assert isinstance(output, str)
