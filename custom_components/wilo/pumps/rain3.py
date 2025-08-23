"""Class to represent the Rain3 pump."""
from parsers import AlarmParser, SettingsParser, StatusParser

from .base import BasePump


class Rain3Pump(BasePump):
    """Represents the Wilo Rain3 pump model."""

    def __init__(self, ip:str):
        super().__init__(
            ip,
            {
                "identity": StatusParser,
                "state": StatusParser,
                "setup": SettingsParser,
                "errors": AlarmParser,
                "installation": SettingsParser,
                "settings": SettingsParser,
                "download": StatusParser
            }
        )
