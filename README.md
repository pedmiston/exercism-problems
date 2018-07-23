# Programming problems on Exercism.io

This repo contains code for scraping metadata about programming problems from Exercism.io.
The data is stored in an R package.

## Installing the R package

```R
remotes::install_github("pedmiston/exercism-problems")  # install exercism R package
library(exercism)                                       # load exercism R package
data(package = "exercism")                              # list datasets
```

## Using the command line client

Exercism.io has a command line client that is used to download and submit
puzzles and their solutions.

```bash
brew install exercism
# go to exercism.io, make an account, copy your CLI token.
exercism configure --token=your-exercism-account-token-here
exercism download --exercise=hello-world --track=python
```

## Candidate problems

- [bowling](https://github.com/exercism/python/tree/master/exercises/bowling)
- [crypto-square](https://github.com/exercism/python/tree/master/exercises/crypto-square)
- [dominoes](https://github.com/exercism/python/tree/master/exercises/dominoes)
- [minesweeper](https://github.com/exercism/python/tree/master/exercises/minesweeper)
