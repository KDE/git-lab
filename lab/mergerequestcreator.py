"""
Module containing classes for creating merge requests
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from gitlab.v4.objects import Project
from gitlab.exceptions import GitlabCreateError

from lab.repositoryconnection import RepositoryConnection
from lab.utils import Utils
from lab.editorinput import EditorInput


class MergeRequestCreator(RepositoryConnection):
    """
    Class for creating a merge request,
    including forking the remote repository and pushing to the fork.
    """

    # private
    __remote_fork: Project
    __gitlab_token: str

    def __init__(self) -> None:
        RepositoryConnection.__init__(self)

    def fork(self) -> None:
        """
        Try to create a fork of the remote repository.
        If the fork already exists, no new fork will be created.
        """
        try:
            self.__remote_fork = self.remote_project().forks.create({})
            self.local_repo().create_remote("fork", url=self.__remote_fork.http_url_to_repo)
        except GitlabCreateError:
            if "fork" in self.local_repo().remotes:
                Utils.log(Utils.LogType.Info, "Fork already exists, continueing")
            else:
                Utils.log(
                    Utils.LogType.Info,
                    "Fork exists, but no fork remote exists locally, trying to guess the url",
                )
                url = self.connection().user.web_url + "/" + self.remote_project().path
                self.local_repo().create_remote("fork", url=url)

            str_id: str = Utils.str_id_for_url(self.local_repo().remotes.fork.url)
            self.__remote_fork = self.connection().projects.get(str_id)

    def push(self) -> None:
        """
        pushes the local repository to the fork remote
        """
        self.local_repo().remotes.fork.push()

    def create_mr(self) -> None:
        """
        Creates a merge request with the changes from the current branch
        """
        e_input = EditorInput()

        try:
            merge_request = self.__remote_fork.mergerequests.create(
                {
                    "source_branch": self.local_repo().active_branch.name,
                    "target_branch": "master",
                    "title": e_input.title,
                    "description": e_input.body,
                    "target_project_id": self.remote_project().id,
                    "allow_maintainer_to_push": True,
                }
            )
            Utils.log(Utils.LogType.Info, "Created merge request at", merge_request.web_url)
        except GitlabCreateError as error:
            if error.response_code == 409:
                Utils.log(Utils.LogType.Info, "Merge request already exists")
