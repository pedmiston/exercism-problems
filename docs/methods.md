# Methods

## Assembling the data

To assemble the data, you need a python environment. This project is configured
to use [pipenv](https://pipenv.readthedocs.io/en/latest/).

```bash
pipenv install  # creates a new python virtualenv and installs the required packages
pipenv run all  # runs the exercism module script that downloads all data
```

The data are fetched from GitHub using the python package
[github3](https://github3.readthedocs.io/en/master/). To authenticate a
connection to GitHub, you need a username and password available as environment
variables. The first time you run the `exercism` module script, you will be
prompted for your GitHub username and password. These values will be stored in
an environment file named ".env". On subsequent runs, pipenv will load these
variables automatically.

## Installing the R package

The R package can be installed manually or from GitHub.

### Installing the R package from GitHub

```R
remotes::install_github("pedmiston/exercism-problems")  # install exercism R package
library(exercism)                                       # load exercism R package
data(package = "exercism")                              # list datasets
data("problem_specifications")                          # load problem specifications
```

### Installing the R package manually

After running `pipenv run all`, run the following
R scripts to compile the csvs to rda files, and to install
the package locally.

```bash
Rscript make-data.R
Rscript install.R
```
