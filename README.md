# pairing-matrix

[![pypi](https://img.shields.io/pypi/v/pairing_matrix.svg)](https://pypi.python.org/pypi/pairing_matrix) [![Build Status](https://travis-ci.org/iile/pairing_matrix.png?branch=master)](http://travis-ci.org/iile/pairing_matrix) [![Coverage](https://coveralls.io/repos/iile/pairing_matrix/badge.png?branch=master)](https://coveralls.io/r/iile/pairing_matrix) ![python version](https://img.shields.io/pypi/pyversions/pairing_matrix.svg) ![Project status](https://img.shields.io/pypi/status/pairing_matrix.svg) ![license](https://img.shields.io/pypi/l/pairing_matrix.svg)

Pair Programming Matrix


## Requirements

* Python 3.7 or newer


## Development

This project uses [poetry](https://poetry.eustace.io/) for packaging and
managing all dependencies and [pre-commit](https://pre-commit.com/) to run
[flake8](http://flake8.pycqa.org/) and [black](https://github.com/python/black).

Clone this repository and run

```bash
poetry develop
```

to create a virtual enviroment containing all dependencies.
Afterwards, You can run the test suite using

```bash
poetry run pytest
```

This repository follows the [Conventional Commits](https://www.conventionalcommits.org/)
style.
