"""
Module containing classes for checking out merge requests
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import sys

from gitlab.v4.objects import ProjectMergeRequest

from lab.repositoryconnection import RepositoryConnection
from lab.utils import Utils
from lab.utils import LogType


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for checking-out merge request command
    :param subparsers: subparsers object from global parser
    :return: checking-out merge request subparser
    """
    checkouter_parser: argparse.ArgumentParser = subparsers.add_parser(
        "checkout", help="check out a remote merge request", aliases=["patch"]
    )
    checkouter_parser.add_argument(
        "number",
        metavar="int",
        type=int,
        nargs=1,
        help="Merge request number to checkout",
    )
    return checkouter_parser


def run(args: argparse.Namespace) -> None:
    """
    run checking-out merge request command
    :param args: parsed arguments
    """
    checkouter: MergeRequestCheckout = MergeRequestCheckout()
    checkouter.checkout(args.number[0])


class MergeRequestCheckout(RepositoryConnection):
    """
    Check out a merge request in the current git repository
    """

    # private
    __mr: ProjectMergeRequest

    def __init__(self) -> None:
        RepositoryConnection.__init__(self)

    def checkout(self, merge_request_id: int) -> None:
        """
        Checks out the merge request with the specified id in the local worktree
        """
        self.__mr = self._remote_project.mergerequests.get(merge_request_id, lazy=False)
        print('Checking out merge request "{}"...'.format(self.__mr.title))
        print("  branch:", self.__mr.source_branch)

        fetch_info = self._local_repo.remotes.origin.fetch(
            "merge-requests/{}/head".format(merge_request_id)
        )[0]
        if self.__mr.source_branch in self._local_repo.refs:
            # Make sure not to overwrite local changes
            overwrite = Utils.ask_bool(
                'Branch "{}" already exists locally, do you want to overwrite it?'.format(
                    self.__mr.source_branch
                )
            )

            if not overwrite:
                print("Aborting")
                sys.exit(1)

            # If the branch that we want to overwrite is currently checked out,
            # that will of course not work, so try to switch to another branch in the meantime.
            if self.__mr.source_branch == self._local_repo.head.reference.name:
                if "main" in self._local_repo.refs:
                    self._local_repo.refs.main.checkout()
                elif "master" in self._local_repo.refs:
                    self._local_repo.refs.master.checkout()
                else:
                    Utils.log(
                        LogType.ERROR,
                        "The branch that you want to overwrite is currently checked out \
                        and no other branch to temporarily switch to could be found. Please check out \
                        a different branch and try again.",
                    )
                    sys.exit(1)

            self._local_repo.delete_head(self.__mr.source_branch, "-f")

        head = self._local_repo.create_head(self.__mr.source_branch, fetch_info.ref)
        head.checkout()
