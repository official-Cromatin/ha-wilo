"""Custom entity implementation for calciumcarbonate protection timer."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime

from .base import WiloBaseEntity


class CalcProtectionTimerSensor(WiloBaseEntity, SensorEntity):
    """Sensor for calciumcarbonate protection timer."""

    def __init__(self, coordinator, pump, category_key, value_key):
        super().__init__(coordinator, pump, category_key, value_key)
        self._category_key = category_key
        self._value_key = value_key
        self._attr_translation_key = "calc_protection_timer"
        self._attr_unique_id = f"{self._attr_base_unique_id}_{self._attr_translation_key}"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_unit_of_measurement = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTime.HOURS

    @property
    def native_value(self) -> float | None:
        raw = self.get_coordinator_value()
        try:
            return self.calculate_minutes_from_string(raw) / 60
        except ValueError:
            return None
