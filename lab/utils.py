"""
Module containing classes for common tasks
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from urllib.parse import ParseResult, urlparse, quote_plus
from enum import IntEnum, auto


class Utils:
    """
    This class contains static methods for common tasks
    """

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
        prefix = Utils.TextFormatting.bold
        if log_type == Utils.LogType.Info:
            prefix += "Info"
        elif log_type == Utils.LogType.Warning:
            prefix += Utils.TextFormatting.yellow + "Warning" + Utils.TextFormatting.end
        elif log_type == Utils.LogType.Error:
            prefix += Utils.TextFormatting.red + "Error" + Utils.TextFormatting.end

        prefix += Utils.TextFormatting.end

        if len(prefix) > 0:
            prefix += ":"

        print(prefix, *message)
