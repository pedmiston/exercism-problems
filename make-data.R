#!/usr/bin/env Rscript --vanilla
library(devtools)
library(readr)

exercises <- read_csv("data-raw/exercises.csv")
languages <- read_csv("data-raw/languages.csv")
problem_specifications <- read_csv("data-raw/problem-specifications.csv")
test_cases <- read_csv("data-raw/test-cases.csv")
topics <- read_csv("data-raw/topics.csv")

use_data(exercises, languages, problem_specifications, test_cases, topics, overwrite = TRUE)
