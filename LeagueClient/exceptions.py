from typing import Optional

__all__ = ["LeagueClientExcepionts", "LeagueClientClosed"]


class LeagueClientExcepionts(Exception):
    """
    Base class for all exceptions.

    """


class LeagueClientClosed(LeagueClientExcepionts):
    """
    Raised when league client is not open.
    """

    message: Optional[str] = "The League client must be running!"

    def __init__(self, message: Optional[str]):
        self.message = message
        super().__init__(self.message)
