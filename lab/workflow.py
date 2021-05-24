"""
functions for setting the workflow of a repository
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from lab.config import RepositoryConfig, Workflow


def parser(
    subparsers: argparse._SubParsersAction,  # pylint: disable=protected-access
) -> argparse.ArgumentParser:
    """
    Subparser for workflow command
    :param subparsers: subparsers object from global parser
    :return: merge request creation subparser
    """
    workflow_parser: argparse.ArgumentParser = subparsers.add_parser(
        "workflow", help="Set the workflow to use for a project"
    )

    group = workflow_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--fork",
        help="Set the fork workflow (branch in a fork of the upstream repository)",
        action="store_true",
    )
    group.add_argument(
        "--workbranch",
        help="Set the work branch workflow (branch in the upstream repository)",
        action="store_true",
    )
    return workflow_parser


def run(args: argparse.Namespace) -> None:
    """
    run workflow command
    :param args: parsed arguments
    """
    repository_config = RepositoryConfig()
    if args.fork:
        repository_config.set_workflow(Workflow.FORK)
    elif args.workbranch:
        repository_config.set_workflow(Workflow.WORKBRANCH)
    repository_config.save()
