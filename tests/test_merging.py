"""Test JSON schema merging."""
import glob
import json
from pathlib import Path

import pytest

from json_schema_fuzz.merging import merge

THIS_DIR = Path(__file__).parent
CASE_DIR = THIS_DIR / "merge_cases"
case_files = glob.glob(str(CASE_DIR / "*.json"))
cases = []
for filename in case_files:
    with open(filename, "r") as stream:
        case = json.load(stream)
        cases.append((case["schemas"], case["merged"]))


@pytest.mark.parametrize("schemas,merged", cases)
def test_merging(schemas, merged):
    """Test that merging the `schemas` results in the `merged` schema."""
    assert merge(*schemas) == merged


def test_merge_doesnt_modify():
    """ Test that merging doesn't modify input values """
    required_a = ["required_property"]
    schema_a = {"required": required_a}
    schema_b = {"required": ["another_required_property"]}
    merged = merge(schema_a, schema_b)

    assert len(merged['required']) == 2
    assert len(required_a) == 1


def test_merge_conflicting():
    """Test that merging conflicting values throws a NotImplementedError."""
    schema_a = {"multipleOf": 3}
    schema_b = {"multipleOf": 5}

    with pytest.raises(NotImplementedError):
        merge(schema_a, schema_b)
