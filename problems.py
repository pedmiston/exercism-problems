#!/usr/bin/env python
import os
import json
import github3
import pandas


github = github3.login(os.environ["GITHUB_USERNAME"], os.environ["GITHUB_PASSWORD"])


def download_problem_specifications():
    """Download information about problems from exercism/problem-specifications.

    Writes to problem-specifications.csv and test-cases.csv.
    """
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
    )
    test_cases[["exercise", "description"]].to_csv("test-cases.csv", index=False)

    del problems["canonical_data"]
    problems.to_csv("problem-specifications.csv", index=False)


def download_language_track(language):
    repo = github.repository("exercism", language)
    try:
        contents = repo.file_contents("config.json")
    except github3.exceptions.NotFoundError:
        print(f"exercism/{language}/config.json does not exist")
        data = pandas.DataFrame()
    else:
        data = json.loads(contents.decoded.decode("utf-8"))
        data = pandas.DataFrame(data["exercises"]).rename(
                columns={"slug": "exercise"})
        data["language"] = language
    return data

def download_all_language_tracks():
    data = pandas.concat(
        [download_language_track(language) for language in list_languages()],
        ignore_index=True,
    )
    data = data[["language", "exercise", "difficulty", "core", "unlocked_by"]]
    data.to_csv("tracks.csv", index=False)


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
    parser.add_argument("-e", "--exercises", action="store_true", help="summarize exercise data")

    args = parser.parse_args()
    if args.specifications:
        download_problem_specifications()

    if args.list_languages:
        print("\n".join(list_languages()))

    if args.exercises:
        download_all_language_tracks()
