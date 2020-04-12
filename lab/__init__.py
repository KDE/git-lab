#!/usr/bin/env python3

from gitlab import Gitlab
from gitlab.v4.objects import Project, ProjectMergeRequest
from gitlab.exceptions import GitlabCreateError, GitlabAuthenticationError
from git import Repo

from urllib.parse import urlparse, ParseResult, quote_plus
import argparse

import os
import sys

from typing import List

from lab.mergerequestcreator import MergeRequestCreator
from lab.mergerequestcheckout import MergeRequestCheckout

def main():
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

if __name__ == "__main__":
    main()
