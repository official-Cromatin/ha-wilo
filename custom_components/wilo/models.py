"""Describes supported pump models as an enum class."""

from enum import Enum


class WiloModels(Enum):
    """Contains supported pump models by the wilo integration."""
    RAIN3 = "rain3"
