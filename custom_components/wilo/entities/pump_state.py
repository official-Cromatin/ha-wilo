"""Custom entity implementation for pump state."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .base import WiloBaseEntity


class PumpStateSensor(WiloBaseEntity, BinarySensorEntity):
    """Sensor for pump state."""

    def __init__(self, coordinator, pump, category_key, value_key):
        super().__init__(coordinator, pump, category_key, value_key)
        self._category_key = category_key
        self._value_key = value_key
        self._attr_translation_key = "pump_state"
        self._attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self) -> bool:
        return self.get_coordinator_value() == "ON"
