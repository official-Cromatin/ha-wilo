"""Providers are implemented by each provider alongside and offer stored data via property functions."""

from .base import BaseDatastore
from .rain3 import Rain3Datastore

__all__ = ["BaseDatastore", "Rain3Datastore"]
Datastores = Rain3Datastore