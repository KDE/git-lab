"""
Module containing classes for the fork command
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from lab.mergerequestcreator import MergeRequestCreator


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for fork command
    :param subparsers: subparsers object from global parser
    :return: fork subparser
    """
    fork_parser: argparse.ArgumentParser = subparsers.add_parser(
        "fork", help="Create a fork of the project"
    )
    return fork_parser


def run(args: argparse.Namespace) -> None:  # pylint: disable=unused-argument
    """
    run fork command
    :param args: parsed arguments
    """
    creator: MergeRequestCreator = MergeRequestCreator("master")
    creator.fork()
