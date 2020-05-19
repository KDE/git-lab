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

    group = login_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--token", help="GitLab api private token")
    group.add_argument("--command", help="Command to run when a token is needed")

    return login_parser


def run(args: argparse.Namespace) -> None:
    """
    run login command
    :param args: parsed arguments
    """
    config: Config = Config()

    if args.command:
        config.set_auth_command(args.host, args.command)
    else:
        config.set_token(args.host, args.token)

    config.save()
