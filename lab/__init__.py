#!/usr/bin/env python3

"""
Base module for the lab package
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from lab.mergerequestcreator import MergeRequestCreator
from lab.mergerequestcheckout import MergeRequestCheckout
from lab.mergerequestlist import MergeRequestList
from lab.config import Config


def main() -> None:
    """
    Entry point
    """
    parser = argparse.ArgumentParser(description="The arcanist of GitLab.")
    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.add_parser("diff", help="Create a new merge request for the current branch")
    parser_patch = subparsers.add_parser("patch", help="check out a remote merge request")
    parser_login = subparsers.add_parser("login", help="Save a token for a GitLab token")
    parser_list = subparsers.add_parser("list", help="List open merge requests")

    parser_patch.add_argument(
        "number", metavar="int", type=int, nargs=1, help="Merge request number to checkout",
    )

    parser_login.add_argument("--host", help="GitLab host (e.g invent.kde.org)", required=True)
    parser_login.add_argument("--token", help="GitLab api private token", required=True)

    parser_list.add_argument(
        "--project",
        help="Show merge requests of the current project, not of the user",
        action="store_true",
    )

    args: argparse.Namespace = parser.parse_args()
    if args.subcommand == "diff":
        creator: MergeRequestCreator = MergeRequestCreator()
        creator.fork()
        creator.push()
        creator.create_mr()
    elif args.subcommand == "patch":
        checkouter: MergeRequestCheckout = MergeRequestCheckout()
        checkouter.checkout(args.number[0])
    elif args.subcommand == "login":
        config: Config = Config()
        config.set_token(args.host, args.token)
        config.save()
    elif args.subcommand == "list":
        lister = MergeRequestList(args.project)
        lister.print_formatted_list()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
