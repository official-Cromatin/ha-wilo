"""Custom entity implementation for cistern level."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength

from .base import WiloBaseEntity


class CisternLevelSensor(WiloBaseEntity, SensorEntity):
    """Sensor for cistern level."""

    def __init__(self, coordinator, pump, category_key, value_key):
        super().__init__(coordinator, pump, category_key, value_key)
        self._category_key = category_key
        self._value_key = value_key
        self._attr_translation_key = "cistern_level"
        self._attr_unique_id = f"{self._attr_base_unique_id}_{self._attr_translation_key}"
        self._attr_native_unit_of_measurement = UnitOfLength.CENTIMETERS
        self._attr_device_class = SensorDeviceClass.DISTANCE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        raw = self.get_coordinator_value()
        try:
            return float(raw.lower().replace("cm", "").strip())
        except ValueError:
            return None
