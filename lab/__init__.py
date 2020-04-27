#!/usr/bin/env python3

"""
Base module for the lab package
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from typing import List, Any

from lab import (
    mergerequestcreator,
    mergerequestcheckout,
    mergerequestlist,
    feature,
    login,
    search,
    fork,
    issues,
)


class Parser:  # pylint: disable=R0903
    """
    Global parser, will instantiate subparser for each commands
    """

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description="The arcanist of GitLab.")
        self.subparsers = self.parser.add_subparsers(dest="subcommand")

        # init all subcommand
        command_list: List[Any] = [
            mergerequestcreator,
            mergerequestcheckout,
            mergerequestlist,
            feature,
            login,
            search,
            fork,
            issues,
        ]
        for command in command_list:
            parser = command.parser(self.subparsers)
            # if no default runner set fallback to default runner, run from command module
            if not parser.get_default(dest="runner"):
                parser.set_defaults(runner=command.run)

    def parse(self) -> None:
        """
        parse args and run command
        """
        args: argparse.Namespace = self.parser.parse_args()
        if hasattr(args, "runner"):
            args.runner(args)
        else:
            self.parser.print_help()


def main() -> None:
    """
    Entry point
    """
    parser: Parser = Parser()
    parser.parse()


if __name__ == "__main__":
    main()
