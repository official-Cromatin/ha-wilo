"""Providers are implemented by each provider alongside and offer stored data via property functions."""

from .base import BaseDatastore

__all__ = ["BaseDatastore"]
Datastores = BaseDatastore