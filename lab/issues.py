"""
Module containing issues command
"""

# SPDX-FileCopyrightText: 2020 Benjamin Port <benjamin.port@kde.org>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import os
import sys
from typing import List, Dict, Optional

from gitlab.v4.objects import ProjectIssue, GitlabGetError

from lab.repositoryconnection import RepositoryConnection
from lab.utils import TextFormatting, Utils, LogType
from lab.table import Table


def run(issue_id: int, opened: bool, closed: bool, assigned: bool, project: bool, web: bool) -> None:
    """
    run merge request list command
    :param args: parsed arguments
    """
    if issue_id != -1:
        issue: IssuesShow = IssuesShow(issue_id)
        if web:
            issue.open_web()
        else:
            print(issue)
    else:
        lister: IssuesList = IssuesList(opened, closed, assigned, project)
        if web:
            lister.open_web()
        else:
            lister.print_formatted_list()


class IssuesList(RepositoryConnection):
    """
    Lists all merge requests of the current repository
    """

    opened: bool = True
    closed: bool = True
    assigned: bool = False
    project: bool = False

    def __init__(self, opened: bool, closed: bool, assigned: bool, for_project: bool) -> None:
        RepositoryConnection.__init__(self)
        self.opened = opened
        self.closed = closed
        self.assigned = assigned
        self.for_project = for_project

    def print_formatted_list(self) -> None:
        """
        prints the list of issues to the terminal formatted as a table
        """
        table = Table()
        args: Dict[str, str] = {}

        # compute filters
        state: str = "all"
        if self.opened and not self.closed:
            state = "opened"
        elif self.closed and not self.opened:
            state = "closed"
        args["state"] = state

        issues: List[ProjectIssue] = []
        if not self.for_project and self.assigned:
            # List issues all over the instance assigned to me
            args["scope"] = "assigned_to_me"
            issues = self._connection.issues.list(**args)
        elif not self.for_project and not self.assigned:
            # Request both created and assigned issues on the whole instance
            args["scope"] = "created_by_me"
            issues = self._connection.issues.list(**args)
            args["scope"] = "assigned_to_me"
            issues += self._connection.issues.list(**args)
        elif self.for_project and not self.assigned:
            # Request all issues on the current project
            args["scope"] = "all"
            issues = self._remote_project.issues.list(**args)

        for issue in issues:
            formatting = TextFormatting.green if issue.state == "opened" else TextFormatting.red
            row: List[str] = [
                TextFormatting.bold + issue.references["full"] + TextFormatting.end,
                issue.title,
                formatting + issue.state + TextFormatting.end,
            ]

            table.add_row(row)

        table.print()

    def open_web(self) -> None:
        """
        Open issue with xdg-open
        """
        if self._remote_project.issues_enabled:
            Utils.xdg_open(f"{self._remote_project.web_url}/-/issues")
        else:
            Utils.log(LogType.Error, "Issue are disabled for this project")


class IssuesShow(RepositoryConnection):
    """
    Show issue
    """

    def __init__(self, issue_id: int):
        RepositoryConnection.__init__(self)
        try:
            self.issue: ProjectIssue = self._remote_project.issues.get(issue_id, lazy=False)
        except GitlabGetError:
            Utils.log(LogType.Warning, f"No issue with ID {issue_id}")
            sys.exit(1)

    def open_web(self) -> None:
        """
        Open issue with xdg-open
        """
        Utils.xdg_open(self.issue.web_url)

    def __str__(self) -> str:
        formatting = TextFormatting.green if self.issue.state == "opened" else TextFormatting.red
        textbuffer: str = ""
        textbuffer += (
            TextFormatting.bold
            + self.issue.title
            + TextFormatting.end
            + f" (#{self.issue.iid}) "
            + formatting
            + self.issue.state
            + TextFormatting.end
            + os.linesep
        )
        textbuffer += self.issue.description
        return textbuffer
