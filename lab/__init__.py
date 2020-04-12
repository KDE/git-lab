#!/usr/bin/env python3

import argparse

import os
import sys

from typing import List

from lab.mergerequestcreator import MergeRequestCreator
from lab.mergerequestcheckout import MergeRequestCheckout
from lab.config import Config

def main():
    parser = argparse.ArgumentParser(description='The arcanist of GitLab.')
    subparsers: argparse._SubParsersAction = parser.add_subparsers(dest="subcommand")
    parser_diff = subparsers.add_parser("diff", help="Create a new merge request for the current branch")
    parser_patch = subparsers.add_parser("patch", help="check out a remote merge request")
    parser_login = subparsers.add_parser("login", help="Save a token for a GitLab token")

    parser_patch.add_argument(
        "number", metavar="int", type=int,
        nargs=1, help="Merge request number to checkout")

    parser_login.add_argument("--host", help="GitLab host (e.g invent.kde.org)")
    parser_login.add_argument("--token", help="GitLab api private token")

    args: argparse.Namespace = parser.parse_args()
    if (args.subcommand == "diff"):
        creator: MergeRequestCreator = MergeRequestCreator()
        creator.fork()
        creator.push()
        creator.create_mr()
    elif (args.subcommand == "patch"):
        checkouter: MergeRequestCheckout = MergeRequestCheckout()
        checkouter.checkout(args.number[0])
    elif (args.subcommand == "login"):
        config: Config = Config()
        config.set_token(args.host, args.token)
        config.save()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
