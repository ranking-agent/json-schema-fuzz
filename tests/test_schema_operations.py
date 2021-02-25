"""Test JSON schema merging."""
import glob
import json
from pathlib import Path

import pytest

from json_schema_fuzz.schema_operations import invert, merge

THIS_DIR = Path(__file__).parent
MERGE_CASE_DIR = THIS_DIR / "merge_cases"
merge_case_files = glob.glob(
    str(MERGE_CASE_DIR / "*.json"))
merge_cases = []
for filename in merge_case_files:
    with open(filename, "r") as stream:
        case = json.load(stream)
        merge_cases.append(
            (case["schemas"], case["merged"]))


@pytest.mark.parametrize("schemas,merged", merge_cases, ids=merge_case_files)
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


def test_merge_nested():
    """ Test that merging nested dictionaries works """
    schema_a = {"properties": {"a": "value"}}
    schema_b = {"properties": {"b": "value"}}
    merged = merge(schema_a, schema_b)

    assert 'a' in merged['properties']
    assert 'b' in merged['properties']


INVERT_CASE_DIR = THIS_DIR / "invert_cases"
invert_case_files = glob.glob(
    str(INVERT_CASE_DIR / "*.json"))
invert_cases = []
for filename in invert_case_files:
    with open(filename, "r") as stream:
        case = json.load(stream)
        invert_cases.append(
            (case["schema"], case["inverted"]))


@pytest.mark.parametrize(
    "schema,inverted", invert_cases, ids=invert_case_files)
def test_invert(schema, inverted):
    """Test that the given schema results in the `inverted` schema."""
    assert invert(schema) == inverted
