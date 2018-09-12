import json
from pathlib import Path
from exercism.problem_specifications import flatten_test_cases

test_data_dir = Path("tests/test_data")

queen_attack_tests = [
    "queen with a valid position",
    "queen must have positive row",
    "can not attack",
    "can attack on same row",
]


def test_extract_flat_test_cases():
    canonical_data = json.load(open(test_data_dir / "queen-attack-flat.json"))
    test_cases = flatten_test_cases(canonical_data["cases"])
    assert len(test_cases) == 4
    assert (test_cases.description == queen_attack_tests).all()


def test_extract_grouped_test_cases():
    canonical_data = json.load(open(test_data_dir / "queen-attack-nested.json"))
    test_cases = flatten_test_cases(canonical_data["cases"])
    assert len(test_cases) == 4
    assert (test_cases.description == queen_attack_tests).all()
    assert (
        test_cases.group.unique()
        == [
            "Test creation of Queens with valid and invalid positions",
            "Test the ability of one queen to attack another",
        ]
    ).all()


def test_extract_nested_test_cases():
    canonical_data = json.load(open(test_data_dir / "rational-numbers.json"))
    test_cases = flatten_test_cases(canonical_data["cases"])
    assert len(test_cases) == 36
    first_level_test_groups = test_cases.group.str.split(";").str[0].unique()
    assert (
        first_level_test_groups
        == [
            "Arithmetic",
            "Absolute value",
            "Exponentiation of a rational number",
            "Exponentiation of a real number to a rational number",
            "Reduction to lowest terms",
        ]
    ).all()


def test_extract_uneven_test_cases():
    canonical_data = json.load(open(test_data_dir / "queen-attack-uneven.json"))
    test_cases = flatten_test_cases(canonical_data["cases"])
    assert len(test_cases) == 4
    assert (test_cases.description == queen_attack_tests).all()
