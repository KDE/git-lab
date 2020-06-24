"""
Module containing classes for creating merge requests
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import re
import os

from typing import List, Any

from gitlab.v4.objects import Project
from gitlab.exceptions import GitlabCreateError, GitlabGetError

from lab.repositoryconnection import RepositoryConnection
from lab.config import RepositoryConfig, Workflow
from lab.utils import Utils, LogType
from lab.editorinput import EditorInput


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for merge request creation command
    :param subparsers: subparsers object from global parser
    :return: merge request creation subparser
    """
    create_parser: argparse.ArgumentParser = subparsers.add_parser(
        "mr", help="Create a new merge request for the current branch", aliases=["diff"]
    )
    create_parser.add_argument(
        "--target-branch", help="Use different target branch than master", default="master",
    )
    return create_parser


def run(args: argparse.Namespace) -> None:
    """
    run merge request creation command
    :param args: parsed arguments
    """
    # To fork or not to fork
    fork: bool = (RepositoryConfig().workflow() == Workflow.Fork)
    creator: MergeRequestCreator = MergeRequestCreator(args.target_branch, fork)
    creator.check()

    if fork:
        creator.fork()

    creator.push()
    creator.create_mr()


class MergeRequestCreator(RepositoryConnection):
    """
    Class for creating a merge request,
    including forking the remote repository and pushing to the fork.
    """

    # private
    __remote_fork: Project
    __target_branch: str
    __fork: bool

    def __init__(self, target_branch: str, fork: bool) -> None:
        RepositoryConnection.__init__(self)
        self.__target_branch = target_branch
        self.__fork = fork

    def check(self) -> None:
        """
        Run some sanity checks and warn the user if necessary
        """
        if (
            not self.local_repo().active_branch.name.startswith("work/")
            and not self.__fork
            and "invent.kde.org" in self.connection().url
        ):
            Utils.log(
                LogType.Warning,
                "Pushing to the upstream repository, but the branch name doesn't start with work/.",
            )
            print(
                "This is not recommended on KDE infrastructure,",
                "as it doesn't allow to rebase or force-push the branch.",
                "To cancel, please press Ctrl + C.",
            )

    def fork(self) -> None:
        """
        Try to create a fork of the remote repository.
        If the fork already exists, no new fork will be created.
        """

        if "fork" in self.local_repo().remotes:
            # Fork already exists
            fork_str_id: str = Utils.str_id_for_url(self.local_repo().remotes.fork.url)

            # Try to retrieve the remote project object, if it doesn't exist on the server,
            # go on with the logic to create a new fork.
            try:
                self.__remote_fork = self.connection().projects.get(fork_str_id)
                return
            except GitlabGetError:
                pass

        try:
            self.__remote_fork = self.remote_project().forks.create({})

            # WORKAROUND: the return of create() is unreliable,
            # and sometimes doesn't allow to create merge requests,
            # so request a fresh project object.
            self.__remote_fork = self.connection().projects.get(self.__remote_fork.id)

            self.local_repo().create_remote("fork", url=self.__remote_fork.ssh_url_to_repo)
        except GitlabCreateError:
            if "fork" in self.local_repo().remotes:
                Utils.log(LogType.Info, "Fork already exists, continuing")
            else:
                Utils.log(
                    LogType.Info,
                    "Fork exists, but no fork remote exists locally, trying to guess the url",
                )
                # Detect ssh url
                url = Utils.ssh_url_from_http(
                    self.connection().user.web_url + "/" + self.remote_project().path
                )

                self.local_repo().create_remote("fork", url=url)

            str_id: str = Utils.str_id_for_url(self.local_repo().remotes.fork.url)
            self.__remote_fork = self.connection().projects.get(str_id)

    def push(self) -> None:
        """
        pushes the local repository to the fork remote
        """
        if self.__fork:
            self.local_repo().remotes.fork.push()
        else:
            self.local_repo().remotes.origin.push(refspec=self.local_repo().head)

    def __upload_assets(self, text: str) -> str:
        """
        Scans the text for local file paths, uploads the files and returns
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
                try:
                    uploaded_file = self.remote_project().upload(filename, filepath=image)
                    output_text = output_text.replace(image, uploaded_file["url"])
                except FileNotFoundError:
                    Utils.log(LogType.Warning, "Failed to upload image", image)
                    print("The file does not exist.")

        return output_text

    def create_mr(self) -> None:
        """
        Creates a merge request with the changes from the current branch
        """
        e_input = EditorInput(
            placeholder_title=self.local_repo().head.commit.summary,
            placeholder_body=self.local_repo().head.commit.message.split("\n", 1)[1].strip(),
            extra_text="The markdown syntax for embedding images "
            + "![description](/path/to/file) can be used to upload images.",
        )

        project: Project = self.__remote_fork if self.__fork else self.remote_project()

        try:
            merge_request = project.mergerequests.create(
                {
                    "source_branch": self.local_repo().active_branch.name,
                    "target_branch": self.__target_branch,
                    "title": e_input.title,
                    "description": self.__upload_assets(e_input.body),
                    "target_project_id": self.remote_project().id,
                    "allow_maintainer_to_push": True,
                    "remove_source_branch": True,
                }
            )
            Utils.log(LogType.Info, "Created merge request at", merge_request.web_url)
        except GitlabCreateError as error:
            if error.response_code == 409:
                Utils.log(LogType.Info, "Merge request already exists")
