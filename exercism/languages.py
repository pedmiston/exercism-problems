import json
import github3
import pandas


def get_languages(github):
    language_names = find_languages(github)
    languages = pandas.DataFrame({"language": language_names})
    languages["repo"] = languages.language.apply(
        lambda language: github.repository("exercism", language)
    )
    languages["config"] = languages.repo.apply(load_config)
    languages["active"] = languages.config.apply(
        lambda config: config.get("active", False)
    ).astype(int)
    languages["blurb"] = languages.config.apply(lambda config: config.get("blurb", ""))
    return languages


def load_config(language_repo):
    try:
        contents = language_repo.file_contents("config.json")
    except github3.exceptions.NotFoundError:
        contents = {}
    else:
        contents = json.loads(contents.decoded.decode("utf-8"))
    return contents


def find_languages(github):
    org = github.organization("exercism")
    languages = []
    repos_to_ignore = ["problem-specifications", "website-icons"]
    for repo in org.repositories():
        if repo.name in repos_to_ignore:
            continue
        try:
            n_exercises = len(repo.directory_contents("exercises"))
        except github3.exceptions.NotFoundError:
            continue
        else:
            if n_exercises > 0:
                languages.append(repo.name)
    return languages


def extract_exercises(languages):
    exercises = []
    for language in languages.itertuples():
        e = pandas.DataFrame(language.config["exercises"]).rename(
            columns={"slug": "exercise"}
        )
        e["core"] = e.core.astype(int)
        e.insert(0, "language", language.language)
        exercises.append(e)
    exercises = pandas.concat(exercises, ignore_index=True, sort=False)
    return exercises


def extract_topics(exercises):
    topics = []
    for exercise in exercises.itertuples():
        if exercise.topics is None:
            continue
        t = pandas.DataFrame(
            {"topic": exercise.topics}, index=list(range(len(exercise.topics)))
        )
        t.insert(0, "language", exercise.language)
        t.insert(1, "exercise", exercise.exercise)
        topics.append(t)
    topics = pandas.concat(topics, ignore_index=True, sort=False)
    return topics
