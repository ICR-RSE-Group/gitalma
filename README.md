# GitAlma

A utility for working with a group's gitlab and github repositories.

## To install this library
Activate an environment first if required.
```bash
python -m pip install git+https://github.com/ICR-RSE-Group/gitalma.git
```

## Quick start
Documentation from [pydoctor is here](docs)

### For command line,
```bash
git-alma init -subgroup 1234
git-alma update
git-alma status
git-alma history
gi-alma change -protocol pat
git-alma change -autoupgrade N 
```

# Repos examples
## Internal ICR
git-alma init -subgroup 1234 -protocol pat
git-alma init -subgroup 1234 -protocol https
git-alma init -subgroup 1234 -protocol ssh

## gitlab public, https://gitlab.com
git-alma init -subgroup 100000123 -protocol https -source gitlab

## github public
git-alma init -protocol https -source github
`and then edit the init.yml, e.g.`
```yaml
home: /home/ralcraft/dev/github-rse
path: /home/ralcraft/dev/github-rse
protocol: https
server: https://github.com
source: github
subgroup: '-1'
repos:
-   SCRSE/LIBS: git@github.com:ICR-RSE-Group/pyalma.git
-   SCRSE/LIBS: git@github.com:ICR-RSE-Group/gitalma.git
-   SCRSE/APPS: git@github.com:ICR-RSE-Group/green-alma.git
-   GENEVOD/HE: git@github.com:instituteofcancerresearch/he-class-app.git
-   GENEVOD/HE: git@github.com:instituteofcancerresearch/he-class-pipeline.git
```
