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


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for paste command
    :param subparsers: subparsers object from global parser
    :return: merge request creation subparser
    """
    snippet_parser: argparse.ArgumentParser = subparsers.add_parser(
        "snippet", help="Create a snippet from stdin or file", aliases=["paste"]
    )
    snippet_parser.add_argument("--title", help="Add a custom title", default="Empty title")
    snippet_parser.add_argument(
        "filename",
        metavar="str",
        type=str,
        nargs="?",
        help="File name to uplad",
    )
    return snippet_parser


def run(args: argparse.Namespace) -> None:
    """
    run snippet creation commands
    :param args: parsed arguments
    """
    snippets = Snippets()
    file: TextIO
    if args.filename:
        try:
            file = open(args.filename, "r")
        except FileNotFoundError:
            Utils.log(LogType.ERROR, "Failed to open file", args.filename)
            sys.exit(1)
    else:
        file = sys.stdin

    snippets.paste(file, title=args.title)


class Snippets(RepositoryConnection):
    """
    Class for creating snippets
    """

    def __init__(self) -> None:
        RepositoryConnection.__init__(self)

    def paste(self, file: TextIO, title: Optional[str]) -> None:
        """
        paste the contents of a TextIO object
        """
        snippet: Snippet = self._connection.snippets.create(
            {"title": title, "file_name": file.name, "content": file.read(), "visibility": "public"}
        )
        Utils.log(LogType.INFO, "Created snippet at", snippet.web_url)
        print("You can access it raw at", snippet.raw_url)
