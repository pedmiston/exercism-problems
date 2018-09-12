import json
import github3
import pandas
import yaml


def get_problem_specifications(github):
    """Download problem metadata from the exercism/problem-specifications repo."""
    repo = github.repository("exercism", "problem-specifications")
    exercise_names = [filename for filename, _ in repo.directory_contents("exercises")]
    problems = pandas.DataFrame({"exercise": exercise_names})
    problems["canonical_data"] = problems.exercise.apply(load_canonical_data, repo=repo)
    problems["problem_description"] = problems.exercise.apply(
        load_description, repo=repo
    )
    problems["metadata"] = problems.exercise.apply(load_metadata, repo=repo)
    problems["blurb"] = problems.metadata.apply(
        lambda metadata: metadata.get("blurb", "")
    )
    return problems


def load_canonical_data(exercise, repo):
    contents = load_exercise_file("canonical-data.json", exercise, repo)
    try:
        data = json.loads(contents)
    except json.JSONDecodeError:
        data = {}
    return data


def load_description(exercise, repo):
    return load_exercise_file("description.md", exercise, repo)


def load_metadata(exercise, repo):
    contents = load_exercise_file("metadata.yml", exercise, repo)
    if not contents:
        data = {}
    else:
        data = yaml.load(contents)
    return data


def load_exercise_file(name, exercise, repo):
    try:
        contents = repo.file_contents(f"exercises/{exercise}/{name}")
    except github3.exceptions.NotFoundError:
        contents = ""
    else:
        contents = contents.decoded.decode("utf-8")
    return contents


def extract_test_cases(problems):
    test_cases = []
    for problem in problems.itertuples():
        if not problem.canonical_data:
            continue
        t = flatten_test_cases(problem.canonical_data["cases"])
        t.insert(0, "exercise", problem.exercise)
        test_cases.append(t)
    test_cases = pandas.concat(test_cases, ignore_index=True, sort=False)
    return test_cases


def flatten_test_cases(cases, group=""):
    test_cases = []
    for case in cases:
        if "cases" in case:
            # case is a test group
            if group and not group.endswith("; "):
                group += "; "
            test_cases.append(
                flatten_test_cases(case["cases"], group=group + case["description"])
            )
        else:
            test_cases.append(
                pandas.DataFrame(
                    {"description": case["description"], "group": group}, index=[0]
                )
            )
    if len(test_cases) == 0:
        test_cases = pandas.DataFrame()
    else:
        test_cases = pandas.concat(test_cases, ignore_index=True, sort=False)
    return test_cases
