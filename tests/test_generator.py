"""Test JSON schema fuzzer."""
import glob
import json
import re
from pathlib import Path

import jsonschema
import pytest

from json_schema_fuzz import generate_json
from json_schema_fuzz.utils import custom_json_loads

# Create a custom validator
# for our custom properties


def not_multiple_of_validator(validator, value, instance, schema):
    """ jsonschema validator function for custom notMultipleOf property """
    if not isinstance(value, list):
        value = [value]
    for num in value:
        if instance % num == 0:
            yield jsonschema.ValidationError(
                f"{instance} is a multiple of {num}")


ExtendedValidator = jsonschema.validators.extend(
    jsonschema.Draft7Validator,
    validators={"notMultipleOf": not_multiple_of_validator}
)

THIS_DIR = Path(__file__).parent
GENERATE_CASE_DIR = THIS_DIR / "generate_cases"
generate_case_files = glob.glob(
    str(GENERATE_CASE_DIR / "**/*.json"), recursive=True)
generate_cases = []
for filename in generate_case_files:
    with open(filename, "r") as stream:
        case_string = stream.read()
        generate_cases.append(
            custom_json_loads(case_string)
        )


@pytest.mark.parametrize("schema", generate_cases, ids=generate_case_files)
def test_generate_validate(schema):
    """
    Test that generated json from the schema
    validates against the schema using the
    jsonschema library.
    """
    num_generated_values = 100
    validator = ExtendedValidator(schema)

    for _ in range(num_generated_values):
        value = generate_json(schema)
        try:
            validator.validate(value)
        except jsonschema.exceptions.ValidationError as exc_info:
            pytest.fail(f"""
                Failed to validate instance:
                {json.dumps(value)}

                Validation information:
                {exc_info}
            """)


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
