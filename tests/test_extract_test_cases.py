import json
from pathlib import Path
from problems import extract_test_cases_from_canonical_data

test_data_dir = Path("tests/test_data")


def test_extract_nested_test_cases():
    canonical_data = json.load(open(test_data_dir / "queen-attack.json"))
    test_cases = extract_test_cases_from_canonical_data(canonical_data)
    assert len(test_cases) == 4
