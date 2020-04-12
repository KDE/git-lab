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

    class TextFormatting:
        purple: str = "\033[0;95m"
        cyan: str = "\033[0;36m"
        darkcyan: str = "\033[0;36m"
        blue: str = "\033[0;34m"
        green: str = "\033[0;32m"
        yellow: str = "\033[0;33m"
        red: str = "\033[0;31m"
        lightred: str = "\033[1;31m"
        bold: str = "\033[1m"
        underline: str = "\033[4m"
        end: str = "\033[0m"

    """
    Returns the url encoded string id for a repository
    """
    @staticmethod
    def str_id_for_url(url: str) -> str:
        repository_url: ParseResult = urlparse(url.replace(".git", ""))
        return quote_plus(repository_url.path[1:])

    @staticmethod
    def log(type: LogType, *message: str) -> None:
        prefix = Utils.TextFormatting.bold
        if (type == Utils.LogType.Info):
            prefix += "Info"
        elif (type == Utils.LogType.Warning):
            prefix += Utils.TextFormatting.yellow + "Warning" + Utils.TextFormatting.end
        elif (type == Utils.LogType.Error):
            prefix += Utils.TextFormatting.red + "Error" + Utils.TextFormatting.end

        prefix += Utils.TextFormatting.end

        if (len(prefix) > 0):
            prefix += ":"

        print(prefix, *message)
