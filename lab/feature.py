"""
This module contains code for the feature command
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import os

from typing import Any

from git import Repo
from git.exc import GitCommandError

from lab.utils import Utils, LogType


def parser(subparsers):
    p = subparsers.add_parser("feature", help="Create branches and list branches")
    p.add_argument("name", nargs="?", help="name for the new branch")
    p.add_argument(
        "start", nargs="?", help="starting point for the new branch", default="HEAD"
    )
    return p


def run(args):
    feature = Feature()
    if args.name:
        feature.checkout(args.start, args.name)
    else:
        feature.list()


class Feature:
    """
    represents the feature command
    """

    # private
    __repo: Repo
    __git: Any

    def __init__(self) -> None:
        self.__repo = Utils.get_cwd_repo()
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
