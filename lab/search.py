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

# See: https://docs.gitlab.com/ce/api/projects.html#list-all-projects
SUPPORTED_ORDER_BY_KWS = (
    "id",
    "name",
    "path",
    "created_at",
    "updated_at",
    "last_activity_at",
    # Note: Keywords below only work for admins
    "repository_size",
    "storage_size",
    "packages_size",
    "wiki_size",
)


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
        nargs="?",
        help="Search query",
    )

    search_parser.add_argument(
        "--order_by",
        dest="order_by",
        type=str,
        required=False,
        choices=SUPPORTED_ORDER_BY_KWS,
        help=f"Return projects ordered by {''.join(SUPPORTED_ORDER_BY_KWS)}",
    )

    search_parser.add_argument(
        "--sort_by",
        dest="sort_by",
        type=str,
        default="desc",
        choices=("asc", "desc"),
        help="Return projects sorted in asc or desc order. Default is desc.",
    )

    return search_parser


def run(args: argparse.Namespace) -> None:
    """
    :param args: parsed arguments
    """
    search = Search()
    search_query = args.search_query[0] if args.search_query else None
    search.search_projects(search_query, args.order_by, args.sort_by)


class Search(AllInstancesConnection):
    """
    Search class
    """

    def __init__(self) -> None:
        AllInstancesConnection.__init__(self)

    def search_projects(
        self,
        query: Optional[str] = None,
        order_by: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> None:
        """
        Search for a project
        :param query: Search query
        :param order_by: Order objects by
        :param sort_by: sort in asc or desc order
        """
        table = Table()

        kwargs = {
            "search": query,
            "order_by": order_by,
            "sort_by": sort_by,
        }

        for connection in self._connections:
            # There are two possible search endpoints: `/search` and `/projects`
            # The general search endpoint `/search` only supports `order_by=created_at`
            # See: https://docs.gitlab.com/ee/api/search.html#advanced-search-api
            for result in connection.projects.list(**kwargs):
                description: Optional[str] = result.description
                if description:
                    description = description.replace("\n", "")
                    if len(description) > 50:
                        description = description[:50] + "…"
                else:
                    description = "No description"

                table.add_row(
                    [
                        TextFormatting.BOLD + result.path_with_namespace + TextFormatting.END,
                        description,
                        TextFormatting.UNDERLINE + result.ssh_url_to_repo + TextFormatting.END,
                    ]
                )

        table.print()
