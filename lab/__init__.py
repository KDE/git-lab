#!/usr/bin/env python3

"""
Base module for the lab package
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import traceback

from typing import List, Any

from git.exc import GitCommandError

from lab import (
    mergerequestcreator,
    mergerequestcheckout,
    mergerequestlist,
    feature,
    login,
    search,
    fork,
    issues,
    snippet,
    workflow,
    rewrite_remote,
)

from lab.utils import Utils, LogType


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
            snippet,
            workflow,
            rewrite_remote,
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

    try:
        parser.parse()
    except GitCommandError as git_error:
        Utils.log(LogType.Error, str(git_error))
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    except:  # noqa: E722
        print()
        Utils.log(LogType.Error, "git-lab crashed. This should not happen.")
        print(
            "Please help us to fix it by opening an issue on",
            "https://invent.kde.org/sdk/git-lab/-/issues.",
            "Make sure to include the information below:",
            "\n```\n",
            traceback.format_exc(),
            "```",
        )


if __name__ == "__main__":
    main()
