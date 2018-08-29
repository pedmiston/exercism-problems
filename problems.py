#!/usr/bin/env python
import os
import sys
import json
from pathlib import Path
import github3
import pandas


github = github3.login(os.environ["GITHUB_USERNAME"], os.environ["GITHUB_PASSWORD"])


def get_problem_specification_data():
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

    def get_problem_description(problem):
        try:
            contents = repo.file_contents(f"exercises/{problem}/description.md")
        except github3.exceptions.NotFoundError:
            description = ""
        else:
            description = contents.decoded.decode('utf-8')
        return description

    problems["description"] = problems.exercise.apply(get_problem_description)

    def melt_test_group(test_group):
        try:
            cases = pandas.DataFrame(test_group.cases)
        except Exception as e:
            cases = pandas.DataFrame()
        else:
            cases["group_description"] = test_group.description
        return cases

    def melt_test_cases(problem_spec):
        try:
            cases = pandas.DataFrame(problem_spec.canonical_data["cases"])
        except Exception as e:
            cases = pandas.DataFrame()
        else:
            if "cases" in cases.columns:
                # test cases are nested with test groups
                cases = pandas.concat([melt_test_group(x) for x in cases.itertuples()], ignore_index=True, sort=True)
            cases["exercise"] = problem_spec.exercise
        return cases

    test_cases = pandas.concat(
        [melt_test_cases(x) for x in problems.itertuples()], ignore_index=True, sort=True
    )[["exercise", "group_description", "description"]]
    del problems["canonical_data"]

    n_test_cases = test_cases.groupby("exercise").size()
    n_test_cases.name = "n_test_cases"
    n_test_cases = n_test_cases.reset_index()
    problems = problems.merge(n_test_cases)

    return dict(problems=problems, test_cases=test_cases)


def get_exercise_data():
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
                columns={"slug": "exercise", "core": "is_core"}
            )
            data["is_core"] = data.is_core.astype(int)
            data["language"] = language
        return data

    data = pandas.concat(
        [_get_exercises(language) for language in languages],
        ignore_index=True,
        sort=False,
    )

    exercises = data[["language", "exercise", "difficulty", "is_core", "unlocked_by"]]

    def melt_topics(row):
        if not row.topics:
            return pandas.DataFrame()
        return pandas.DataFrame({"exercise": row.exercise, "language": row.language, "topic": row.topics})
    topics = pandas.concat([melt_topics(r) for r in data.itertuples()], ignore_index=True, sort=True)

    return dict(exercises=exercises, topics=topics)


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


def download_problem_specifications():
    data = get_problem_specification_data()
    data["problems"].to_csv(data_dir / "problem-specifications.csv", index=False)
    data["test_cases"].to_csv(data_dir / "test-cases.csv", index=False)


def download_exercises():
    data = get_exercise_data()
    data["exercises"].to_csv(data_dir / "exercises.csv", index=False)
    data["topics"].to_csv(data_dir / "exercise-topics.csv", index=False)


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
    parser.add_argument(
        "-a", "--all", action="store_true", help="run all download commands"
    )

    if not len(sys.argv) > 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    if args.list_languages:
        print("\n".join(list_languages()))
        sys.exit()

    data_dir = Path("data-raw")
    if not data_dir.is_dir():
        data_dir.mkdir()

    if args.specifications:
        download_problem_specifications()

    if args.exercises:
        download_exercises()

    if args.descriptions:
        print_problem_descriptions()

    if args.all:
      download_problem_specifications()
      download_exercises()
