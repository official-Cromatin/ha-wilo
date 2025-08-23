"""Parsers are used to parse html documents into dictionaries."""

from .alarm import AlarmParser
from .base import BaseParser
from .settings import SettingsParser
from .status import StatusParser

__all__ = ["AlarmParser", "BaseParser", "SettingsParser", "StatusParser"]
