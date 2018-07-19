#!/usr/bin/env python
import os
import json
import github3
import pandas


github = github3.login(os.environ["GITHUB_USERNAME"], os.environ["GITHUB_PASSWORD"])


def download_problem_specifications():
    repo = github.repository("exercism", "problem-specifications")
    problems = pandas.DataFrame({
        "exercise": [filename for filename, _ in repo.directory_contents("exercises")]
    })

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
            print(e)
            cases = pandas.DataFrame()
        else:
            cases["exercise"] = problem_spec.exercise
        return cases

    # test_cases = pandas.concat([melt_test_cases(x) for x in problems.itertuples()],
    #         ignore_index=True)
    # test_cases.to_csv("test-cases.csv", index=False)

    del problems["canonical_data"]
    problems.to_csv("problem-specifications.csv", index=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--specifications', action='store_true',
            help='download problem specifications')
    args = parser.parse_args()
    if args.specifications:
        download_problem_specifications()
