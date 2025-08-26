"""Class to represent the Rain3 pump."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DOMAIN
from ..entities import PumpPressureSensor, PumpStateSensor, CisternLevelSensor
from ..parsers import AlarmParser, SettingsParser, StatusParser
from .base import BasePump


class Rain3Pump(BasePump):
    """Represents the Wilo Rain3 pump model."""

    ENTITY_MAP = {
        ("state", "MP"): PumpStateSensor,
        ("state", "Pressure"): PumpPressureSensor,
        ("state", "Level"): CisternLevelSensor
    }

    def __init__(self, ip:str, device_id:int):
        super().__init__(
            ip,
            device_id,
            "rain3",
            {
                "identity": StatusParser,
                "state": StatusParser,
                "setup": SettingsParser,
                "errors": AlarmParser,
                "installation": SettingsParser,
                "settings": SettingsParser,
                "download": StatusParser
            }
        )

    async def create_device_info(self, hass:HomeAssistant):
        device_data = await self.update(hass)

        self._device_info = DeviceInfo(
            configuration_url=f"http://{self._ip}",
            connections={("ip", self._ip)},
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer=DOMAIN.capitalize(),
            model=self._model.capitalize(),
            name=f"{DOMAIN.capitalize()} {self._model.capitalize()} ({self._ip})",
            serial_number=device_data["identity"]["Serial number"],
            sw_version=device_data["identity"]["SW Version"],
        )
