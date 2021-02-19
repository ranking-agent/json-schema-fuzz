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
