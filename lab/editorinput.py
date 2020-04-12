# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import subprocess
import tempfile

from typing import List

from lab.utils import Utils

"""
Structure representing the editorinput.
"""
class EditorInput:
    __fulltext: str = "\n"
    title: str
    body: str

    def __fulltext_remove_comments(self):
        newtext = ""

        for line in self.__fulltext.splitlines():
            if line.startswith("#"):
                continue

            newtext += (line + "\n")

        self.__fulltext = newtext

    def __input(self) -> None:
        file = tempfile.NamedTemporaryFile("r+")
        file.write("# Please enter a title below (one line)\n")
        file.write("\n")
        file.write("# Please enter a description below (optional) (multiple lines)\n")
        file.write("\n")
        file.write("\n")
        file.write("# Lines starting with '#' will be ignored.\n")
        file.write("# An empty title aborts the workflow.")
        file.flush()

        subprocess.call(["editor", file.name])

        file.seek(0)
        self.__fulltext = file.read()

    def __fulltext_valid(self) -> bool:
        lines = self.__fulltext.splitlines()

        try:
            if (lines[0] == ""):
                Utils.log(Utils.LogType.Error, "The first line (title) can't be empty")
                return False
        except IndexError:
            Utils.log(Utils.LogType.Error, "The first line (title) can't be empty")
            return False

        return True


    def __init__(self) -> None:
        self.__input()
        self.__fulltext_remove_comments()
        if (not self.__fulltext_valid()):
            Utils.log(Utils.LogType.Error, "Text not valid, aborting")
            exit(1)

        lines: List[str] = self.__fulltext.splitlines()
        self.title = lines[0]
        self.body = "\n".join(lines[1:])
