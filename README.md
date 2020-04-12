# Git Lab

Subcommand for git providing an arcanist-style interface to GitLab.

## Workflow 

### For creating a merge request

```
git checkout -b feature
```
Do changes
```
git commit -m "Commit message"
git lab diff
```

### For testing a merge request

```
git lab patch ${NUMBER}
```

## Installation

```
sudo pip3 install -r requirements.txt
sudo setup.py install
```
