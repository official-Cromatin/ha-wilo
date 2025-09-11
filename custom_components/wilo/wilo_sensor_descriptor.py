"""Implements the EntityDescriptor dataclass."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import (
    EntityCategory,
    SensorDeviceClass,
    SensorStateClass,
)

from .datastores import BaseDatastore


@dataclass
class WiloSensorDescriptor:
    """Describes the main sensor attributes."""

    partial_unique_entity_id: str
    translation_key: str
    value_update_function: Callable[[BaseDatastore], Any]
    extra_value_update_function: Callable[[BaseDatastore], Any] = lambda *args, **kwargs: None
    device_class: SensorDeviceClass | None = None
    native_unit_of_measurement: str | None = None
    unit_of_measurement: str | None = None
    state_class: SensorStateClass | None = None
    entity_registry_enabled_default: bool = True
    entity_category: EntityCategory | None = None

@dataclass
class WiloBinarySensorDescriptor:
    """Describes the main binary sensor attributes."""

    partial_unique_entity_id: str
    translation_key: str
    value_update_function: Callable[[BaseDatastore], Any]
    extra_value_update_function: Callable[[BaseDatastore], Any] = lambda *args, **kwargs: None
    device_class: BinarySensorDeviceClass | None = None
    entity_registry_enabled_default: bool = True
    entity_category: EntityCategory | None = None


WiloSensorDescriptors = WiloSensorDescriptor | WiloBinarySensorDescriptor
