"""
Base class for creating a connection to the GitLab instance used by the repository in pwd
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import sys

from typing import Optional

from urllib.parse import ParseResult, urlparse

from gitlab import Gitlab
from gitlab.v4.objects import Project
from gitlab.exceptions import GitlabAuthenticationError
from git import Repo

from lab.utils import Utils, LogType
from lab.config import Config


class RepositoryConnection:
    """
    Creates a connection to the gitlab instance used by the current repository
    """

    # private
    __connection: Gitlab
    __local_repo: Repo
    __remote_project: Project
    __gitlab_token: str
    __config: Config = Config()

    def __init__(self) -> None:
        self.__local_repo: Repo = Repo(os.getcwd())

        try:
            origin = self.__local_repo.remote(name="origin")
        except ValueError:
            Utils.log(LogType.Error, "No origin remote exists")
            sys.exit(1)

        repository: str = next(origin.urls)

        repository_url: ParseResult = urlparse(repository)

        if not (repository_url.scheme == "https" or repository_url.scheme == "http"):
            Utils.log(
                LogType.Error,
                "git lab only supports https and http urls for the origin remote currently",
            )
            print('The url "{}" cannot be used'.format(repository))
            sys.exit(1)

        if not repository_url.scheme or not repository_url.hostname:
            Utils.log(LogType.Error, "Failed to detect GitLab instance url")
            sys.exit(1)

        gitlab_url = repository_url.scheme + "://" + repository_url.hostname

        auth_token: Optional[str] = self.__config.token(repository_url.hostname)
        if not auth_token:
            Utils.log(LogType.Error, "No authentication token found. ")
            print(
                "Please create a token with the api and write_repsitory scopes on {}/{}.".format(
                    gitlab_url, "profile/personal_access_tokens"
                )
            )
            print(
                'Afterwards use "git lab login --host {} --token t0k3n"'.format(
                    repository_url.hostname
                )
            )
            sys.exit(1)

        self.__login(gitlab_url, auth_token)
        if not self.__connection:
            Utils.log(LogType.Error, "Failed to connect to GitLab")
            sys.exit(0)

        self.__remote_project = self.__connection.projects.get(Utils.str_id_for_url(repository))

    def __login(self, instance: str, token: str) -> None:
        try:
            self.__connection: Gitlab = Gitlab(instance, private_token=token)
            self.__gitlab_token = token
            self.__connection.auth()
        except GitlabAuthenticationError:
            Utils.log(LogType.Error, "Could not log into GitLab")
            sys.exit(1)

    def connection(self) -> Gitlab:
        """
        Returns the Gitlab connection
        """
        return self.__connection

    def local_repo(self) -> Repo:
        """
        Returns the local repository
        """
        return self.__local_repo

    def remote_project(self) -> Project:
        """
        Returns the remote project (for the origin remote)
        """
        return self.__remote_project
