"""Parsers are used to parse html documents into dictionaries."""

from typing import Union

from .alarm import AlarmParser
from .base import BaseParser
from .settings import SettingsParser
from .status import StatusParser

WiloParser = Union[AlarmParser, SettingsParser, StatusParser]

__all__ = ["AlarmParser", "BaseParser", "SettingsParser", "StatusParser"]
