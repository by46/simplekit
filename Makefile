#!/usr/bin/env bash

COVER=coverage
CWD=$(shell pwd)

.PHONY: test clean release

release:
	@python setup.py sdist upload

test:
	@rm -vf .coverage coverage.xml
	@$(COVER) run -m unittest discover --start-directory tests --pattern *_test.py
	@$(COVER) html
	@python -m webbrowser -t "$(CWD)/htmlcov/index.html"

clean:
	@rm -vf .coverage
	@rm -rvf build dist htmlcov log* tests/log*
