"""
Module providing search capabilities
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from lab.repositoryconnection import RepositoryConnection
from lab.table import Table
from lab.utils import TextFormatting


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for merge request creation command
    :param subparsers: subparsers object from global parser
    :return: merge request creation subparser
    """
    search_parser: argparse.ArgumentParser = subparsers.add_parser(
        "search", help="Search for a repository"
    )
    search_parser.add_argument(
        "search_query", type=str, nargs=1, help="Search query",
    )
    return search_parser


def run(args: argparse.Namespace) -> None:
    """
    :param args: parsed arguments
    """
    search = Search()
    search.search_projects(args.search_query)


class Search(RepositoryConnection):
    """
    Search class
    """

    def __init__(self) -> None:
        RepositoryConnection.__init__(self)

    def search_projects(self, query: str) -> None:
        """
        Search for a project
        :param query: Search query
        """
        table = Table()
        for result in self.connection().search("projects", query):
            table.add_row(
                [
                    TextFormatting.bold + result["path_with_namespace"] + TextFormatting.end,
                    result["description"],
                    TextFormatting.underline + result["ssh_url_to_repo"] + TextFormatting.end,
                ]
            )

        table.print()
