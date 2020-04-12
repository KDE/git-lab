import subprocess
import tempfile

from typing import List

from lab.utils import Utils

"""
Structure representing the editorinput.
"""
class EditorInput:
    __fulltext: str = "\n"
    title: str
    body: str

    def __input(self) -> None:
        file = tempfile.NamedTemporaryFile("r")
        subprocess.call(["editor", file.name])

        self.__fulltext = file.read()

    def __fulltext_valid(self) -> bool:
        lines = self.__fulltext.splitlines()

        try:
            if (lines[0] == ""):
                Utils.log(Utils.LogType.Error, "The first line (title) can't be empty")
                return False
        except IndexError:
            Utils.log(Utils.LogType.Error, "The first line (title) can't be empty")
            return False

        # Anything after the title is optional, so the index might not exist
        try:
            if (lines[1] != ""):
                Utils.log(Utils.LogType.Error, "The second line (separator) must be empty")
                return False
        except IndexError:
            return True

        return True


    def __init__(self) -> None:
        self.__input()
        if (not self.__fulltext_valid()):
            Utils.log(Utils.LogType.Error, "Text not valid, aborting")
            exit(1)

        lines: List[str] = self.__fulltext.splitlines()
        self.title = lines[0]
        self.body = "\n".join(lines[2:])
