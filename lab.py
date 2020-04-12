#!/usr/bin/env python3

from gitlab import Gitlab
from gitlab.v4.objects import Project
from gitlab.exceptions import GitlabCreateError, GitlabAuthenticationError
from git import Repo

from urllib.parse import urlparse, ParseResult, quote_plus

import os
import sys

from typing import List

class MergeRequestCreator:
    # private
    __connection: Gitlab
    __local_repo: Repo
    __remote_project: Project
    __remote_fork: Project
    __gitlab_token: str

    def __init__(self) -> None:
        self.__local_repo: Repo = Repo(os.getcwd())

        try:
            origin = self.__local_repo.remote(name="origin")
        except ValueError:
            print("Error: No origin remote exists")
            sys.exit(1)

        repository_url: ParseResult = urlparse(next(origin.urls))
        if (not repository_url.scheme and repository_url.hostname):
            print("Error: Failed to detect GitLab instance url")
            exit(1)

        gitlab_url = str(repository_url.scheme) + "://" + str(repository_url.hostname)

        self.__login(gitlab_url, os.environ.get("GITLAB_TOKEN"))
        if (not self.__connection):
            print("Error: Failed to connect to GitLab")
            exit(0)

        self.__remote_project = self.__connection.projects.get(quote_plus(repository_url.path[1:]))

    def __str_id_for_url(self, url) -> str:
        repository_url: ParseResult = urlparse(url.replace(".git", ""))
        return quote_plus(repository_url.path[1:])

    def __login(self, instance: str, token: str) -> None:
        try:
            self.__connection: Gitlab = Gitlab(instance, private_token=token)
            self.__gitlab_token = token
            self.__connection.auth()
        except GitlabAuthenticationError:
            print("Error: Could not log into GitLab, check your API Tokein in the GITLAB_TOKEN environment variable")
            exit(1)

    def fork(self) -> None:
        try:
            self.__remote_fork = self.__remote_project.forks.create({})
            self.__local_repo.create_remote("fork", url=self.__remote_fork.http_url_to_repo)
        except GitlabCreateError:
            print("Info: Fork already exists, continueing")
            id: str = self.__str_id_for_url(self.__local_repo.remotes.fork.url)
            self.__remote_fork = self.__connection.projects.get(id)

        print(self.__remote_fork)

    def push(self) -> None:
        self.__local_repo.remotes.fork.push()

    def create_mr(self) -> None:
        target_project = self.__connection.projects.get(self.__str_id_for_url(self.__local_repo.remotes.origin.url))
        print(target_project)

        mr = self.__remote_fork.mergerequests.create({
            'source_branch': str(self.__local_repo.active_branch),
            'target_branch': 'master',
            'title': 'merge cool feature',
            "target_project_id": target_project.id
        })


if __name__ == "__main__":
    creator: MergeRequestCreator = MergeRequestCreator()
    creator.fork()
    creator.push()
    creator.create_mr()
