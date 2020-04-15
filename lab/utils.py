"""
Module containing classes for common tasks
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sys

from urllib.parse import ParseResult, urlparse, quote_plus
from enum import IntEnum, auto


class LogType(IntEnum):
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
        repository_url: ParseResult = urlparse(url.replace(".git", ""))
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
        result = urlparse(url)

        # url is already fine
        if result.scheme != "":
            return url

        if "@" in url and ":" in url:
            return "ssh://" + url.replace(":", "/")

        Utils.log(LogType.Error, "Invalid url", url)
        exit(1)

    @staticmethod
    def gitlab_instance_url(repository: str) -> str:
        # parse url
        repository_url: ParseResult = urlparse(repository)

        # Valid url
        if repository_url.scheme != "" and repository_url.path != "":
            # If the repository is using some kind of http, can know whether to use http or https
            if "http" in repository_url.scheme:
                return repository_url.scheme + "://" + repository_url.hostname

            # Else assume https.
            # redirects don't work according to https://python-gitlab.readthedocs.io/en/stable/api-usage.html.
            return "https://" + repository_url.hostname

        # non valid url (probably scp syntax)
        if "@" in repository and ":" in repository:
            # create url in form of ssh://git@github.com/KDE/kaidan
            repository_url = urlparse("ssh://" + repository.replace(":", "/"))

            return "https://" + repository_url.hostname

        # If everything failed, exit
        Utils.log(LogType.Error, "Failed to detect GitLab instance url")
        sys.exit(1)
