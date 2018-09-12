# Analysis of programming problems on Exercism.io

This repo contains code for extracting metadata about programming problems from
Exercism.io via GitHub. The code for assembling the data is in the python module
["exercism"](./exercism). The data is available in csvs in the ["data-raw/"](./data-raw)
directory, or in an R package, which can be installed with
`remotes::install_github("pedmiston/exercism-problems")`.

## Methods

To work on this project or reproduce results, see the [Methods](docs/methods.md) document.

## Results

Our results are presented in the following dynamic documents:

[Exercism.io Problems](docs/exercism-problems.md)
:   Analyses of the problems available on Exercism.io including number of test cases and self-assigned difficulty. Source document: [docs/exercism-problems.Rmd](docs/exercism-problems.Rmd)
