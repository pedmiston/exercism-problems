# Methods

## Assembling the data

To assemble the data, you need a python environment. Here's how I set up to work on this project.

```bash
pipenv install --dev
```

The data are fetched from GitHub using the python package "github3.py". To
authenticate a connection to the GitHub API, you need a username and password
available as environment variables. The first time you run the problems.py
script, you will be prompted for your GitHub username and password. On subsequent runs, these will be loaded automatically.

```bash
pipenv run python problems.py -h     # show help and options
pipenv run python problems.py --all  # scrape all data into csvs in data-raw/
```

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

After running `python problems.py --all`, run the following
R scripts to compile the csvs to rda files, and to install
the package locally.

```bash
Rscript make-data.R
Rscript install.R
```

## Using the `exercism` command line client

Exercism.io has a command line client that is used to download and submit
puzzles and their solutions.

```bash
brew install exercism
# go to exercism.io, make an account, copy your CLI token.
exercism configure --token=your-exercism-account-token-here
exercism download --exercise=hello-world --track=python
```
