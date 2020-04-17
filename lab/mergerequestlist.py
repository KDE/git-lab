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
    merged: bool = True
    opened: bool = True
    closed: bool = True

    def __init__(self, for_project: bool, merged: bool, opened: bool, closed: bool) -> None:
        RepositoryConnection.__init__(self)
        self.for_project = for_project
        if not merged and not opened and not closed:
            return
        self.merged = merged
        self.opened = opened
        self.closed = closed

    def print_formatted_list(self) -> None:
        """
        prints the list of merge requests to the terminal formatted as a table
        """
        merge_requests: List[ProjectMergeRequest] = []

        if self.for_project:
            base = self.remote_project()
        else:
            base = self.connection()

        if self.merged and self.opened and self.closed:
            merge_requests = base.mergerequests.list()
        else:
            if self.merged:
                merge_requests += base.mergerequests.list(state="merged")
            if self.opened:
                merge_requests += base.mergerequests.list(state="opened")
            if self.closed:
                merge_requests += base.mergerequests.list(state="closed")

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
