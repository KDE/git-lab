"""
Module containing classes for getting user input using an editor
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import subprocess
import tempfile

import sys

from typing import List

from lab.utils import Utils, LogType


class EditorInput:  # pylint: disable=too-few-public-methods
    """
    Structure representing the editorinput.
    """

    __fulltext: str = "\n"
    title: str
    body: str

    def __fulltext_remove_comments(self) -> None:
        newtext = ""

        for line in self.__fulltext.splitlines():
            if line.startswith("#"):
                continue

            newtext += line + "\n"

        self.__fulltext = newtext

    def __input(self, extra_text: str, placeholder_title: str, placeholder_body: str) -> None:
        file = tempfile.NamedTemporaryFile("r+")
        file.write("# Please enter a title below (one line)\n")
        file.write("{}\n".format(placeholder_title))
        file.write("# Please enter a description below (optional) (multiple lines)\n")
        file.write("{}\n".format(placeholder_body))
        file.write("\n")
        file.write("# Lines starting with '#' will be ignored.\n")
        file.write("# An empty title aborts the workflow.\n")
        file.write("# {}".format(extra_text))
        file.flush()

        subprocess.call([Utils.editor(), file.name], shell=True)

        file.seek(0)
        self.__fulltext = file.read()

    def __fulltext_valid(self) -> bool:
        lines = self.__fulltext.splitlines()

        if not lines or not lines[0]:
            Utils.log(LogType.Error, "The first line (title) can't be empty")
            return False

        return True

    def __init__(
        self, extra_text: str = "", placeholder_title: str = "", placeholder_body: str = ""
    ) -> None:
        self.__input(extra_text, placeholder_title, placeholder_body)
        self.__fulltext_remove_comments()
        if not self.__fulltext_valid():
            Utils.log(LogType.Error, "Text not valid, aborting")
            sys.exit(1)

        lines: List[str] = self.__fulltext.splitlines()

        self.title = lines[0]
        self.body = "\n".join(lines[1:])
