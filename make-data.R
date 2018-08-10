#!/usr/bin/env Rscript --vanilla
library(devtools)
library(readr)

problem_specifications <- read_csv("data-raw/problem-specifications.csv")
test_cases <- read_csv("data-raw/test-cases.csv")
exercises <- read_csv("data-raw/exercises.csv")
exercise_topics <- read_csv("data-raw/exercise-topics.csv")

use_data(problem_specifications, test_cases, exercises, exercise_topics, overwrite = TRUE)
