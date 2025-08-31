"""Implements the datastore for the rain3 pump."""

from typing import Any

from .base import BaseDatastore

class Rain3Datastore(BaseDatastore):
    """Datastore used to make fetched data accessible to rain3 sensors."""

    @property
    def serial_number(self) -> str:
        """Serial number of the pump."""
        return self._data["identity"]["Serial number"]

    @property
    def software_version(self) -> str:
        """Software version running on the controller."""
        return self._data["identity"]["SW Version"]
