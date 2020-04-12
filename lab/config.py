import json
import os
from pathlib import Path

from typing import TextIO, Dict, Any

CONFIG_PATH = os.path.expanduser("~") + "/.gitlabconfig"

class Config:
    __file: TextIO
    __config: Dict[str, Any]

    def __init__(self):
        if (not os.path.isfile(CONFIG_PATH)):
            file = open(CONFIG_PATH, "w+")
            json.dump({}, file)
            file.close()

        self.__file = open(CONFIG_PATH, "r+")
        self.__config = json.load(self.__file)

    def save(self):
        self.__file.seek(0)
        json.dump(self.__config, self.__file, indent=4)
        self.__file.truncate()
        self.__file.close()

    def token(self, instance: str) -> str:
        try:
            return self.__config[instance]
        except KeyError:
            self.__config[instance] = str()

    def set_token(self, instance: str, token: str) -> None:
        self.__config[instance] = token
