export PATH := $(shell pwd)/venv/bin/:$(PATH)
export VERSION := $(shell python3.6 setup.py --version)
all: venv

venv:
	virtualenv -p python3.6 venv
	pip install -r requirements-dev.txt -r requirements.txt -e .
	pre-commit install --install-hooks

.PHONY: clean
clean:
	rm -rf venv
	rm -rf *.egg-info/
	find -name '*.pyc' -delete
	find -name '__pycache__' -delete

.PHONY: test
test: venv
	pre-commit run --all-files
	pytest tests
	pylint weechat_notify tests
