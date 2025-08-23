"""Base parser class."""
from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Base parser, outlines abstract methods other parsers need to implement."""

    @staticmethod
    @abstractmethod
    def parse(html:str) -> dict:
        """Parses the given html document into an dictionary."""
        ...
