"""
Module containing login command
"""

# SPDX-FileCopyrightText: 2020 Benjamin Port <benjamin.port@kde.org>
#
# SPDX-License-Identifier: GPL-2.0-or-later
import argparse

from lab.config import Config


def run(host: str, token: str, command: str) -> None:
    """
    run login command
    :param args: parsed arguments
    """
    config: Config = Config()

    if args.command:
        config.set_auth_command(host, command)
    else:
        config.set_token(host, token)

    config.save()
