# [GitAlma](https://github.com/ICR-RSE-Group/gitalma)

A utility for working with a group's gitlab and github repositories.

## To install this library
Activate an environment first if required.
```bash
python -m pip install git+https://github.com/ICR-RSE-Group/gitalma.git

# uninstall
python -m pip uninstall gitalma
```

## Install as a single file gitlab.py
The alternative installation is as the single file gitlab.py, which can be done either by installing it and using the explicit path, or by making it seem like a package.  
**Explicit path and exactly as now**
```
mkdir bcrbioinformatics
cd bcrbioinformatics
wget https://raw.githubusercontent.com/ICR-RSE-Group/gitalma/refs/heads/main/api/gitlab.py
python3 gitlab.py init -subgroup 2879
python3 gitlab.py update
rm gitlab.py
python3 Utils/gitlab.py status
```
**Pretending it is a package**
```
mkdir bcrbioinformatics
cd bcrbioinformatics
wget https://raw.githubusercontent.com/ICR-RSE-Group/gitalma/refs/heads/main/api/gitlab
chmod +x gitlab
gitlab init -subgroup 2879
gitlab update
chmod +x Utils/gitlab
export PATH="$PWD/Utils:$PATH"
rm gitlab
gitlab status
```

## Quick start
Documentation from [pydoctor is here](https://github.com/ICR-RSE-Group/gitalma)

### For command line (the commands `gitlab` and `gitalma` are aliases of each other and interchangeable):
```bash
gitalma init -subgroup 1234
gitlab update
gitalma status
gitlab history
gitalma change -protocol pat 
```

# Repos examples
```bash
# Internal ICR
gitalma init -subgroup 1234 -protocol pat
# gitlab public, https://gitlab.com
git-alma init -subgroup 100000123 -protocol https -source gitlab
# github public
git-alma init -protocol https -source github
```
and then edit the init.yml, e.g.
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
