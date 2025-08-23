"""Pump classes group assigned sensors and define endpoint specifications."""

from .base import BasePump
from .rain3 import Rain3Pump

__all__ = ["BasePump", "Rain3Pump"]
