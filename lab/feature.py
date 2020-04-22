"""
This module contains code for the feature command
"""

import os

from typing import Any

from git import Repo
from git.exc import GitCommandError

from lab.utils import Utils, LogType


class Feature:
    """
    represents the feature command
    """

    # private
    __repo: Repo
    __git: Any

    def __init__(self) -> None:
        self.__repo = Repo(os.getcwd())
        self.__git = self.__repo.git

    def checkout(self, start: str, name: str) -> None:
        """
        Checkouts a branch if it exists or creates a new one
        """
        try:
            if name in self.__repo.refs:
                self.__git.checkout(name)
                Utils.log(LogType.Info, "Switched to branch '{}'".format(name))
            else:
                self.__git.checkout(start, b=name)  # create a new branch
                Utils.log(LogType.Info, "Switched to a new branch '{}'".format(name))

        except GitCommandError as git_error:
            Utils.log(LogType.Error, git_error.stderr.strip())

    def list(self) -> None:
        """
        lists branches
        """
        print(self.__git.branch())
