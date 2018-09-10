import json
from pathlib import Path
from problems import extract_test_cases_from_canonical_data

test_data_dir = Path("tests/test_data")

queen_attack_tests = [
    "queen with a valid position",
    "queen must have positive row",
    "can not attack",
    "can attack on same row",
]


def test_extract_test_cases_retains_exercise_name():
    canonical_data = json.load(open(test_data_dir / "queen-attack-flat.json"))
    test_cases = extract_test_cases_from_canonical_data(canonical_data)
    assert "exercise" in test_cases.columns
    assert len(test_cases.exercise.unique()) == 1
    assert test_cases.exercise.iloc[0] == "queen-attack"


def test_extract_flat_test_cases():
    canonical_data = json.load(open(test_data_dir / "queen-attack-flat.json"))
    test_cases = extract_test_cases_from_canonical_data(canonical_data)
    assert len(test_cases) == 4
    assert (test_cases.description == queen_attack_tests).all()


def test_extract_nested_test_cases():
    canonical_data = json.load(open(test_data_dir / "queen-attack-nested.json"))
    test_cases = extract_test_cases_from_canonical_data(canonical_data)
    assert len(test_cases) == 4
    assert (test_cases.description == queen_attack_tests).all()
    assert (
        test_cases.group.unique()
        == [
            "Test creation of Queens with valid and invalid positions",
            "Test the ability of one queen to attack another",
        ]
    ).all()


def test_extract_deep_test_cases():
    canonical_data = json.load(open(test_data_dir / "queen-attack-deep.json"))
    test_cases = extract_test_cases_from_canonical_data(canonical_data)
    assert len(test_cases) == 4
    assert (test_cases.description == queen_attack_tests).all()
    assert test_cases.group.unique()[0] == "Level 1; Level 2; Level 3"


def test_extract_uneven_test_cases():
    canonical_data = json.load(open(test_data_dir / "queen-attack-uneven.json"))
    test_cases = extract_test_cases_from_canonical_data(canonical_data)
    assert len(test_cases) == 4
    assert (test_cases.description == queen_attack_tests).all()
