"""Basic error classes."""
from dataclasses import dataclass


class RobotoError(Exception):
    """Base class for Roboto errors."""


@dataclass
class BotAPIError(Exception):
    """Signal error with an API access."""

    error_code: int
    description: str

    def __post_init__(self):
        super().__init__(f'Error {self.error_code}: {self.description}')
