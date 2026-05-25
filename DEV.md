# Dev of this lib

## Code development
1. Use a conda environment with the util installed as editable
```bash
conda create -n gitalma-env -c conda-forge python==3.12
conda activate gitalma-env
```

2. install the package in editable mode with the dev profile, and the pre-commit
```bash
python -m pip install -e .[dev]
pre-commit install
```
You may need to re-install the package if the cli is changed.

## Making a release
CHange the version in pyproject.toml

## Automated documentation
the github-action pydoctor builds the documentation from the doc strings

## If testing with another repo --stack
conda activate --stack new-env
