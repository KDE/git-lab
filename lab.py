#!/usr/bin/env python3

from gitlab import Gitlab
from gitlab.v4.objects import Project, ProjectMergeRequest
from gitlab.exceptions import GitlabCreateError, GitlabAuthenticationError
from git import Repo

from urllib.parse import urlparse, ParseResult, quote_plus
import argparse

import os
import sys

from typing import List

"""
This class contains static methods for common tasks
"""
class Utils:
    """
    Returns the url encoded string id for a repository
    """
    @staticmethod
    def str_id_for_url(url: str) -> str:
        repository_url: ParseResult = urlparse(url.replace(".git", ""))
        return quote_plus(repository_url.path[1:])


"""
Creates a connection to the gitlab instance used by the current repository
"""
class RepositoryConnection:
    # private
    __connection: Gitlab
    __local_repo: Repo
    __remote_project: Project
    __gitlab_token: str

    def __init__(self) -> None:
        self.__local_repo: Repo = Repo(os.getcwd())

        try:
            origin = self.__local_repo.remote(name="origin")
        except ValueError:
            print("Error: No origin remote exists")
            exit(1)

        repository: str = next(origin.urls)
        repository_url: ParseResult = urlparse(repository)
        if (not repository_url.scheme and repository_url.hostname):
            print("Error: Failed to detect GitLab instance url")
            exit(1)

        gitlab_url = str(repository_url.scheme) + "://" + str(repository_url.hostname)

        self.__login(gitlab_url, os.environ.get("GITLAB_TOKEN"))
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
            print("Error: Could not log into GitLab, check your API Tokein in the GITLAB_TOKEN environment variable")
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

class MergeRequestCreator(RepositoryConnection):
    # private
    __remote_fork: Project
    __gitlab_token: str

    def __init__(self) -> None:
        RepositoryConnection.__init__(self)

    def fork(self) -> None:
        try:
            self.__remote_fork = self.remote_project().forks.create({})
            self.local_repo().create_remote("fork", url=self.__remote_fork.http_url_to_repo)
        except GitlabCreateError:
            print("Info: Fork already exists, continueing")
            id: str = Utils.str_id_for_url(self.local_repo().remotes.fork.url)
            self.__remote_fork = self.connection().projects.get(id)

        print(self.__remote_fork)

    def push(self) -> None:
        self.local_repo().remotes.fork.push()

    def create_mr(self) -> None:
        mr = self.__remote_fork.mergerequests.create({
            'source_branch': str(self.local_repo().active_branch),
            'target_branch': 'master',
            'title': 'merge cool feature',
            "target_project_id": self.remote_project().id
        })

class MergeRequestCheckout(RepositoryConnection):
    # private
    __mr: ProjectMergeRequest

    def __init__(self):
        RepositoryConnection.__init__(self)

    def checkout(self, id: int):
        self.__mr = self.remote_project().mergerequests.get(id, lazy=False)
        #print(self.__mr)
        print("Checking out merge request \"{}\"...".format(self.__mr.title))
        print("  branch:", self.__mr.source_branch)

        fetch_info = self.local_repo().remotes.origin.fetch("merge-requests/{}/head".format(id))[0]
        head = self.local_repo().create_head(self.__mr.source_branch, fetch_info.ref)
        head.checkout()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The arcanist of GitLab.')
    subparsers: argparse._SubParsersAction = parser.add_subparsers(dest="subcommand")
    parser_diff = subparsers.add_parser("diff")
    parser_patch = subparsers.add_parser("patch")

    parser_patch.add_argument(
        "number", metavar="int", type=int,
        nargs=1, help="Merge request number to checkout")

    args: argparse.Namespace = parser.parse_args()
    if (args.subcommand == "diff"):
        creator: MergeRequestCreator = MergeRequestCreator()
        creator.fork()
        creator.push()
        creator.create_mr()
    elif (args.subcommand == "patch"):
        checkouter: MergeRequestCheckout = MergeRequestCheckout()
        checkouter.checkout(args.number[0])
