# Git Lab

Subcommand for git providing a command line interface to GitLab.
An arc-style interface is also provided for a simplified transition from Phabricator to GitLab.

## Workflow

### Logging in

```
git lab login --host invent.kde.org --token ${YOUR_PRIVATE_TOKEN}
```

Your token is saved in the json file `~/.config/gitlabconfig` by default.
Alternatively, instead of a token, you can also specify a command (`--command`) that returns the token.
This way, you can store the token in a password manager or gpg-encrypted.

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

### Searching for a project

```
git lab search ${NAME}
```

### Creating a snippet

```
git lab snippet ${FILENAME}
```

or

```
echo "Paste data" | git lab snippet
```

## Installation

```
sudo pip3 install -r requirements.txt
sudo ./setup.py install
```

## Contributing

### Run tests
```
pytest
```

### Run linter
```
./scripts/lint.sh
```