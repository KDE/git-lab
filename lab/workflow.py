"""
functions for setting the workflow of a repository
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse

from lab.config import RepositoryConfig, Workflow


def run(fork: bool, workbranch: bool) -> None:
    """
    run workflow command
    :param args: parsed arguments
    """
    repository_config = RepositoryConfig()
    if args.fork:
        repository_config.set_workflow(Workflow.Fork)
    elif args.workbranch:
        repository_config.set_workflow(Workflow.Workbranch)
    repository_config.save()
