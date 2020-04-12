from urllib.parse import ParseResult, urlparse, quote_plus

"""
This class contains static methods for common tasks
"""
class Utils:
    """
    Returns the url encoded string id for a repository
    """
    @staticmethod
    def str_id_for_url(url: str) -> str:
        repository_url: ParseResult = urlparse(url.replace(".git", ""))
        return quote_plus(repository_url.path[1:])
