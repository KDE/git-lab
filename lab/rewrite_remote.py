"""
Module of the rewrite-remote subcommand
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
from git import Repo

from lab.utils import Utils

def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    rewrite_remote_parser: argparse.ArgumentParser = subparsers.add_parser(
        "rewrite-remote", help="Rewrite the remote url to ssh"
    )
    rewrite_remote_parser.add_argument(
        "remote",
        type=str,
        nargs=1,
        help="Name of the remote to rewrite",
    )
    return rewrite_remote_parser

def run(args: argparse.Namespace) -> None:
    repo: Repo = Utils.get_cwd_repo()
    remote_url = repo.git.remote("get-url", args.remote)
    ssh_url = Utils.ssh_url_from_http(Utils.normalize_url(remote_url))
    repo.git.remote("set-url", args.remote, ssh_url)
