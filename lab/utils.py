"""
Module containing classes for common tasks
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later
import shutil
import subprocess

import sys
import os
import shlex
from typing import List

from urllib.parse import ParseResult, urlparse, quote_plus
from enum import Enum, auto

from git import Repo
from git.exc import InvalidGitRepositoryError


class LogType(Enum):
    """
    Enum representing the type of log message
    """

    Info = auto()
    Warning = auto()
    Error = auto()


class TextFormatting:  # pylint: disable=too-few-public-methods
    """
    Structure containing constants for working with text formatting
    """

    purple: str = "\033[0;95m"
    cyan: str = "\033[0;36m"
    darkcyan: str = "\033[0;96m"
    blue: str = "\033[0;34m"
    green: str = "\033[0;32m"
    yellow: str = "\033[0;33m"
    red: str = "\033[0;31m"
    lightred: str = "\033[1;31m"
    bold: str = "\033[1m"
    underline: str = "\033[4m"
    end: str = "\033[0m"


class Utils:
    """
    This class contains static methods for common tasks
    """

    @staticmethod
    def str_id_for_url(url: str) -> str:
        """
        Returns the url encoded string id for a repository
        """
        normalized_url: str = Utils.normalize_url(url)
        repository_url: ParseResult = urlparse(normalized_url.replace(".git", ""))
        return quote_plus(repository_url.path[1:])

    @staticmethod
    def log(log_type: LogType, *message: str) -> None:
        """
        Prints a message in a colorful and consistent way
        """
        prefix = TextFormatting.bold
        if log_type == LogType.Info:
            prefix += "Info"
        elif log_type == LogType.Warning:
            prefix += TextFormatting.yellow + "Warning" + TextFormatting.end
        elif log_type == LogType.Error:
            prefix += TextFormatting.red + "Error" + TextFormatting.end

        prefix += TextFormatting.end

        if len(prefix) > 0:
            prefix += ":"

        print(prefix, *message)

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Creates a correctly parsable url from a git remote url.
        Git remote urls can also be written in scp syntax, which is technically not a real url.

        Example: git@invent.kde.org:KDE/kaidan becomes ssh://git@invent.kde.org/KDE/kaidan
        """
        result = urlparse(url)

        # url is already fine
        if result.scheme != "":
            return url

        if "@" in url and ":" in url:
            return "ssh://" + url.replace(":", "/")

        Utils.log(LogType.Error, "Invalid url", url)
        sys.exit(1)

    @staticmethod
    def ssh_url_from_http(url: str) -> str:
        """
        Creates an ssh url from a http url

        :return ssh url
        """

        return url.replace("https://", "ssh://git@").replace("http://", "ssh://git@")

    @staticmethod
    def gitlab_instance_url(repository: str) -> str:
        """
        returns the gitlab instance url of a git remote url
        """
        # parse url
        repository_url: ParseResult = urlparse(repository)

        # Valid url
        if repository_url.scheme != "" and repository_url.path != "":
            # If the repository is using some kind of http, can know whether to use http or https
            if "http" in repository_url.scheme:
                if repository_url.scheme and repository_url.hostname:
                    return repository_url.scheme + "://" + repository_url.hostname

            # Else assume https.
            # redirects don't work according to
            # https://python-gitlab.readthedocs.io/en/stable/api-usage.html.
            if repository_url.hostname:
                return "https://" + repository_url.hostname

        # non valid url (probably scp syntax)
        if "@" in repository and ":" in repository:
            # create url in form of ssh://git@github.com/KDE/kaidan
            repository_url = urlparse("ssh://" + repository.replace(":", "/"))

            if repository_url.hostname:
                return "https://" + repository_url.hostname

        # If everything failed, exit
        Utils.log(LogType.Error, "Failed to detect GitLab instance url")
        sys.exit(1)

    @staticmethod
    def get_cwd_repo() -> Repo:
        """
        Creates a Repo object for the current directory.
        If it is not a git repository, an error is shown.
        """
        try:
            return Repo(os.getcwd())
        except InvalidGitRepositoryError:
            Utils.log(LogType.Error, "Current directory is not a git repository")
            sys.exit(1)

    @staticmethod
    def editor() -> List[str]:
        """
        return prefered user editor using git configuration
        """
        repo = Utils.get_cwd_repo()
        config = repo.config_reader()
        editor: str = config.get_value("core", "editor", "")
        if not editor:
            if "EDITOR" in os.environ:
                editor = os.environ["EDITOR"]
            elif "VISUAL" in os.environ:
                editor = os.environ["VISUAL"]
            elif shutil.which("editor"):
                editor = "editor"
            else:
                editor = "vi"

        return shlex.split(editor)

    @staticmethod
    def xdg_open(path: str) -> None:
        """
        Open path with xdg-open
        :param path: path to open
        """
        subprocess.call(("xdg-open", path))

    @staticmethod
    def ask_bool(question: str) -> bool:
        """
        Ask a yes or no question
        :param question: text for the question
        :return: whether the user answered yes
        """
        answer: str = input("{} (y/n)\n".format(question))
        if answer != "y":
            return False

        return True
