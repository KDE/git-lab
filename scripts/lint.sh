#!/usr/bin/env sh

pylint lab
flake8 lab --max-line-length 100
mypy --strict lab
black -l 100 lab --diff
