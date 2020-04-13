"""
Module containing classes for checking out merge requests
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sys

from gitlab.v4.objects import ProjectMergeRequest

from lab.repositoryconnection import RepositoryConnection


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
        self.__mr = self.remote_project().mergerequests.get(merge_request_id, lazy=False)
        print('Checking out merge request "{}"...'.format(self.__mr.title))
        print("  branch:", self.__mr.source_branch)

        fetch_info = self.local_repo().remotes.origin.fetch(
            "merge-requests/{}/head".format(merge_request_id)
        )[0]
        if self.__mr.source_branch in self.local_repo().refs:
            # Make sure not to overwrite local changes
            answer: str = input(
                'Branch "{}" already exists locally, do you want to overwrite it? (y/n)\n'.format(
                    self.__mr.source_branch
                )
            )
            if answer != "y":
                print("Aborting")
                sys.exit(1)

            self.local_repo().refs.master.checkout()
            self.local_repo().delete_head(self.__mr.source_branch, "-f")

        head = self.local_repo().create_head(self.__mr.source_branch, fetch_info.ref)
        head.checkout()
