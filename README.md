# Programming problems on Exercism.io

This repo contains code for scraping metadata about programming problems from
Exercism.io. The data is available in an R package, which can be installed with
`remotes::install_github("pedmiston/exercism-problems")`. The code for
assembling the data is in the python script "problems.py".

Our results are presented in the following dynamic documents:

[Exercism.io Problems](docs/exercism-problems.md)
:   Analyses of the problems available on Exercism.io including number of test cases and self-assigned difficulty. Source document: [docs/exercism-problems.Rmd](docs/exercism-problems.Rmd)

To work on this project or reproduce results, see the [Methods](docs/methods.md) document.

