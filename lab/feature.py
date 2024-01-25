"""
This module contains code for the feature command
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from typing import Any

from git import Repo
from git.exc import GitCommandError

from lab.utils import Utils, LogType


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for feature command
    :param subparsers: subparsers object from global parser
    :return: feature request subparser
    """
    feature_parser: argparse.ArgumentParser = subparsers.add_parser(
        "feature", help="Create branches and list branches"
    )
    feature_parser.add_argument("name", nargs="?", help="name for the new branch")
    feature_parser.add_argument(
        "start",
        nargs="?",
        help="starting point for the new branch",
        default="origin/" + Utils.get_default_branch(Utils.get_cwd_repo()),
    )
    return feature_parser


def run(args: argparse.Namespace) -> None:
    """
    run feature command
    :param args: parsed arguments
    """
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
                Utils.log(LogType.INFO, "Switched to branch '{}'".format(name))
            else:
                self.__git.checkout(start, b=name)  # create a new branch
                Utils.log(LogType.INFO, "Switched to a new branch '{}'".format(name))

        except GitCommandError as git_error:
            Utils.log(LogType.ERROR, git_error.stderr.strip())

    def list(self) -> None:
        """
        lists branches
        """
        print(self.__git.branch())
