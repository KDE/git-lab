# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import os
from pathlib import Path

from typing import TextIO, Dict, Any, Optional

CONFIG_PATH = os.path.expanduser("~") + "/.gitlabconfig"

class Config:
    __file: TextIO
    __config: Dict[str, str]

    def __init__(self) -> None:
        if (not os.path.isfile(CONFIG_PATH)):
            file = open(CONFIG_PATH, "w+")
            json.dump({}, file)
            file.close()

        self.__file = open(CONFIG_PATH, "r+")
        self.__config = json.load(self.__file)

    def save(self) -> None:
        self.__file.seek(0)
        json.dump(self.__config, self.__file, indent=4)
        self.__file.truncate()
        self.__file.close()

    def token(self, instance: str) -> Optional[str]:
        try:
            return self.__config[instance]
        except KeyError:
            return None

    def set_token(self, instance: str, token: str) -> None:
        self.__config[instance] = token
