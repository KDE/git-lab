"""
Module containing classes for creating merge requests
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import sys

from typing import TextIO, Optional

from gitlab.v4.objects import Snippet

from lab.repositoryconnection import RepositoryConnection
from lab.utils import Utils, LogType


def run(filename: Optional[str], title: Optional[str]) -> None:
    """
    run snippet creation commands
    :param args: parsed arguments
    """
    snippets = Snippets()
    file: TextIO
    if filename:
        try:
            file = open(filename, "r")
        except FileNotFoundError:
            Utils.log(LogType.Error, "Failed to open file", filename)
            sys.exit(1)
    else:
        file = sys.stdin

    snippets.paste(file, title=title)


class Snippets(RepositoryConnection):
    """
    Class for creating snippets
    """

    def __init__(self) -> None:
        RepositoryConnection.__init__(self)

    def paste(self, file: TextIO, title: str) -> None:
        """
        paste the contents of a TextIO object
        """
        snippet: Snippet = self._connection.snippets.create(
            {"title": title, "file_name": file.name, "content": file.read(), "visibility": "public"}
        )
        Utils.log(LogType.Info, "Created snippet at", snippet.web_url)
        print("You can access it raw at", snippet.raw_url)
