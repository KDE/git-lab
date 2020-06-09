"""
Module containing classes for working with configuration
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import os
import subprocess
from enum import Enum, auto

from typing import TextIO, Dict, Optional, Any, Tuple

from lab.utils import Utils, LogType


class Config:
    """
    Class that can load and store settings

    Config file layout:
    {
        "version": 1,
        "instances": {
            "gitlab.com": {
                "auth_type": "token",
                "token": "dkasjdlaksjdlkj",
                "command": None
            },
            "invent.kde.org": {
                "auth_type": "command",
                "command": "gpg --decrypt",
                "token": None
            }
        }
    }
    """

    config_path: str = os.path.expanduser("~") + "/.gitlabconfig"
    __file: TextIO
    __config: Dict[str, Any]

    def __migrate_to_version_1(self) -> None:
        if "version" not in self.__config:
            Utils.log(LogType.Info, "Migrating configuration file to version 1")

            new_config: Dict[str, Any] = {"version": 1, "instances": {}}

            for hostname in self.__config.keys():
                new_config["instances"][hostname] = {
                    "auth_type": "token",
                    "token": self.__config[hostname],
                }

            self.__config = new_config
            self.save()

    def __init__(self) -> None:
        if not os.path.isfile(self.config_path):
            file = open(self.config_path, "w+")
            json.dump({"version": 1, "instances": {}}, file)
            file.close()

        self.__file = open(self.config_path, "r+")
        self.__config = json.load(self.__file)

        self.__migrate_to_version_1()

    def save(self) -> None:
        """
        Save the config to disk. This function has to be manually called,
        otherwise the config won't be saved.
        """
        self.__file.seek(0)
        json.dump(self.__config, self.__file, indent=4)
        self.__file.truncate()
        self.__file.flush()

    def token(self, hostname: str) -> Optional[str]:
        """
        Returns the token for a GitLab instance.
        If none was found, it returns None
        """
        if hostname in self.__config["instances"]:
            # Command case
            if (
                "auth_type" in self.__config["instances"][hostname]
                and self.__config["instances"][hostname]["auth_type"] == "command"
            ):
                return (
                    subprocess.check_output(
                        self.__config["instances"][hostname]["command"], shell=True
                    )
                    .decode()
                    .strip()
                )

            # Token case
            token = self.__config["instances"][hostname]["token"]
            if isinstance(token, str):
                return token

        return None

    def set_token(self, hostname: str, token: str) -> None:
        """
        Sets the token for a GitLab instance
        """
        if hostname not in self.__config["instances"]:
            self.__config["instances"][hostname] = {}

        self.__config["instances"][hostname]["token"] = token
        self.__config["instances"][hostname]["auth_type"] = "token"

    def set_auth_command(self, hostname: str, command: str) -> None:
        """
        Sets the command that git-lab runs when it needs an access token
        """
        if hostname not in self.__config["instances"]:
            self.__config["instances"][hostname] = {}

        self.__config["instances"][hostname]["command"] = command
        self.__config["instances"][hostname]["auth_type"] = "command"

    def instances(self) -> Tuple[str, ...]:
        """
        Returns the list of known instances
        """
        try:
            return tuple(self.__config["instances"].keys())
        except KeyError:
            return ()

        return ()

class Workflow(Enum):
    """
    Different values for workflow
    """
    # Never reorder this values! The config file stores the actual numbers.
    fork = auto()  # push merge request branches to a fork of the upstream repository
    workbranch = auto()  # push merge request branches to the upstream repository

class RepositoryConfig:
    """
    Per-repository config file
    """

    config_path: str = os.getcwd() + "/.git/gitlabconfig"
    __file: TextIO
    __config: Dict[str, Any]

    def __init__(self) -> None:
        if not os.path.isfile(self.config_path):
            file = open(self.config_path, "w+")
            json.dump({}, file)
            file.close()

        self.__file = open(self.config_path, "r+")
        self.__config = json.load(self.__file)

    def workflow(self) -> Workflow:
        """
        get the workflow used for the repository. Defaults to RepositoryConfig.workflow.fork
        """
        value: Any
        try:
            value = self.__config["workflow"]
        except KeyError:
            return Workflow.fork

        return Workflow(value)

    def set_workflow(self, workflow: Workflow) -> None:
        """
        Set the workflow to one of RepositoryConfig.Workflow
        """

        # Make sure not to corrupt the config file with invalid numbers
        if not isinstance(workflow, Workflow):
            raise TypeError()

        self.__config["workflow"] = workflow.value

    def save(self) -> None:
        """
        Save the config to disk. This function has to be manually called,
        otherwise the config won't be saved.
        """
        self.__file.seek(0)
        json.dump(self.__config, self.__file, indent=4)
        self.__file.truncate()
        self.__file.flush()
