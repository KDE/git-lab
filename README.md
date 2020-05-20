# Git Lab

Subcommand for git providing a command line interface to GitLab.
An arc-style interface is also provided for a simplified transition from Phabricator to GitLab.

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
git lab mr
```

### Listing merge requests

* Merge requests for the current repository

```
git lab mrs --project
```

* Merge requests for the current GitLab instance (detected from the repository)
```
git lab mrs
```

* To only show merge requests in specific states, any combination of `--merged`, `--opened` and `--closed` can be added

### Testing a merge request

```
git lab checkout ${NUMBER}
```

## Installation

```
sudo pip3 install -r requirements.txt
sudo python3 setup.py install
```
