import subprocess
import tempfile

from typing import List

"""
Structure representing the editorinput.
Should not be used directly
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
                print("Error: The first line (title) can't be empty")
                return False
        except IndexError:
            print("Error: The first line (title) can't be empty")
            return False

        # Anything after the title is optional, so the index might not exist
        try:
            if (lines[1] != ""):
                print("Error: The second line (separator) must be empty")
                return False
        except IndexError:
            return True

        return True


    def __init__(self):
        self.__input()
        if (not self.__fulltext_valid()):
            print("Text not valid, aborting")
            exit(1)

        lines: List[str] = self.__fulltext.splitlines()
        self.title = lines[0]
        self.body = "\n".join(lines[2:])
