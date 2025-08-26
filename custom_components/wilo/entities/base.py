"""Base entity implementation all custom entites inherit from."""
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class WiloBaseEntity(CoordinatorEntity):
    """Base entity for Wilo devices."""

    def __init__(self, coordinator, pump, category_key:str, value_key:str):
        super().__init__(coordinator)
        self._pump = pump
        self._category_key = category_key
        self._value_key = value_key
        self._attr_base_unique_id = pump.unique_id

    def get_coordinator_value(self) -> Any:
        """Returns the coordinator value assigned to this entity."""
        category = self.coordinator.data.get(self._category_key)
        return category.get(self._value_key)

    @property
    def device_info(self) -> DeviceInfo:
        print("DEVICE", self._pump.device_info)
        return self._pump.device_info
