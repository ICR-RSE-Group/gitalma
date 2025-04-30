# Dev of this lib

## Code development
1. Virtual environment
```bash
python3 -m venv .env-git
source .env-git/bin/activate
```
2. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. install the package in editable mode with the dev profile, and the pre-commit
```bash
python -m pip install -e .[dev]
pre-commit install
```
You may need to re-install the package if the cli is changed.

## Making a release
CHange the version in pyproject.toml

## Automated documentation
the github-action pydoctor builds the documentation from the doc strings