"""Defines the base datastore pumps implement alongside to present data to entites."""

from typing import Any


class BaseDatastore:
    """Base class all providers implement alongside to store data in uniform structure."""
    def __init__(self, data:dict[str, Any]):
        """Initialize the PumpData class.

        :param dict[str, Any] data:
            Dictionary containing extracted data.

        Note: Use .update instead of creating a new instance.
        """
        self._data = data

    def update(self, data:dict[str, Any]):
        """Replaces the stored data with the new provided version.

        :param dict[str, Any] data:
            New dictionary replacing the internally stores one.
        """
        self._data = data

    @property
    def data(self) -> dict[str, Any]:
        """Returns the internally stored dictonary.

        :returns dict[str, Any]:
            Dictionary containing extracted data by the pump provider.
        """
        return self._data
