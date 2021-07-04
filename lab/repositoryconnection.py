"""
Base class for creating a connection to the GitLab instance used by the repository in pwd
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sys

from typing import Optional

from urllib.parse import urlparse

from gitlab import Gitlab
from gitlab.v4.objects import Project
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError, GitlabHttpError
from git import Repo

from lab.utils import Utils, LogType
from lab.config import Config


class RepositoryConnection:
    """
    Creates a connection to the gitlab instance used by the current repository
    """

    # protected
    _connection: Gitlab
    _local_repo: Repo
    _remote_project: Project

    # private
    __config: Config

    def __init__(self) -> None:
        self._local_repo = Utils.get_cwd_repo()
        self.__config = Config()

        try:
            origin = self._local_repo.remote(name="origin")
        except ValueError:
            Utils.log(LogType.ERROR, "No origin remote exists")
            sys.exit(1)

        repository: str = next(origin.urls)

        gitlab_url = Utils.gitlab_instance_url(repository)
        gitlab_hostname: Optional[str] = urlparse(gitlab_url).hostname

        if not gitlab_hostname:
            Utils.log(LogType.ERROR, "Failed to detect GitLab hostname")
            sys.exit(1)

        auth_token: Optional[str] = self.__config.token(gitlab_hostname)
        if not auth_token:
            Utils.log(LogType.ERROR, "No authentication token found. ")
            print(
                "Please create a token with the api and write_repository scopes on {}/-/{}.".format(
                    gitlab_url, "profile/personal_access_tokens"
                )
            )
            print('Afterwards use "git lab login --host {} --token t0k3n"'.format(gitlab_hostname))
            sys.exit(1)

        self.__login(gitlab_url, auth_token)
        if not self._connection:
            Utils.log(LogType.ERROR, "Failed to connect to GitLab")
            sys.exit(1)

        try:
            self._remote_project = self._connection.projects.get(Utils.str_id_for_url(repository))
        except (GitlabHttpError, GitlabGetError):
            Utils.log(
                LogType.ERROR,
                "The repository could not be found on the GitLab instance.",
            )
            print(
                "If the repository was recently moved, please update the origin remote using git."
            )
            sys.exit(1)

    def __login(self, hostname: str, token: str) -> None:
        try:
            self._connection: Gitlab = Gitlab(hostname, private_token=token)
            self._connection.auth()
        except (GitlabAuthenticationError, GitlabGetError):
            Utils.log(LogType.ERROR, "Could not log into GitLab: {}".format(hostname))
            sys.exit(1)
