"""Basic error classes."""


class RobotoError(Exception):
    """Base class for Roboto errors."""


class BotAPIError(Exception):
    """Signal error with an API access."""
