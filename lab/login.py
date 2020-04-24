"""
Module containing login command
"""

# SPDX-FileCopyrightText: 2020 Benjamin Port <benjamin.port@kde.org>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from lab import Config


def parser(subparsers):
    p = subparsers.add_parser("login", help="Save a token for a GitLab token")
    p.add_argument("--host", help="GitLab host (e.g invent.kde.org)", required=True)
    p.add_argument("--token", help="GitLab api private token", required=True)
    return p


def run(args):
    config: Config = Config()
    config.set_token(args.host, args.token)
    config.save()
