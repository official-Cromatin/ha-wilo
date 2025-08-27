"""Base entity implementation all custom entites inherit from."""
from typing import Any
import regex

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

    @staticmethod
    def calculate_minutes_from_string(value:str) -> int | None:
        """Calculates the minutes from a string formatted in different ways."""
        pattern = regex.compile(
            r"""
            (?:(?P<days>\d+)\s*(?:d|days))?
            \s*
            (?:(?P<hours>\d+)\s*(?:h|hours))?
            \s*
            (?:(?P<minutes>\d+)\s*(?:m|min|minutes))?
            \s*
            (?:(?P<seconds>\d+)\s*(?:s|sec|seconds))?
            """,
            regex.VERBOSE | regex.IGNORECASE
        )
        match = pattern.fullmatch(value.strip())
        if match:
            days = int(match.group("days") or 0)
            hours = int(match.group("hours") or 0)
            minutes = int(match.group("minutes") or 0)
            seconds = int(match.group("seconds") or 0)
            return days * 1440 + hours * 60 + minutes + (seconds // 60)
        return None

    @property
    def device_info(self) -> DeviceInfo:
        print("DEVICE", self._pump.device_info)
        return self._pump.device_info
