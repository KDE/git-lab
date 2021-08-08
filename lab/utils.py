"""
Module containing classes for common tasks
"""

import os
import shlex

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from enum import Enum, auto
from typing import List, Optional, Final
from urllib.parse import ParseResult, urlparse

from git import Repo
from git.exc import InvalidGitRepositoryError


def removesuffix(string: str, suffix: str) -> str:
    """
    Compatiblity function for python < 3.9
    """
    if sys.version_info >= (3, 9):
        return string.removesuffix(suffix)

    if string.endswith(suffix):
        return string[: -len(suffix)]

    return string


class LogType(Enum):
    """
    Enum representing the type of log message
    """

    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class TextFormatting:  # pylint: disable=too-few-public-methods
    """
    Structure containing constants for working with text formatting
    """

    PURPLE: Final[str] = "\033[0;95m"
    CYAN: Final[str] = "\033[0;36m"
    DARKCYAN: Final[str] = "\033[0;96m"
    BLUE: Final[str] = "\033[0;34m"
    GREEN: Final[str] = "\033[0;32m"
    YELLOW: Final[str] = "\033[0;33m"
    RED: Final[str] = "\033[0;31m"
    LIGHTRED: Final[str] = "\033[1;31m"
    BOLD: Final[str] = "\033[1m"
    UNDERLINE: Final[str] = "\033[4m"
    END: Final[str] = "\033[0m"


class Utils:
    """
    This class contains static methods for common tasks
    """

    @staticmethod
    def str_id_for_url(url: str) -> str:
        """
        Returns the unencoded string id for a repository
        """
        normalized_url: str = Utils.normalize_url(url)
        normalized_url = removesuffix(normalized_url, ".git")
        normalized_url = removesuffix(normalized_url, "/")

        repository_url: ParseResult = urlparse(normalized_url)
        return repository_url.path[1:]

    @staticmethod
    def log(log_type: LogType, *message: str) -> None:
        """
        Prints a message in a colorful and consistent way
        """
        prefix = TextFormatting.BOLD
        if log_type == LogType.INFO:
            prefix += "Info"
        elif log_type == LogType.WARNING:
            prefix += TextFormatting.YELLOW + "Warning" + TextFormatting.END
        elif log_type == LogType.ERROR:
            prefix += TextFormatting.RED + "Error" + TextFormatting.END

        prefix += TextFormatting.END

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

        Utils.log(LogType.ERROR, "Invalid url", url)
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
        Utils.log(LogType.ERROR, "Failed to detect GitLab instance url")
        sys.exit(1)

    @staticmethod
    def get_cwd_repo() -> Repo:
        """
        Creates a Repo object from one of the parent directories of the current directories.
        If it can not find a git repository, an error is shown.
        """
        try:
            return Repo(Utils.find_dotgit(os.getcwd()))
        except InvalidGitRepositoryError:
            Utils.log(LogType.ERROR, "Current directory is not a git repository")
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
        answer: str = input("{} [y/n] ".format(question))
        if answer == "y":
            return True

        return False

    @staticmethod
    def find_dotgit(path: str) -> Optional[str]:
        """
        Finds the parent directory containing .git, and returns it
        :param: path to start climbing from
        :return: resulting path
        """
        abspath = os.path.abspath(path)

        if ".git" in os.listdir(abspath):
            return abspath

        parent_dir: str = os.path.abspath(abspath + os.path.sep + os.path.pardir)

        # No parent dir exists, we are at the root filesystem
        if os.path.samefile(parent_dir, path):
            return None

        return Utils.find_dotgit(parent_dir)

    @staticmethod
    def pretty_date(date_string: str, now: datetime = datetime.now(timezone.utc)) -> str:
        """Transform an ISO-8601 date-string and transform it into a human readable format.
        Taken almost verbatim from:
            https://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python
        """
        time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        try:
            diff = now - time
        except TypeError:
            # We most likely tried to subtract an offset-naive and  an offset-aware date
            now = now.replace(tzinfo=None)
            time = time.replace(tzinfo=None)
            diff = now - time

        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ""

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return "a minute ago"
            if second_diff < 3600:
                return str(second_diff // 60) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str(second_diff // 3600) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff // 7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff // 30) + " months ago"
        return str(day_diff // 365) + " years ago"

    @staticmethod
    def pretty_time_delta(seconds: int = 0) -> str:
        """
        Pretty print a given timedelta in seconds human readable.
        """
        seconds = abs(seconds)  # Make seconds unsigned
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days:
            return "%dd %dh %dm %ds" % (days, hours, minutes, seconds)
        if hours:
            return "%dh %dm %ds" % (hours, minutes, seconds)
        if minutes:
            return "%dm %ds" % (minutes, seconds)
        return "%ds" % (seconds,)
