"""
Base class for creating connections to all known instances
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import sys

from typing import List, Optional

from gitlab import Gitlab
from gitlab.exceptions import GitlabAuthenticationError

from lab.config import Config
from lab.utils import Utils, LogType


class AllInstancesConnection:  # pylint: disable=too-few-public-methods
    """
    Base class that connects to all known instances
    """

    # protected
    _connections: List[Gitlab] = []

    # private
    __config: Config

    def __login(self, hostname: str, token: str) -> None:
        try:
            connection: Gitlab = Gitlab(hostname, private_token=token)
            connection.auth()
            self._connections.append(connection)
        except GitlabAuthenticationError:
            Utils.log(LogType.Error, "Could not log into GitLab")
            sys.exit(1)

    def __init__(self) -> None:
        self.__config = Config()
        instances = self.__config.instances()

        for hostname in instances:
            token: Optional[str] = self.__config.token(hostname)

            if isinstance(token, str):
                self.__login("https://" + hostname, token)
