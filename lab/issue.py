"""
Module with functionality around single issues.
"""
import argparse
import sys
from typing import Dict, Any, Callable

from gitlab import GitlabGetError
from gitlab.v4.objects import ProjectIssue

from lab.repositoryconnection import RepositoryConnection
from lab.utils import Utils, LogType, TextFormatting, is_valid_time_str


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for issue command
    :param subparsers: subparsers object from global parser
    :return: issues subparser
    """

    issue_parser: argparse.ArgumentParser = subparsers.add_parser(
        "issue", help="Gitlab issue commands."
    )

    issue_parser.add_argument("issue_id", help="Issue ID", metavar="issue_id", type=int)

    issue_subparsers = issue_parser.add_subparsers(
        dest="command", required=True, help="Issue sub command"
    )

    estimate_parser = issue_subparsers.add_parser("estimate")
    estimate_parser_group = estimate_parser.add_mutually_exclusive_group()

    spend_parser = issue_subparsers.add_parser("spend")
    spend_parser_group = spend_parser.add_mutually_exclusive_group()

    estimate_parser_group.add_argument(
        "--update",
        help="Update estimated time (override). E.g. '2d4h'.",
        metavar="time_str",
        type=str,
    )
    estimate_parser_group.add_argument(
        "--reset",
        help="Reset a time estimate for an issue.",
        action="store_true",
    )

    spend_parser_group.add_argument(
        "--update",
        help="Add new time entry (time spent). E.g. '5h30m'.",
        metavar="time_str",
        type=str,
    )
    spend_parser_group.add_argument(
        "--reset",
        help="Reset spent time for an issue.",
        action="store_true",
    )

    return issue_parser


def run(args: argparse.Namespace) -> None:
    """
    Run issue command.
    :param args: parsed arguments
    """
    issue = IssueConnection(args.issue_id)
    if args.command == "estimate":
        if args.update:
            issue.update_estimated(args.update)
        elif args.reset:
            issue.reset_time_estimate()
        else:
            issue.print_estimated()
    elif args.command == "spend":
        if args.update:
            issue.update_spent(args.update)
        elif args.reset:
            issue.reset_spent_time()
        else:
            issue.print_spent()


class IssueConnection(RepositoryConnection):
    def __init__(self, issue_id: int):
        """
        Creates a new issue connection. Requires a valid issue ID for the current project.
        """
        RepositoryConnection.__init__(self)
        try:
            self.issue: ProjectIssue = self._remote_project.issues.get(issue_id, lazy=False)
        except GitlabGetError:
            Utils.log(LogType.WARNING, f"No issue with ID {issue_id}")
            sys.exit(1)

    @property
    def title_bold(self) -> str:
        """Get the title formatted as f´bold text."""
        return f"{TextFormatting.BOLD}{self.issue.title}{TextFormatting.END}"

    @property
    def overdue(self) -> bool:
        """True if the issue has more time spent than was originally estimated."""
        ts: Dict[str, Any] = self.issue.attributes["time_stats"]
        return bool(ts["time_estimate"] <= ts["total_time_spent"])

    def print_estimated(self) -> None:
        """Print short info about the estimated time for the issue."""
        # API endpoint https://python-gitlab.readthedocs.io/en/stable/gl_objects/issues.html
        ts: Dict[str, Any] = self.issue.attributes["time_stats"]

        color: Callable[[str], str] = TextFormatting.red if self.overdue else TextFormatting.green
        estimated: str = ts["human_time_estimate"] or "0h"
        spent: str = color(ts["human_total_time_spent"] or "0h")

        text = f"{self.title_bold} is estimated at {estimated} (spent: {spent})"

        print(text)

    def update_estimated(self, time_str: str) -> None:
        """Updates the estimated time for the issue. Overrides the old value."""
        if not is_valid_time_str(time_str):
            Utils.log(LogType.WARNING, f"{time_str} is an invalid time string.")
            sys.exit(1)

        self.issue.time_estimate(time_str)
        self.issue.save()
        print(TextFormatting.green(f"Set estimate to {time_str}"))

    def print_spent(self) -> None:
        """Prints a short info about the total time spent on this issue."""
        # API endpoint https://python-gitlab.readthedocs.io/en/stable/gl_objects/issues.html
        ts: Dict[str, Any] = self.issue.attributes["time_stats"]

        color: Callable[[str], str] = TextFormatting.red if self.overdue else TextFormatting.green
        estimated: str = color(ts["human_time_estimate"] or "0h")
        spent: str = ts["human_total_time_spent"] or "0h"

        text = f"{self.title_bold} has {spent} tracked (estimated: {estimated})"

        print(text)

    def update_spent(self, time_str: str) -> None:
        """Adds time spent to the already existing time spent."""
        if not is_valid_time_str(time_str):
            Utils.log(LogType.WARNING, f"{time_str} is an invalid time string.")
            sys.exit(1)

        self.issue.add_spent_time(time_str)
        self.issue.save()
        print(TextFormatting.green(f"Added time entry of {time_str}"))

    def reset_time_estimate(self) -> None:
        """Reset time estimate on an issue"""
        self.issue.reset_time_estimate()
        print(TextFormatting.green(f"Time estimate reset."))

    def reset_spent_time(self) -> None:
        """Rest time spent on an issue"""
        self.issue.reset_spent_time()
        print(TextFormatting.green(f"Spent time reset."))
