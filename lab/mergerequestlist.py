"""
Module containing classes for listing merge requests
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from typing import List

from gitlab.v4.objects import ProjectMergeRequest

from lab.repositoryconnection import RepositoryConnection
from lab.utils import TextFormatting
from lab.table import Table


class MergeRequestList(RepositoryConnection):
    """
    Lists all merge requests of the current repository
    """

    for_project: bool = False

    def __init__(self, for_project: bool) -> None:
        RepositoryConnection.__init__(self)
        self.for_project = for_project

    def print_formatted_list(self) -> None:
        """
        prints the list of merge requests to the terminal formatted as a table
        """
        merge_requests: List[ProjectMergeRequest] = []
        if self.for_project:
            merge_requests = self.remote_project().mergerequests.list()
        else:
            merge_requests = self.connection().mergerequests.list()

        table = Table()

        for merge_request in merge_requests:
            row: List[str] = []
            row.append(TextFormatting.bold + merge_request.references["full"] + TextFormatting.end)
            row.append(merge_request.title)

            if merge_request.state == "merged":
                row.append(TextFormatting.green + merge_request.state + TextFormatting.end)
            elif merge_request.state == "opened":
                row.append(merge_request.state)
            elif merge_request.state == "closed":
                row.append(TextFormatting.red + merge_request.state + TextFormatting.end)

            table.add_row(row)

        table.print()
