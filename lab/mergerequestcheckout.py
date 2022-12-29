"""
Module containing classes for checking out merge requests
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import sys

from gitlab.v4.objects import ProjectMergeRequest
from gitlab.v4.objects import Project
from gitlab.exceptions import GitlabHttpError, GitlabGetError

from git.remote import Remote
from git.refs.reference import Reference

from lab.repositoryconnection import RepositoryConnection
from lab.utils import Utils
from lab.utils import LogType

from typing import Optional


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


    def add_remote(self) -> Optional[Reference]:
        fork_project: Project
        try:
            fork_project = self._connection.projects.get(self.__mr.source_project_id)
        except (GitlabHttpError, GitlabGetError):
            Utils.log(
                LogType.ERROR,
                "The source repository of this merge request could not be found on the GitLab instance.",
            )
            sys.exit(1)

        remote_url: str = fork_project.ssh_url_to_repo
        user: str = self.__mr.author["username"]
        remote_name = f"fork-{user}"

        remote: Remote
        if remote_name not in self._local_repo.remotes:
            remote = Remote.add(self._local_repo, remote_name, remote_url)
        else:
            remote = self._local_repo.remotes[remote_name]

        remote.fetch()

        for ref in remote.refs:
            if ref.name == f"{remote_name}/{self.__mr.source_branch}":
                return ref

        Utils.log(LogType.ERROR, "Failed to find remote ref")
        sys.exit(1)


    def checkout(self, merge_request_id: int) -> None:
        """
        Checks out the merge request with the specified id in the local worktree
        """
        self.__mr = self._remote_project.mergerequests.get(merge_request_id, lazy=False)
        print('Checking out merge request "{}"...'.format(self.__mr.title))
        print("  branch:", self.__mr.source_branch)

        remote_ref = self.add_remote()

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

        head = self._local_repo.create_head(self.__mr.source_branch, remote_ref)
        head.checkout()
        self._local_repo.active_branch.set_tracking_branch(remote_ref)
