"""
Module containing login command
"""

# SPDX-FileCopyrightText: 2020 Benjamin Port <benjamin.port@kde.org>
#
# SPDX-License-Identifier: GPL-2.0-or-later
import argparse

from lab.config import Config


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for login command
    :param subparsers: subparsers object from global parser
    :return: login subparser
    """

    login_parser: argparse.ArgumentParser = subparsers.add_parser(
        "login", help="Save a token for a GitLab instance"
    )
    login_parser.add_argument("--host", help="GitLab host (e.g invent.kde.org)", required=True)
    login_parser.add_argument("--token", help="GitLab api private token", required=True)
    return login_parser


def run(args: argparse.Namespace) -> None:
    """
    run login command
    :param args: parsed arguments
    """
    config: Config = Config()
    config.set_token(args.host, args.token)
    config.save()
