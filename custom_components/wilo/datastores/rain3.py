"""Implements the datastore for the rain3 pump."""

from typing import Any

from .base import BaseDatastore

class Rain3Datastore(BaseDatastore):
    """Datastore used to make fetched data accessible to rain3 sensors."""
