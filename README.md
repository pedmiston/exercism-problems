# Programming problems on Exercism.io

This repo contains code for scraping metadata about programming problems from Exercism.io.
The data is available in an R package, which can be installed with `remotes::install_github("pedmiston/exercism-problems")`.
The code for assembling the data is in the python script "problems.py".

Our results are presented in the following dynamic documents:

[Exercism.io Problems](docs/exercism-problems.md)
:   Analyses of the problems available on Exercism.io including number of test cases and self-assigned difficulty. Source document: [docs/exercism-problems.Rmd](docs/exercism-problems.Rmd)

## Assembling the data

To assemble the data, you need a python environment. Here's how I set up to work on this project.

```bash
$ python3 -m venv ~/.venvs/exercism-problems           # create a new venv named "exercism-problems"
$ source ~/.venvs/exercism-problems/bin/activate       # activate the newly created venv
(exercism-problems) $ pip install -r requirements.txt  # install the packages required for this project
```

The data are fetched from GitHub using the python package "github3.py". To authenticate
a connection to the GitHub API, you need a username and password available as environment
variables.

```bash
export GITHUB_USERNAME=myusername
export GITHUB_PASSWORD=mypassword
python problems.py -h     # show help and options
python problems.py --all  # scrape all data into csvs in data-raw/
```

If you get the following KeyError when running the problems.py program,
it likely means you forgot to export your GitHub username and password
as the environment variables GITHUB_USERNAME and GITHUB_PASSWORD.

```
$ python problems.py -h
Traceback (most recent call last):
  File "problems.py", line 10, in <module>
    github = github3.login(os.environ["GITHUB_USERNAME"], os.environ["GITHUB_PASSWORD"])
  File "/usr/local/Cellar/python/3.7.0/Frameworks/Python.framework/Versions/3.7/lib/python3.7/os.py", line 678, in __getitem__
    raise KeyError(key) from None
KeyError: 'GITHUB_USERNAME'
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
