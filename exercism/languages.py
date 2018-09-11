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


def melt_language_exercises(languages):
    language_exercises = []
    for row in languages.itertuples():
        exercises = pandas.DataFrame(row.config["exercises"]).rename(
            columns={"slug": "exercise"}
        )
        exercises["core"] = exercises.core.astype(int)
        exercises.insert(0, "language", row.language)
        language_exercises.append(exercises)
    language_exercises = pandas.concat(
        language_exercises, ignore_index=True, sort=False
    )
    return language_exercises


def melt_language_exercise_topics(language_exercises):
    language_exercise_topics = []
    for row in language_exercises.itertuples():
        if row.topics is None:
            continue
        topics = pandas.DataFrame(
            {"topic": row.topics}, index=list(range(len(row.topics)))
        )
        topics.insert(0, "language", row.language)
        topics.insert(1, "exercise", row.exercise)
        language_exercise_topics.append(topics)
    language_exercise_topics = pandas.concat(
        language_exercise_topics, ignore_index=True, sort=False
    )
    return language_exercise_topics
