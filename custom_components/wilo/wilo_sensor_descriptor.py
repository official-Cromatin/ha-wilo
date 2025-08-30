"""Implements the EntityDescriptor dataclass."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from datastores import BaseDatastore

from homeassistant.components.sensor import (
    EntityCategory,
    SensorDeviceClass,
    SensorStateClass,
)


@dataclass
class WiloEntityDescriptor:
    """Describes the main entity attributes."""

    partial_unique_entity_id: str
    translation_key: str
    device_class: SensorDeviceClass | None
    state_class: SensorStateClass | None
    native_unit_of_measurement: str | None
    unit_of_measurement: str | None
    entity_registry_enabled_default: bool = True
    entity_category: EntityCategory | None = None
    value_update_function: Callable[[BaseDatastore], Any]
