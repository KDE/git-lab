"""
Module containing classes for creating merge requests
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import re
import os

from typing import List, Any

from gitlab.v4.objects import Project
from gitlab.exceptions import GitlabCreateError

from lab.repositoryconnection import RepositoryConnection
from lab.utils import Utils, LogType
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
                Utils.log(LogType.Info, "Fork already exists, continueing")
            else:
                Utils.log(
                    LogType.Info,
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

    def __upload_assets(self, text: str) -> str:
        """
        Scans the text for local file pathes, uploads the files and returns
        the text modified to load the files from the uploaded urls
        """
        find_expr = re.compile(r"!\[[^\[\(]*\]\([^\[\(]*\)")
        extract_expr = re.compile(r"(?<=\().+?(?=\))")

        matches: List[Any] = find_expr.findall(text)

        output_text: str = text

        for match in matches:
            image = extract_expr.findall(match)[0]

            if not image.startswith("http"):
                Utils.log(LogType.Info, "Uploading", image)

                filename: str = os.path.basename(image)
                uploaded_file = self.remote_project().upload(filename, filepath=image)

                output_text = output_text.replace(image, uploaded_file["url"])

        return output_text

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
                    "description": self.__upload_assets(e_input.body),
                    "target_project_id": self.remote_project().id,
                    "allow_maintainer_to_push": True,
                }
            )
            Utils.log(LogType.Info, "Created merge request at", merge_request.web_url)
        except GitlabCreateError as error:
            if error.response_code == 409:
                Utils.log(LogType.Info, "Merge request already exists")
