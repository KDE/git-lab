"""
Module containing classes for working with configuration
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import os

from typing import TextIO, Dict, Optional

CONFIG_PATH = os.path.expanduser("~") + "/.gitlabconfig"


class Config:
    """
    Class that can load and store settings
    """

    __file: TextIO
    __config: Dict[str, str]

    def __init__(self) -> None:
        if not os.path.isfile(CONFIG_PATH):
            file = open(CONFIG_PATH, "w+")
            json.dump({}, file)
            file.close()

        self.__file = open(CONFIG_PATH, "r+")
        self.__config = json.load(self.__file)

    def save(self) -> None:
        """
        Save the config to disk. This function has to be manually called,
        otherwise the config won't be saved.
        """
        self.__file.seek(0)
        json.dump(self.__config, self.__file, indent=4)
        self.__file.truncate()
        self.__file.close()

    def token(self, instance: str) -> Optional[str]:
        """
        Returns the token for a GitLab instance.
        If none was found, it returns None
        """
        try:
            return self.__config[instance]
        except KeyError:
            return None

    def set_token(self, instance: str, token: str) -> None:
        """
        Sets the token for a GitLab instance
        """
        self.__config[instance] = token
