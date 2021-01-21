"""Test JSON schema fuzzer."""
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
