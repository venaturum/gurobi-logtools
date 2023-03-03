.PHONY: install format lint test tox clean-mac

install:
	poetry run python -m pip install --upgrade pip
	poetry install

format:
	poetry run black .\src\

lint:
	poetry run flake8 --max-line-length 88 --ignore=E203,E231,E402,E501,F401,W503

mypy:
	@echo "mypy not configured for this project"
#	poetry run mypy .\src\

test:
	poetry run pytest

tox:
	poetry run tox

clean-mac:
	poetry run find . -type d -name __pycache__ -exec rm -rf {} +
	poetry run find . -type d -name .tox -maxdepth 1 -exec rm -rf {} +
	poetry run find . -type d -name .pytest_cache -exec rm -rf {} +
	poetry run find . -type f -name test.xlsx -maxdepth 1 -exec rm -f {} \;