from urllib.parse import ParseResult, urlparse, quote_plus
from enum import IntEnum, auto

"""
This class contains static methods for common tasks
"""
class Utils:
    class LogType(IntEnum):
        Info = auto()
        Warning = auto()
        Error = auto()

    """
    Returns the url encoded string id for a repository
    """
    @staticmethod
    def str_id_for_url(url: str) -> str:
        repository_url: ParseResult = urlparse(url.replace(".git", ""))
        return quote_plus(repository_url.path[1:])

    @staticmethod
    def log(type: LogType, *message: str) -> None:
        prefix = ""
        if (type == Utils.LogType.Info):
            prefix = "Info:"
        elif (type == Utils.LogType.Warning):
            prefix = "Warning:"
        elif (type == Utils.LogType.Error):
            prefix = "Error"

        print(prefix, *message)
