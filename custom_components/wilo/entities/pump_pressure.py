"""Custom entity implementation for pressure."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfPressure

from .base import WiloBaseEntity


class PumpPressureSensor(WiloBaseEntity, SensorEntity):
    """Sensor for pump pressure."""

    def __init__(self, coordinator, pump, category_key, value_key):
        super().__init__(coordinator, pump, category_key, value_key)
        self._category_key = category_key
        self._value_key = value_key
        self._attr_native_unit_of_measurement = UnitOfPressure.BAR
        self._attr_device_class = SensorDeviceClass.PRESSURE
        self._attr_translation_key = "pump_pressure"
        # self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        raw = self.get_coordinator_value()
        try:
            return float(raw.lower().replace("bar", "").strip())
        except ValueError:
            return None
