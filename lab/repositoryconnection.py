from gitlab import Gitlab
from gitlab.v4.objects import Project
from gitlab.exceptions import GitlabCreateError, GitlabAuthenticationError
from git import Repo

from urllib.parse import ParseResult, urlparse, quote_plus
from lab.utils import Utils
from lab.config import Config

import os

from typing import Optional

"""
Creates a connection to the gitlab instance used by the current repository
"""
class RepositoryConnection:
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
            print("Error: No origin remote exists")
            exit(1)

        repository: str = next(origin.urls)

        repository_url: ParseResult = urlparse(repository)

        if not (repository_url.scheme == "https" or repository_url.scheme == "http"):
            print("Error: git lab only supports https and http urls for the origin remote currently")
            print("The url \"{}\" cannot be used".format(repository))
            exit(1)

        if (not repository_url.scheme or not repository_url.hostname):
            print("Error: Failed to detect GitLab instance url")
            exit(1)

        gitlab_url = repository_url.scheme + "://" + repository_url.hostname

        auth_token: Optional[str] = self.__config.token(repository_url.hostname)
        if (not auth_token):
            print("No authentication token found. You need to use \"git lab login --host {}\" first".format(repository_url.hostname))
            exit(1)

        self.__login(gitlab_url, auth_token)
        if (not self.__connection):
            print("Error: Failed to connect to GitLab")
            exit(0)

        self.__remote_project = self.__connection.projects.get(Utils.str_id_for_url(repository))

    def __login(self, instance: str, token: str) -> None:
        try:
            self.__connection: Gitlab = Gitlab(instance, private_token=token)
            self.__gitlab_token = token
            self.__connection.auth()
        except GitlabAuthenticationError:
            print("Error: Could not log into GitLab")
            exit(1)

    """
    Returns the Gitlab connection
    """
    def connection(self) -> Gitlab:
        return self.__connection

    """
    Returns the local repository
    """
    def local_repo(self) -> Repo:
        return self.__local_repo

    """
    Returns the remote project (for the origin remote)
    """
    def remote_project(self) -> Project:
        return self.__remote_project
