"""
Module providing search capabilities
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from typing import Optional

from lab.allinstancesconnection import AllInstancesConnection
from lab.table import Table
from lab.utils import TextFormatting


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for search command
    :param subparsers: subparsers object from global parser
    :return: search subparser
    """
    search_parser: argparse.ArgumentParser = subparsers.add_parser(
        "search", help="Search for a repository"
    )
    search_parser.add_argument(
        "search_query",
        type=str,
        nargs=1,
        help="Search query",
    )
    return search_parser


def run(args: argparse.Namespace) -> None:
    """
    :param args: parsed arguments
    """
    search = Search()
    search.search_projects(args.search_query[0])


class Search(AllInstancesConnection):
    """
    Search class
    """

    def __init__(self) -> None:
        AllInstancesConnection.__init__(self)

    def search_projects(self, query: str) -> None:
        """
        Search for a project
        :param query: Search query
        """
        table = Table()

        for connection in self._connections:
            for result in connection.search("projects", query):
                description: Optional[str] = result["description"]
                if description:
                    description = description.replace("\n", "")
                    if len(description) > 50:
                        description = description[:50] + "…"
                else:
                    description = "No description"

                table.add_row(
                    [
                        TextFormatting.BOLD + result["path_with_namespace"] + TextFormatting.END,
                        description,
                        TextFormatting.UNDERLINE + result["ssh_url_to_repo"] + TextFormatting.END,
                    ]
                )

        table.print()
