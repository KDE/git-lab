"""
Module containing issues command
"""

# SPDX-FileCopyrightText: 2020 Benjamin Port <benjamin.port@kde.org>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import os
import sys
from typing import List, Dict

from gitlab.v4.objects import ProjectIssue
from gitlab.exceptions import GitlabGetError

from lab.repositoryconnection import RepositoryConnection
from lab.utils import TextFormatting, Utils, LogType
from lab.table import Table


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for issues command
    :param subparsers: subparsers object from global parser
    :return: issues subparser
    """

    issues_parser: argparse.ArgumentParser = subparsers.add_parser("issues", help="Gitlab issues")

    issues_parser.add_argument(
        "--opened",
        help="Show opened issues",
        action="store_true",
    )
    issues_parser.add_argument(
        "--closed",
        help="Show closed issues",
        action="store_true",
    )
    group = issues_parser.add_mutually_exclusive_group()
    group.add_argument(
        "--assigned",
        help="Show only issues assigned to me",
        action="store_true",
    )
    group.add_argument(
        "--project",
        help="Show all project issues and not only the one you authored",
        action="store_true",
    )
    issues_parser.add_argument(
        "issue_id", help="Show issue by id if provided", metavar="issue_id", type=int, nargs="?"
    )
    issues_parser.add_argument("--web", help="open on web browser", action="store_true")
    return issues_parser


def run(args: argparse.Namespace) -> None:
    """
    run merge request list command
    :param args: parsed arguments
    """
    if args.issue_id is not None:
        issue: IssuesShow = IssuesShow(args.issue_id)
        if args.web:
            issue.open_web()
        else:
            print(issue)
    else:
        lister: IssuesList = IssuesList(args.opened, args.closed, args.assigned, args.project)
        if args.web:
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
            formatting = TextFormatting.GREEN if issue.state == "opened" else TextFormatting.RED
            row: List[str] = [
                TextFormatting.BOLD + issue.references["full"] + TextFormatting.END,
                issue.title,
                formatting + issue.state + TextFormatting.END,
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
            Utils.log(LogType.ERROR, "Issue are disabled for this project")


class IssuesShow(RepositoryConnection):
    """
    Show issue
    """

    def __init__(self, issue_id: int):
        RepositoryConnection.__init__(self)
        try:
            self.issue: ProjectIssue = self._remote_project.issues.get(issue_id, lazy=False)
        except GitlabGetError:
            Utils.log(LogType.WARNING, f"No issue with ID {issue_id}")
            sys.exit(1)

    def open_web(self) -> None:
        """
        Open issue with xdg-open
        """
        Utils.xdg_open(self.issue.web_url)

    def __str__(self) -> str:
        formatting = TextFormatting.GREEN if self.issue.state == "opened" else TextFormatting.RED
        textbuffer: str = ""
        textbuffer += (
            TextFormatting.BOLD
            + self.issue.title
            + TextFormatting.END
            + f" (#{self.issue.iid}) "
            + formatting
            + self.issue.state
            + TextFormatting.END
            + os.linesep
        )
        textbuffer += self.issue.description
        return textbuffer
