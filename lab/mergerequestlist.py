# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>

from gitlab.v4.objects import ProjectMergeRequest

from lab.repositoryconnection import RepositoryConnection
from lab.utils import Utils
from lab.table import Table

from typing import List

"""
Lists all merge requests of the current repository
"""
class MergeRequestList(RepositoryConnection):
    for_project: bool = False

    def __init__(self, for_project: bool) -> None:
        RepositoryConnection.__init__(self)
        self.for_project = for_project

    def print_formatted_list(self) -> None:
        mrs: List[ProjectMergeRequest] = []
        if (self.for_project):
            mrs = self.remote_project().mergerequests.list()
        else:
            mrs = self.connection().mergerequests.list()

        t = Table()

        for mr in mrs:
            row: List[str] = []
            row.append(Utils.TextFormatting.bold + mr.references["full"] + Utils.TextFormatting.end)
            row.append(mr.title)

            if (mr.state == "merged"):
                row.append(Utils.TextFormatting.green + mr.state + Utils.TextFormatting.end)
            elif (mr.state == "opened"):
                row.append(mr.state)
            elif (mr.state == "closed"):
                row.append(Utils.TextFormatting.red + mr.state + Utils.TextFormatting.end)

            t.add_row(row)

        t.print()
