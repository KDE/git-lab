#!/usr/bin/env python3

"""
Base module for the lab package
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from lab import (
    mergerequestcreator,
    mergerequestcheckout,
    mergerequestlist,
    feature,
)

from lab.config import Config


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="The arcanist of GitLab.")
        self.subparsers = self.parser.add_subparsers(dest="subcommand")
        # init all subcommand
        command_list = [
            mergerequestcreator,
            mergerequestcheckout,
            mergerequestlist,
            feature,
        ]
        for command in command_list:
            parser = command.parser(self.subparsers)
            # if no default runner set fallback to default runner, run from command module
            if not parser.get_default(dest="runner"):
                parser.set_defaults(runner=command.run)

    def parse(self):
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
