# Git Lab

Subcommand for git providing an arcanist-style interface to GitLab.

## Workflow

### Logging in

```
git lab login --host invent.kde.org --token ${YOUR_PRIVATE_TOKEN}
```

### Creating a merge request

```
git checkout -b feature
```

Do your changes

```
git commit -m "Commit message"
git lab diff
```

### Listing merge requests

* Merge requests for the current repository

```
git lab list --project
```

* Merge requests for the current GitLab instance (detected from the repository)
```
git lab list
```

* To only show merge requests in specific states, any combination of `--merged`, `--opened` and `--closed` can be added

### Testing a merge request

```
git lab patch ${NUMBER}
```

## Installation

```
sudo pip3 install -r requirements.txt
sudo setup.py install
```
