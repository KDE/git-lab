#!/usr/bin/env python3

from gitlab import Gitlab
from gitlab.v4.objects import Project, ProjectMergeRequest
from gitlab.exceptions import GitlabCreateError, GitlabAuthenticationError
from git import Repo

from urllib.parse import urlparse, ParseResult, quote_plus
import argparse
import tempfile
import subprocess

import os
import sys

from typing import List

"""
Structure representing the editorinput.
Should not be used directly
"""
class EditorInput:
    __fulltext: str = "\n"
    title: str
    body: str

    def __input(self) -> None:
        file = tempfile.NamedTemporaryFile("r")
        subprocess.call(["editor", file.name])

        self.__fulltext = file.read()

    def __fulltext_valid(self) -> bool:
        lines = self.__fulltext.splitlines()

        try:
            if (lines[0] == ""):
                print("Error: The first line (title) can't be empty")
                return False
        except IndexError:
            print("Error: The first line (title) can't be empty")
            return False

        # Anything after the title is optional, so the index might not exist
        try:
            if (lines[1] != ""):
                print("Error: The second line (separator) must be empty")
                return False
        except IndexError:
            return True

        return True


    def __init__(self):
        self.__input()
        if (not self.__fulltext_valid()):
            print("Text not valid, aborting")
            exit(1)

        lines: List[str] = self.__fulltext.splitlines()
        self.title = lines[0]
        self.body = "\n".join(lines[2:])


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

        if (repository_url.scheme != "https" or repository_url.scheme != "http"):
            print("Error: git lab only supports https and http urls for the origin remote currently")
            print("The url \"{}\" cannot be used".format(repository))
            exit(1)

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
        einput = EditorInput()

        mr = self.__remote_fork.mergerequests.create({
            "source_branch": str(self.local_repo().active_branch),
            "target_branch": "master",
            "title": einput.title,
            "description": einput.body,
            "target_project_id": self.remote_project().id
        })

class MergeRequestCheckout(RepositoryConnection):
    # private
    __mr: ProjectMergeRequest

    def __init__(self):
        RepositoryConnection.__init__(self)

    def checkout(self, id: int):
        self.__mr = self.remote_project().mergerequests.get(id, lazy=False)
        print("Checking out merge request \"{}\"...".format(self.__mr.title))
        print("  branch:", self.__mr.source_branch)

        fetch_info = self.local_repo().remotes.origin.fetch("merge-requests/{}/head".format(id))[0]
        head = self.local_repo().create_head(self.__mr.source_branch, fetch_info.ref)
        head.checkout()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The arcanist of GitLab.')
    subparsers: argparse._SubParsersAction = parser.add_subparsers(dest="subcommand")
    parser_diff = subparsers.add_parser("diff", help="Create a new merge request for the current branch")
    parser_patch = subparsers.add_parser("patch", help="check out a remote merge request")

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
    else:
        parser.print_help()
