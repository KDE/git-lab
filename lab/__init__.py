#!/usr/bin/env python3

"""
Base module for the lab package
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import os

from lab.mergerequestcreator import MergeRequestCreator
from lab.mergerequestcheckout import MergeRequestCheckout
from lab.mergerequestlist import MergeRequestList
from lab.config import Config
from lab.utils import Utils, LogType

from git import Repo
from git.exc import GitCommandError


def main() -> None:
    """
    Entry point
    """
    parser = argparse.ArgumentParser(description="The arcanist of GitLab.")
    subparsers = parser.add_subparsers(dest="subcommand")
    parser_diff = subparsers.add_parser(
        "diff", help="Create a new merge request for the current branch"
    )
    parser_patch = subparsers.add_parser("patch", help="check out a remote merge request")
    parser_login = subparsers.add_parser("login", help="Save a token for a GitLab token")
    parser_list = subparsers.add_parser("list", help="List open merge requests")
    parser_feature = subparsers.add_parser("feature", help="Create branches and list branches")

    parser_diff.add_argument(
        "--target-branch", help="Use different target branch than master", default="master"
    )

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
    parser_list.add_argument(
        "--opened", help="Show opened merge requests", action="store_true",
    )
    parser_list.add_argument(
        "--merged", help="Show merged merge requests", action="store_true",
    )
    parser_list.add_argument(
        "--closed", help="Show closed merge requests", action="store_true",
    )

    parser_feature.add_argument(
        "name", nargs="?", help="name for the new branch"
    )

    parser_feature.add_argument(
        "start", nargs="?", help="starting point for the new branch", default="HEAD"
    )

    args: argparse.Namespace = parser.parse_args()
    if args.subcommand == "diff":
        creator: MergeRequestCreator = MergeRequestCreator(args.target_branch)
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
        lister = MergeRequestList(args.project, args.merged, args.opened, args.closed)
        lister.print_formatted_list()
    elif args.subcommand == "feature":
        repo = Repo(os.getcwd())
        git = repo.git

        if args.name:
            try:
                if args.name in repo.refs:
                    git.checkout(args.name)
                    Utils.log(LogType.Info, "Switched to branch '{}'".format(args.name))
                else:
                    git.checkout(args.start, b=args.name) # create a new branch
                    Utils.log(LogType.Info, "Switched to a new branch '{}'".format(args.name))

            except GitCommandError as e:
                Utils.log(LogType.Error, e.stderr.strip())
        else:
            print(git.branch())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
