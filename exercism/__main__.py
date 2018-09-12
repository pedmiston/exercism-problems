#!/usr/bin/env python
import os
import sys
import json
import argparse
from pathlib import Path

import github3
import jinja2

from .problem_specifications import get_problem_specifications, extract_test_cases
from .languages import get_languages, extract_exercises, extract_topics


env_tmpl = """\
export GITHUB_USERNAME={{ github_username }}
export GITHUB_PASSWORD={{ github_password }}
"""


def login_to_github():
    github_username = os.environ.get("GITHUB_USERNAME")
    github_password = os.environ.get("GITHUB_PASSWORD")

    if "GITHUB_USERNAME" not in os.environ or "GITHUB_PASSWORD" not in os.environ:
        github_username = input("Enter your GitHub username: ")
        github_password = input("Enter your GitHub password: ")
        print("Writing .env")
        open(".env", "w").write(
            jinja2.Template(env_tmpl).render(
                github_username=github_username, github_password=github_password
            )
        )

    github = github3.login(github_username, github_password)
    return github


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="python -m exercism")
    parser.add_argument(
        "-p",
        "--problem-specifications",
        action="store_true",
        help="download problem specifications",
    )

    parser.add_argument(
        "-l", "--languages", action="store_true", help="download language data"
    )
    parser.add_argument(
        "-a", "--all", action="store_true", help="download all datasets"
    )

    if not len(sys.argv) > 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    github = login_to_github()
    data_dir = Path("data-raw")
    if not data_dir.is_dir():
        data_dir.mkdir()

    args = parser.parse_args()
    args.problem_specifications |= args.all
    args.languages |= args.all

    if args.problem_specifications:
        problem_specifications = get_problem_specifications(github)
        test_cases = extract_test_cases(problem_specifications)
        del problem_specifications["canonical_data"]
        del problem_specifications["metadata"]
        del problem_specifications["problem_description"]
        problem_specifications.to_csv(
            data_dir / "problem-specifications.csv", index=False
        )
        test_cases.to_csv(data_dir / "test-cases.csv", index=False)

    if args.languages:
        languages = get_languages(github)
        exercises = extract_exercises(languages)
        topics = extract_topics(exercises)
        del languages["repo"]
        del languages["config"]
        languages.to_csv(data_dir / "languages.csv", index=False)
        exercises[["language", "exercise", "core", "difficulty"]].to_csv(
            data_dir / "exercises.csv", index=False
        )
        topics.to_csv(data_dir / "topics.csv", index=False)
