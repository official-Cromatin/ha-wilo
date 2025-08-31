"""Providers implement update functionality and describe supported entities."""

from .base import BaseProvider
from .rain3 import Rain3Provider

__all__ = ["BaseProvider", "Rain3Provider"]

Providers = Rain3Provider
