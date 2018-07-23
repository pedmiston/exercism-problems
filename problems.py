#!/usr/bin/env python
import os
import sys
import json
from pathlib import Path
import github3
import pandas


github = github3.login(os.environ["GITHUB_USERNAME"], os.environ["GITHUB_PASSWORD"])


def get_problem_specifications():
    """Summarize information about problems from exercism/problem-specifications."""
    repo = github.repository("exercism", "problem-specifications")
    problems = pandas.DataFrame(
        {"exercise": [filename for filename, _ in repo.directory_contents("exercises")]}
    )

    def load_canonical_data(name):
        try:
            contents = repo.file_contents(f"exercises/{name}/canonical-data.json")
        except github3.exceptions.NotFoundError:
            data = {"cases": []}
        else:
            data = json.loads(contents.decoded.decode("utf-8"))
        return data

    problems["canonical_data"] = problems.exercise.apply(load_canonical_data)
    problems["n_test_cases"] = problems.canonical_data.apply(lambda x: len(x["cases"]))

    def melt_test_cases(problem_spec):
        try:
            cases = pandas.DataFrame(problem_spec.canonical_data["cases"])
        except Exception as e:
            cases = pandas.DataFrame()
        else:
            if "cases" in cases.columns:
                cases = pandas.DataFrame()
            else:
                cases["exercise"] = problem_spec.exercise
        return cases

    test_cases = pandas.concat(
        [melt_test_cases(x) for x in problems.itertuples()], ignore_index=True
    )[["exercise", "description"]]
    del problems["canonical_data"]

    return dict(problems=problems, test_cases=test_cases)


def get_exercises():
    languages = list_languages()

    def _get_exercises(language):
        repo = github.repository("exercism", language)
        try:
            contents = repo.file_contents("config.json")
        except github3.exceptions.NotFoundError:
            print(f"exercism/{language}/config.json does not exist")
            data = pandas.DataFrame()
        else:
            data = json.loads(contents.decoded.decode("utf-8"))
            data = pandas.DataFrame(data["exercises"]).rename(
                columns={"slug": "exercise"}
            )
            data["language"] = language
        return data

    data = pandas.concat(
        [_get_exercises(language) for language in languages],
        ignore_index=True,
        sort=False,
    )
    return data[["language", "exercise", "difficulty", "core", "unlocked_by"]]


def list_languages():
    exercism = github.organization("exercism")
    languages = []
    for repo in exercism.repositories():
        if repo.name == "problem-specifications":
            continue
        try:
            n_exercises = len(repo.directory_contents("exercises"))
        except github3.exceptions.NotFoundError:
            continue
        else:
            if n_exercises > 0:
                languages.append(repo.name)

    return languages


def list_problems():
    repo = github.repository("exercism", "problem-specifications")
    problems = [filename for filename, _ in repo.directory_contents("exercises")]
    return problems


def print_problem_descriptions():
    repo = github.repository("exercism", "problem-specifications")
    problems = [problem.strip() for problem in open('target-problems.txt')]

    descriptions_dir = Path("problem-descriptions")
    if not descriptions_dir.is_dir():
        descriptions_dir.mkdir()

    for problem in problems:
        try:
            contents = repo.file_contents(f"exercises/{problem}/description.md")
        except github3.exceptions.NotFoundError:
            print(f"description.md not found for exercise '{problem}'")
        else:
            with open(descriptions_dir / f"{problem}.md", "w") as dest:
                dest.write(f"# {problem}\n\n{contents.decoded.decode('utf-8')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--specifications",
        action="store_true",
        help="download problem specifications",
    )
    parser.add_argument(
        "-l", "--list-languages", action="store_true", help="list language tracks"
    )
    parser.add_argument(
        "-e", "--exercises", action="store_true", help="summarize exercise data"
    )
    parser.add_argument(
        "-d", "--descriptions", action="store_true", help="list problem descriptions"
    )

    args = parser.parse_args()
    if args.list_languages:
        print("\n".join(list_languages()))
        sys.exit()

    data_dir = Path("data-raw")
    if not data_dir.is_dir():
        data_dir.mkdir()

    if args.specifications:
        data = get_problem_specifications()
        data["problems"].to_csv(data_dir / "problem-specifications.csv", index=False)
        data["test_cases"].to_csv(data_dir / "test-cases.csv", index=False)

    if args.exercises:
        exercises = get_exercises()
        exercises.to_csv(data_dir / "exercises.csv", index=False)

    if args.descriptions:
        print_problem_descriptions()
