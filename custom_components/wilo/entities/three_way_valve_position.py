"""Custom entity implementation for pressure."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfLength

from .base import WiloBaseEntity


class ThreeWayValvePositionSensor(WiloBaseEntity, SensorEntity):
    """Sensor for pump pressure."""

    def __init__(self, coordinator, pump, category_key, value_key):
        super().__init__(coordinator, pump, category_key, value_key)
        self._category_key = category_key
        self._value_key = value_key
        self._attr_translation_key = "valve_position"
        self._attr_unique_id = f"{self._attr_base_unique_id}_{self._attr_translation_key}"

    @property
    def native_value(self) -> str:
        raw:str = self.get_coordinator_value()
        return raw.lower().replace(" ", "_")
