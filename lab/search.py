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


def run(search_query: str) -> None:
    """
    :param args: parsed arguments
    """
    search = Search()
    search.search_projects(search_query)


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
                        TextFormatting.bold + result["path_with_namespace"] + TextFormatting.end,
                        description,
                        TextFormatting.underline + result["ssh_url_to_repo"] + TextFormatting.end,
                    ]
                )

        table.print()
